"""Module for converting TIFF images to Zarr format and vice versa."""
import os
import re
from pathlib import Path

import tifffile
import zarr
from tqdm import tqdm
from zarr.storage import DirectoryStore as LocalStore

from ari3d.gui.ari3d_logging import Ari3dLogger


def glob_re(pattern, strings):
    """Filter a list of strings based on a regular expression pattern."""
    return filter(re.compile(pattern).match, strings)


def tiffs2zarr(load_dir: str, save_dir: str, n_jobs: int = -1):
    """Convert a set of TIFF image slices to a Zarr image."""
    in_path = Path(load_dir)
    save_path = Path(save_dir)

    name = in_path.stem
    img_files = list(
        glob_re(r".*\.(tif|tiff|TIF|TIFF)$", os.listdir(path=str(in_path)))
    )
    img_files = sorted(img_files)  # Ensure files are processed in order

    ex_img = tifffile.imread(str(in_path.joinpath(img_files[0])))

    output_shape = ex_img.shape
    data_type = ex_img.dtype
    output_shape = (len(img_files), *output_shape)

    zarr_storage = LocalStore(str(save_path.joinpath(name + ".zarr")))

    # log starting the conversion
    Ari3dLogger().log.info(
        f"Converting {len(img_files)} tiff files to zarr format... this may take a while"
    )

    image_zarr = zarr.open(
        store=zarr_storage, shape=output_shape, dtype=data_type, mode="w"
    )
    for i, filepath in enumerate(tqdm(img_files)):
        image_slice = tifffile.imread(str(in_path.joinpath(filepath)))
        image_zarr[i] = image_slice

    return str(save_path.joinpath(name + ".zarr"))


def zarr2float(load_dir: str, save_dir: str):
    """Convert a Zarr image to a float32 format."""
    in_path = Path(load_dir)
    save_path = Path(save_dir)

    # open zarr
    image_zarr = zarr.open(load_dir, mode="r")

    # store as float
    Ari3dLogger().log.info("Converting zarr to float value... this may take a while")

    image_zarr_float_storage = LocalStore(
        str(save_path.joinpath(in_path.stem + ".zarr"))
    )
    image_zarr_float = zarr.create(
        shape=image_zarr.shape,
        chunks=image_zarr.chunks,
        dtype="float32",
        store=image_zarr_float_storage,
        overwrite=True,
    )

    image_zarr_float[:] = image_zarr[:]
