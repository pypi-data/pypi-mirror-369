"""CIDC schemas-specific constants relevant to prismifying/merging functionality."""

from typing import Dict


PROTOCOL_ID_FIELD_NAME = "protocol_identifier"

SUPPORTED_ASSAYS = [
    "atacseq_fastq",
    "wes_fastq",
    "wes_bam",
    "olink",
    "cytof",
    "ihc",
    "elisa",
    "rna_fastq",
    "rna_bam",
    "mibi",
    "mif",
    "tcr_adaptive",
    "tcr_fastq",
    "hande",
    "nanostring",
    "clinical_data",
    "misc_data",
    "ctdna",
    "microbiome",
    "mihc",
    "scrnaseq",
    "visium",
]

SUPPORTED_SHIPPING_MANIFESTS = [
    "pbmc",
    "plasma",
    "tissue_slide",
    "normal_blood_dna",
    "normal_tissue_dna",
    "tumor_tissue_dna",
    "tumor_tissue_rna",
    "h_and_e",
    "microbiome_dna",
]
# weird non shipping manifest
SUPPORTED_WEIRD_MANIFESTS = [
    "tumor_normal_pairing",
]
SUPPORTED_MANIFESTS = SUPPORTED_SHIPPING_MANIFESTS + SUPPORTED_WEIRD_MANIFESTS

SUPPORTED_ANALYSES = [
    "atacseq_analysis",
    "cytof_analysis",
    "rna_level1_analysis",
    "tcr_analysis",
    "wes_analysis",
    "wes_tumor_only_analysis",
    "scrnaseq_analysis",
    "visium_analysis",
]

"""
Since most of the definitions are json files which don't allow comments, I'm putting
our scrnaseq_analysis documentation here. These are the files (and folder structure) that are expected in the gcloud
directory to fully create a record for scRNA analysis:
./sample_metadata.csv
./config.yaml
./R_package_versions.csv
./clustering/SRR8318954_clustering.rds
./integration/integrated.rds
./integration/heatmap_plots.zip
./integration/markers.zip
./integration/split_percent_plots.zip
./integration/split_umap_plots.zip
./integration/umap_plots.zip
./report/SRR8318954_report.html
./star/SRR8318954.Aligned.sortedByCoord.out.bam
./star/SRR8318954.Aligned.sortedByCoord.out.bam.bai
./star/SRR8318954.Log.final.out
./star/SRR8318954.Log.out
./star/SRR8318954.Log.progress.out
./star/SRR8318954.SJ.out.tab
./star/SRR8318954.Solo.out/Barcodes.stats
./star/SRR8318954.Solo.out/Gene/Features.stats
./star/SRR8318954.Solo.out/Gene/Summary.csv
./star/SRR8318954.Solo.out/Gene/UMIperCellSorted.txt
./star/SRR8318954.Solo.out/Gene/filtered/features.tsv
./star/SRR8318954.Solo.out/Gene/filtered/barcodes.tsv
./star/SRR8318954.Solo.out/Gene/filtered/matrix.mtx
./star/SRR8318954.Solo.out/Gene/raw/features.tsv
./star/SRR8318954.Solo.out/Gene/raw/barcodes.tsv
./star/SRR8318954.Solo.out/Gene/raw/matrix.mtx

These are the files required for visium analysis:
./sample_metadata.csv
./config.yaml
./R_package_versions.csv
./spatial_variable_features/{id}_spatial_variable_features.rds
./report/{id}_report.html
./merge/merged.rds
./{id}_spaceranger.zip
"""

SUPPORTED_TEMPLATES = SUPPORTED_ASSAYS + SUPPORTED_MANIFESTS + SUPPORTED_ANALYSES

# provide a way to get file-path prefix for each upload_type
ASSAY_TO_FILEPATH: Dict[str, str] = {
    # analysis is removed on some
    "atacseq_analysis": "atacseq/",
    "rna_level1_analysis": "rna/",
    "wes_analysis": "wes/",
    "wes_tumor_only_analysis": "wes_tumor_only/",
    # assay specifics removed
    "atacseq_fastq": "atacseq/",
    "rna_bam": "rna/",
    "rna_fastq": "rna/",
    "tcr_adaptive": "tcr/",
    "tcr_fastq": "tcr/",
    "wes_bam": "wes/",
    "wes_fastq": "wes/",
    # special cases
    "clinical_data": "clinical/",
    "participants info": "participants.",
    "samples info": "samples.",
    # invariant
    **{
        k: f"{k}/"
        for k in [
            "cytof_analysis",
            "tcr_analysis",
            "ctdna",
            "cytof",
            "elisa",
            "hande",
            "ihc",
            "microbiome",
            "mibi",
            "mif",
            "misc_data",
            "nanostring",
            "olink",
            "mihc",
            "scrnaseq",
            "scrnaseq_analysis",
            "visium",
            "visium_analysis",
        ]
    },
}
assert all(
    not prefix1.startswith(prefix2)
    for prefix1 in ASSAY_TO_FILEPATH.values()
    for prefix2 in ASSAY_TO_FILEPATH.values()
    if prefix1 != prefix2
), "Prefix codes may not be overlapping"
