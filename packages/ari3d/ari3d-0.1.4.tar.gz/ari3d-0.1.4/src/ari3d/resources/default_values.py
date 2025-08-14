"""Module for default values used in the ari3d project."""
import os
from enum import Enum

N_JOBS = os.cpu_count() - 1 if os.cpu_count() > 1 else 1


class DefaultValues(Enum):
    """Add an entry here to initialize default attributes for this project."""

    gray_folder_name = "gray"
    analysis_folder_name = "analysis"
    raw_folder_name = "raw"
    project_files_folder_name = "project"
    report_folder_name = "report"
    masks_folder_name = "mask"
    segmentation_folder_name = ".particle_seg"
    segmentation_input_folder_name = "images"

    instance_segmentation_layer_name = "segmentation"
    semantic_segmentation_layer_name = "binary_segmentation"
    label_list_file_name = "labelList.csv"
    label_list_header = [
        "bbox-0",
        "bbox-1",
        "bbox-2",
        "bbox-3",
        "bbox-5",
        "centroid-0",
        "centroid-1",
        "centroid-2",
        "Label Index",
    ]
    label_list_label_index = "Label Index"
    instance_segmentation_tiff_name = "instance_mask.tiff"
    properties_file_name = "Properties.csv"
    properties_file_label_index = "label"

    n_jobs = N_JOBS

    forbidden_project_names = [
        "gray",
        "grey",
        "binary",
        "analysis",
        "raw",
        "project",
        "report",
        ".particle_seg",
        ".git",
        ".github",
        ".vscode",
        "resources",
        "zarr",
        "segmentation",
    ]

    repo_link = "https://gitlab.com/ida-mdc/ari3d.git"
    documentation_link = (
        "https://gitlab.com/ida-mdc/ari3d/-/blob/main/README.md"
    )
    tutorial_link = "https://gitlab.com/ida-mdc/ari3d/-/blob/main/README.md"
    article_link = "https://gitlab.com/ida-mdc/ari3d.git"

    project_description = "ARI3D is an interactive workflow that lets you analyse your mineral particles in micro CT images."  # noqa: E501
    developed_by = (
        "Helmholtz Imaging together with Helmholtz-Zentrum Dresden-Rossendorf"
    )
