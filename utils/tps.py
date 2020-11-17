from .landmark_selector_visualizer import Frame, Origin, numpy_to_frame
from typing import Tuple
import numpy as np
import cv2


class ThinPlateSplinesAlgorithm:
    def __init__(self, moving_pts_frame: Frame, fixed_pts_frame: Frame):
        """
        Args:
            moving_pts_frame: Verify that the points in the reference frame are from top left
            fixed_pts_frame: Verify that the points in the reference frame are from top left

        """
        if moving_pts_frame.origin.value != Origin.TOP_LEFT.value:
            raise ValueError(
                "moving_pts_frame reference points should be from top left")

        if fixed_pts_frame.origin.value != Origin.TOP_LEFT.value:
            raise ValueError(
                "moving_pts_frame reference points should be from top left")

        if moving_pts_frame.count != fixed_pts_frame.count:
            raise ValueError(
                f"The number of points selected in each refrence frame do not match (moving_pts_frame:{moving_pts_frame.count}, fixed_pts_frame: {fixed_pts_frame.count}).")

        self.moving_pts_frame = moving_pts_frame
        self.fixed_pts_frame = fixed_pts_frame

    def warp_affine(self, fixed_img: np.ndarray, moving_img: np.ndarray) -> Tuple[Frame, np.ndarray]:
        "Applied affine transformation to moving_image using landmarks"
        moving = self.moving_pts_frame.to_numpy()
        fixed = self.fixed_pts_frame.to_numpy()
        moving_landmarks = moving.reshape(1, -1, 2)
        fixed_landmarks = fixed.reshape(1, -1, 2)

        t, i = cv2.estimateAffine2D(
            moving_landmarks, fixed_landmarks)

        h, w = fixed_img.shape

        affined_image = cv2.warpAffine(moving_img, t, fixed_img.shape)

        new_moving_landmarks = cv2.transform(moving_landmarks, t)

        return numpy_to_frame(new_moving_landmarks, origin=Origin.TOP_LEFT), affined_image

    def warp(self, fixed_img: np.ndarray, moving_img: np.ndarray) -> np.ndarray:
        """
        Applies both affine and thin plate splines warping to moving_image using landmarks
        """
        fixed = self.fixed_pts_frame.to_numpy()
        fixed_landmarks = fixed.reshape(1, -1, 2)

        new_landmarks_frame, affined_image = self.warp_affine(
            fixed_img, moving_img)
        new_moving_landmarks = new_landmarks_frame.to_numpy().reshape(1, -1, 2)
        matches = [cv2.DMatch(i, i, 0)
                   for i in range(new_landmarks_frame.count)]

        tpst = cv2.createThinPlateSplineShapeTransformer()
        tpst.estimateTransformation(
            fixed_landmarks, new_moving_landmarks, matches)
        wi = np.ones_like(affined_image)

        return tpst.warpImage(affined_image, wi)
