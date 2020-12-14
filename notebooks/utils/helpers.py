import cv2
from typing import Tuple
import numpy as np

Height = int
Width = int
Cv2Shape = Tuple[Height, Width]


def defaul_factor_by_area(dim: Cv2Shape, max_pixels=2e3*2e3):
    h, w = dim
    factor = np.ceil(np.sqrt(h*w))
    return factor


def default_factor(dim: Cv2Shape, SIZE=2000):
    if len(dim) == 2:
        h, w = dim
    elif len(dim) == 3:
        h, w, _ = dim
    else:
        raise ValueError('Not supported image type')
    factor = SIZE / max(w, h)
    return factor


def scale_image_dim(img: np.ndarray, factor: float, interpolation=cv2.INTER_AREA):
    """
    Args:
        img: An opencv2 image
        factor: the scaling factor
        interpoloation: interpolation method
            cubic  -> upscaling
            linear -> default
            area   -> downscaling

    Returns:
        the scaled imaged
    """
    h, w = int(factor*img.shape[0]), int(factor*img.shape[1])
    dst = cv2.resize(img, (w, h), interpolation=interpolation)
    return dst


def rotate_bound(image: np.ndarray, angle: float):
    """
    Args:
        image: An opencv2 image
        angle: In degrees

    Returns:
        the rotated image with new bounds
    """
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))
