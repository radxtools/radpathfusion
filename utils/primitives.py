import numpy as np
import cv2
from pathlib import Path
from .helpers import rotate_bound, scale_image_dim
from enum import Enum, auto
from typing import Union, List
import uuid
import json


class Point:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return f"({self.x},{self.y})"

    def __repr__(self):
        return str(self)


class Origin(Enum):
    BOTTOM_LEFT = 0  # reference frame used by holoviews
    TOP_LEFT = 1  # reference frame used by opencv


class Frame:
    origin: Origin
    points: List[Point]

    @property
    def count(self):
        return len(self.points)

    def to_numpy(self):
        arr = []
        for p in self.points:
            x, y = p.x, p.y
            arr.append([x, y])
        return np.array(arr, dtype=np.float32)

    def __str__(self):
        return (f"Frame(origin={self.origin},"
                f"points={self.points})"
                )

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "origin": str(self.origin),
            "points": [(p.x, p.y) for p in self.points]
        }


def numpy_to_frame(arr: np.ndarray, origin: Origin) -> Frame:
    # todo, check shape
    # might be 2d or 3d array, might have to squeeze a dimension
    points = []
    for row in arr.squeeze():
        x, y = row
        points.append(Point(x, y))
    f = Frame()
    f.points = points
    f.origin = origin
    return f


def translate_vertical_reference_frames(origin: Point, points: List[Point]) -> List[Point]:
    new_points = []
    for p in points:
        p = Point(p.x, origin.y - p.y)
        new_points.append(p)
    return new_points


ANGLE_DEFAULT = 0.0
SCALE_DEFAULT = 1.0


INTERPOLATION_STR_MAP_TO_CV2 = {
    "INTER_LINEAR": cv2.INTER_LINEAR,
    "INTER_CUBIC": cv2.INTER_CUBIC,
    "INTER_AREA": cv2.INTER_AREA
}


class Image:

    def __init__(self,
                 img: np.ndarray,
                 angle: float = ANGLE_DEFAULT,
                 scale: float = SCALE_DEFAULT,
                 interpolation: str = "INTER_LINEAR",
                 flip_x: bool = False,
                 flip_y: bool = False,
                 landmarks: Frame = None):
        self.__image = img
        self.__angle = angle
        self.__scale = scale
        self.__interpolation = interpolation
        self.__landmarks = landmarks
        self.__flip_x = flip_x
        self.__flip_y = flip_y

    def __call__(self):
        img = self.__image

        if self.scale != SCALE_DEFAULT:
            cv2_interpolation = INTERPOLATION_STR_MAP_TO_CV2[self.interpolation]
            img = scale_image_dim(
                img, self.scale, cv2_interpolation)

        if self.angle != ANGLE_DEFAULT:
            img = rotate_bound(img, self.angle)

        if self.flip_x and self.flip_y:
            img = cv2.flip(img, -1)
        elif self.flip_x and not self.flip_y:
            img = cv2.flip(img, 0)
        elif not self.flip_x and self.flip_y:
            img = cv2.flip(img, 1)

        return img

    def normalize(self):
        """
        Applies the transformation and setting all attributes to their defaul values
        """
        img = self()
        return Image(img, angle=ANGLE_DEFAULT, scale=SCALE_DEFAULT, interpolation=self.interpolation, landmarks=self.landmarks)

    @property
    def shape(self):
        # todo - figure out rotation before scaling
        # return tuple([int(self.scale * x) for x in self.__image.shape])
        return self.__image.shape

    @property
    def scale(self) -> float:
        return self.__scale

    @property
    def angle(self) -> float:
        return self.__angle

    @property
    def interpolation(self) -> str:
        return self.__interpolation

    @property
    def landmarks(self) -> Frame:
        return self.__landmarks

    @property
    def flip_x(self) -> bool:
        return self.__flip_x

    @property
    def flip_y(self) -> bool:
        return self.__flip_y

    def change_landmarks_reference(self, to_origin: Origin) -> 'Image':
        if to_origin.value == self.landmarks.origin.value:
            return self.update()
        if to_origin.value == Origin.BOTTOM_LEFT.value:
            h = self().shape[0]
            new_origin = Point(0, h)
            new_landmark_points = translate_vertical_reference_frames(
                origin=new_origin, points=self.landmarks.points)
            f = Frame()
            f.points = new_landmark_points
            f.origin = Origin.BOTTOM_LEFT
            return self.update(
                landmarks=f
            )
        if to_origin.value == Origin.TOP_LEFT.value:
            h = self().shape[0]
            new_origin = Point(0, h)
            new_landmark_points = translate_vertical_reference_frames(
                origin=new_origin, points=self.landmarks.points)
            f = Frame()
            f.points = new_landmark_points
            f.origin = Origin.TOP_LEFT
            return self.update(
                landmarks=f
            )

    def update(self,
               scale: float = None,
               angle: float = None,
               interpolation: str = None,
               flip_x: bool = False,
               flip_y: bool = False,
               landmarks: Frame = None):
        _scale = scale if scale else self.scale
        _angle = angle if angle else self.angle
        _interpolations = interpolation if interpolation else self.interpolation
        _landmark = landmarks if landmarks else self.landmarks
        _flip_x = flip_x if flip_x else self.flip_x
        _flip_y = flip_y if flip_y else self.flip_y
        return Image(self.__image,
                     angle=_angle,
                     scale=_scale,
                     interpolation=_interpolations,
                     landmarks=_landmark,
                     flip_x=_flip_x,
                     flip_y=_flip_y
                     )

    def save(self, dir_path: Path, name: str = None, data=True):
        _id = uuid.uuid4()
        if dir_path.is_file():
            raise "dir_path needs to be a directory"
        img = self()
        ext = ".tif" if len(img.shape) > 2 else ".jpg"
        img_path = dir_path / f"{name}.{_id}.{ext}"

        cv2.imwrite(str(img_path), img)
        if data:
            data_path = dir_path / f"{name}.{_id}.json"
            data = {
                "angle": self.angle,
                "scale": self.scale,
                "interpolation": self.interpolation,
                "flip_x": self.flip_x,
                "flip_y": self.flip_y,
                "landmarks": self.landmarks.to_dict()
            }
            json.dump(data, data_path.open('w'))

    def copy_attributes(self, other: 'Image'):
        return self.update(
            scale=other.scale,
            angle=other.angle,
            interpolation=other.interpolation,
            flip_x=other.flip_x,
            flip_y=other.flip_y,
            landmarks=other.landmarks
        )

    @staticmethod
    def load(path: Union[str, Path]):
        img = cv2.imread(str(path))
        return Image(img)

    def __repr__(self):
        return f"Image(scale={self.scale},angle={self.angle},interpolation={self.interpolation},flip_x={self.flip_x},flip_y={self.flip_y},landmarks={self.landmarks})"
