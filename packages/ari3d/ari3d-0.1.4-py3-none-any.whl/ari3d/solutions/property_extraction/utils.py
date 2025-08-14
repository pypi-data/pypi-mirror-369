import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy import ndimage
from skimage import morphology
from tqdm import tqdm


def replace_extra_rows_with_zeros(data1, data2):
    # If after erosion the particle disappers a rows of 0s are added

    # Find indices in data1 but not in data2
    missing_indices = data1.index.difference(data2.index)
    # Create a DataFrame with missing indices filled with zeros
    missing_rows = pd.DataFrame(0, index=missing_indices, columns=data2.columns)
    # Append the missing rows to data2
    data2_updated = pd.concat([data2, missing_rows])
    # Sort data2_updated by index to maintain order (optional)
    data2_updated = data2_updated.sort_index()
    return data2_updated


def extract_histograms(labels, gray_scale_thresh, number_treads):
    """Extract histograms for each label."""

    def _get_histogram(label, gst):
        hist, bins = np.histogram(
            gst[labels == label], bins=range(65537)
        )  # full Half-precision range
        return hist, label

    unique_labels = np.unique(labels)
    results = Parallel(n_jobs=number_treads, prefer="threads")(
        delayed(_get_histogram)(label, gray_scale_thresh)
        for label in tqdm(unique_labels)
        if label != 0
    )
    histograms = [result[0] for result in results]
    index = [result[1] for result in results]

    # convert to pandas dataframe
    histograms_df = pd.DataFrame(tqdm(histograms))
    histograms_df.index = index
    return histograms_df


def erosion_based_on_labels(label_mask, surface_properties_mean_intensity):
    """Create an eroded image for each label based on the number of erosions fulfilling the threshold criteria."""
    eroded_images = []

    # calculate how many erosion's have to be maximally performed
    unique_erosions = surface_properties_mean_intensity["no_of_erosions"].unique()

    # loop over the maximal number of erosion's
    for no_of_erosions in unique_erosions:
        # all labels for which the calculated no equals current iteration
        labels_with_erosions = surface_properties_mean_intensity.index[
            surface_properties_mean_intensity["no_of_erosions"] == no_of_erosions
        ].values

        # group mask of label mask of selected indices
        group_mask = np.isin(label_mask, labels_with_erosions)

        # erode selected labels no_of_erosions times
        eroded_mask = ndimage.binary_erosion(group_mask, iterations=no_of_erosions)
        eroded_images.append(
            eroded_mask.astype(np.uint8)
        )  # Convert to uint16 to save memory

    # remove potential overlaps of labels caused by multiple erosions and return
    final_eroded_image = np.sum(eroded_images, axis=0)
    final_eroded_image = (final_eroded_image > 0).astype(np.int8)
    del labels_with_erosions, group_mask, eroded_mask

    return final_eroded_image


def get_unique_labels(labels):
    """Get unique labels not toching the border."""
    # Keeping only the unique labels in labelled image and turing rest to 0
    unique = np.unique(labels)

    # assess labels that touch the border of the volume
    unique1 = np.unique(labels[0])
    unique2 = np.unique(labels[-1])
    unique3 = np.unique(labels[:, 0, :])
    unique4 = np.unique(labels[:, -1, :])
    unique5 = np.unique(labels[:, :, 0])
    unique6 = np.unique(labels[:, :, -1])

    # filter for these
    particles_to_delete = np.concatenate(
        [unique1, unique2, unique3, unique4, unique5, unique6]
    )
    unique_filtered = np.array([i for i in unique if i not in particles_to_delete])

    return np.delete(unique_filtered, np.where(unique_filtered == 0))


def delete_small_particles(labels, binary, gray_scale_volume, size_threshold):
    """Remove the particles smaller than 'Size_threshold' from labels and gray scale volume."""
    binary = np.array(binary, dtype=bool)

    # remove small objects
    binary = morphology.remove_small_objects(binary, size_threshold, connectivity=1)
    binary = binary.astype(int)

    # keep only labels that pass the threshold
    labels = labels * binary
    binary = binary.astype(np.uint8)
    gray_scale_thresholded = binary * gray_scale_volume
    return labels, binary, gray_scale_thresholded


def _process_slice(slice_data, unique_labels):
    slice_data = slice_data.copy()  # Make a copy to ensure it is modifiable
    for label in np.unique(slice_data):
        if label not in unique_labels:
            slice_data[slice_data == label] = 0  # Set label to background
    return slice_data


def filter_mask_image(label_mask, unique_labels, n_jobs=-1):
    """Filter mask image for values not in a unique set of labels."""
    result = Parallel(n_jobs=n_jobs)(
        delayed(_process_slice)(label_mask[:, :, i], unique_labels)
        for i in tqdm(range(label_mask.shape[2]), desc="Processing slices")
    )
    return np.stack(result, axis=2)
