import os
from copy import deepcopy

import pytest
from deepdiff import DeepDiff, grep

from cidc_schemas.json_validation import load_and_validate_schema
from cidc_schemas.prism import (
    PROTOCOL_ID_FIELD_NAME,
    ArtifactInfo,
    merge_artifacts,
    merge_clinical_trial_metadata,
    prismify,
)
from cidc_schemas.template import Template
from cidc_schemas.template_reader import XlTemplateReader

from .cidc_test_data import PrismTestData, list_test_data


@pytest.fixture(params=list_test_data(), ids=lambda ptd: ptd.upload_type)
def prism_test(request):
    return request.param


@pytest.fixture
def ct_validator():
    return load_and_validate_schema("clinical_trial.json", return_validator=True)


def assert_metadata_matches(received: dict, expected: dict, upload_entries: list):
    """Check that the `received` metadata dict matches the `expected` metadata dict."""
    # Take the difference of the received patch and the expected patch.
    # We expect these patches to differ by upload placeholder UUID only,
    # so the number of differences should equal the number of expected
    # upload entries.
    diff = DeepDiff(expected, received)

    if upload_entries and diff:
        assert len(diff) == 2, str(
            diff
        )  # only "values_changed" and "dictionary_item_added"
        assert len(diff["dictionary_item_added"]) == len(upload_entries), str(diff)
        assert len(diff["values_changed"]) == len(upload_entries), str(diff)
        for changed_key in diff["values_changed"].keys():
            assert changed_key.endswith("['upload_placeholder']"), str(diff)
        for new_key in diff["dictionary_item_added"]:
            assert new_key.endswith("['facet_group']"), str(diff)
    else:
        # For manifest uploads, we expect no artifacts, so there should
        # be no difference between expected and received trial objects.
        assert diff == {}


def test_gcs_uri_format(prism_test: PrismTestData):
    for ue in prism_test.upload_entries:
        prot_id = prism_test.base_trial[PROTOCOL_ID_FIELD_NAME]
        assay = prism_test.upload_type.split("_", 1)[0]
        assert ue.gs_key.startswith(f"{prot_id}/{assay}")


def test_prismify(prism_test: PrismTestData, monkeypatch):
    # TODO: make tests work for all manifest types. It was a lot of work to make one work
    if prism_test.upload_type != "plasma":
        pytest.skip("Manifest tests not set up yet")
    monkeypatch.setattr(
        "cidc_schemas.prism.core._encrypt", lambda x: f"test_encrypted({str(x)!r})"
    )

    monkeypatch.setattr("cidc_schemas.prism.core._check_encrypt_init", lambda: None)

    # Run prismify on the given test case
    patch, upload_entries, errs = prismify(*prism_test.prismify_args)

    # Ensure no errors resulted from the prismify run
    assert len(errs) == 0, "\n".join([str(e) for e in errs])

    # Compare the received upload entries with the expected upload entries.
    # These should differ by upload placeholder UUID only.
    received = [
        (e.local_path, e.gs_key, e.metadata_availability) for e in upload_entries
    ]
    expected = [
        (e.local_path, e.gs_key, e.metadata_availability)
        for e in prism_test.upload_entries
    ]
    assert sorted(expected) == sorted(received)
    for received, expected in zip(
        sorted(upload_entries), sorted(prism_test.upload_entries)
    ):
        assert received.local_path == expected.local_path
        assert received.gs_key == expected.gs_key
        assert received.metadata_availability == expected.metadata_availability

    # Compare the received and expected prism metadata patches
    assert_metadata_matches(
        received=patch,
        expected=prism_test.prismify_patch,
        upload_entries=upload_entries,
    )


def test_merge_patch_into_trial(prism_test: PrismTestData, ct_validator):
    # Merge the prismify patch into the base trial metadata
    result, errs = merge_clinical_trial_metadata(
        prism_test.prismify_patch, prism_test.base_trial
    )

    # Ensure no errors resulted from the merge
    assert len(errs) == 0, "\n".join([str(e) for e in errs])

    # Ensure that the merge result passes validation
    ct_validator.validate(result)

    target = prism_test.target_trial
    assert_metadata_matches(
        received=result, expected=target, upload_entries=prism_test.upload_entries
    )


def test_merge_artifacts(prism_test: PrismTestData, ct_validator):
    # Some upload types won't have any artifacts to merge
    if len(prism_test.upload_entries) == 0:
        return

    # Merge the upload entries into the prismify patch
    uuids_and_artifacts = []
    patch = deepcopy(prism_test.prismify_patch)
    patch, artifact_results = merge_artifacts(
        patch,
        [
            ArtifactInfo(
                artifact_uuid=entry.upload_placeholder,
                object_url=entry.gs_key,
                upload_type=prism_test.upload_type,
                file_size_bytes=0,
                uploaded_timestamp="",
                md5_hash="foo",
                crc32c_hash="bar",
            )
            for entry in prism_test.upload_entries
        ],
    )
    for entry, (artifact, additional_metadata) in zip(
        prism_test.upload_entries, artifact_results
    ):
        # Check that artifact has expected fields for the given entry
        assert artifact["object_url"] == entry.gs_key
        assert artifact["upload_placeholder"] == entry.upload_placeholder
        assert additional_metadata != {}

        # Keep track of the artifact metadata
        uuids_and_artifacts.append((entry.upload_placeholder, artifact, entry))

    # Check that the artifact objects have been merged in the right places.
    placeholder_key = "['upload_placeholder']"
    for uuid, artifact, entry in uuids_and_artifacts:
        # Get the path in the *original* patch to the placeholder uuid.
        paths = (prism_test.prismify_patch | grep(uuid))["matched_values"]

        assert len(paths) == 1, "UUID should only occur once in a metadata patch"
        path = paths.pop()
        assert path.endswith(
            placeholder_key
        ), f"UUID values should have key {placeholder_key}"
        path = path[: -len(placeholder_key)]

        # Ensure that evaluating this same path in the *new* patch gets the expected
        # artifact metadata dictionary.
        assert eval(path, {}, {"root": patch}) == artifact

    # Merge the patch-with-artifacts into the base trial
    result, errs = merge_clinical_trial_metadata(patch, prism_test.base_trial)
    assert len(errs) == 0, "\n".join([str(e) for e in errs])

    # Make sure the modified patch is still valid
    ct_validator.validate(result)


def test_prismify_hande_w_errors(monkeypatch):
    monkeypatch.setattr(
        "cidc_schemas.prism.core._encrypt", lambda x: f"test_encrypted({str(x)!r})"
    )
    monkeypatch.setattr("cidc_schemas.prism.core._check_encrypt_init", lambda: None)
    xlsx_path = os.path.join("tests", "data", "hande_err_template.xlsx")
    reader, _ = XlTemplateReader.from_excel(xlsx_path)
    template = Template.from_type("hande")
    _, _, errs = prismify(reader, template)
    assert len(errs) == 1
    assert (
        str(errs[0]) == "Expected .none for 'annotated image' but got '.svs' instead."
    )


def test_prismify_do_not_merge_entry_number(monkeypatch):
    xlsx_path = os.path.join("tests", "data", "pbmc_manifest_valid.xlsx")
    reader, _ = XlTemplateReader.from_excel(xlsx_path)
    template = Template.from_type("pbmc")

    entry_number_field_def = template.key_lu["samples"]["entry (#)"]
    # confirm entry number does not have a FieldDef as it is a do_not_merge property
    assert not entry_number_field_def

    merged_data, _, errs = prismify(reader, template)
    assert len(errs) == 0
    merged_samples = merged_data["participants"][0]["samples"]
    # confirm shipping_entry_number property is not in either of the merged samples
    assert "shipping_entry_number" not in merged_samples[0]
    assert "cimac_id" in merged_samples[0]
    assert merged_samples[0]["cimac_id"] == "CQGK016CU.01"
    assert "shipping_entry_number" not in merged_samples[1]
    assert "cimac_id" in merged_samples[1]
    assert merged_samples[1]["cimac_id"] == "CQGK016CU.02"
