import gc
import os
import re
from tkinter.filedialog import askdirectory

import anndata
import nibabel as nib
import numpy as np
import pandas as pd
from skimage import io, measure


def glob_re(pattern, strings):
    """Regular expression matching."""
    return filter(re.compile(pattern).match, strings)


def _load_images(binary_image_path, start_slice, end_slice):
    """Load the images. Supported formate is TIFF and NIFTI."""
    tiff_files = sorted(
        list(
            glob_re(
                r".*\.(tif|tiff|TIF|TIFF)$", os.listdir(path=str(binary_image_path))
            )
        )
    )
    tiff_files = [os.path.join(binary_image_path, f) for f in tiff_files]

    nifti_files = sorted(
        list(glob_re(r".*\.(nii|nii.gz)$", os.listdir(path=str(binary_image_path))))
    )
    nifti_files = [os.path.join(binary_image_path, f) for f in nifti_files]

    if len(tiff_files) > 1:
        # Multiple TIFF files - treat as 2D stack
        cv_img = []
        for img in tiff_files:
            n = io.imread(img, as_gray=True)
            cv_img.append(n)
        images = np.dstack(cv_img)
        images = np.rollaxis(images, -1)
        del cv_img
        del n
    elif len(tiff_files) == 1:
        # Single TIFF file - treat as 3D image
        images = io.imread(tiff_files[0])
    elif len(nifti_files) == 1:
        # Single NIfTI file - treat as 3D image
        images = nib.load(nifti_files[0]).get_fdata()
    else:
        raise ValueError("No compatible image files found in the specified directory.")

    # slicing
    if start_slice is not None and end_slice is not None:
        if start_slice == end_slice:
            raise ValueError("Start and end slice cannot be the same.")
        if images.ndim == 3:
            if start_slice >= 0 and end_slice < images.shape[0]:
                images = images[start_slice : end_slice + 1, :, :]
            else:
                raise ValueError("Invalid slice range for the 3D image stack.")
        else:
            raise ValueError("Slice range can only be specified for 3D image stacks.")

    # Calculate the maximum grey value
    max_grey_value = np.max(images)

    # Decide which unit type image should be based on the max grey value
    if max_grey_value <= 255:
        # Convert to uint8
        images = images.astype(np.uint8)
    elif max_grey_value <= 65535:
        # Convert to uint16
        images = images.astype(np.uint16)
    else:
        images = images.astype(np.uint32)

    gc.collect()
    return images


def load_and_process_labelled_image(binary_image_path, start_slice, end_slice):
    """Load and process labelled images."""
    labels = _load_images(binary_image_path, start_slice, end_slice)
    if (
        len(np.unique(labels)) < 3
    ):  # if mask was exported from Dragonfly the particles have greyvalue 255, from Avizo or ImageJ change to 1.
        labels = measure.label(labels)
    else:
        labels = labels
    binary = np.where(labels >= 1, 1, 0)
    binary = binary.astype(np.uint8)
    print("Number of particles before processing", labels.max())
    print("Image size", labels.shape)
    return labels, binary


def load_non_binary_images(non_binary_image_path, start_slice, end_slice):
    """Load gray-scale images."""
    non_binary = _load_images(non_binary_image_path, start_slice, end_slice)
    non_binary = non_binary.astype(np.uint16)
    return non_binary


def directory():
    """Ask for a directory."""
    # prompt to choose the directory. Must have folders with names 'binary','grey','data'
    path = askdirectory(title="select folder")
    return path


def convert_h5ad(histograms_df, path_to_save_histograms):
    """Convert histograms to h5ad and save."""
    histograms_df.index = histograms_df.index.astype(str)
    histograms_df.columns = histograms_df.columns.astype(str)
    histograms_df.columns = ["bin_" + str(col) for col in histograms_df.columns]

    obs = pd.DataFrame(index=histograms_df.index)
    var = pd.DataFrame(index=histograms_df.columns)

    adata = anndata.AnnData(X=histograms_df, obs=obs, var=var)
    adata.write(path_to_save_histograms)

    return histograms_df
