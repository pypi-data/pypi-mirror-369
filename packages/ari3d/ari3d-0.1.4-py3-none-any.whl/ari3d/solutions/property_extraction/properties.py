import gc

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from skimage import measure, morphology
from skimage.measure import marching_cubes, mesh_surface_area
from tqdm import tqdm


def calculate_surface_area(label, labels, voxel_spacing, step_size):
    """Calculate the Surface area of the mesh of a label"""
    non_zero_indices = np.argwhere(labels == label)

    # required minimal shape
    if non_zero_indices.shape[0] < 2:
        return 0

    min_indices = non_zero_indices.min(axis=0) - 2
    max_indices = non_zero_indices.max(axis=0) + 2
    min_indices = np.maximum(min_indices, 0)
    max_indices = np.minimum(max_indices, np.array(labels.shape) - 1)

    # get the isolated regions
    isolated_region = labels[
        min_indices[0] : max_indices[0] + 1,
        min_indices[1] : max_indices[1] + 1,
        min_indices[2] : max_indices[2] + 1,
    ]

    # get the label mask of the isolated region
    label_mask = (isolated_region == label).astype(np.uint8)
    label_mask[label_mask != 1] = 0

    # minimum required shape of the mask
    if np.any(np.array(label_mask.shape) < 2) or label_mask.sum() == 0:
        return 0

    # get spatial coordinates for the Volume - unique mesh vertices, triangles as face with exactly three indices.
    verts, faces, _, _ = marching_cubes(
        label_mask, level=0, spacing=voxel_spacing, step_size=step_size
    )

    # compute surface area, given vertices and triangular faces
    surface_area = mesh_surface_area(verts, faces)

    # free space
    del isolated_region, verts, faces, non_zero_indices, min_indices, max_indices
    return surface_area


def calculate_surface_areas(labels, unique_labels, voxel_spacing, step_size):
    """Calculate the surface area of all unique labels."""
    # Parallelizing the process to save time
    results = Parallel(n_jobs=-1)(
        delayed(calculate_surface_area)(
            label, labels, voxel_spacing=voxel_spacing, step_size=step_size
        )
        for label in tqdm(
            unique_labels, desc="Processing Labels", total=len(unique_labels)
        )
    )
    return pd.DataFrame({"label": unique_labels, "Surface Area": results})


def PVE_gradient(binary, gray_scale_thresh, labels, background_mean):
    """Calculate the PVE gradient of the volume."""
    surface_properties_list = []
    eroded_image = binary.astype(int)
    eroded_image_1 = None
    eroded_image_2 = None

    # perform 6 erosion iterations and calculate surface difference
    for i in range(1, 7):
        eroded_image = morphology.binary_erosion(eroded_image).astype(np.uint8)
        if i == 1:  # Store the image after 1 voxel erosion
            eroded_image_1 = eroded_image.copy()
            eroded_image_1 = eroded_image_1.astype(np.uint8)
        if i == 2:  # Store the image after 2 voxel erosions
            eroded_image_2 = eroded_image.copy()
            eroded_image_2 = eroded_image_2.astype(np.uint8)

        # surface difference
        surface_diff = binary - eroded_image
        surface_diff = surface_diff.astype(np.uint8)

        # gray scale image masked with surface difference
        surface_non_binary = gray_scale_thresh * surface_diff
        surface_non_binary = surface_non_binary.astype(np.uint16)

        # get mean intensity of the gray scale image masked with surface difference
        surface_mesh_properties = pd.DataFrame(
            measure.regionprops_table(
                labels, surface_non_binary, properties=["label", "mean_intensity"]
            )
        ).set_index("label")

        # rename columns and append to output list
        surface_mesh_properties = surface_mesh_properties.rename(
            columns={"mean_intensity": f"mean_intensity{i}"}
        )
        surface_properties_list.append(surface_mesh_properties)
        del surface_diff, surface_non_binary, surface_mesh_properties
        gc.collect()

    # convert list to pandas database
    surface_properties = pd.concat(surface_properties_list, axis=1)

    # reset columns
    cols = [f"mean_intensity{i}" for i in range(1, 7)]
    surface_properties = surface_properties[cols]

    # get gradient intensities for the 6 erosion iterations
    gradient_columns = []
    max_mean_intensity = surface_properties.max(axis=1)
    for i in range(1, 7):
        gradient_col_name = f"Gradient_{i}"
        surface_properties[gradient_col_name] = (
            surface_properties[f"mean_intensity{i}"] - background_mean
        ) / (max_mean_intensity - background_mean)
        gradient_columns.append(gradient_col_name)

    return surface_properties, eroded_image_1, eroded_image_2


def count_erosions(row):
    """Count the number of erosion's where the gradient is < 0.9 or larger 1."""
    gradient_cols = row.filter(like="Gradient")
    return sum(1 for value in gradient_cols if value < 0.9 or value > 1)


def calculate_properties(
    labels, gray_scale_thresholded, properties_list, voxel_size, surface_areas_df
):
    """Calculate basic properties given by a list of all particles."""
    bulk_properties = (
        pd.DataFrame(
            measure.regionprops_table(
                labels, gray_scale_thresholded, properties=properties_list
            )
        )
        .set_index("label")
        .rename(columns={"area": "Volume"})
    )
    properties_bulk = surface_areas_df.merge(bulk_properties, how="left", on="label")
    properties_bulk["Volume"] = (
        properties_bulk["Volume"] * voxel_size * voxel_size * voxel_size
    )
    properties_bulk["Surface Area"] = (
        properties_bulk["Surface Area"] * voxel_size * voxel_size
    )
    properties_bulk["equivalent_diameter"] = (
        properties_bulk["equivalent_diameter"] * voxel_size
    )
    properties_bulk["Sphericity"] = (
        np.pi ** (1 / 3) * (6 * properties_bulk["Volume"]) ** (2 / 3)
    ) / (properties_bulk["Surface Area"])

    def process_angles(coords, angle1, angle2, angle3):
        theta1 = np.radians(angle1)
        theta2 = np.radians(angle2)
        theta3 = np.radians(angle3)
        rotation_matrix1 = np.array(
            [
                [np.cos(theta1), -np.sin(theta1), 0],
                [np.sin(theta1), np.cos(theta1), 0],
                [0, 0, 1],
            ]
        )
        rotation_matrix2 = np.array(
            [
                [np.cos(theta2), 0, -np.sin(theta2)],
                [0, 1, 0],
                [np.sin(theta2), 0, np.cos(theta2)],
            ]
        )
        rotation_matrix3 = np.array(
            [
                [1, 0, 0],
                [0, np.cos(theta3), -np.sin(theta3)],
                [0, np.sin(theta3), np.cos(theta3)],
            ]
        )
        rotated_coords = np.dot(coords, rotation_matrix1)
        rotated_coords = np.dot(rotated_coords, rotation_matrix2)
        rotated_coords = np.dot(rotated_coords, rotation_matrix3)
        max_distance = np.max(rotated_coords[:, 0]) - np.min(rotated_coords[:, 0])
        min_distance = np.max(rotated_coords[:, 1]) - np.min(rotated_coords[:, 1])
        depth_distance = np.max(rotated_coords[:, 2]) - np.min(rotated_coords[:, 2])
        return max_distance, min_distance, depth_distance

    def calculate_feret_diameters(label, coords, angle_spacing):
        max_feret_diameter = 0
        min_feret_diameter = np.inf
        angle_combinations = [
            (angle1, angle2, angle3)
            for angle1 in range(0, 180, angle_spacing)
            for angle2 in range(0, 180, angle_spacing)
            for angle3 in range(0, 180, angle_spacing)
        ]
        results = Parallel(n_jobs=-1)(
            delayed(process_angles)(coords, angle1, angle2, angle3)
            for angle1, angle2, angle3 in tqdm(
                angle_combinations, desc=f"Processing label {label}"
            )
        )
        for max_distance, min_distance, depth_distance in results:
            if max_distance > max_feret_diameter:
                max_feret_diameter = max_distance
            if min_distance < min_feret_diameter:
                min_feret_diameter = min_distance
            if depth_distance < min_feret_diameter:
                min_feret_diameter = depth_distance
        return label, max_feret_diameter, min_feret_diameter

    # Filter region_coords to include only labels in unique_labels
    #### link to ferets
    # region_coords_filtered = [(region.label, region.coords) for region in measure.regionprops(labels, intensity_image=li_thresholded, cache=False, extra_properties=None) if region.label in unique_labels]
    # results = Parallel(n_jobs=-1)(delayed(calculate_feret_diameters)(label, coords,Angle_spacing) for label, coords in tqdm(region_coords_filtered, desc="Calculating Feret diameters"))
    # feret_df = pd.DataFrame(results, columns=['label', 'Max_Feret_Diameter', 'Min_Feret_Diameter']).set_index('label')
    # Properties_Bulk = Properties_Bulk.merge(feret_df, how='left', on='label')
    # Properties_Bulk['Feret_ratio'] = Properties_Bulk['Min_Feret_Diameter'] / Properties_Bulk['Max_Feret_Diameter']

    return properties_bulk
