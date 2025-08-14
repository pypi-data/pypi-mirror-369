# for old versions see https://gitlab.com/ida-mdc/ari3d/-/tree/b74a5db7a4e69dc99be10ef3aa47a83fb5dc70b6/src/ari3d/solutions/data_viewer
import os
import time
import sys
from pathlib import Path

import altair as alt
import anndata
import numpy as np
import pandas as pd
import yaml
from joblib import Parallel, delayed
from scipy.signal import find_peaks, savgol_filter
from tqdm import tqdm

############################### IO #################################


def create_path_recursively(path):
    """Create a path. Creates missing parent folders."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)

    return True


def write_report_to_yml(yml_file, report_dict):
    """Write a dictionary to a file in yml format."""
    yml_file = Path(yml_file)
    create_path_recursively(yml_file.parent)

    string_data = {}
    # Convert to string
    for key, value in report_dict.items():
        if isinstance(value, int):
            str_val = str(value)
        elif isinstance(value, np.ndarray):
            str_val = np.array2string(value)
        else:
            str_val = str(value)
        string_data[key] = str_val

    with open(yml_file, "w+") as yml_f:
        yml_f.write(yaml.dump(string_data, Dumper=yaml.Dumper))

    return True


def get_dict_from_yml(yml_file):
    """Read a dictionary from a file in yml format."""
    with open(yml_file) as yml_f:
        d = yaml.safe_load(yml_f)

    if not isinstance(d, dict):
        raise TypeError("Yaml file %s invalid!" % str(yml_file))

    return d


def write_dict_to_yml(yml_file, d):
    """Write a dictionary to a file in yml format."""
    yml_file = Path(yml_file)
    create_path_recursively(yml_file.parent)

    with open(yml_file, "w+") as yml_f:
        yml_f.write(yaml.dump(d, Dumper=yaml.Dumper))

    return True


def _load_ann_data(path, message):
    try:
        adata = anndata.read_h5ad(path, backed="r")
        with tqdm(total=100, desc="Converting to DataFrame") as pbar_convert:
            df = adata.to_df()
            pbar_convert.update(100)
        df.columns = [
            int("".join(filter(str.isdigit, col)))
            if any(char.isdigit() for char in col)
            else np.nan
            for col in df.columns
        ]
        df.index = df.index.astype(int)
        print(message)
        return df
    except Exception as e:
        print(f"An error occurred while uploading and converting the h5ad file: {e}")
    return df


def directory():
    path = askdirectory(title="select folder with data")  ## folder 'data'
    return path


def load_histograms(path_bulk_histogram):
    """Load the bulk histograms from the h5ad file and convert it to a DataFrame."""
    print("path histograms:", path_bulk_histogram)
    histogram_ds = _load_ann_data(
        path_bulk_histogram, "h5ad bulk converted to DataFrame successfully."
    )
    initial_bins = len(histogram_ds.columns)

    return histogram_ds, initial_bins


def load_properties(path):
    """Load the properties from the csv file and convert it to a DataFrame."""
    path_and_name = os.path.join(path, "Properties.csv")
    properties_data = pd.read_csv(path_and_name, encoding="unicode_escape")
    return properties_data


def load_in_volume(_path_load_inner_histograms):
    """Load the Inner histograms from the h5ad file and convert it to a DataFrame."""
    return _load_ann_data(
        _path_load_inner_histograms,
        "h5ad inner histogram converted to DataFrame successfully.",
    )


def load_out_volume(_path_load_outer_histograms):
    """Load the Outer histograms from the h5ad file and convert it to a DataFrame."""
    return _load_ann_data(
        _path_load_outer_histograms,
        "h5ad outer histogram converted to DataFrame successfully.",
    )


def load_mesh(_path_load_surface_mesh_histograms):
    """Load the Mesh data from the h5ad file and convert it to a DataFrame."""
    return _load_ann_data(
        _path_load_surface_mesh_histograms,
        "h5ad Surface mesh converted to DataFrame successfully.",
    )


def load_gradient(path_load_gradient):
    """Load the gradient from the csv file and convert it to a DataFrame."""
    gradient = pd.read_csv(path_load_gradient)
    gradient.index = gradient["label"]
    return gradient


def create_histogram_subdata(n, histograms_data, particle_x=0):
    """Create a Sub-dataset for of the histogram data."""
    labels_array = np.array(histograms_data.index)
    labels_array = labels_array[labels_array > 0]
    random_labels = np.random.choice(labels_array, n, replace=False)
    if (
        particle_x > 0
    ):  # add a specific Region to the random dataset. Be sure the label exists
        random_labels = np.append(random_labels, particle_x)

    random_labels = np.sort(random_labels)
    random_labels = pd.DataFrame(random_labels, columns=["Label Index"])

    # get histogram data of chosen labels
    hist_sub_data = histograms_data[
        histograms_data.index.isin(random_labels["Label Index"])
    ]

    return hist_sub_data, random_labels


def load_label_list(data_directory):
    """Load the label List csv containing the label (particle) Indices of interest."""
    path_label_list = os.path.join(data_directory, "labelList.csv")
    label_list = pd.read_csv(path_label_list)
    label_indices = label_list["Label Index"]
    sub_data_from_list = chosen_histograms_data[
        chosen_histograms_data.index.isin(label_indices)
    ]

    # show head of list
    label_list.head()

    return sub_data_from_list, label_indices


def process_histogram_row(row, array, binning):
    # allows to input images with any binnig. This function is parallelized and used in the binning.
    num = row.to_numpy()
    num = np.pad(num, (0, 1), "constant")
    num = num.ravel()
    # Define bins and digitization
    rang = int(round(len(num) / binning))
    bins = np.linspace(0, max(array) + 1, rang)
    full_range = np.linspace(0, max(array), len(array) + 1)
    digitized = np.digitize(full_range, bins)
    # Calculate bin sums
    bin_sum = [num[digitized == i].sum() for i in range(1, len(bins))]
    bin_sum = np.array(bin_sum)
    row1 = bin_sum[bin_sum > 0]
    bin_sum[bin_sum > 0] = row1
    yhat = row1
    bin_sum = [num[digitized == i].sum() for i in range(1, len(bins))]
    bin_sum = np.array(bin_sum)
    bin_sum[bin_sum > 0] = yhat
    result1 = bin_sum
    return result1


def binning(bin_input, histograms_data, n_jobs=-1):
    histograms_data_int = np.array(histograms_data.columns).astype(int)
    # Parallel processing
    binned_hist_list = Parallel(n_jobs=n_jobs)(
        delayed(process_histogram_row)(row, histograms_data_int, bin_input)
        for _, row in tqdm(
            histograms_data.iterrows(),
            total=histograms_data.shape[0],
            desc="Processing Rows",
        )
    )
    # Convert lists to DataFrames
    rang = int(round(len(histograms_data.columns) / bin_input))
    bin_ranges = np.linspace(0, len(histograms_data.columns) - 1, rang - 1).astype(int)
    binned_hist_list = np.array(binned_hist_list).reshape(len(binned_hist_list), -1)

    # convert binned histogram do dataset with columns as lower bin range
    binned_hist_list = pd.DataFrame(binned_hist_list, columns=bin_ranges)
    binned_hist_list.index = histograms_data.index

    binned_hist_list[binned_hist_list < 0] = 0
    return binned_hist_list


def normalize_volume(un_normalized):
    un_normalized = pd.DataFrame(un_normalized)
    df_new = un_normalized.loc[:, :].div(un_normalized.sum(axis=1), axis=0)
    df_new = df_new.fillna(0)
    return df_new


def transform_columns_xy(sub_data_ready):
    # transpose dataset
    x = sub_data_ready.transpose()
    # build array as long as particles are available, repeat the index
    bin_indices = np.tile(x.index, len(x.columns))
    # build array with particle names
    name_particles = (
        np.array([np.array([c] * len(x)) for c in x.columns])
        .transpose()
        .flatten(order="F")
    )
    # flatten frequencies of each particle
    frequencies = (
        np.array([np.array(x[f]) for f in x.columns]).transpose().flatten(order="F")
    )

    # build and return dataframe
    return pd.DataFrame(
        {"X": name_particles, "Y": bin_indices, "frequency": frequencies}
    )


def smooth_histograms_savgol(binned_histograms, savgol_window_length, n_jobs=-1):
    smoothed_histogram = Parallel(n_jobs=n_jobs)(
        delayed(
            lambda row: savgol_filter(
                row, window_length=savgol_window_length, polyorder=3
            )
        )(row)
        for _, row in tqdm(
            binned_histograms.iterrows(),
            total=binned_histograms.shape[0],
            desc="Smoothing Rows",
        )
    )

    # convert to data frame
    smoothed_histogram_ds = pd.DataFrame(
        smoothed_histogram,
        columns=binned_histograms.columns,
        index=binned_histograms.index,
    )

    # Clip negative values to 0
    smoothed_histogram_ds[smoothed_histogram_ds < 0] = 0

    # Ensure integer values if required
    smoothed_histogram_ds = smoothed_histogram_ds.astype(int)

    return smoothed_histogram_ds


def process_peaks(
    normalized_data,
    histograms_data,
    properties,
    number_bins,
    peak_width,
    peak_height,
    peak_prominence,
    peak_vertical_distance,
    peak_horizontal_distance,
    num_bins_input,
):
    # binned but maintaining the range, e.g.16bit to 8bit: 256 bins between 0-65535 (0, 256,512,768...)
    normalized_data = pd.DataFrame(normalized_data)
    peaks_position = []
    peaks_height = []

    # iterate over the particles
    for index, row in tqdm(
        normalized_data.iterrows(),
        total=normalized_data.shape[0],
        desc="Processing Peaks",
    ):
        # flatten the row
        row_flatten = np.array(row).ravel()

        # convert to float and pad the array to start from 0
        row_flatten = row_flatten.astype(float)
        row_flatten = np.pad(row_flatten, (0, 1), constant_values=0)

        # grey scale intensity range
        grey_scale = np.array(histograms_data.columns, dtype=float)
        grey_scale = np.pad(grey_scale, (0, 1), constant_values=0)
        grey_scale = grey_scale.astype(int)

        # replace NaN values with 0 and negative values with 0
        row_flatten[np.isnan(row_flatten)] = 0
        row_flatten[row_flatten < 0] = 0

        # Find peaks
        peaks_scipy = find_peaks(
            row_flatten,
            rel_height=0.5,
            width=peak_width,
            height=peak_height,
            prominence=peak_prominence,
            threshold=peak_vertical_distance,
            distance=peak_horizontal_distance,
        )
        # calculate the bin value of the peak
        peak_pos = grey_scale[peaks_scipy[0]]
        peak_pos = peak_pos * num_bins_input

        # append peak positions and heights to lists
        peaks_position.append([peak_pos])
        peaks_height.append([peaks_scipy[1]["peak_heights"]])

    # convert lists to DataFrames
    peaks_positions = pd.DataFrame(peaks_position)
    peaks_height = pd.DataFrame(peaks_height)

    # flatten rows and rename columns
    peaks_positions = pd.concat([peaks_positions[0].str[i] for i in range(22)], axis=1)
    peaks_height = pd.concat([peaks_height[0].str[i] for i in range(22)], axis=1)
    peaks_positions.columns = [f"Peak_{i + 1}" for i in range(22)]
    peaks_height.columns = [f"Peaks_Height_{i + 1}" for i in range(22)]

    # fill NaN values with 0
    peaks_positions = peaks_positions.fillna(0)
    peaks_height = peaks_height.fillna(0)

    # merge to a single DataFrame
    peaks = pd.concat([peaks_positions, peaks_height], axis=1)

    # apply indexing from the normalized data
    peaks.index = normalized_data.index

    # locate properties based on the normalized data index
    properties = properties.loc[normalized_data.index]

    # combine properties with peaks
    peaks = pd.concat([peaks, properties], axis=1)

    # save binning value
    peaks["Binning"] = number_bins

    # replace NaN values with 0, inf with 0, and -inf with 0, typecast to float
    peaks = peaks.astype(float)
    peaks.replace([np.inf, -np.inf], 0, inplace=True)
    peaks.replace([np.nan], 0, inplace=True)

    return peaks


def _process_phase(
    peaks1,
    peaks_height_cols,
    peaks_col,
    phase_start,
    phase_end,
    phase_label,
    background_peak,
):
    # Apply thresholds, set np.nan for values outside the phase range
    peaks_filtered = peaks_col.where(
        (peaks_col >= phase_start) & (peaks_col < phase_end), np.nan
    )

    # get the peak height
    peaks_height = peaks1[peaks_height_cols]

    # Filter out rows with all NaN values, fill NaN values with 0
    peaks_filtered = peaks_filtered.loc[peaks_filtered.any(axis=1), :].fillna(0)

    # merge the filtered peaks with their peak heights
    peaks_filtered = peaks_filtered.merge(
        peaks_height, left_index=True, right_index=True
    )

    # Adjust peak positions and heights
    for i in range(1, 23):
        # remove negative values
        peaks_filtered[f"Peak_{i}"] = peaks_filtered[f"Peak_{i}"].clip(lower=0)

        # set all Peaks_Height values to 0 if the corresponding Peak value is outside the phase range
        peaks_filtered[f"Peaks_Height_{i}"] = (
            peaks_filtered[f"Peaks_Height_{i}"]
            .where(
                (peaks_filtered[f"Peak_{i}"] >= phase_start)
                & (peaks_filtered[f"Peak_{i}"] < phase_end),
                0,
            )
            .where(peaks_filtered[f"Peak_{i}"] >= background_peak, 0)
        )

    # check whether there exist rows where at least one peak is within the phase range
    if peaks_filtered[peaks_height_cols].notna().any().any():
        # Find the index of the maximum height peak for each row
        max_peak_idx = peaks_filtered[peaks_height_cols].idxmax(axis=1)
        # Initialize a new DataFrame with zeros
        peaks_data = pd.DataFrame(
            0,
            index=peaks_filtered.index,
            columns=[f"Peak_{phase_label}", f"Peaks_Height_{phase_label}"],
        )
        for i, col_name in enumerate(peaks_height_cols):
            mask = max_peak_idx == col_name
            # set the peak gray value and height for the row where the peak has the maximum height
            peaks_data[f"Peak_{phase_label}"] = np.where(
                mask, peaks_filtered[f"Peak_{i + 1}"], peaks_data[f"Peak_{phase_label}"]
            )
            peaks_data[f"Peaks_Height_{phase_label}"] = np.where(
                mask,
                peaks_filtered[col_name],
                peaks_data[f"Peaks_Height_{phase_label}"],
            )
    else:
        # Return an empty DataFrame if no valid peaks were found
        peaks_data = pd.DataFrame(
            0,
            index=peaks_col.index,
            columns=[f"Peak_{phase_label}", f"Peaks_Height_{phase_label}"],
        )
    return peaks_data


def arrange_peaks(
    peaks1,
    threshold_dict,
    properties,
):
    # Define column names
    cols = [f"Peak_{i}" for i in range(1, 23)]
    peaks_height_cols = [f"Peaks_Height_{i}" for i in range(1, 23)]

    # Process each phase
    peaks_data_T1 = _process_phase(
        peaks1,
        peaks_height_cols,
        peaks1[cols],
        threshold_dict["BackgroundT"],
        threshold_dict["Max greyvalue A"],
        1,
        threshold_dict["BackgroundT"],
    )
    peaks_data_T2 = _process_phase(
        peaks1,
        peaks_height_cols,
        peaks1[cols],
        threshold_dict["Max greyvalue A"],
        threshold_dict["Max greyvalue B"],
        2,
        threshold_dict["BackgroundT"],
    )
    peaks_data_T3 = _process_phase(
        peaks1,
        peaks_height_cols,
        peaks1[cols],
        threshold_dict["Max greyvalue B"],
        threshold_dict["Max greyvalue C"],
        3,
        threshold_dict["BackgroundT"],
    )
    peaks_data_T4 = _process_phase(
        peaks1,
        peaks_height_cols,
        peaks1[cols],
        threshold_dict["Max greyvalue C"],
        threshold_dict["Max greyvalue D"],
        4,
        threshold_dict["BackgroundT"],
    )
    peaks_data_T5 = _process_phase(
        peaks1,
        peaks_height_cols,
        peaks1[cols],
        threshold_dict["Max greyvalue D"],
        threshold_dict["Max greyvalue E"],
        5,
        threshold_dict["BackgroundT"],
    )
    peaks_data_T6 = _process_phase(
        peaks1,
        peaks_height_cols,
        peaks1[cols],
        threshold_dict["Max greyvalue E"],
        np.inf,
        6,
        threshold_dict["BackgroundT"],
    )

    # Merge all phase data
    all_peaks_data = [
        peaks_data_T1,
        peaks_data_T2,
        peaks_data_T3,
        peaks_data_T4,
        peaks_data_T5,
        peaks_data_T6,
    ]
    non_empty_peaks_data = [df for df in all_peaks_data if not df.empty]

    if non_empty_peaks_data:
        peaks = pd.concat(non_empty_peaks_data, axis=1, join="outer")
    else:
        peaks = pd.DataFrame(
            index=peaks1.index,
            columns=[f"Peak_{i}" for i in range(1, 7)]
            + [f"Peaks_Height_{i}" for i in range(1, 7)],
        )

    # Fill NaN values with 0
    peaks = peaks.fillna(0)
    # replace peak position values less than background peak with background peak
    peaks[["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5", "Peak_6"]] = peaks[
        ["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5", "Peak_6"]
    ].replace(0, threshold_dict["BackgroundT"])

    # Find the maximum peak value for each row, hence which phase the peak belongs to
    peaks["Max_peak"] = peaks[
        ["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5", "Peak_6"]
    ].max(axis=1)
    peaks = peaks.sort_values(by=["label"])

    # Combine with Properties
    properties_and_peaks = pd.concat([peaks, properties], axis=1)
    properties_and_peaks = properties_and_peaks.dropna()
    properties_and_peaks.replace([np.inf, -np.inf], 0, inplace=True)

    # remove all rows where the maximum peak is less or equal to the background peak
    properties_and_peaks = properties_and_peaks.drop(
        properties_and_peaks[
            properties_and_peaks.Max_peak <= threshold_dict["BackgroundT"]
        ].index
    )

    return properties_and_peaks


def _update_peak_positions(
    properties, background_peak, height_threshold, max_value=65535
):
    array = properties[["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5"]]
    # Fill NaN values with 0
    array = array.fillna(0)
    # Cap values at max_value
    array[array > max_value] = max_value
    for i in range(1, 5):  # Assuming there are 6 peaks (1 to 7)
        peak_position_col = f"Peak_{i}"
        peak_height_col = f"Peaks_Height_{i}"
        # set all peaks to background peak if the peak position is less than the background peak
        array[peak_position_col] = np.where(
            array[peak_position_col] < background_peak,
            background_peak,
            array[peak_position_col],
        )
        # set all peaks to background peak if the peak height is less than a given threshold
        array[peak_position_col] = np.where(
            properties[peak_height_col] < float(height_threshold),
            background_peak,
            array[peak_position_col],
        )
    return array


def quantify_liberated_regions(
    histograms_subdata,
    surface_mesh_subdata,
    subdata_properties,
    background_peak,
    phase_1_threshold,
    phase_2_threshold,
    phase_3_threshold,
    phase_4_threshold,
    phase_5_threshold,
    regions_analysed,
    volume_analysed,
    enable_pvb,
):
    """Quantify liberated regions."""
    q_1_phases_append = []
    index_1_phase = []
    peaks_1_phase = []
    weighted_q_phase_1_append = []
    surface_q_append = []
    regions_liberated = 0

    # iterate over particles
    for i, (index, row) in enumerate(histograms_subdata.iterrows()):
        # Getting the peaks values
        peaks = subdata_properties.iloc[[i]].values

        # Condition that only 1 peak has value greater than background
        if np.count_nonzero(peaks > background_peak) == 1:
            particle_peak = peaks[peaks > background_peak].astype(int)[0]
            if enable_pvb:
                # Takes the sum of ith row from phase 1 minimum threshold greyscale value till Phase1_max_limit
                q_phase_1 = row.iloc[particle_peak:65535].sum()

                # weighting the voxels to the background peak
                weights_to_bg = np.linspace(0, 1, particle_peak - background_peak)
                voxels_to_bg_phase_1 = row.iloc[background_peak:particle_peak]

                # calculate the weighted quantification for phase 1
                weighted_q_phase_1 = (voxels_to_bg_phase_1 * weights_to_bg).sum()
                weighted_q_phase_1_append.append([weighted_q_phase_1])

                volume_analysed += weighted_q_phase_1 + q_phase_1
            else:
                # Takes the sum of ith row from background peak till Phase1_max_limit
                q_phase_1 = row.iloc[(background_peak + particle_peak // 2) :].sum()
                volume_analysed += q_phase_1

            # surface quantification
            s_q_liberated = surface_mesh_subdata.iloc[i, background_peak:65535].sum()

            # append to DS
            q_1_phases_append.append([q_phase_1])
            surface_q_append.append([s_q_liberated])
            index_1_phase.append([index])
            peaks_1_phase.append([particle_peak])

            # count
            regions_liberated += 1
            regions_analysed += 1

    if enable_pvb:
        # Outer refers to bins lower grey value than the peak (affected by partial volume)
        q_outer_phase_1 = pd.DataFrame(
            weighted_q_phase_1_append, columns=["Quantification_Outer_phase_1"]
        )
    # datasets to return
    q_1_phases = pd.DataFrame(q_1_phases_append, columns=["Quantification_phase_1"])
    s_q_1_phases = pd.DataFrame(surface_q_append, columns=["Surface_quantification"])
    if enable_pvb:
        q_1_phases["total_quantification_phase_1"] = (
            q_1_phases["Quantification_phase_1"]
            + q_outer_phase_1["Quantification_Outer_phase_1"]
        )
    else:
        q_1_phases["total_quantification_phase_1"] = q_1_phases[
            "Quantification_phase_1"
        ]

    index_1_phase = pd.DataFrame(index_1_phase, columns=["Label"])
    peaks_1_phase = pd.DataFrame(peaks_1_phase, columns=["Peak_1"])
    q_1_phase_sorted = pd.DataFrame(index=index_1_phase["Label"])

    # Define phase thresholds for categorizing peaks
    thresholds = [
        background_peak,
        phase_1_threshold,
        phase_2_threshold,
        phase_3_threshold,
        phase_4_threshold,
        phase_5_threshold,
    ]

    # assign the quantification to the correct peak column in the overall dataset
    for i in range(1, 6):
        mask = (peaks_1_phase["Peak_1"] > thresholds[i - 1]) & (
            peaks_1_phase["Peak_1"] <= thresholds[i]
        )
        q_1_phase_sorted[f"Peak_{i}"] = np.where(mask, peaks_1_phase["Peak_1"], 0)
        q_1_phase_sorted[f"Phase_{i}_quantification"] = np.where(
            mask, q_1_phases["total_quantification_phase_1"], 0
        )
        q_1_phase_sorted[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_q_1_phases["Surface_quantification"], 0
        )

    return (
        q_1_phase_sorted,
        regions_liberated,
        regions_analysed,
        volume_analysed,
    )


def quantify_two_phases_particle(
    histograms_subdata,
    inner_hist_subdata,
    outer_hist_subdata,
    surface_mesh_subdata,
    grad_subdata,
    subdata_properties,
    background_peak,
    phase_1_threshold,
    phase_2_threshold,
    phase_3_threshold,
    phase_4_threshold,
    phase_5_threshold,
    regions_analysed,
    volume_analysed,
    enable_pvb,
    gradient_threshold=0.75,
):
    """Quantify two phases particle."""

    if enable_pvb:
        q_all_2_phases_1 = []
        q_all_2_phases_2 = []
        q_out_of_peaks_phase_1 = []
        q_out_of_peaks_phase_2 = []
        q_s_phase_1_append = []
        q_s_phase_2_append = []
        q_outer_phase_1 = []
        q_outer_phase_2 = []
        peaks_1_phase = []
        peaks_2_phase = []
        index_2_phase = []
        regions_2_phases = 0

        # iterate over particles
        for i, (index, row) in enumerate(inner_hist_subdata.iterrows()):
            peaks = subdata_properties.iloc[[i]].values
            if (np.count_nonzero(peaks > background_peak) == 2) and i > -1:
                # get the particle peak positions
                particle_peak = peaks[peaks > background_peak]
                particle_peak_1 = int(float((particle_peak).flat[0]))
                particle_peak_2 = int(float((particle_peak).flat[1]))

                gradient_ratio = grad_subdata["Gradient_3"].iloc[i]
                if gradient_ratio < gradient_threshold:
                    gradient_ratio = gradient_threshold

                ### Inner Histogram Analysis

                # taking the sum of ith row from phase X minimum threshold greyscale value till PhaseX_max_limit
                sum_phase_1 = inner_hist_subdata.iloc[
                    i, background_peak:particle_peak_1
                ].sum()
                sum_phase_2 = inner_hist_subdata.iloc[i, particle_peak_2:].sum()

                # Appending the phase 1 quantification sum
                q_all_2_phases_1.append([sum_phase_1])
                q_all_2_phases_2.append([sum_phase_2])

                # saving peak positions
                peaks_1_phase.append([particle_peak_1])
                peaks_2_phase.append([particle_peak_2])

                # voxels to phase 1 to phase 2
                voxels_p1_to_p2 = inner_hist_subdata.iloc[
                    i, particle_peak_1:particle_peak_2
                ]
                voxels_p1_to_p2 = np.array(voxels_p1_to_p2)

                # weighting for phase 1 to phase 2
                weights_p1_to_p2 = np.arange(
                    0, 1, 1 / ((particle_peak_2) - particle_peak_1)
                )
                weights_p1_to_p2 = np.array(weights_p1_to_p2)

                # weighting for phase 2 to phase 1 is reverse of phase 1 to phase 2
                weights_p2_to_p1 = weights_p1_to_p2[::-1]

                # weighted quantification of phase 2 towards phase 1 voxels
                out_of_peak_volume_2 = voxels_p1_to_p2 * weights_p1_to_p2

                # weighted quantification of phase 1 towards phase 2 voxels
                out_of_peak_volume_1 = voxels_p1_to_p2 * weights_p2_to_p1

                # Appending the phase 1 quantification sum
                out_of_peak_volume_1 = out_of_peak_volume_1.sum()
                q_out_of_peaks_phase_1.append([out_of_peak_volume_1])

                # Appending the phase 2 quantification sum
                out_of_peak_volume_2 = out_of_peak_volume_2.sum()
                q_out_of_peaks_phase_2.append([out_of_peak_volume_2])

                ### Outer Histogram Analysis

                # Voxels pure phase 2
                outer_volume_pure_phase_2 = outer_hist_subdata.iloc[
                    i, particle_peak_2:65535
                ].sum()

                # weighting BG to phase 1
                weights_p1_to_bg = np.arange(
                    0, 1, 1 / ((particle_peak_1 - 1) - background_peak)
                )
                weights_p1_to_bg = np.array(weights_p1_to_bg)

                # voxels to background to phase 1
                voxels_bg_to_p1 = outer_hist_subdata.iloc[
                    i, background_peak : particle_peak_1 - 1
                ]

                # weighted quantification for background to phase 1
                q_outer_phase_1_array = voxels_bg_to_p1 * weights_p1_to_bg

                # weighting for background to phase 2
                weights_bg_to_p2 = np.arange(
                    0, 1, 1 / ((particle_peak_2 - 1) - background_peak)
                )
                weights_bg_to_p2 = np.array(weights_bg_to_p2)

                # voxels to background to phase 2
                voxel_bg_to_p2 = outer_hist_subdata.iloc[
                    i, background_peak : particle_peak_2 - 1
                ]

                # weighted quantification for background to phase 2
                q_outer_phase_2_array = voxel_bg_to_p2 * weights_bg_to_p2

                # Sum of outer phase 1 within phase 2
                vol_phase_1_within_phase_2 = q_outer_phase_2_array[
                    background_peak:particle_peak_1
                ]
                vol_phase_1_within_phase_2 = vol_phase_1_within_phase_2.sum()

                # Sum of outer phase 1 and outer phase 2
                q_outer_phase_2_array = (
                    q_outer_phase_2_array.sum() - vol_phase_1_within_phase_2
                )
                q_outer_phase_1_array = q_outer_phase_1_array.sum()

                # assemble the PVE adjusted outer volume
                pve_adjusted_volume = (
                    outer_volume_pure_phase_2
                    + q_outer_phase_1_array
                    + q_outer_phase_2_array
                )

                # sort out the phase limits based on user thresholds
                if particle_peak_1 < phase_1_threshold:
                    phase_limit = phase_1_threshold
                elif phase_1_threshold <= particle_peak_1 < phase_2_threshold:
                    phase_limit = phase_2_threshold
                elif phase_2_threshold <= particle_peak_1 < phase_3_threshold:
                    phase_limit = phase_3_threshold
                elif phase_3_threshold <= particle_peak_1 < phase_4_threshold:
                    phase_limit = phase_4_threshold

                # calculate surface volume
                surface_ratio = (
                    surface_mesh_subdata.iloc[
                        i, background_peak : int(gradient_ratio * phase_limit)
                    ].sum()
                ) / (surface_mesh_subdata.iloc[i, background_peak:].sum())
                phase_1_s_v = (
                    surface_mesh_subdata.iloc[i, background_peak:65535].sum()
                    * surface_ratio
                )
                phase_2_s_v = (
                    surface_mesh_subdata.iloc[i, background_peak:65535].sum()
                    - phase_1_s_v
                )

                # append the quantification values
                q_s_phase_1_append.append([phase_1_s_v])
                q_s_phase_2_append.append([phase_2_s_v])

                # correct the outer quantification based on surface ratio
                q_outer_phase_1_volume = surface_ratio * pve_adjusted_volume
                q_outer_phase_2_volume = pve_adjusted_volume - q_outer_phase_1_volume

                # append the outer quantification values
                q_outer_phase_1.append([q_outer_phase_1_volume])
                q_outer_phase_2.append([q_outer_phase_2_volume])

                # store the index of the particle
                index_2_phase.append([index])

                # count
                regions_2_phases += 1
                regions_analysed += 1
                volume_analysed += (
                    sum_phase_1
                    + sum_phase_2
                    + out_of_peak_volume_1
                    + out_of_peak_volume_2
                    + q_outer_phase_1_volume
                    + q_outer_phase_2_volume
                )

        # indices of second phase
        index_2_phase = pd.DataFrame(index_2_phase, columns=["Label"])

        # store the peaks positions to DataFrames
        peaks_1_phase = pd.DataFrame(peaks_1_phase, columns=["Peak_1"])
        peaks_1_phase.index = index_2_phase["Label"]
        peaks_2_phase = pd.DataFrame(peaks_2_phase, columns=["Peak_2"])
        peaks_2_phase.index = index_2_phase["Label"]

        # create DataFrames for surface quantification
        surface_volume_phase_1 = pd.DataFrame(
            q_s_phase_1_append, columns=["Surface_volume_phase_1"]
        )
        surface_volume_phase_1.index = index_2_phase["Label"]
        surface_volume_phase_2 = pd.DataFrame(
            q_s_phase_2_append, columns=["Surface_volume_phase_2"]
        )
        surface_volume_phase_2.index = index_2_phase["Label"]

        # create DataFrames for outer quantification
        q_all_2_phases_1 = pd.DataFrame(
            q_all_2_phases_1, columns=["Phase_1_quantification_outer"]
        )
        q_all_2_phases_1.index = index_2_phase["Label"]
        q_all_2_phases_2 = pd.DataFrame(
            q_all_2_phases_2, columns=["Phase_2_quantification_outer"]
        )
        q_all_2_phases_2.index = index_2_phase["Label"]

        q_outer_phase_1 = pd.DataFrame(
            q_outer_phase_1, columns=["Quantification_Outer_phase_1"]
        )
        q_outer_phase_1 = q_outer_phase_1.fillna(0)
        q_outer_phase_1.index = index_2_phase["Label"]
        q_outer_phase_2 = pd.DataFrame(
            q_outer_phase_2, columns=["Quantification_Outer_phase_2"]
        )
        q_outer_phase_2 = q_outer_phase_2.fillna(0)
        q_outer_phase_2.index = index_2_phase["Label"]

        # create DataFrames for inner quantification
        q_out_of_peaks_1 = pd.DataFrame(
            q_out_of_peaks_phase_1,
            columns=["Quantification_out_of_peaks_1_outer"],
        )
        q_out_of_peaks_1 = q_out_of_peaks_1.fillna(0)
        q_out_of_peaks_1.index = index_2_phase["Label"]

        q_out_of_peaks_2 = pd.DataFrame(
            q_out_of_peaks_phase_2,
            columns=["Quantification_out_of_peaks_2_outer"],
        )
        q_out_of_peaks_2 = q_out_of_peaks_2.fillna(0)
        q_out_of_peaks_2.index = index_2_phase["Label"]

        q_2_phases_inner = pd.concat(
            [
                peaks_1_phase,
                peaks_2_phase,
                q_all_2_phases_1,
                q_all_2_phases_2,
                q_out_of_peaks_1,
                q_out_of_peaks_2,
            ],
            axis=1,
        )
        q_2_phases_inner["Phase_1_inner_quantification"] = (
            q_2_phases_inner["Phase_1_quantification_outer"]
            + q_2_phases_inner["Quantification_out_of_peaks_1_outer"]
        )
        q_2_phases_inner["Phase_2_inner_quantification"] = (
            q_2_phases_inner["Phase_2_quantification_outer"]
            + q_2_phases_inner["Quantification_out_of_peaks_2_outer"]
        )
        q_2_phases_inner = q_2_phases_inner[
            [
                "Peak_1",
                "Peak_2",
                "Phase_1_inner_quantification",
                "Phase_2_inner_quantification",
            ]
        ]

        # create DataFrame for the final quantification of two phases
        q_2_phases = pd.concat(
            [
                q_2_phases_inner,
                q_outer_phase_1,
                q_outer_phase_2,
                peaks_1_phase,
                peaks_2_phase,
            ],
            axis=1,
        )
        q_2_phases["total_quantification_phase_1"] = (
            q_2_phases["Phase_1_inner_quantification"]
            + q_2_phases["Quantification_Outer_phase_1"]
        )
        q_2_phases["total_quantification_phase_2"] = (
            q_2_phases["Phase_2_inner_quantification"]
            + q_2_phases["Quantification_Outer_phase_2"]
        )
        q_2_phases = q_2_phases[
            [
                "Peak_1",
                "Peak_2",
                "total_quantification_phase_1",
                "total_quantification_phase_2",
            ]
        ]
        q_2_phases["Phase_1_surface_quantification"] = surface_volume_phase_1[
            "Surface_volume_phase_1"
        ]
        q_2_phases["Phase_2_surface_quantification"] = surface_volume_phase_2[
            "Surface_volume_phase_2"
        ]

        # assign the quantification to the correct peak column in the overall dataset
        cols = ["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5"]
        thresholds = [
            background_peak,
            phase_1_threshold,
            phase_2_threshold,
            phase_3_threshold,
            phase_4_threshold,
            phase_5_threshold,
        ]

        q_2_phase_sorted = pd.DataFrame(
            columns=cols + [f"Phase_{i}_quantification" for i in range(1, 6)]
        )
        q_2_phase_sorted_1 = q_2_phase_sorted.copy()
        for i in range(1, 6):
            mask = (peaks_1_phase["Peak_1"] > thresholds[i - 1]) & (
                peaks_1_phase["Peak_1"] <= thresholds[i]
            )
            q_2_phase_sorted[f"Peak_{i}"] = np.where(mask, peaks_1_phase["Peak_1"], 0)
            q_2_phase_sorted[f"Phase_{i}_quantification"] = np.where(
                mask, q_2_phases["total_quantification_phase_1"], 0
            )
            q_2_phase_sorted[f"Phase_{i}_surface_quantification"] = np.where(
                mask, q_2_phases["Phase_1_surface_quantification"], 0
            )
        for i in range(1, 6):
            mask = (peaks_2_phase["Peak_2"] > thresholds[i - 1]) & (
                peaks_2_phase["Peak_2"] <= thresholds[i]
            )
            q_2_phase_sorted_1[f"Peak_{i}"] = np.where(mask, peaks_2_phase["Peak_2"], 0)
            q_2_phase_sorted_1[f"Phase_{i}_quantification"] = np.where(
                mask, q_2_phases["total_quantification_phase_2"], 0
            )
            q_2_phase_sorted_1[f"Phase_{i}_surface_quantification"] = np.where(
                mask, q_2_phases["Phase_2_surface_quantification"], 0
            )

        # merge the two DataFrames
        q_2_phase_sorted = q_2_phase_sorted.mask(
            q_2_phase_sorted == 0, q_2_phase_sorted_1
        )
        q_2_phase_sorted.index = q_2_phases.index
    else:
        # No PVE enabled
        q_all_2_phases_1 = []
        q_all_2_phases_2 = []
        peaks_1_phase = []
        peaks_2_phase = []
        index_2_phase = []
        s_vol_phase_1_append = []
        s_vol_phase_2_append = []
        regions_2_phases = 0

        # iterate over particles
        for i, (index, row) in enumerate(surface_mesh_subdata.iterrows()):
            peaks = subdata_properties.iloc[[i]].values
            if (np.count_nonzero(peaks > background_peak) == 2) and i > -1:
                # get the particle peak positions
                particle_peak = peaks[peaks > background_peak]
                particle_peak_1 = int(float(particle_peak.flat[0]))
                particle_peak_2 = int(float(particle_peak.flat[1]))

                # Taking the sum of ith row from phase 1 minimum threshold greyscale value till Phase1_max_limit
                sum_phase_1 = histograms_subdata.iloc[
                    i, background_peak : int((particle_peak_1 + particle_peak_2) / 2)
                ].sum()

                # Appending the phase 1 quantification sum
                q_all_2_phases_1.append([sum_phase_1])

                # Taking the sum of ith row from phase 1 minimum threshold greyscale value till Phase1_max_limit
                sum_phase_2 = histograms_subdata.iloc[
                    i, int((particle_peak_1 + particle_peak_2) / 2) :
                ].sum()

                # Appending the phase 1 quantification sum
                q_all_2_phases_2.append([sum_phase_2])

                # store index and peaks positions
                index_2_phase.append([index])
                peaks_1_phase.append([particle_peak_1])
                peaks_2_phase.append([particle_peak_2])

                # Do not correct surface with the gradient ratio if PVE is not enabled
                gradient_ratio = 1

                # sort out the phase limits based on user thresholds
                if particle_peak_1 < phase_1_threshold:
                    phase_limit_1 = phase_1_threshold
                elif phase_1_threshold <= particle_peak_1 < phase_2_threshold:
                    phase_limit_1 = phase_2_threshold
                elif phase_2_threshold <= particle_peak_1 < phase_3_threshold:
                    phase_limit_1 = phase_3_threshold
                else:
                    phase_limit_1 = phase_4_threshold

                # calculate surface volume
                phase_1_s_vol = surface_mesh_subdata.iloc[
                    i, background_peak : int(phase_limit_1 * gradient_ratio)
                ].sum()
                phase_2_s_vol = surface_mesh_subdata.iloc[
                    i, int(phase_limit_1 * gradient_ratio) :
                ].sum()

                # store surface volume
                s_vol_phase_1_append.append([phase_1_s_vol])
                s_vol_phase_2_append.append([phase_2_s_vol])

                # count
                regions_2_phases += 1
                regions_analysed += 1
                volume_analysed += sum_phase_1 + sum_phase_2

        # indices amd peaks of third phase
        index_2_phase = pd.DataFrame(index_2_phase, columns=["Label"])
        peaks_1_phase = pd.DataFrame(peaks_1_phase, columns=["Peak_1"])
        peaks_2_phase = pd.DataFrame(peaks_2_phase, columns=["Peak_2"])

        # Quantification DataFrames
        q_all_2_phases_1 = pd.DataFrame(
            q_all_2_phases_1, columns=["total_quantification_phase_1"]
        )
        q_all_2_phases_2 = pd.DataFrame(
            q_all_2_phases_2, columns=["total_quantification_phase_2"]
        )

        # Surface volume DataFrames
        s_vol_phase_1 = pd.DataFrame(
            s_vol_phase_1_append, columns=["Surface_volume_phase_1"]
        )
        s_vol_phase_1.index = index_2_phase["Label"]
        s_vol_phase_2 = pd.DataFrame(
            s_vol_phase_2_append, columns=["Surface_volume_phase_2"]
        )
        s_vol_phase_2.index = index_2_phase["Label"]

        q_2_phases = pd.concat(
            [
                index_2_phase,
                q_all_2_phases_1,
                q_all_2_phases_2,
                peaks_1_phase,
                peaks_2_phase,
            ],
            axis=1,
        )

        # assign the quantification to the correct peak column in the overall dataset
        cols = ["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5"]
        thresholds = [
            background_peak,
            phase_1_threshold,
            phase_2_threshold,
            phase_3_threshold,
            phase_4_threshold,
            phase_5_threshold,
        ]
        q_2_phase_sorted = pd.DataFrame(
            columns=cols + [f"Phase_{i}_quantification" for i in range(1, 6)]
        )
        q_2_phase_sorted_1 = q_2_phase_sorted.copy()

        for i in range(1, 6):
            mask = (peaks_1_phase["Peak_1"] > thresholds[i - 1]) & (
                peaks_1_phase["Peak_1"] <= thresholds[i]
            )
            q_2_phase_sorted[f"Peak_{i}"] = np.where(mask, peaks_1_phase["Peak_1"], 0)
            q_2_phase_sorted[f"Phase_{i}_quantification"] = np.where(
                mask, q_2_phases["total_quantification_phase_1"], 0
            )
            q_2_phase_sorted[f"Phase_{i}_surface_quantification"] = np.where(
                mask, s_vol_phase_1["Surface_volume_phase_1"], 0
            )
        for i in range(1, 6):
            mask = (peaks_2_phase["Peak_2"] > thresholds[i - 1]) & (
                peaks_2_phase["Peak_2"] <= thresholds[i]
            )
            q_2_phase_sorted_1[f"Peak_{i}"] = np.where(mask, peaks_2_phase["Peak_2"], 0)
            q_2_phase_sorted_1[f"Phase_{i}_quantification"] = np.where(
                mask, q_2_phases["total_quantification_phase_2"], 0
            )
            q_2_phase_sorted_1[f"Phase_{i}_surface_quantification"] = np.where(
                mask, s_vol_phase_2["Surface_volume_phase_2"], 0
            )

        # merge the two DataFrames
        q_2_phase_sorted = q_2_phase_sorted.mask(
            q_2_phase_sorted == 0, q_2_phase_sorted_1
        )
        q_2_phase_sorted.index = q_2_phases["Label"]

    return (
        q_2_phase_sorted,
        regions_2_phases,
        regions_analysed,
        volume_analysed,
    )


def quantify3_phases_particle(
    histograms_subdata,
    gradient_subdata,
    surface_mesh_subdata,
    subdata_properties,
    background_peak,
    phase_1_threshold,
    phase_2_threshold,
    phase_3_threshold,
    phase_4_threshold,
    phase_5_threshold,
    regions_analysed,
    volume_analysed,
    regions_3_phases,
    enable_pvb=False,
):
    """Quantify 3 phases particle."""
    q_all_3_phases_1 = []
    q_all_3_phases_2 = []
    q_all_3_phases_3 = []
    peaks_1_phase = []
    peaks_2_phase = []
    peaks_3_phase = []
    index_3_phase = []
    s_vol_phase_1_append = []
    s_vol_phase_2_append = []
    s_vol_phase_3_append = []

    # iterate over particles
    for i, (index, row) in enumerate(surface_mesh_subdata.iterrows()):
        peaks = subdata_properties.iloc[[i]].values
        if (np.count_nonzero(peaks > background_peak) == 3) and i > -1:
            # get the particle peak positions
            particle_peak = peaks[peaks > background_peak]
            particle_peak_1 = int(float(particle_peak.flat[0]))
            particle_peak_2 = int(float(particle_peak.flat[1]))
            particle_peak_3 = int(float(particle_peak.flat[2]))

            # Taking the sum of ith row from phase 1 minimum threshold greyscale value till Phase1_max_limit
            sum_phase_1 = histograms_subdata.iloc[
                i, background_peak : int((particle_peak_1 + particle_peak_2) / 2)
            ].sum()

            # Appending the phase 1 quantification sum
            q_all_3_phases_1.append([sum_phase_1])

            # Taking the sum of ith row from phase 1 minimum threshold greyscale value till Phase1_max_limit
            sum_phase_2 = histograms_subdata.iloc[
                i,
                int((particle_peak_1 + particle_peak_2) / 2) : int(
                    (particle_peak_2 + particle_peak_3) / 2
                ),
            ].sum()

            # Appending the phase 1 quantification sum
            q_all_3_phases_2.append([sum_phase_2])

            # Taking the sum of ith row from phase 1 minimum threshold greyscale value till Phase1_max_limit
            sum_phase_3 = histograms_subdata.iloc[
                i, int((particle_peak_2 + particle_peak_3) / 2) : 65535
            ].sum()

            # Appending the phase 1 quantification sum
            q_all_3_phases_3.append([sum_phase_3])

            # store index and peaks positions
            index_3_phase.append([index])
            peaks_1_phase.append([particle_peak_1])
            peaks_2_phase.append([particle_peak_2])
            peaks_3_phase.append([particle_peak_3])

            # cannot correct for partial volume effect in 3 phases
            if enable_pvb:
                gradient_ratio = gradient_subdata["Gradient_3"].iloc[i]
            else:
                gradient_ratio = 1

            # sort out the phase limits based on user thresholds
            if particle_peak_1 < phase_1_threshold:
                phase_limit_1 = phase_1_threshold
            elif phase_1_threshold <= particle_peak_1 < phase_2_threshold:
                phase_limit_1 = phase_2_threshold
            elif phase_2_threshold <= particle_peak_1 < phase_3_threshold:
                phase_limit_1 = phase_3_threshold
            else:
                phase_limit_1 = phase_4_threshold

            if phase_1_threshold <= particle_peak_2 < phase_2_threshold:
                phase_limit_2 = phase_2_threshold
            elif phase_2_threshold <= particle_peak_2 < phase_3_threshold:
                phase_limit_2 = phase_3_threshold
            else:
                phase_limit_2 = phase_4_threshold

            # calculate surface volume
            phase_1_s_vol = surface_mesh_subdata.iloc[
                i, background_peak : int(phase_limit_1 * gradient_ratio)
            ].sum()
            phase_2_s_vol = surface_mesh_subdata.iloc[
                i,
                int(phase_limit_1 * gradient_ratio) : int(
                    phase_limit_2 * gradient_ratio
                ),
            ].sum()
            phase_3_s_vol = surface_mesh_subdata.iloc[
                i, int(phase_limit_2 * gradient_ratio) : 65535
            ].sum()

            # store surface volume
            s_vol_phase_1_append.append([phase_1_s_vol])
            s_vol_phase_2_append.append([phase_2_s_vol])
            s_vol_phase_3_append.append([phase_3_s_vol])

            # count
            regions_3_phases += 1
            regions_analysed += 1
            volume_analysed += sum_phase_1 + sum_phase_2 + sum_phase_3

    # indices amd peaks of third phase
    index_3_phase = pd.DataFrame(index_3_phase, columns=["Label"])
    peaks_1_phase = pd.DataFrame(peaks_1_phase, columns=["Peak_1"])
    peaks_2_phase = pd.DataFrame(peaks_2_phase, columns=["Peak_2"])
    peaks_3_phase = pd.DataFrame(peaks_3_phase, columns=["Peak_3"])

    # Quantification DataFrames
    q_all_3_phases_1 = pd.DataFrame(
        q_all_3_phases_1, columns=["total_quantification_phase_1"]
    )
    q_all_3_phases_2 = pd.DataFrame(
        q_all_3_phases_2, columns=["total_quantification_phase_2"]
    )
    q_all_3_phases_3 = pd.DataFrame(
        q_all_3_phases_3, columns=["total_quantification_phase_3"]
    )

    # Surface volume DataFrames
    s_vol_phase_1 = pd.DataFrame(
        s_vol_phase_1_append, columns=["Surface_volume_phase_1"]
    )
    s_vol_phase_1.index = index_3_phase["Label"]
    s_vol_phase_2 = pd.DataFrame(
        s_vol_phase_2_append, columns=["Surface_volume_phase_2"]
    )
    s_vol_phase_2.index = index_3_phase["Label"]
    s_vol_phase_3 = pd.DataFrame(
        s_vol_phase_3_append, columns=["Surface_volume_phase_3"]
    )
    s_vol_phase_3.index = index_3_phase["Label"]

    q_3_phases = pd.concat(
        [
            index_3_phase,
            q_all_3_phases_1,
            q_all_3_phases_2,
            q_all_3_phases_3,
            peaks_1_phase,
            peaks_2_phase,
            peaks_3_phase,
        ],
        axis=1,
    )

    # assign the quantification to the correct peak column in the overall dataset
    cols = ["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5"]
    thresholds = [
        background_peak,
        phase_1_threshold,
        phase_2_threshold,
        phase_3_threshold,
        phase_4_threshold,
        phase_5_threshold,
    ]
    q_3_phase_sorted = pd.DataFrame(
        columns=cols + [f"Phase_{i}_quantification" for i in range(1, 6)]
    )
    q_3_phase_sorted_1 = q_3_phase_sorted.copy()
    q_3_phase_sorted_2 = q_3_phase_sorted.copy()

    for i in range(1, 6):
        mask = (peaks_1_phase["Peak_1"] > thresholds[i - 1]) & (
            peaks_1_phase["Peak_1"] <= thresholds[i]
        )
        q_3_phase_sorted[f"Peak_{i}"] = np.where(mask, peaks_1_phase["Peak_1"], 0)
        q_3_phase_sorted[f"Phase_{i}_quantification"] = np.where(
            mask, q_3_phases["total_quantification_phase_1"], 0
        )
        q_3_phase_sorted[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_vol_phase_1["Surface_volume_phase_1"], 0
        )
    for i in range(1, 6):
        mask = (peaks_2_phase["Peak_2"] > thresholds[i - 1]) & (
            peaks_2_phase["Peak_2"] <= thresholds[i]
        )
        q_3_phase_sorted_1[f"Peak_{i}"] = np.where(mask, peaks_2_phase["Peak_2"], 0)
        q_3_phase_sorted_1[f"Phase_{i}_quantification"] = np.where(
            mask, q_3_phases["total_quantification_phase_2"], 0
        )
        q_3_phase_sorted_1[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_vol_phase_2["Surface_volume_phase_2"], 0
        )
    for i in range(1, 6):
        mask = (peaks_3_phase["Peak_3"] > thresholds[i - 1]) & (
            peaks_3_phase["Peak_3"] <= thresholds[i]
        )
        q_3_phase_sorted_2[f"Peak_{i}"] = np.where(mask, peaks_3_phase["Peak_3"], 0)
        q_3_phase_sorted_2[f"Phase_{i}_quantification"] = np.where(
            mask, q_3_phases["total_quantification_phase_3"], 0
        )
        q_3_phase_sorted_2[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_vol_phase_3["Surface_volume_phase_3"], 0
        )

    # merge the three DataFrames
    q_3_phase_sorted = q_3_phase_sorted.mask(q_3_phase_sorted == 0, q_3_phase_sorted_1)
    q_3_phase_sorted = q_3_phase_sorted.mask(q_3_phase_sorted == 0, q_3_phase_sorted_2)
    q_3_phase_sorted.index = q_3_phases["Label"]

    return (
        q_3_phase_sorted,
        regions_analysed,
        volume_analysed,
        regions_3_phases,
    )


def quaternary_regions(
    histograms_subdata,
    gradient_subdata,
    surface_mesh_subdata,
    array,
    background_peak,
    phase_1_threshold,
    phase_2_threshold,
    phase_3_threshold,
    phase_4_threshold,
    phase_5_threshold,
    regions_analysed,
    volume_analysed,
    regions_3_phases,
    enable_pvb,
):
    """Quantify 4 phases particle."""
    q_all_4_phases_1 = []
    q_all_4_phases_2 = []
    q_all_4_phases_3 = []
    q_all_4_phases_4 = []
    peaks_1_phase = []
    peaks_2_phase = []
    peaks_3_phase = []
    peaks_4_phase = []
    index_4_phase = []
    s_vol_phase_1_append = []
    s_vol_phase_2_append = []
    s_vol_phase_3_append = []
    s_vol_phase_4_append = []

    # iterate over particles
    for i, (index, row) in enumerate(surface_mesh_subdata.iterrows()):
        peaks = array.iloc[[i]].values
        if (np.count_nonzero(peaks > background_peak) == 4) and i > -1:
            particle_peak = peaks[peaks > background_peak]
            particle_peak_1 = int(float(particle_peak.flat[0]))
            particle_peak_2 = int(float(particle_peak.flat[1]))
            particle_peak_3 = int(float(particle_peak.flat[2]))
            particle_peak_4 = int(float(particle_peak.flat[3]))

            # Quantification of phase 1
            sum_phase_1 = histograms_subdata.iloc[
                i, background_peak : int((particle_peak_1 + particle_peak_2) / 2)
            ].sum()
            q_all_4_phases_1.append([sum_phase_1])

            # Quantification of phase 2
            sum_phase_2 = histograms_subdata.iloc[
                i,
                int((particle_peak_1 + particle_peak_2) / 2) : int(
                    (particle_peak_2 + particle_peak_3) / 2
                ),
            ].sum()
            q_all_4_phases_2.append([sum_phase_2])

            # Quantification of phase 3
            sum_phase_3 = histograms_subdata.iloc[
                i,
                int((particle_peak_2 + particle_peak_3) / 2) : int(
                    (particle_peak_3 + particle_peak_4) / 2
                ),
            ].sum()
            q_all_4_phases_3.append([sum_phase_3])

            # Quantification of phase 4
            sum_phase_4 = histograms_subdata.iloc[
                i, int((particle_peak_3 + particle_peak_4) / 2) : 65535
            ].sum()
            q_all_4_phases_4.append([sum_phase_4])

            # store index and peaks positions
            index_4_phase.append([index])
            peaks_1_phase.append([particle_peak_1])
            peaks_2_phase.append([particle_peak_2])
            peaks_3_phase.append([particle_peak_3])
            peaks_4_phase.append([particle_peak_4])

            if enable_pvb:
                gradient_ratio = gradient_subdata["Gradient_3"].iloc[i]
            else:
                gradient_ratio = 1

            # sort out the phase limits based on user thresholds
            if particle_peak_1 < phase_1_threshold:
                phase_limit_1 = phase_1_threshold
            elif phase_1_threshold <= particle_peak_1 < phase_2_threshold:
                phase_limit_1 = phase_2_threshold
            elif phase_2_threshold <= particle_peak_1 < phase_3_threshold:
                phase_limit_1 = phase_3_threshold
            else:
                phase_limit_1 = phase_4_threshold

            if phase_1_threshold <= particle_peak_2 < phase_2_threshold:
                phase_limit_2 = phase_2_threshold
            elif phase_2_threshold <= particle_peak_2 < phase_3_threshold:
                phase_limit_2 = phase_3_threshold
            else:
                phase_limit_2 = phase_4_threshold

            if phase_2_threshold <= particle_peak_3 < phase_3_threshold:
                phase_limit_3 = phase_3_threshold
            else:
                phase_limit_3 = phase_4_threshold

            # calculate surface volume
            phase_1_surface_volume = surface_mesh_subdata.iloc[
                i, background_peak : int(phase_limit_1 * gradient_ratio)
            ].sum()
            phase_2_surface_volume = surface_mesh_subdata.iloc[
                i,
                int(phase_limit_1 * gradient_ratio) : int(
                    phase_limit_2 * gradient_ratio
                ),
            ].sum()
            phase_3_surface_volume = surface_mesh_subdata.iloc[
                i,
                int(phase_limit_2 * gradient_ratio) : int(
                    phase_limit_3 * gradient_ratio
                ),
            ].sum()
            phase_4_surface_volume = surface_mesh_subdata.iloc[
                i, int(phase_limit_3 * gradient_ratio) : 65535
            ].sum()

            # store surface volume
            s_vol_phase_1_append.append([phase_1_surface_volume])
            s_vol_phase_2_append.append([phase_2_surface_volume])
            s_vol_phase_3_append.append([phase_3_surface_volume])
            s_vol_phase_4_append.append([phase_4_surface_volume])

            # count
            regions_3_phases += 1
            regions_analysed += 1
            volume_analysed += sum_phase_1 + sum_phase_2 + sum_phase_3 + sum_phase_4

    # indices and peaks of fourth phase
    index_4_phase = pd.DataFrame(index_4_phase, columns=["Label"])
    peaks_1_phase = pd.DataFrame(peaks_1_phase, columns=["Peak_1"])
    peaks_2_phase = pd.DataFrame(peaks_2_phase, columns=["Peak_2"])
    peaks_3_phase = pd.DataFrame(peaks_3_phase, columns=["Peak_3"])
    peaks_4_phase = pd.DataFrame(peaks_4_phase, columns=["Peak_4"])

    # Quantification DataFrames
    q_all_4_phases_1 = pd.DataFrame(
        q_all_4_phases_1, columns=["total_quantification_phase_1"]
    )
    q_all_4_phases_2 = pd.DataFrame(
        q_all_4_phases_2, columns=["total_quantification_phase_2"]
    )
    q_all_4_phases_3 = pd.DataFrame(
        q_all_4_phases_3, columns=["total_quantification_phase_3"]
    )
    q_all_4_phases_4 = pd.DataFrame(
        q_all_4_phases_4, columns=["total_quantification_phase_4"]
    )

    # Surface volume DataFrames
    surface_volume_phase_1 = pd.DataFrame(
        s_vol_phase_1_append, columns=["Surface_volume_phase_1"]
    )
    surface_volume_phase_1.index = index_4_phase["Label"]
    surface_volume_phase_2 = pd.DataFrame(
        s_vol_phase_2_append, columns=["Surface_volume_phase_2"]
    )
    surface_volume_phase_2.index = index_4_phase["Label"]
    surface_volume_phase_3 = pd.DataFrame(
        s_vol_phase_3_append, columns=["Surface_volume_phase_3"]
    )
    surface_volume_phase_3.index = index_4_phase["Label"]
    surface_volume_phase_4 = pd.DataFrame(
        s_vol_phase_4_append, columns=["Surface_volume_phase_4"]
    )
    surface_volume_phase_4.index = index_4_phase["Label"]
    quantification_4_phases = pd.concat(
        [
            index_4_phase,
            q_all_4_phases_1,
            q_all_4_phases_2,
            q_all_4_phases_3,
            q_all_4_phases_4,
            peaks_1_phase,
            peaks_2_phase,
            peaks_3_phase,
            peaks_4_phase,
        ],
        axis=1,
    )

    # assign the quantification to the correct peak column in the overall dataset
    cols = ["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5"]
    thresholds = [
        background_peak,
        phase_1_threshold,
        phase_2_threshold,
        phase_3_threshold,
        phase_4_threshold,
        phase_5_threshold,
    ]

    q_4_phase_sorted = pd.DataFrame(
        columns=cols + [f"Phase_{i}_quantification" for i in range(1, 6)]
    )
    q_4_phase_sorted_1 = q_4_phase_sorted.copy()
    q_4_phase_sorted_2 = q_4_phase_sorted.copy()
    q_4_phase_sorted_3 = q_4_phase_sorted.copy()
    for i in range(1, 6):
        mask = (peaks_1_phase["Peak_1"] > thresholds[i - 1]) & (
            peaks_1_phase["Peak_1"] <= thresholds[i]
        )
        q_4_phase_sorted[f"Peak_{i}"] = np.where(mask, peaks_1_phase["Peak_1"], 0)
        q_4_phase_sorted[f"Phase_{i}_quantification"] = np.where(
            mask, quantification_4_phases["total_quantification_phase_1"], 0
        )
        q_4_phase_sorted[f"Phase_{i}_surface_quantification"] = np.where(
            mask, surface_volume_phase_1["Surface_volume_phase_1"], 0
        )
    for i in range(1, 6):
        mask = (peaks_2_phase["Peak_2"] > thresholds[i - 1]) & (
            peaks_2_phase["Peak_2"] <= thresholds[i]
        )
        q_4_phase_sorted_1[f"Peak_{i}"] = np.where(mask, peaks_2_phase["Peak_2"], 0)
        q_4_phase_sorted_1[f"Phase_{i}_quantification"] = np.where(
            mask, quantification_4_phases["total_quantification_phase_2"], 0
        )
        q_4_phase_sorted_1[f"Phase_{i}_surface_quantification"] = np.where(
            mask, surface_volume_phase_2["Surface_volume_phase_2"], 0
        )
    for i in range(1, 6):
        mask = (peaks_3_phase["Peak_3"] > thresholds[i - 1]) & (
            peaks_3_phase["Peak_3"] <= thresholds[i]
        )
        q_4_phase_sorted_2[f"Peak_{i}"] = np.where(mask, peaks_3_phase["Peak_3"], 0)
        q_4_phase_sorted_2[f"Phase_{i}_quantification"] = np.where(
            mask, quantification_4_phases["total_quantification_phase_3"], 0
        )
        q_4_phase_sorted_2[f"Phase_{i}_surface_quantification"] = np.where(
            mask, surface_volume_phase_3["Surface_volume_phase_3"], 0
        )
    for i in range(1, 6):
        mask = (peaks_4_phase["Peak_4"] > thresholds[i - 1]) & (
            peaks_4_phase["Peak_4"] <= thresholds[i]
        )
        q_4_phase_sorted_3[f"Peak_{i}"] = np.where(mask, peaks_4_phase["Peak_4"], 0)
        q_4_phase_sorted_3[f"Phase_{i}_quantification"] = np.where(
            mask, quantification_4_phases["total_quantification_phase_4"], 0
        )
        q_4_phase_sorted_3[f"Phase_{i}_surface_quantification"] = np.where(
            mask, surface_volume_phase_4["Surface_volume_phase_4"], 0
        )

    # merge the four DataFrames
    q_4_phase_sorted = q_4_phase_sorted.mask(q_4_phase_sorted == 0, q_4_phase_sorted_1)
    q_4_phase_sorted = q_4_phase_sorted.mask(q_4_phase_sorted == 0, q_4_phase_sorted_2)
    q_4_phase_sorted = q_4_phase_sorted.mask(q_4_phase_sorted == 0, q_4_phase_sorted_3)
    q_4_phase_sorted.index = quantification_4_phases["Label"]

    return (
        q_4_phase_sorted,
        regions_analysed,
        volume_analysed,
        regions_3_phases,
    )


def quinary_regions(
    histograms_subdata,
    gradient_subdata,
    surface_mesh_subdata,
    subdata_properties,
    background_peak,
    phase_1_threshold,
    phase_2_threshold,
    phase_3_threshold,
    phase_4_threshold,
    phase_5_threshold,
    regions_analysed,
    volume_analysed,
    regions_3_phases,
    enable_pvb,
):
    """Quantify 5 phases particle."""
    q_all_5_phases_1 = []
    q_all_5_phases_2 = []
    q_all_5_phases_3 = []
    q_all_5_phases_4 = []
    q_all_5_phases_5 = []
    peaks_1_phase = []
    peaks_2_phase = []
    peaks_3_phase = []
    peaks_4_phase = []
    peaks_5_phase = []
    index_5_phase = []
    s_vol_phase_1_append = []
    s_vol_phase_2_append = []
    s_vol_phase_3_append = []
    s_vol_phase_4_append = []
    s_vol_phase_5_append = []

    # loop through each particles
    for i, (index, row) in enumerate(surface_mesh_subdata.iterrows()):
        peaks = subdata_properties.iloc[[i]].values
        if (np.count_nonzero(peaks > background_peak) == 5) and i > -1:
            particle_peak = peaks[peaks > background_peak]
            particle_peak_1 = int(float(particle_peak.flat[0]))
            particle_peak_2 = int(float(particle_peak.flat[1]))
            particle_peak_3 = int(float(particle_peak.flat[2]))
            particle_peak_4 = int(float(particle_peak.flat[3]))
            particle_peak_5 = int(float(particle_peak.flat[4]))

            # Quantification of phase 1
            sum_phase_1 = histograms_subdata.iloc[
                i, background_peak : int((particle_peak_1 + particle_peak_2) / 2)
            ].sum()
            q_all_5_phases_1.append([sum_phase_1])

            # Quantification of phase 2
            sum_phase_2 = histograms_subdata.iloc[
                i,
                int((particle_peak_1 + particle_peak_2) / 2) : int(
                    (particle_peak_2 + particle_peak_3) / 2
                ),
            ].sum()
            q_all_5_phases_2.append([sum_phase_2])

            # Quantification of phase 3
            sum_phase_3 = histograms_subdata.iloc[
                i,
                int((particle_peak_2 + particle_peak_3) / 2) : int(
                    (particle_peak_3 + particle_peak_4) / 2
                ),
            ].sum()
            q_all_5_phases_3.append([sum_phase_3])

            # Quantification of phase 4
            sum_phase_4 = histograms_subdata.iloc[
                i,
                int((particle_peak_3 + particle_peak_4) / 2) : int(
                    (particle_peak_4 + particle_peak_5) / 2
                ),
            ].sum()
            q_all_5_phases_4.append([sum_phase_4])

            # Quantification of phase 5
            sum_phase_5 = histograms_subdata.iloc[
                i, int((particle_peak_4 + particle_peak_5) / 2) : 65535
            ].sum()
            sum_phase_5 = sum_phase_5.sum()
            q_all_5_phases_5.append([sum_phase_5])

            # store index and peaks positions
            index_5_phase.append([index])
            peaks_1_phase.append([particle_peak_1])
            peaks_2_phase.append([particle_peak_2])
            peaks_3_phase.append([particle_peak_3])
            peaks_4_phase.append([particle_peak_4])
            peaks_5_phase.append([particle_peak_5])

            if enable_pvb:
                gradient_ratio = gradient_subdata["Gradient_3"].iloc[i]
            else:
                gradient_ratio = 1

            # Since all phases occur in the same particle, we can use the user-defined thresholds
            phase_limit_1 = phase_1_threshold
            phase_limit_2 = phase_2_threshold
            phase_limit_3 = phase_3_threshold
            phase_limit_4 = phase_4_threshold

            # Calculate surface volume
            s_vol_phase_1 = surface_mesh_subdata.iloc[
                i, background_peak : int(phase_limit_1 * gradient_ratio)
            ].sum()
            s_vol_phase_2 = surface_mesh_subdata.iloc[
                i,
                int(phase_limit_1 * gradient_ratio) : int(
                    phase_limit_2 * gradient_ratio
                ),
            ].sum()
            s_vol_phase_3 = surface_mesh_subdata.iloc[
                i,
                int(phase_limit_2 * gradient_ratio) : int(
                    phase_limit_3 * gradient_ratio
                ),
            ].sum()
            s_vol_phase_4 = surface_mesh_subdata.iloc[
                i,
                int(phase_limit_3 * gradient_ratio) : int(
                    phase_limit_4 * gradient_ratio
                ),
            ].sum()
            s_vol_phase_5 = surface_mesh_subdata.iloc[
                i, int(phase_limit_4 * gradient_ratio) : 65535
            ].sum()

            # store surface volume
            s_vol_phase_1_append.append([s_vol_phase_1])
            s_vol_phase_2_append.append([s_vol_phase_2])
            s_vol_phase_3_append.append([s_vol_phase_3])
            s_vol_phase_4_append.append([s_vol_phase_4])
            s_vol_phase_5_append.append([s_vol_phase_5])

            # count
            regions_3_phases += 1
            regions_analysed += 1
            volume_analysed += (
                sum_phase_1 + sum_phase_2 + sum_phase_3 + sum_phase_4 + sum_phase_5
            )

    # indices and peaks of fifth phase
    index_5_phase = pd.DataFrame(index_5_phase, columns=["Label"])
    peaks_1_phase = pd.DataFrame(peaks_1_phase, columns=["Peak_1"])
    peaks_2_phase = pd.DataFrame(peaks_2_phase, columns=["Peak_2"])
    peaks_3_phase = pd.DataFrame(peaks_3_phase, columns=["Peak_3"])
    peaks_4_phase = pd.DataFrame(peaks_4_phase, columns=["Peak_4"])
    peaks_5_phase = pd.DataFrame(peaks_5_phase, columns=["Peak_5"])

    # Quantification DataFrames
    q_all_5_phases_1 = pd.DataFrame(
        q_all_5_phases_1, columns=["total_quantification_phase_1"]
    )
    q_all_5_phases_2 = pd.DataFrame(
        q_all_5_phases_2, columns=["total_quantification_phase_2"]
    )
    q_all_5_phases_3 = pd.DataFrame(
        q_all_5_phases_3, columns=["total_quantification_phase_3"]
    )
    q_all_5_phases_4 = pd.DataFrame(
        q_all_5_phases_4, columns=["total_quantification_phase_4"]
    )
    q_all_5_phases_5 = pd.DataFrame(
        q_all_5_phases_5, columns=["total_quantification_phase_5"]
    )

    # Surface volume DataFrames
    s_vol_phase_1 = pd.DataFrame(
        s_vol_phase_1_append, columns=["Surface_volume_phase_1"]
    )
    s_vol_phase_1.index = index_5_phase["Label"]

    s_vol_phase_2 = pd.DataFrame(
        s_vol_phase_2_append, columns=["Surface_volume_phase_2"]
    )
    s_vol_phase_2.index = index_5_phase["Label"]

    s_vol_phase_3 = pd.DataFrame(
        s_vol_phase_3_append, columns=["Surface_volume_phase_3"]
    )
    s_vol_phase_3.index = index_5_phase["Label"]

    s_vol_phase_4 = pd.DataFrame(
        s_vol_phase_4_append, columns=["Surface_volume_phase_4"]
    )
    s_vol_phase_4.index = index_5_phase["Label"]

    s_vol_phase_5 = pd.DataFrame(
        s_vol_phase_5_append, columns=["Surface_volume_phase_5"]
    )
    s_vol_phase_5.index = index_5_phase["Label"]

    # Concatenate all DataFrames
    q_5_phases = pd.concat(
        [
            index_5_phase,
            q_all_5_phases_1,
            q_all_5_phases_2,
            q_all_5_phases_3,
            q_all_5_phases_4,
            q_all_5_phases_5,
            peaks_1_phase,
            peaks_2_phase,
            peaks_3_phase,
            peaks_4_phase,
            peaks_5_phase,
        ],
        axis=1,
    )

    # assign the quantification to the correct peak column in the overall dataset
    cols = ["Peak_1", "Peak_2", "Peak_3", "Peak_4", "Peak_5"]
    thresholds = [
        background_peak,
        phase_1_threshold,
        phase_2_threshold,
        phase_3_threshold,
        phase_4_threshold,
        phase_5_threshold,
    ]
    q_5_phase_sorted = pd.DataFrame(
        columns=cols + [f"Phase_{i}_quantification" for i in range(1, 6)]
    )
    q_5_phase_sorted_1 = q_5_phase_sorted.copy()
    q_5_phase_sorted_2 = q_5_phase_sorted.copy()
    q_5_phase_sorted_3 = q_5_phase_sorted.copy()
    q_5_phase_sorted_4 = q_5_phase_sorted.copy()
    for i in range(1, 6):
        mask = (peaks_1_phase["Peak_1"] > thresholds[i - 1]) & (
            peaks_1_phase["Peak_1"] <= thresholds[i]
        )
        q_5_phase_sorted[f"Peak_{i}"] = np.where(mask, peaks_1_phase["Peak_1"], 0)
        q_5_phase_sorted[f"Phase_{i}_quantification"] = np.where(
            mask, q_5_phases["total_quantification_phase_1"], 0
        )
        q_5_phase_sorted[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_vol_phase_1["Surface_volume_phase_1"], 0
        )
    for i in range(1, 6):
        mask = (peaks_2_phase["Peak_2"] > thresholds[i - 1]) & (
            peaks_2_phase["Peak_2"] <= thresholds[i]
        )
        q_5_phase_sorted_1[f"Peak_{i}"] = np.where(mask, peaks_2_phase["Peak_2"], 0)
        q_5_phase_sorted_1[f"Phase_{i}_quantification"] = np.where(
            mask, q_5_phases["total_quantification_phase_2"], 0
        )
        q_5_phase_sorted_1[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_vol_phase_2["Surface_volume_phase_2"], 0
        )
    for i in range(1, 6):
        mask = (peaks_3_phase["Peak_3"] > thresholds[i - 1]) & (
            peaks_3_phase["Peak_3"] <= thresholds[i]
        )
        q_5_phase_sorted_2[f"Peak_{i}"] = np.where(mask, peaks_3_phase["Peak_3"], 0)
        q_5_phase_sorted_2[f"Phase_{i}_quantification"] = np.where(
            mask, q_5_phases["total_quantification_phase_3"], 0
        )
        q_5_phase_sorted_2[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_vol_phase_3["Surface_volume_phase_3"], 0
        )
    for i in range(1, 6):
        mask = (peaks_4_phase["Peak_4"] > thresholds[i - 1]) & (
            peaks_4_phase["Peak_4"] <= thresholds[i]
        )
        q_5_phase_sorted_3[f"Peak_{i}"] = np.where(mask, peaks_4_phase["Peak_4"], 0)
        q_5_phase_sorted_3[f"Phase_{i}_quantification"] = np.where(
            mask, q_5_phases["total_quantification_phase_4"], 0
        )
        q_5_phase_sorted_3[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_vol_phase_4["Surface_volume_phase_4"], 0
        )
    for i in range(1, 6):
        mask = (peaks_5_phase["Peak_5"] > thresholds[i - 1]) & (
            peaks_5_phase["Peak_5"] <= thresholds[i]
        )
        q_5_phase_sorted_4[f"Peak_{i}"] = np.where(mask, peaks_5_phase["Peak_5"], 0)
        q_5_phase_sorted_4[f"Phase_{i}_quantification"] = np.where(
            mask, q_5_phases["total_quantification_phase_5"], 0
        )
        q_5_phase_sorted_4[f"Phase_{i}_surface_quantification"] = np.where(
            mask, s_vol_phase_5["Surface_volume_phase_5"], 0
        )

    # merge the five DataFrames
    q_5_phase_sorted = q_5_phase_sorted.mask(q_5_phase_sorted == 0, q_5_phase_sorted_1)
    q_5_phase_sorted = q_5_phase_sorted.mask(q_5_phase_sorted == 0, q_5_phase_sorted_2)
    q_5_phase_sorted = q_5_phase_sorted.mask(q_5_phase_sorted == 0, q_5_phase_sorted_3)
    q_5_phase_sorted = q_5_phase_sorted.mask(q_5_phase_sorted == 0, q_5_phase_sorted_4)
    q_5_phase_sorted.index = q_5_phases["Label"]

    return (
        q_5_phase_sorted,
        regions_analysed,
        volume_analysed,
        regions_3_phases,
    )


def arrange_columns(df):
    df["Label"] = df.index
    column_order = [
        "Label",
        "Peak_1",
        "Peak_2",
        "Peak_3",
        "Peak_4",
        "Peak_5",
        "Phase_1_quantification",
        "Phase_2_quantification",
        "Phase_3_quantification",
        "Phase_4_quantification",
        "Phase_5_quantification",
        "Phase_1_surface_quantification",
        "Phase_2_surface_quantification",
        "Phase_3_surface_quantification",
        "Phase_4_surface_quantification",
        "Phase_5_surface_quantification",
    ]
    # Check if all columns in column_order exist in the DataFrame
    missing_columns = [col for col in column_order if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Columns {missing_columns} not found in DataFrame.")
    # Arrange columns
    arranged_df = df[column_order]
    arranged_df = arranged_df.fillna(0)
    return arranged_df


def quantify_mineralogy(
    properties_data_w_peaks,
    peak_height,
    histograms_data,
    surface_mesh_histograms,
    inner_volume_histograms,
    outer_volume_histograms,
    phase_thresholds_dict,
    enable_pvb,
):
    """Quantify mineralogy based on histograms."""
    properties_data_w_peaks = pd.DataFrame(properties_data_w_peaks)
    part_list = properties_data_w_peaks.index.to_list()

    # filter the histogram data to contain only the particles for which a valid peak was found
    out_histogram_subdata = outer_volume_histograms.loc[part_list]
    surface_mesh_subdata = surface_mesh_histograms.loc[part_list]
    in_histogram_subdata = inner_volume_histograms.loc[part_list]
    histograms_subdata = histograms_data.loc[part_list]
    gradient_subdata = gradient.loc[part_list]

    # subdata_properties is a subdataset from properties that contains only the peaks
    subdata_properties = _update_peak_positions(
        properties_data_w_peaks, phase_thresholds_dict["BackgroundT"], peak_height
    )

    # counter variables
    regions_3_phases = 0
    regions_analysed = 0
    volume_analysed = 0

    phaseA = 0
    phaseB = 0
    phaseC = 0
    phaseD = 0
    phaseE = 0

    (
        q_liberated,
        regions_liberated,
        regions_analysed,
        volume_analysed,
    ) = quantify_liberated_regions(
        histograms_subdata,
        surface_mesh_subdata,
        subdata_properties,
        phase_thresholds_dict["BackgroundT"],
        phase_thresholds_dict["Max greyvalue A"],
        phase_thresholds_dict["Max greyvalue B"],
        phase_thresholds_dict["Max greyvalue C"],
        phase_thresholds_dict["Max greyvalue D"],
        phase_thresholds_dict["Max greyvalue E"],
        regions_analysed,
        volume_analysed,
        enable_pvb,
    )
    (
        q_binary,
        regions_2_phases,
        regions_analysed,
        volume_analysed,
    ) = quantify_two_phases_particle(
        histograms_subdata,
        in_histogram_subdata,
        out_histogram_subdata,
        surface_mesh_subdata,
        gradient_subdata,
        subdata_properties,
        phase_thresholds_dict["BackgroundT"],
        phase_thresholds_dict["Max greyvalue A"],
        phase_thresholds_dict["Max greyvalue B"],
        phase_thresholds_dict["Max greyvalue C"],
        phase_thresholds_dict["Max greyvalue D"],
        phase_thresholds_dict["Max greyvalue E"],
        regions_analysed,
        volume_analysed,
        enable_pvb,
    )
    (
        q_ternary,
        regions_analysed,
        volume_analysed,
        regions_3_phases,
    ) = quantify3_phases_particle(
        histograms_subdata,
        gradient_subdata,
        surface_mesh_subdata,
        subdata_properties,
        phase_thresholds_dict["BackgroundT"],
        phase_thresholds_dict["Max greyvalue A"],
        phase_thresholds_dict["Max greyvalue B"],
        phase_thresholds_dict["Max greyvalue C"],
        phase_thresholds_dict["Max greyvalue D"],
        phase_thresholds_dict["Max greyvalue E"],
        regions_analysed,
        volume_analysed,
        regions_3_phases,
        False,
    )
    (
        q_quarternary,
        regions_analysed,
        volume_analysed,
        regions_3_phases,
    ) = quaternary_regions(
        histograms_subdata,
        gradient_subdata,
        surface_mesh_subdata,
        subdata_properties,
        phase_thresholds_dict["BackgroundT"],
        phase_thresholds_dict["Max greyvalue A"],
        phase_thresholds_dict["Max greyvalue B"],
        phase_thresholds_dict["Max greyvalue C"],
        phase_thresholds_dict["Max greyvalue D"],
        phase_thresholds_dict["Max greyvalue E"],
        regions_analysed,
        volume_analysed,
        regions_3_phases,
        False,
    )
    q_quintary, regions_analysed, volume_analysed, regions_3_phases = quinary_regions(
        histograms_subdata,
        gradient_subdata,
        surface_mesh_subdata,
        subdata_properties,
        phase_thresholds_dict["BackgroundT"],
        phase_thresholds_dict["Max greyvalue A"],
        phase_thresholds_dict["Max greyvalue B"],
        phase_thresholds_dict["Max greyvalue C"],
        phase_thresholds_dict["Max greyvalue D"],
        phase_thresholds_dict["Max greyvalue E"],
        regions_analysed,
        volume_analysed,
        regions_3_phases,
        False,
    )
    q_liberated = arrange_columns(q_liberated)
    q_binary = arrange_columns(q_binary)
    q_ternary = arrange_columns(q_ternary)
    q_quarternary = arrange_columns(q_quarternary)
    q_quintary = arrange_columns(q_quintary)

    non_empty_quantification_ds = [
        df.dropna(how="all")
        for df in [q_liberated, q_binary, q_ternary, q_quarternary, q_quintary]
        if not df.dropna(how="all").empty
    ]
    quantification = pd.concat(non_empty_quantification_ds, axis=0)
    quantification["Total_quantification"] = (
        quantification["Phase_1_quantification"]
        + quantification["Phase_2_quantification"]
        + quantification["Phase_3_quantification"]
        + quantification["Phase_4_quantification"]
        + quantification["Phase_5_quantification"]
    )
    quantification = quantification.sort_index(ascending=True)
    surfaceA = quantification["Phase_1_surface_quantification"].sum()
    surfaceB = quantification["Phase_2_surface_quantification"].sum()
    surfaceC = quantification["Phase_3_surface_quantification"].sum()
    surfaceD = quantification["Phase_4_surface_quantification"].sum()
    surfaceE = quantification["Phase_5_surface_quantification"].sum()

    phaseA_mass = (
        quantification["Phase_1_quantification"].sum()
        * phase_thresholds_dict["DensityA"]
    )
    phaseB_mass = (
        quantification["Phase_2_quantification"].sum()
        * phase_thresholds_dict["DensityB"]
    )
    phaseC_mass = (
        quantification["Phase_3_quantification"].sum()
        * phase_thresholds_dict["DensityC"]
    )
    phaseD_mass = (
        quantification["Phase_4_quantification"].sum()
        * phase_thresholds_dict["DensityD"]
    )
    phaseE_mass = (
        quantification["Phase_5_quantification"].sum()
        * phase_thresholds_dict["DensityE"]
    )

    volumeAnalysed2 = (
        quantification["Phase_1_quantification"].sum()
        + quantification["Phase_2_quantification"].sum()
        + quantification["Phase_3_quantification"].sum()
        + quantification["Phase_4_quantification"].sum()
        + quantification["Phase_5_quantification"].sum()
    )
    surfaceAnalysed = surfaceA + surfaceB + surfaceC + surfaceD + surfaceE

    totalMass = phaseA_mass + phaseB_mass + phaseC_mass + phaseD_mass + phaseE_mass
    if totalMass > 0:
        phaseA = round(phaseA_mass * 100 / totalMass, 1)
        phaseB = round(phaseB_mass * 100 / totalMass, 1)
        phaseC = round(phaseC_mass * 100 / totalMass, 1)
        phaseD = round(phaseD_mass * 100 / totalMass, 1)
        phaseE = round(phaseE_mass * 100 / totalMass, 1)
        surfaceA = round(surfaceA * 100 / surfaceAnalysed, 1)
        surfaceB = round(surfaceB * 100 / surfaceAnalysed, 1)
        surfaceC = round(surfaceC * 100 / surfaceAnalysed, 1)
        surfaceD = round(surfaceD * 100 / surfaceAnalysed, 1)
        surfaceE = round(surfaceE * 100 / surfaceAnalysed, 1)

    properties_data_w_peaks.index = properties_data_w_peaks["label"]
    columns_to_keep = [
        col
        for col in properties_data_w_peaks.columns
        if col not in quantification.columns or col == "Label"
    ]
    properties_data_w_peaks = properties_data_w_peaks[columns_to_keep]
    quantification = pd.merge(
        quantification, properties_data_w_peaks, left_index=True, right_index=True
    )

    report = {
        "regions2Phases": regions_2_phases,
        "regions3Phases": regions_3_phases,
        "regionsAnalysed": regions_analysed,
        "volumeAnalysed2": volumeAnalysed2,
        "regionsLiberated": regions_liberated,
        "volumeAnalysed": volume_analysed,
        "surfaceAnalysed": surfaceAnalysed,
        "totalMass": totalMass,
        "phaseA": phaseA,
        "phaseB": phaseB,
        "phaseC": phaseC,
        "phaseD": phaseD,
        "phaseE": phaseE,
        "phaseA_mass": phaseA_mass,
        "phaseB_mass": phaseB_mass,
        "phaseC_mass": phaseC_mass,
        "phaseD_mass": phaseD_mass,
        "phaseE_mass": phaseE_mass,
        "surfaceA": surfaceA,
        "surfaceB": surfaceB,
        "surfaceC": surfaceC,
        "surfaceD": surfaceD,
        "surfaceE": surfaceE,
    }

    return report, quantification


def file_name(path):
    """Select the type of histograms using a dropdown menu, must be h5ad."""
    import streamlit as st

    # initialize streamlit
    st.set_page_config(layout="wide", page_title="All streamlit steps in 1 app")

    histogram_files = [f for f in os.listdir(path) if f.endswith(".h5ad")]
    histogram_type = st.sidebar.selectbox(
        "Histogram type",
        histogram_files,
        index=0,
        help="TIP: Bulk histograms should be used for a general assessment of the parameters.",
    )  # it resets if new files are created in folder 'Data'
    return histogram_type


############################### Streamlit #################################

################## CMD Arguments ##################
data_directory = sys.argv[1]
report_directory = sys.argv[2]
parameters_json = sys.argv[3]
run_online =  sys.argv[4]  # option to run this script without streamlit offline


if not run_online:
    print("Data Directory:", data_directory)
    print("Report Directory:", report_directory)
    print("Parameters JSON:", parameters_json)
    print("Run Online:", run_online)

parameters_dict = get_dict_from_yml(parameters_json)

################## Data ##################
if run_online == "True":  # do not use bool here without converting cmd argument
    print("Running in online mode")
    file = file_name(data_directory)
else:
    print("Running in offline mode")
    file = "Bulk_histograms.h5ad"  # default file name for offline mode

# bulk histograms (= Inner + Outer)
path_load_chosen_histogram = os.path.join(data_directory, file)
# inner histograms (inside the region without the eroded voxels)
path_load_inner_histograms = os.path.join(data_directory, "Inner_histograms.h5ad")
# outer (surface layers consisting of all voxels eroded) volume histograms
path_load_outer_histograms = os.path.join(data_directory, "Outer_histograms.h5ad")
# mesh histograms
path_load_surface_mesh_histograms = os.path.join(
    data_directory, "Surface_histogram.h5ad"
)
# gradient
path_load_gradient = os.path.join(data_directory, "Gradient.csv")

################## load global parameters ##################
enable_pvb = parameters_dict["enablePVB"]

################## offline Arguments ##################
if run_online == "False":
    # load data without streamlit caching
    bulk_histograms_data, initialBins = load_histograms(path_load_chosen_histogram)
    bulk_histograms_data = bulk_histograms_data.rename_axis("label")
    bulk_histograms_data = bulk_histograms_data.astype("float64")
    bulk_histograms_data = bulk_histograms_data.iloc[:, 1:]

    propertiesData = load_properties(data_directory)
    propertiesData.index = propertiesData["label"]

    inner_volume_histograms = load_in_volume(path_load_inner_histograms)
    outer_volume_histograms = load_out_volume(path_load_outer_histograms)
    surface_mesh_histogram = load_mesh(path_load_surface_mesh_histograms)
    gradient = load_gradient(path_load_gradient)

    peak_width = parameters_dict["gray_value_width"]
    peak_height = parameters_dict["min_frequency"]
    peak_prominence = parameters_dict["prominence"]
    peak_horizontal_distance = parameters_dict["horizDistance"]
    peak_vertical_distance = parameters_dict["vertDistance"]

    binInput = parameters_dict["binInput"]
    number_bins = int(initialBins / binInput)
    savgolInput = parameters_dict["savgolInput"]
    enable_savgol = parameters_dict["enableSavgol"]

    phase_thresholds_dict = {
        "BackgroundT": parameters_dict["background_q"],
        "DensityA": parameters_dict["DensityA"],
        "Max greyvalue A": parameters_dict["MaxGreyValueA"],
        "DensityB": parameters_dict["DensityB"],
        "Max greyvalue B": parameters_dict["MaxGreyValueB"],
        "DensityC": parameters_dict["DensityC"],
        "Max greyvalue C": parameters_dict["MaxGreyValueC"],
        "DensityD": parameters_dict["DensityD"],
        "Max greyvalue D": parameters_dict["MaxGreyValueD"],
        "DensityE": parameters_dict["DensityE"],
        "Max greyvalue E": parameters_dict["MaxGreyValueE"],
    }

    ################## offline process ##################

    bulk_histograms_binned = binning(binInput, bulk_histograms_data, n_jobs=-1)
    if enable_savgol:
        savgolSmooth = smooth_histograms_savgol(
            bulk_histograms_binned, savgolInput, n_jobs=-1
        )
        normalized_chosen_histograms_binned = normalize_volume(savgolSmooth)
    else:
        normalized_chosen_histograms_binned = normalize_volume(bulk_histograms_binned)

    PeaksSubData = process_peaks(
        normalized_chosen_histograms_binned,
        bulk_histograms_data,
        propertiesData,
        number_bins,
        peak_width,
        peak_height,
        peak_prominence,
        peak_vertical_distance,
        peak_horizontal_distance,
        binInput,
    )
    propertiesAndPeaks = arrange_peaks(
        PeaksSubData,
        phase_thresholds_dict,
        propertiesData,
    )

    report, quantification = quantify_mineralogy(
        propertiesAndPeaks,
        peak_height,
        bulk_histograms_data,
        surface_mesh_histogram,
        inner_volume_histograms,
        outer_volume_histograms,
        phase_thresholds_dict,
        enable_pvb,
    )
    # add particle volume to report
    report["totalParticleVolume"] = str(propertiesData["Volume"].sum())

    # save report
    report_path = os.path.join(report_directory, "report.yml")
    write_report_to_yml(report_path, report)

    # save quantification
    path_save_Quantification = os.path.join(report_directory, "Quantification.csv")
    quantification.to_csv(path_save_Quantification, index=False)

################## online Arguments ##################
else:
    from tkinter.filedialog import askdirectory

    import streamlit as st

    ############################### Streamlit #################################
    tabHistOverview, tabFindPeaks, tabHistogramProperty, tabQuantify = st.tabs(
        ["Histogram Overview", "Peak Finder", "Properties", "Quantification"]
    )

    @st.cache_data
    def directory():
        path = askdirectory(title="select folder with data")  ## folder 'data'
        return path

    @st.cache_data
    def load_histograms(path_bulk_histogram):
        """Load the bulk histograms from the h5ad file and convert it to a DataFrame."""
        print("path histograms:", path_bulk_histogram)
        histogram_ds = _load_ann_data(
            path_bulk_histogram, "h5ad bulk converted to DataFrame successfully."
        )
        initial_bins = len(histogram_ds.columns)

        return histogram_ds, initial_bins

    @st.cache_data
    def load_properties(path):
        """Load the properties from the csv file and convert it to a DataFrame."""
        path_and_name = os.path.join(path, "Properties.csv")
        properties_data = pd.read_csv(path_and_name, encoding="unicode_escape")
        return properties_data

    @st.cache_data
    def load_in_volume(_path_load_inner_histograms):
        """Load the Inner histograms from the h5ad file and convert it to a DataFrame."""
        return _load_ann_data(
            _path_load_inner_histograms,
            "h5ad inner histogram converted to DataFrame successfully.",
        )

    @st.cache_data
    def load_out_volume(_path_load_outer_histograms):
        """Load the Outer histograms from the h5ad file and convert it to a DataFrame."""
        return _load_ann_data(
            _path_load_outer_histograms,
            "h5ad outer histogram converted to DataFrame successfully.",
        )

    @st.cache_data
    def load_mesh(_path_load_surface_mesh_histograms):
        """Load the Mesh data from the h5ad file and convert it to a DataFrame."""
        return _load_ann_data(
            _path_load_surface_mesh_histograms,
            "h5ad Surface mesh converted to DataFrame successfully.",
        )

    @st.cache_data
    def load_gradient(path_load_gradient):
        """Load the gradient from the csv file and convert it to a DataFrame."""
        gradient = pd.read_csv(path_load_gradient)
        gradient.index = gradient["label"]
        return gradient

    ############################### Online Plot #################################

    @st.cache_data
    def plot_histogram_overview(plot_data):
        color_std = alt.Color(
            "frequency:Q",
            scale=alt.Scale(scheme="viridis", domainMax=0.06),
            legend=alt.Legend(orient="bottom"),
            title="Frequency",
        )
        particle_number = alt.X("X:N", title="Region")
        grey_bin = alt.Y("Y:O", title="Binned Greyscale").bin(maxbins=52)
        heat_map_part_select = alt.selection_point(
            encodings=["x"], fields=["X"]
        )  # to select points on a trigger defined in "encodings", e.g. XY position
        opacity_selection = alt.condition(
            heat_map_part_select, alt.value(1.0), alt.value(0.2)
        )
        plot_all_histograms = (
            alt.Chart(plot_data, width=1500, height=1000)
            .mark_area(opacity=0.3)
            .encode(
                x=alt.X("Y", title="Greyscale"),
                y=alt.Y("frequency", title="Frequency").stack(None),
                color=(particle_number),
                tooltip=("X"),
            )
            .transform_filter(heat_map_part_select)
            .interactive(bind_x=False, bind_y=True)
        )
        heat_map_histograms = (
            alt.Chart(plot_data, width=900, height=900)
            .mark_rect()
            .encode(
                x=particle_number,
                y=grey_bin,
                color=color_std,
                opacity=opacity_selection,
                tooltip=("X", "Y"),
            )
            .add_params(heat_map_part_select)
            .interactive()
        )
        plot = plot_all_histograms | heat_map_histograms
        st.altair_chart(plot, use_container_width=True)

    def _make_peak_mark(peaks_df, x_col, y_col, color):
        return (
            alt.Chart(peaks_df, width=1000, height=500)
            .mark_circle(color=color, size=200, opacity=0.85)
            .encode(
                x=alt.X(x_col, title="Greyscale"), y=alt.Y(y_col, title="Frequency")
            )
        )

    def _make_threshold_line(thresh_val, color, label):
        return (
            alt.Chart(pd.DataFrame({"threshold": [thresh_val]}))
            .mark_rule(color=color, strokeDash=[4, 4], size=2)
            .encode(x="threshold:Q")
            .properties(title=label)
        )

    @st.cache_data
    def plot_peaks(plot_data, peaks_df, phase_thresholds):
        particle_number = alt.X("X:N", title="Region")
        plot_all_histograms = (
            alt.Chart(plot_data, width=1000, height=500)
            .mark_line()
            .encode(
                x=alt.X("Y", title="Greyscale"),
                y=alt.Y("frequency", title="Frequency"),
                color=(particle_number),
                tooltip=("X"),
            )
            .interactive(bind_x=True, bind_y=True)
        )
        peak1_marks = _make_peak_mark(peaks_df, "Peak_1", "Peaks_Height_1", "#7fc97f")
        peak2_marks = _make_peak_mark(peaks_df, "Peak_2", "Peaks_Height_2", "#beaed4")
        peak3_marks = _make_peak_mark(peaks_df, "Peak_3", "Peaks_Height_3", "#fdc086")
        peak4_marks = _make_peak_mark(peaks_df, "Peak_4", "Peaks_Height_4", "yellow")
        peak5_marks = _make_peak_mark(peaks_df, "Peak_5", "Peaks_Height_5", "#386cb0")

        threshold_lines = (
            _make_threshold_line(phase_thresholds["BackgroundT"], "black", "Phase 1")
            + _make_threshold_line(
                phase_thresholds["Max greyvalue A"], "#7fc97f", "Phase 1"
            )
            + _make_threshold_line(
                phase_thresholds["Max greyvalue B"], "#beaed4", "Phase 2"
            )
            + _make_threshold_line(
                phase_thresholds["Max greyvalue C"], "#fdc086", "Phase 3"
            )
            + _make_threshold_line(
                phase_thresholds["Max greyvalue D"], "#BBD82C", "Phase 4"
            )
            + _make_threshold_line(
                phase_thresholds["Max greyvalue E"], "#386cb0", "Phase 5"
            )
        )

        plot = (
            plot_all_histograms
            + peak1_marks
            + peak2_marks
            + peak3_marks
            + peak4_marks
            + peak5_marks
            + threshold_lines
        )
        with st.container():
            st.altair_chart(plot, use_container_width=True)

    def plot_properties(
        props_and_peaks, props_size, props_color, props_Y, props_X
    ):  # Plot in the properties tab
        color_std2 = alt.Color(
            "X:N",
            scale=alt.Scale(scheme="accent"),
            legend=alt.Legend(title="Region Label", orient="bottom"),
        )
        color_std3 = alt.Color(
            props_color,
            scale=alt.Scale(scheme="spectral"),
            legend=alt.Legend(title="Color Property", orient="bottom"),
        )
        color_std4 = alt.Color("label:N", scale=alt.Scale(scheme="accent"), legend=None)
        size_std1 = alt.Size(
            props_size, legend=alt.Legend(title="Size Property", orient="bottom")
        )
        list_ofregions = [
            st.session_state["Particle_X"],
            st.session_state["Particle_A"],
            st.session_state["Particle_B"],
            st.session_state["Particle_C"],
            st.session_state["Particle_D"],
            st.session_state["Particle_E"],
            st.session_state["Particle_F"],
        ]
        plot_hist2 = (
            alt.Chart(st.session_state["data_to_plot"], height=1000)
            .mark_line()
            .encode(
                x=alt.X("Y", title="Greyscale"),
                y=alt.Y("frequency", title="Frequency"),
                color=color_std2,
            )
            .transform_filter(alt.FieldOneOfPredicate(field="X", oneOf=list_ofregions))
            .interactive()
        )
        plot_prop_select = (
            alt.Chart(props_and_peaks, height=1000)
            .mark_point(filled=True, opacity=1)
            .encode(x=props_X, y=props_Y, size=props_size, color=color_std4)
            .transform_filter(
                alt.FieldOneOfPredicate(field="label", oneOf=list_ofregions)
            )
        )
        plot_prop_all = (
            alt.Chart(props_and_peaks)
            .mark_point(shape="triangle", opacity=0.3)
            .encode(x=props_X, y=props_Y, color=color_std3, size=size_std1)
            .interactive()
        )
        plot_prop = plot_prop_all + plot_prop_select

        with tabHistogramProperty:
            col_hist, col_prop = st.columns(2)
            with col_hist:
                st.altair_chart(plot_hist2, use_container_width=True)
            with col_prop:
                st.altair_chart(plot_prop, use_container_width=True)

    def plot_mineralogy(report):
        """Plots the mineralogy from the report"""
        # convert report to DataFrame
        mineral_mass = pd.DataFrame(
            {
                "mineral": ["A", "B", "C", "D", "E"],
                "value": [
                    report["phaseA"],
                    report["phaseB"],
                    report["phaseC"],
                    report["phaseD"],
                    report["phaseE"],
                ],
            }
        )
        mineral_surface = pd.DataFrame(
            {
                "Surface": ["A", "B", "C", "D", "E"],
                "value": [
                    report["surfaceA"],
                    report["surfaceB"],
                    report["surfaceC"],
                    report["surfaceD"],
                    report["surfaceE"],
                ],
            }
        )

        # define color schema
        color_std_mass = alt.Color(
            "mineral:N",
            scale=alt.Scale(scheme="accent"),
            legend=alt.Legend(title="Mass", orient="right"),
        )
        color_std_surface = alt.Color(
            "Surface:N",
            scale=alt.Scale(scheme="accent"),
            legend=alt.Legend(title="Surface", orient="right"),
        )

        # define plots
        mineral_plot_mass = (
            alt.Chart(mineral_mass, title="Mass %")
            .mark_arc()
            .encode(theta="value", color=color_std_mass)
        )
        mineral_plot_surface = (
            alt.Chart(mineral_surface, title="Surface %")
            .mark_arc()
            .encode(theta="value", color=color_std_surface)
        )

        # combine plots
        combined_plot = mineral_plot_mass & mineral_plot_surface

        # plot
        st.altair_chart(combined_plot, use_container_width=True)

    def plot_peaks_balls(properties_and_peaks):
        properties_and_peaks = pd.DataFrame(properties_and_peaks)
        allPeaks = pd.concat(
            [
                properties_and_peaks["Peak_1"],
                properties_and_peaks["Peak_2"],
                properties_and_peaks["Peak_3"],
                properties_and_peaks["Peak_4"],
                properties_and_peaks["Peak_5"],
                properties_and_peaks["Peak_6"],
            ],
            ignore_index=True,
        )
        counts_total = pd.DataFrame({"counts": (allPeaks.value_counts())})
        counts_total = counts_total.reset_index()
        counts_total = counts_total.drop(0)
        grey_bin = alt.X("index:Q", title="Greyscale")
        test_peak_balls = (
            alt.Chart(counts_total, height=300)
            .mark_circle(opacity=0.8, stroke="black", strokeWidth=2, strokeOpacity=0.4)
            .encode(
                x=grey_bin,
                size="counts:N",
                color=alt.Color(
                    "counts:N",
                    scale=alt.Scale(scheme="viridis"),
                    legend=alt.Legend(title="count", orient="bottom"),
                ),
            )
            .properties(width=450, height=180)
            .configure_axisX(grid=True)
            .configure_view(stroke=None)
            .interactive()
        )
        st.altair_chart(test_peak_balls, use_container_width=True)

    def save_label_list(data_directory):
        """Save the label List csv to disk."""
        labels_array = np.array(
            [
                st.session_state["Particle_A"],
                st.session_state["Particle_B"],
                st.session_state["Particle_C"],
                st.session_state["Particle_D"],
                st.session_state["Particle_E"],
                st.session_state["Particle_F"],
            ]
        )

        if (
            st.session_state["Particle_X"] > 0
        ):  # add a specific particle to the random dataset. Be sure the label exists
            labels_array = np.append(labels_array, st.session_state["Particle_X"])

        labels_array = np.sort(labels_array)
        filtered_ROI_properties = propertiesData.loc[labels_array]
        filtered_ROI_properties = filtered_ROI_properties.filter(
            [
                "bbox-0",
                "bbox-1",
                "bbox-2",
                "bbox-3",
                "bbox-5",
                "centroid-0",
                "centroid-1",
                "centroid-2",
            ],
            axis=1,
        )
        filtered_ROI_properties["Label Index"] = labels_array
        path_label_list = os.path.join(data_directory, "labelList.csv")
        filtered_ROI_properties.to_csv(path_label_list, index=False)

    def bin_and_smooth(
        histograms_subdata, num_bins, enable_savgol, savgol_window_length
    ):
        """Binning and smoothing based on user thresholds"""
        start_time = time.time()

        # perform binning
        histograms_subdata_binned = binning(num_bins, histograms_subdata, n_jobs=-1)

        # smoothing if requested + normalization
        if enable_savgol:
            histograms_binned_smoothed = smooth_histograms_savgol(
                histograms_subdata_binned, savgol_window_length, n_jobs=-1
            )
            histogram_subdata_binned_smoothed_normed = normalize_volume(
                histograms_binned_smoothed
            )
        else:
            histogram_subdata_binned_smoothed_normed = normalize_volume(
                histograms_subdata_binned
            )

        finish_time = time.time()
        print("Binning in smoothing done in s:", finish_time - start_time)

        return histogram_subdata_binned_smoothed_normed

    # load data with streamlit caching
    chosen_histograms_data, initialBins = load_histograms(path_load_chosen_histogram)
    chosen_histograms_data = chosen_histograms_data.rename_axis("label")
    chosen_histograms_data = chosen_histograms_data.astype("float64")
    chosen_histograms_data = chosen_histograms_data.iloc[:, 1:]

    propertiesData = load_properties(data_directory)
    propertiesData.index = propertiesData["label"]

    inner_volume_histograms = load_in_volume(path_load_inner_histograms)
    outer_volume_histograms = load_out_volume(path_load_outer_histograms)
    surface_mesh_histogram = load_mesh(path_load_surface_mesh_histograms)
    gradient = load_gradient(path_load_gradient)

    # build the phase_thresholds_dict used throughout the calculations
    phase_thresholds_dict = {
        "BackgroundT": parameters_dict["background_q"],
        "DensityA": parameters_dict["DensityA"],
        "Max greyvalue A": parameters_dict["MaxGreyValueA"],
        "DensityB": parameters_dict["DensityB"],
        "Max greyvalue B": parameters_dict["MaxGreyValueB"],
        "DensityC": parameters_dict["DensityC"],
        "Max greyvalue C": parameters_dict["MaxGreyValueC"],
        "DensityD": parameters_dict["DensityD"],
        "Max greyvalue D": parameters_dict["MaxGreyValueD"],
        "DensityE": parameters_dict["DensityE"],
        "Max greyvalue E": parameters_dict["MaxGreyValueE"],
    }

    # initialize session state variables needed
    if "Particle_X" not in st.session_state:
        st.session_state["Particle_X"] = 0

    def change_radio():
        st.session_state["selected data"] = "Random regions"

    def click_quantify_all():
        st.session_state["selected data"] = "All regions"

    def change_threshold_data():
        global phase_thresholds_edited
        new_data = phase_thresholds_edited.to_dict(orient="records")[0]

        updated_data = st.session_state["pt_e"]["edited_rows"][0]
        for key, value in updated_data.items():
            new_data[key] = value

        global parameters_dict
        parameters_dict["background_q"] = new_data["BackgroundT"]
        parameters_dict["MaxGreyValueA"] = new_data["Max greyvalue A"]
        parameters_dict["MaxGreyValueB"] = new_data["Max greyvalue B"]
        parameters_dict["MaxGreyValueC"] = new_data["Max greyvalue C"]
        parameters_dict["MaxGreyValueD"] = new_data["Max greyvalue D"]
        parameters_dict["MaxGreyValueE"] = new_data["Max greyvalue E"]
        parameters_dict["DensityA"] = new_data["DensityA"]
        parameters_dict["DensityB"] = new_data["DensityB"]
        parameters_dict["DensityC"] = new_data["DensityC"]
        parameters_dict["DensityD"] = new_data["DensityD"]
        parameters_dict["DensityE"] = new_data["DensityE"]

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    def change_savgol():
        """Write session change to parameters yml"""
        val = st.session_state["change_savgol"]

        global parameters_dict
        parameters_dict["enableSavgol"] = val

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    def change_pvb():
        """Write session change to parameters yml"""
        val = st.session_state["change_pvb"]

        global parameters_dict
        parameters_dict["enablePVB"] = val

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    def change_savgol_win_length():
        """Write session change to parameters yml"""
        val = st.session_state["savgol_win_len"]

        global parameters_dict
        parameters_dict["savgolInput"] = val

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    def change_peak_width():
        """Write session change to parameters yml"""
        val = st.session_state["peak_width"]

        global parameters_dict
        parameters_dict["gray_value_width"] = val

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    def change_peak_height():
        """Write session change to parameters yml"""
        val = st.session_state["peak_height"]

        global parameters_dict
        parameters_dict["min_frequency"] = val

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    def change_peak_prom():
        """Write session change to parameters yml"""
        val = st.session_state["peak_prom"]

        global parameters_dict
        parameters_dict["prominence"] = val

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    def change_peak_h_dist():
        """Write session change to parameters yml"""
        val = st.session_state["peak_h_dist"]

        global parameters_dict
        parameters_dict["horizDistance"] = val

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    def change_peak_v_dist():
        """Write session change to parameters yml"""
        val = st.session_state["peak_v_dist"]

        global parameters_dict
        parameters_dict["vertDistance"] = val

        # write altered parameters to parameters dict
        global parameters_json
        write_dict_to_yml(parameters_json, parameters_dict)

    # additional buttons
    buttRandomize = st.sidebar.button("Randomize", on_click=change_radio)

    # show metrics
    number_regions = len(chosen_histograms_data)
    st.sidebar.metric(
        label="Number of regions",
        value=number_regions,
        help="Total number of regions loaded from the histogram file.",
    )

    # slider for number of bins
    num_bins_input = st.sidebar.number_input(
        "Bins",
        value=256,
        max_value=initialBins,
        step=16,
        help="Number to be divided by the initial number of bins. The higher the input the less number of bins plotted",
    )
    number_bins = int(initialBins / num_bins_input)

    # slider for savgol smoothing
    savgol_window_length = st.sidebar.slider(
        "Savgol smoothing intensity",
        min_value=3,
        value=parameters_dict["savgolInput"],
        max_value=26,
        help="Tip: higher values increase the smoothness.",
        on_change=change_savgol_win_length,
        key="savgol_win_len",
    )

    # input for number of subregions
    num_rand_particles = st.sidebar.number_input(
        "Number of regions in subset",
        value=3,
        min_value=3,
        max_value=number_regions,
        step=2,
    )

    # input for particle label
    peak_width = st.sidebar.slider(
        label="Grey-value width",
        max_value=int(number_bins / 10),
        min_value=0,
        step=1,
        value=int(parameters_dict["gray_value_width"]),
        help="Distance between two valleys on either side of a peak.",
        on_change=change_peak_width,
        key="peak_width",
    )

    # input for peak parameters
    peak_height = st.sidebar.slider(
        label="Min. Frequency",
        max_value=0.1,
        min_value=0.0,
        value=float(parameters_dict["min_frequency"]),
        step=0.001,
        format="%f",
        help="Minimum height of peaks from bottom.",
        on_change=change_peak_height,
        key="peak_height",
    )

    peak_prominence = st.sidebar.slider(
        label="Frequency prominence",
        max_value=0.05,
        min_value=0.00,
        value=float(parameters_dict["prominence"]),
        step=0.002,
        format="%f",
        help="Minimum height of climb from a valley left or right from the peak.",
        on_change=change_peak_prom,
        key="peak_prom",
    )

    peak_horizontal_distance = st.sidebar.slider(
        label="Grey-value variation",
        max_value=int(number_bins - (number_bins * 0.3)),
        min_value=1,
        value=int(parameters_dict["horizDistance"]),
        step=1,
        help="Minimum horizontal distance between neighbour peaks.",
        on_change=change_peak_h_dist,
        key="peak_h_dist",
    )

    peak_vertical_distance = st.sidebar.slider(
        label="Frequency variation",
        max_value=0.005,
        min_value=0.000,
        value=float(parameters_dict["vertDistance"]),
        step=0.0002,
        format="%f",
        help="Minimum vertical distance between neighbour peaks.",
        on_change=change_peak_v_dist,
        key="peak_v_dist",
    )

    # button to trigger run of all regions
    butt_quantify_all = st.sidebar.button(
        label="Quantify all",
        help="Applies the peak parameters to all regions and appends the grey-values of the peaks to the properties file.",
        on_click=click_quantify_all,
        key="quantify_all",
    )

    ################## online functionality ##################
    with tabHistOverview:
        (
            col_load,
            col_save,
            col_savgol,
            colA,
            colB,
            colC,
            colD,
            colE,
            colF,
            colX,
        ) = st.columns(10)

        # histogram smoothing checkbox
        with col_savgol:
            savgol_box = st.checkbox(
                "Activate Savgol",
                value=parameters_dict["enableSavgol"],
                help="Smoothens the histograms. Use together with slider in the sidebar.",
                on_change=change_savgol,
                key="change_savgol",
            )

        # Load label regions
        with col_load:
            butt_load_list_labels = st.button(
                "Load regions",
                help="Loads a list of labels as csv created in the 3D viewer.",
            )
        # save label regions
        with col_save:
            butt_save_list_labels = st.button(
                "Save regions",
                help="Saves a list of labels as csv that are loaded automatically in the 3D viewer.",
            )

    with tabFindPeaks:  # table with threshold inputs
        col1, col2 = st.columns(spec=[0.8, 0.2])
        with col2:
            load_input_files = st.file_uploader(
                label="Load input densities and thresholds",
                help="Thresholds and densities can be loaded from a csv pre-saved from the table.",
            )
        with col1:
            # histogram smoothing checkbox
            enable_pvb = st.checkbox(
                "Activate Partial Volume Blurr (PVB) correction for liberated and two phase particles.",
                value=parameters_dict["enablePVB"],
                help="Trigger Partial Volume correction. This will correct the greyvalue peaks for the partial volume effect. Only enable for CT data.",
                on_change=change_pvb,
                key="change_pvb",
            )
            st.markdown(
                "[Learn more](https://doi.org/10.1016/j.tmater.2025.100050)",
                unsafe_allow_html=True,
            )
            st.subheader("Greyvalue phase thresholds and densities")

            phase_thresholds = pd.DataFrame([phase_thresholds_dict])
            phase_thresholds_edited = st.data_editor(
                phase_thresholds, on_change=change_threshold_data, key="pt_e"
            )

            # convert edited thresholds to phase_thresholds_dict used throughout the calculations
            phase_thresholds_dict = phase_thresholds_edited.to_dict(orient="records")[0]

    # radio button to select how many regions to plot
    if "selected data" not in st.session_state:
        st.session_state["selected data"] = "Random regions"

    plot_data_button = st.sidebar.radio(
        "How many regions",
        ["All regions", "Random regions", "Regions of interest"],
        key="selected data",
    )

    # option to load thresholds from csv
    if load_input_files:
        phase_thresholds = pd.read_csv(load_input_files)
        phase_thresholds = phase_thresholds.drop(phase_thresholds.columns[0], axis=1)

        # build the phase_thresholds_dict used throughout the calculations
        phase_thresholds_dict = {
            "BackgroundT": int(phase_thresholds.iloc[0]["BackgroundT"]),
            "DensityA": int(phase_thresholds.iloc[0]["DensityA"]),
            "Max greyvalue A": int(phase_thresholds.iloc[0]["Max greyvalue A"]),
            "DensityB": parameters_dict["DensityB"],
            "Max greyvalue B": int(phase_thresholds.iloc[0]["Max greyvalue B"]),
            "DensityC": parameters_dict["DensityC"],
            "Max greyvalue C": int(phase_thresholds.iloc[0]["Max greyvalue C"]),
            "DensityD": parameters_dict["DensityD"],
            "Max greyvalue D": int(phase_thresholds.iloc[0]["Max greyvalue D"]),
            "DensityE": parameters_dict["DensityE"],
            "Max greyvalue E": int(phase_thresholds.iloc[0]["Max greyvalue E"]),
        }

    # select dataset to work with based on user config
    if plot_data_button == "Random regions":
        (
            chosen_histograms_subdata,
            chosen_histograms_subdata_labels,
        ) = create_histogram_subdata(
            num_rand_particles, chosen_histograms_data, st.session_state["Particle_X"]
        )
    elif plot_data_button == "All regions":
        chosen_histograms_subdata_labels = chosen_histograms_data.index
        chosen_histograms_subdata = chosen_histograms_data
    elif plot_data_button == "Regions of interest":
        list6regions = {
            "Label Index": [
                st.session_state["Particle_A"],
                st.session_state["Particle_B"],
                st.session_state["Particle_C"],
                st.session_state["Particle_D"],
                st.session_state["Particle_E"],
                st.session_state["Particle_F"],
            ]
        }
        chosen_histograms_subdata_labels = pd.DataFrame(list6regions)
        chosen_histograms_subdata = chosen_histograms_data[
            chosen_histograms_data.index.isin(list6regions["Label Index"])
        ]
    else:
        raise RuntimeError("Data selection not supported!")

    # re-shuffle if button clicked
    if buttRandomize:
        (
            chosen_histograms_subdata,
            chosen_histograms_subdata_labels,
        ) = create_histogram_subdata(
            num_rand_particles, chosen_histograms_data, st.session_state["Particle_X"]
        )

    # load from label if load labels clicked
    if butt_load_list_labels:
        sub_data_from_list, sub_data_from_list_labels = load_label_list(data_directory)

    # perform smoothing and update session variables for selected data
    chosen_histograms_binned_smoothed_normed = bin_and_smooth(
        chosen_histograms_subdata, num_bins_input, savgol_box, savgol_window_length
    )

    # calculate properties and peaks once for the respective dataset
    start_time = time.time()
    # process peaks from selected data
    processed_peaks = process_peaks(
        chosen_histograms_binned_smoothed_normed,
        chosen_histograms_data,
        propertiesData,
        number_bins,
        peak_width,
        peak_height,
        peak_prominence,
        peak_vertical_distance,
        peak_horizontal_distance,
        num_bins_input,
    )

    processed_arranged_peaks = arrange_peaks(
        processed_peaks,
        phase_thresholds_dict,
        propertiesData,
    )

    finish_time = time.time()
    print("Process selected peaks:", finish_time - start_time)

    # update session state
    st.session_state["data_to_plot"] = transform_columns_xy(
        chosen_histograms_binned_smoothed_normed
    )
    st.session_state["normalized_data"] = chosen_histograms_binned_smoothed_normed
    st.session_state["particle_labels"] = chosen_histograms_subdata_labels
    st.session_state["properties_and_peaks"] = processed_arranged_peaks

    with tabHistOverview:
        lenghtOfList = len(st.session_state["particle_labels"])
        with colX:
            particleNumberBox = st.number_input(
                "Label particle X",
                step=1,
                help="specific region label. Does not need to be in the random dataset, but the label must exist in the full dataset",
            )
            st.session_state["Particle_X"] = particleNumberBox
        with colA:
            st.session_state["Particle_A"] = st.selectbox(
                label="Label Region A",
                options=st.session_state["particle_labels"],
                index=0,
            )
        with colB:
            st.session_state["Particle_B"] = st.selectbox(
                label="Label Region B",
                options=st.session_state["particle_labels"],
                index=1,
            )
        with colC:
            st.session_state["Particle_C"] = st.selectbox(
                label="Label Region C",
                options=st.session_state["particle_labels"],
                index=2,
            )
        with colD:
            if lenghtOfList > 3:
                dropdown4 = st.selectbox(
                    label="Label Region D",
                    options=st.session_state["particle_labels"],
                    index=3,
                )
            else:
                dropdown4 = st.selectbox(
                    label="Label Region D",
                    options=st.session_state["particle_labels"],
                    index=0,
                )
            st.session_state["Particle_D"] = dropdown4
        with colE:
            if lenghtOfList > 4:
                dropdown5 = st.selectbox(
                    label="Label Region E",
                    options=st.session_state["particle_labels"],
                    index=4,
                )
            else:
                dropdown5 = st.selectbox(
                    label="Label Region E",
                    options=st.session_state["particle_labels"],
                    index=0,
                )
            st.session_state["Particle_E"] = dropdown5
        with colF:
            if lenghtOfList > 5:
                dropdown6 = st.selectbox(
                    label="Label Region F",
                    options=st.session_state["particle_labels"],
                    index=5,
                )
            else:
                dropdown6 = st.selectbox(
                    label="Label Region F",
                    options=st.session_state["particle_labels"],
                    index=0,
                )
            st.session_state["Particle_F"] = dropdown6

        plot_histogram_overview(st.session_state["data_to_plot"])
        with st.expander("Histograms regions of interest"):
            st.dataframe(st.session_state["normalized_data"], hide_index=True)

    if butt_save_list_labels:
        save_label_list(data_directory)

    with tabFindPeaks:  # table with threshold inputs
        with col1:
            plot_peaks(
                st.session_state["data_to_plot"],
                st.session_state["properties_and_peaks"],
                phase_thresholds_dict,
            )
            plot_peaks_balls(st.session_state["properties_and_peaks"])
        with col2:
            with st.expander("List of Peaks"):
                st.dataframe(st.session_state["properties_and_peaks"])

            propertiesAndPeaks = st.session_state["properties_and_peaks"]
            st.write(
                "Number of peaks class A:",
                propertiesAndPeaks["Peaks_Height_1"].astype(bool).sum(axis=0),
            )
            st.write(
                "Number of peaks class B:",
                propertiesAndPeaks["Peaks_Height_2"].astype(bool).sum(axis=0),
            )
            st.write(
                "Number of peaks class C:",
                propertiesAndPeaks["Peaks_Height_3"].astype(bool).sum(axis=0),
            )
            st.write(
                "Number of peaks class D:",
                propertiesAndPeaks["Peaks_Height_4"].astype(bool).sum(axis=0),
            )
            st.write(
                "Number of peaks class E:",
                propertiesAndPeaks["Peaks_Height_5"].astype(bool).sum(axis=0),
            )

    if butt_quantify_all:
        if plot_data_button == "All regions":
            properties_and_peaks = st.session_state["properties_and_peaks"]
        else:
            # re-calculate properties for all particles
            chosen_histograms_subdata_labels = chosen_histograms_data.index
            chosen_histograms_subdata = chosen_histograms_data

            # perform smoothing and update session variables for selected data
            chosen_histograms_binned_smoothed_normed = bin_and_smooth(
                chosen_histograms_subdata,
                num_bins_input,
                savgol_box,
                savgol_window_length,
            )

            # calculate properties and peaks once for the respective dataset
            start_time = time.time()
            # process peaks from selected data
            processed_peaks = process_peaks(
                chosen_histograms_binned_smoothed_normed,
                chosen_histograms_data,
                propertiesData,
                number_bins,
                peak_width,
                peak_height,
                peak_prominence,
                peak_vertical_distance,
                peak_horizontal_distance,
                num_bins_input,
            )
            properties_and_peaks = arrange_peaks(
                processed_peaks,
                phase_thresholds_dict,
                propertiesData,
            )

        with tabQuantify:
            report, quantification = quantify_mineralogy(
                properties_and_peaks,
                peak_height,
                chosen_histograms_data,
                surface_mesh_histogram,
                inner_volume_histograms,
                outer_volume_histograms,
                phase_thresholds_dict,
                enable_pvb,
            )
            st.subheader("Statistics for all regions")
            col1Stats, col2PiePlot = st.columns(2)

            with col1Stats:
                # statistics for the mineral quantification
                totalParticleVolume = propertiesData["Volume"].sum()
                st.metric(
                    label="regions analysed",
                    value=report["regionsAnalysed"],
                    delta=number_regions,
                    delta_color="inverse",
                    help="If number of regions analysed is very different from the number of regions segmented means something is wrong with the classification. Check the peaks and thresholds",
                )
                st.metric(
                    label="Volume analysed",
                    value=round(report["volumeAnalysed2"], 0),
                    delta=round(
                        report["volumeAnalysed"] / report["volumeAnalysed2"], 2
                    ),
                    delta_color="inverse",
                    help=" compare volume fraction analysed = volume analysed / total volume",
                )
                st.metric(
                    label="Number regions liberated",
                    value=report["regionsLiberated"],
                    help="regions with only one phase",
                )
                st.metric(
                    label="Number regions with 2 phases", value=report["regions2Phases"]
                )
                st.metric(
                    label="Number regions with more than 2 phases",
                    value=report["regions3Phases"],
                    help="partial volume not corrected",
                )
                print("Volume analyzed: " + str(report["volumeAnalysed"]))
                print("Volume analyzed summarized: " + str(report["volumeAnalysed2"]))
                print("Total particle volume: " + str(totalParticleVolume))

            with col2PiePlot:
                # plot area of the mineralogy
                plot_mineralogy(report)

            # save report
            report_path = os.path.join(report_directory, "report.yml")
            print("Write report to disk: %s" % str(report_path))
            write_report_to_yml(report_path, report)

            # save quantification
            path_save_Quantification = os.path.join(
                report_directory, "Quantification.csv"
            )
            quantification.to_csv(path_save_Quantification, index=False)

    with tabHistogramProperty:
        colActivate, column1, column2, column3, column4 = st.columns(5)

        with colActivate:
            # activate property plot checkbox
            plotPropActive = st.checkbox("Plot properties", value=False)

        if plotPropActive:
            propertiesAndPeaks = st.session_state["properties_and_peaks"]

            with column4:
                properties_size = st.selectbox(
                    "Size property", propertiesAndPeaks.columns[:].unique(), index=19
                )
            with column3:
                properties_color = st.selectbox(
                    "Color property", propertiesAndPeaks.columns[:].unique(), index=14
                )
            with column2:
                properties_y = st.selectbox(
                    "Y-property", propertiesAndPeaks.columns[:].unique(), index=16
                )
            with column1:
                properties_x = st.selectbox(
                    "X-property", propertiesAndPeaks.columns[:].unique(), index=12
                )
            plot_properties(
                propertiesAndPeaks,
                properties_size,
                properties_color,
                properties_y,
                properties_x,
            )

        with st.expander("Properties And Peaks"):
            st.dataframe(st.session_state["properties_and_peaks"])

    with tabFindPeaks:
        colPartA, colPartB, colPartC, colPartD, colPartE, colPartF = st.columns(6)
        propertiesAndPeaks = st.session_state["properties_and_peaks"]
        with colPartA:
            prop_w_peak_a = propertiesAndPeaks.loc[[st.session_state["Particle_A"]]]
            st.subheader(st.session_state["Particle_A"])
            report, _ = quantify_mineralogy(
                prop_w_peak_a,
                peak_height,
                chosen_histograms_data,
                surface_mesh_histogram,
                inner_volume_histograms,
                outer_volume_histograms,
                phase_thresholds_dict,
                enable_pvb,
            )
            plot_mineralogy(report)
        with colPartB:
            prop_w_peak_b = propertiesAndPeaks.loc[[st.session_state["Particle_B"]]]
            st.subheader(st.session_state["Particle_B"])
            report, _ = quantify_mineralogy(
                prop_w_peak_b,
                peak_height,
                chosen_histograms_data,
                surface_mesh_histogram,
                inner_volume_histograms,
                outer_volume_histograms,
                phase_thresholds_dict,
                enable_pvb,
            )
            plot_mineralogy(report)
        with colPartC:
            prop_w_peak_c = propertiesAndPeaks.loc[[st.session_state["Particle_C"]]]
            st.subheader(st.session_state["Particle_C"])
            report, _ = quantify_mineralogy(
                prop_w_peak_c,
                peak_height,
                chosen_histograms_data,
                surface_mesh_histogram,
                inner_volume_histograms,
                outer_volume_histograms,
                phase_thresholds_dict,
                enable_pvb,
            )
            plot_mineralogy(report)
        with colPartD:
            prop_w_peak_d = propertiesAndPeaks.loc[[st.session_state["Particle_D"]]]
            st.subheader(st.session_state["Particle_D"])
            report, _ = quantify_mineralogy(
                prop_w_peak_d,
                peak_height,
                chosen_histograms_data,
                surface_mesh_histogram,
                inner_volume_histograms,
                outer_volume_histograms,
                phase_thresholds_dict,
                enable_pvb,
            )
            plot_mineralogy(report)
        with colPartE:
            prop_w_peak_e = propertiesAndPeaks.loc[[st.session_state["Particle_E"]]]
            st.subheader(st.session_state["Particle_E"])
            report, _ = quantify_mineralogy(
                prop_w_peak_e,
                peak_height,
                chosen_histograms_data,
                surface_mesh_histogram,
                inner_volume_histograms,
                outer_volume_histograms,
                phase_thresholds_dict,
                enable_pvb,
            )
            plot_mineralogy(report)
        with colPartF:
            prop_w_peak_f = propertiesAndPeaks.loc[[st.session_state["Particle_F"]]]
            st.subheader(st.session_state["Particle_F"])
            report, _ = quantify_mineralogy(
                prop_w_peak_f,
                peak_height,
                chosen_histograms_data,
                surface_mesh_histogram,
                inner_volume_histograms,
                outer_volume_histograms,
                phase_thresholds_dict,
                enable_pvb,
            )
            plot_mineralogy(report)
