import cv2
import numpy as np
from landmark_selector_visualizer import Frame
from pathlib import Path
from enum import Enum
import json


class ImageFormats(Enum):
    jpeg,
    png,
    tiff,


def download(path: str,
             format: ImageFormats,
             fixed_transformed: np.ndarray = None,
             moving_transformed: np.ndarray = None,
             annotated_transformed: np.ndarray = None,
             landmarks: Frame = None,

             ):
    p = Path(P)

    if fixed_transformed is not None:
        img_path = p / f"fixed.{format.name}"
        cv2.imwrite(str(img_path), fixed_transformed)

    if moving_transformed is not None:
        img_path = p / f"moving.{format.name}"
        cv2.imwrite(str(img_path), fixed_transformed)

    if annotated_transformed is not None:
        img_path = p / f"annotated.{format.name}"
        cv2.imwrite(str(img_path), annotated_transformed)

    if landmarks is not None:
        data_path = p / f"landmarks.json"
        landmarks.to_dict()
        with data_path.open('w') as w:
            json.dump(landmarks.to_dict(), w)
