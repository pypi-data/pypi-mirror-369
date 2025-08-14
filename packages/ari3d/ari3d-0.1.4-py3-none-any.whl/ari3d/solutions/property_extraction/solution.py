# for old versions see https://gitlab.com/ida-mdc/ari3d/-/tree/b74a5db7a4e69dc99be10ef3aa47a83fb5dc70b6/src/ari3d/solutions/property_extraction
from album.runner.api import get_args, setup

env_file = """name:  property_extraction
channels:
  - conda-forge
dependencies:
  - python=3.9
  - setuptools<=80.0
  - imagecodecs
  - pip
  - pip:
      - numpy
      - pandas
      - scikit-image
      - anndata
      - joblib
      - scipy
      - nibabel
      - tqdm
"""


def run():
    from pathlib import Path

    import numpy as np
    from io_op import (
        convert_h5ad,
        load_and_process_labelled_image,
        load_non_binary_images,
    )
    from properties import (
        PVE_gradient,
        calculate_properties,
        calculate_surface_areas,
        count_erosions,
    )
    from utils import (
        delete_small_particles,
        erosion_based_on_labels,
        extract_histograms,
        filter_mask_image,
        get_unique_labels,
        replace_extra_rows_with_zeros,
    )

    ### link to inputs
    # Size threshold in number of voxels, default 1000
    size_threshold = get_args().Size_threshold  # 800
    # Defines the number of logical processors used in paralel. -1 is default (uses all)
    # Only change if it crashes.
    numb_threads = get_args().numberTreads  # -1
    # Stepsize for creating mesh (called mesh size in window - resolution of mesh)
    stepsize = get_args().Stepsize  # 1
    # Voxel spacing for creating mesh (keep constant)
    voxel_spacing = (1, 1, 1)
    # Enter angle spacing for calculationg Feret dia
    angle_spacing = get_args().Angle_spacing  # 10
    # voxel size in micron
    voxel_size = get_args().Voxel_size  # 16
    background_mean = get_args().Background_mean  # 6600
    # To load only part of the data
    start_slice = get_args().start_slice  # If loading all data set to: None
    end_slice = get_args().end_slice

    if start_slice == -1:
        start_slice = None

    if end_slice == -1:
        end_slice = None

    #################################################################################
    ############################### Load-Save Paths #################################
    ### it reads tif, tiff, nii.gz and nii

    path = Path(get_args().path)
    # Load binary image with particle mask
    binary_image_path = path.joinpath("mask")
    print(binary_image_path)
    # Load non binary image (grey-scale 16bit)
    non_binary_image_path = path.joinpath("gray")
    print(non_binary_image_path)
    # save geometrical properties
    path_to_save_geometrical_properties = path.joinpath("analysis", "Properties.csv")
    # save inner histograms (inside the particle without the eroded voxels)
    path_to_save_inner_volume_histograms = path.joinpath(
        "analysis", "Inner_histograms.h5ad"
    )
    # save outer (surface layers consisting of all voxels eroded) volume histograms
    path_to_save_outer_volume_histograms = path.joinpath(
        "analysis", "Outer_histograms.h5ad"
    )
    # save bulk histograms (= Inner + Outer)
    path_to_save_bulk_histogram = path.joinpath("analysis", "Bulk_histograms.h5ad")
    # save mesh histograms
    path_to_save_surface_mesh_histograms = path.joinpath(
        "analysis", "Surface_histogram.h5ad"
    )
    # save bulk histograms obtained sfter sobel and smoothening
    path_to_save_bulk_eroded_histogram = path.joinpath(
        "analysis", "Eroded_histograms.h5ad"
    )
    # save gradient
    path_to_save_gradient = path.joinpath("analysis", "Gradient.csv")

    ###################################################################################
    ########################### load the images from stacks ###########################
    print("loading from:", path)

    label_mask, binary_mask = load_and_process_labelled_image(
        binary_image_path, start_slice, end_slice
    )
    print("Label loaded!")

    gray_scale_volume = load_non_binary_images(
        non_binary_image_path, start_slice, end_slice
    )
    print("Grey image loaded!")

    unique_labels = get_unique_labels(label_mask)
    print("Image labeled loaded!")

    ###################################################################################
    ########################### Image processing ######################################

    # prepare label mask, binary mask
    label_mask, binary_mask_rm_small, gray_scale_thresh = delete_small_particles(
        label_mask, binary_mask, gray_scale_volume, size_threshold
    )

    # remove non unique labels
    label_mask_filtered = filter_mask_image(label_mask, unique_labels)
    del label_mask

    unique_labels = np.unique(label_mask_filtered)

    # remove background from unique_labels
    unique_labels = unique_labels[unique_labels != 0]

    # log output
    print("Number of particles after processing:", len(unique_labels))

    # get the surface area of the label mask
    print("Calculating surface areas...")
    surface_areas_df = calculate_surface_areas(
        label_mask_filtered, unique_labels, voxel_spacing, stepsize
    )

    # PVE gradient dataset
    print("Calculating PVE Gradients...")
    surface_properties_mean_intensity, eroded_image_1, eroded_image_2 = PVE_gradient(
        binary_mask_rm_small, gray_scale_thresh, label_mask_filtered, background_mean
    )
    surface_properties_mean_intensity["Ratio"] = surface_properties_mean_intensity[
        "Gradient_2"
    ]
    surface_properties_mean_intensity.to_csv(path_to_save_gradient)

    # count for each row number of erosions of which the gradient is < 0.9 or > 1
    print("Performing optimal number of erosions ...")
    surface_properties_mean_intensity[
        "no_of_erosions"
    ] = surface_properties_mean_intensity.apply(count_erosions, axis=1)
    final_eroded_image = erosion_based_on_labels(
        label_mask_filtered, surface_properties_mean_intensity
    )

    print("Processing finished!")

    #################################################################################
    ############################### HISTOGRAMS ######################################
    # BULK HISTOGRAMS
    print("Starting bulk histogram extraction...")
    bulk_histograms = extract_histograms(
        label_mask_filtered, gray_scale_thresh, numb_threads
    )

    # INNER HISTOGRAM
    print("Starting inner volume histogram extraction...")
    inner_volume_labels = final_eroded_image * label_mask_filtered
    inner_volume_histograms = extract_histograms(
        inner_volume_labels, gray_scale_thresh, numb_threads
    )
    del inner_volume_labels, final_eroded_image

    inner_volume_histograms = replace_extra_rows_with_zeros(
        bulk_histograms, inner_volume_histograms
    )

    # OUTER HISTOGRAMS
    print("Starting outer volume histogram extraction...")
    outer_volume_histograms = bulk_histograms - inner_volume_histograms
    outer_volume_histograms[outer_volume_histograms < 0] = 0
    convert_h5ad(inner_volume_histograms, path_to_save_inner_volume_histograms)
    convert_h5ad(outer_volume_histograms, path_to_save_outer_volume_histograms)

    # SURFACE MESH HISTOGRAM
    # Gets the voxel layer at 1 voxel depth surface mesh and convert/save as h5ad
    binary_surface_mesh_eroded2 = eroded_image_1 - eroded_image_2
    binary_surface_mesh_eroded2_labels = (
        binary_surface_mesh_eroded2 * label_mask_filtered
    )
    del binary_surface_mesh_eroded2
    histograms_surface_mesh = extract_histograms(
        binary_surface_mesh_eroded2_labels, gray_scale_thresh, numb_threads
    )
    histograms_surface_mesh = replace_extra_rows_with_zeros(
        bulk_histograms, histograms_surface_mesh
    )

    # Save the histograms
    convert_h5ad(histograms_surface_mesh, path_to_save_surface_mesh_histograms)
    convert_h5ad(bulk_histograms, path_to_save_bulk_histogram)

    ##################################################################################################
    ############################################# PROPERTIES #########################################
    # List of properties
    # area; #bbox; #bbox_area; #centroid; #convex_image; #coords; #equivalent_diameter; #euler_number; #extent
    # feret_diameter_max; #filled_area; #filled_image; #image; #inertia_tensor; #inertia_tensor_eigvals; #intensity_image
    # label; #local_centroid; #major_axis_length; #max_intensity; #mean_intensity; #min_intensity; #minor_axis_length
    # moments; #moments_central; #moments_normalized; #slice; #solidity; #weighted_centroid; #weighted_local_centroid
    # weighted_moments; #weighted_moments_central; #weighted_moments_normalized

    # From the list above, add to the list the properties to be calculated. Note: area is actually volume

    # ['label', 'area', 'min_intensity', 'max_intensity', 'equivalent_diameter', 'mean_intensity', 'bbox', 'centroid']
    properties = get_args().properties_list.split(",")

    # Call the function with appropriate properties
    properties_bulk = calculate_properties(
        label_mask_filtered, gray_scale_thresh, properties, voxel_size, surface_areas_df
    )
    properties_bulk.to_csv(path_to_save_geometrical_properties)


setup(
    group="de.mdc",
    name="property_extraction",
    version="0.1.0",
    title="Extracts histograms and properties from labelled 3D images",
    description="property_extraction",
    solution_creators=["Jan Philipp Albrecht", "Jose Ricardo da Assuncao Guadiniho"],
    tags=["interactivity", "workflow"],
    license="MIT",
    documentation=[],
    covers=[],
    album_api_version="0.7.0",
    run=run,
    args=[
        {
            "name": "path",
            "type": "directory",
            "required": True,
            "description": "Path to the directory containing masks and grey images",
        },
        {
            "name": "properties_list",
            "type": "string",
            "required": True,
            "description": "List of properties to be calculated seperated by comma without spaces",
        },
        {
            "name": "Size_threshold",
            "type": "integer",
            "required": False,
            "description": "Size threshold in number of voxels, default 800",
        },
        {
            "name": "numberTreads",
            "type": "integer",
            "required": False,
            "description": "Defines the number of logical processors used in parallel. -1 is default (uses all)",
        },
        {
            "name": "Stepsize",
            "type": "integer",
            "required": False,
            "description": "Stepsize for creating mesh (called mesh size in window - resolution of mesh)",
        },
        {
            "name": "Angle_spacing",
            "type": "integer",
            "required": False,
            "description": "Enter angle spacing for calculating Feret diameter",
        },
        {
            "name": "Voxel_size",
            "type": "integer",
            "required": False,
            "description": "Voxel size in micron",
        },
        {
            "name": "Background_mean",
            "type": "integer",
            "required": False,
            "description": "Background mean value",
        },
        {
            "name": "start_slice",
            "type": "integer",
            "required": False,
            "description": "To load only part of the data, set to None if loading all data",
        },
        {
            "name": "end_slice",
            "type": "integer",
            "required": False,
            "description": "To load only part of the data, set to None if loading all data",
        },
    ],
    dependencies={"environment_file": env_file},
)
