from .primitives import Frame, Origin, numpy_to_frame
from typing import Tuple
import numpy as np
import cv2
from .primitives import Image


class TpsAlgorithm:
    def __init__(self, moving_img: Image, fixed_img: Image):
        """
        Args:
            moving_img: Verify that the points in the reference frame are from top left
            fixed_img: Verify that the points in the reference frame are from top left

        """
        if moving_img == None:
            raise ValueError("moving_img cannot be None")

        if fixed_img == None:
            raise ValueError("fixed_img cannot be None")

        if moving_img.landmarks == None:
            raise ValueError("no landmarks found for moving_img")

        if fixed_img.landmarks == None:
            raise ValueError("no landmarks found for fixed_img")

        if moving_img.landmarks.count != fixed_img.landmarks.count:
            raise ValueError(
                f"The number of points selected in each reference frame do not match (moving_img.landmarks:{moving_pts_frame.count}, fixed_img.landmarks: {fixed_pts_frame.count}).")

        if moving_img.landmarks.origin.value != Origin.TOP_LEFT.value:
            print("Incorrect reference origin. Changing reference frame for moving_img")
            moving_img = moving_img.change_landmarks_reference(Origin.TOP_LEFT)

        if fixed_img.landmarks.origin.value != Origin.TOP_LEFT.value:
            print("Incorrect reference origin. Changing reference frame for fixed_img")
            fixed_img = fixed_img.change_landmarks_reference(Origin.TOP_LEFT)

        self.moving_img = moving_img
        self.fixed_img = fixed_img

    def warp_affine(self) -> Image:
        "Applied affine transformation to moving_image using landmarks"
        moving = self.moving_img.landmarks.to_numpy()
        fixed = self.fixed_img.landmarks.to_numpy()

        moving_landmarks = moving.reshape(1, -1, 2)
        fixed_landmarks = fixed.reshape(1, -1, 2)

        t, i = cv2.estimateAffine2D(
            moving_landmarks, fixed_landmarks, method=cv2.LMEDS)

        fixed = self.fixed_img()
        moving = self.moving_img()

        affined_image = cv2.warpAffine(moving, t, fixed.shape)

        new_moving_landmarks = cv2.transform(moving_landmarks, t)

        frame = numpy_to_frame(new_moving_landmarks, origin=Origin.TOP_LEFT)

        return Image(affined_image, landmarks=frame)

    def warp(self) -> Image:
        """
        Applies both affine and thin plate splines warping to moving_image using landmarks
        """
        fixed = self.fixed_img.landmarks.to_numpy()
        fixed_landmarks = fixed.reshape(1, -1, 2)

        affined_image = self.warp_affine()

        new_moving_landmarks = (affined_image.landmarks
                                             .to_numpy()
                                             .astype(np.float32)
                                             .reshape(1, -1, 2))
        matches = [cv2.DMatch(i, i, 0)
                   for i in range(affined_image.landmarks.count)]

        # todo: this is for the image
        tpst: cv2.ThinPlateSplineShapeTransformer = cv2.createThinPlateSplineShapeTransformer()
        tpst.estimateTransformation(
            transformingShape=fixed_landmarks,  targetShape=new_moving_landmarks, matches=matches)
        img = affined_image()
        wi = np.ones_like(img)
        warp_img = tpst.warpImage(img, wi)

        # todo: this is for the points (transforming shape and targe shape are reversed from the image)
        tpst: cv2.ThinPlateSplineShapeTransformer = cv2.createThinPlateSplineShapeTransformer()
        tpst.estimateTransformation(
            transformingShape=new_moving_landmarks, targetShape=fixed_landmarks, matches=matches)

        _, tps_landmarks = tpst.applyTransformation(new_moving_landmarks)

        frame = numpy_to_frame(tps_landmarks, origin=Origin.TOP_LEFT)

        return Image(warp_img, landmarks=frame)
