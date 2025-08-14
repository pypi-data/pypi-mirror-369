"""Module for image operations."""
import numpy as np

from ari3d.gui.ari3d_logging import Ari3dLogger

logger = Ari3dLogger()


def center_crop(image_array, shape):
    """Center crop an image array to the specified shape."""
    d1, d2, d3 = shape

    # check if image already has the correct dimension
    if image_array.shape[:3] == [d1, d2, d3]:
        return image_array, shape

    # check if dimension too large
    if any([d > s for d, s in zip([d1, d2, d3], image_array.shape[:3])]):
        logger.log.error(
            "Crop dimension %s in a dimension larger that input %s"
            % ([d1, d2, d3], image_array.shape[:3])
        )
        return image_array, None

    # center crop image to dimension d1, d2, d3
    x_target_size = np.array([d1, d2, d3])
    offset = tuple((a - b) // 2 for a, b in zip(image_array.shape, x_target_size))
    slices = tuple(slice(o, o + s) for o, s in zip(offset, x_target_size))

    return image_array[slices], shape


def center_pad(image_array, shape):
    """Pad an image array to the specified shape."""
    s1, s2, s3 = shape

    if image_array.shape[:3] == [s1, s2, s3]:
        return image_array, shape

    # check if dimension too small
    if any([d < s for d, s in zip([s1, s2, s3], image_array.shape[:3])]):
        logger.log.error(
            "Dimension of input %s larger than padded to %s"
            % (image_array.shape[:3], [s1, s2, s3])
        )
        return image_array, None

    # center pad image to dimension s1, s2, s3
    pad_left_s1 = (s1 - image_array.shape[0]) // 2
    pad_left_s2 = (s2 - image_array.shape[1]) // 2
    pad_left_s3 = (s3 - image_array.shape[2]) // 2

    pad_right_s1 = s1 - image_array.shape[0] - pad_left_s1
    pad_right_s2 = s2 - image_array.shape[1] - pad_left_s2
    pad_right_s3 = s3 - image_array.shape[2] - pad_left_s3

    image_array = np.pad(
        image_array,
        (
            (pad_left_s1, pad_right_s1),
            (pad_left_s2, pad_right_s2),
            (pad_left_s3, pad_right_s3),
        ),
        mode="constant",
        constant_values=0,
    )
    return image_array, shape
