import holoviews as hv
from holoviews import opts
import panel.widgets as pnw
import panel as pn
import numpy as np
from .primitives import Image, Origin, Frame
from .tps import TpsAlgorithm

VISUAL_WIDTH = 800
VISUAL_HEIGHT = 800
POINT_SIZE = 15


class TpsAlgoVisualizer:

    def __init__(self, fixed_image: Image, moving_image: Image):
        self.fixed_image = fixed_image
        self.moving_image = moving_image

    def mri_with_fixed_points(self):
        img = self.fixed_image.change_landmarks_reference(Origin.BOTTOM_LEFT)
        mri = img()
        h, w = mri.shape
        points = [(p.x, p.y) for p in img.landmarks.points]
        return (
            hv.Image(mri, bounds=(0, 0, w, h)).opts(cmap='gray')
            * hv.Points(points, label="mri points").opts(
                color='red',
                size=POINT_SIZE,
                alpha=.25,
                tools=['hover'])
        ).opts(
            title="MRI with landmarks"
        )

    def pathology_with_affine_points(self):
        tps = TpsAlgorithm(self.moving_image, self.fixed_image)
        moved = tps.warp_affine()

        img = moved.change_landmarks_reference(Origin.BOTTOM_LEFT)
        pathology = img()
        h, w = pathology.shape[0:2]
        points = [(p.x, p.y) for p in img.landmarks.points]
        return (
            hv.RGB(pathology, bounds=(0, 0, w, h))
            * hv.Points(points, label="pathology affined points").opts(
                color='blue',
                size=POINT_SIZE,
                alpha=.25,
                tools=['hover'])
        ).opts(
            title="Pathology affined with landmarks"
        )

    def pathology_with_tps_points(self):
        tps = TpsAlgorithm(moving_img=self.moving_image,
                           fixed_img=self.fixed_image)
        moved = tps.warp()

        img = moved.change_landmarks_reference(Origin.BOTTOM_LEFT)
        print(img)

        pathology = img()
        h, w = pathology.shape[0:2]
        points = [(p.x, p.y) for p in img.landmarks.points]
        return (
            hv.RGB(pathology, bounds=(0, 0, w, h))
            * hv.Points(points, label="pathology tps points").opts(
                color='green',
                size=POINT_SIZE,
                alpha=.5,
                tools=['hover'])
        ).opts(
            title="Pathology tps with landmarks"
        )

    def mri_with_affine_overlay(self):
        tps = TpsAlgorithm(self.moving_image, self.fixed_image)
        moved = tps.warp_affine()

        moved_img = moved.change_landmarks_reference(Origin.BOTTOM_LEFT)
        pathology = moved_img()
        ph, pw = pathology.shape[0:2]
        moved_points = [(p.x, p.y) for p in moved_img.landmarks.points]

        fixed_img = self.fixed_image.change_landmarks_reference(
            Origin.BOTTOM_LEFT)
        mri = fixed_img()
        fh, fw = mri.shape
        fixed_points = [(p.x, p.y) for p in fixed_img.landmarks.points]

        # print(moved_points)
        # print(fixed_points)

        return (
            hv.Image(mri, bounds=(0, 0, fw, fh)).opts(cmap='gray')
            * hv.RGB(pathology, bounds=(0, 0, pw, ph)).opts(alpha=.5)
            * hv.Points(fixed_points, label="mri points").opts(color='red',
                                                               size=POINT_SIZE,
                                                               # alpha=.25,
                                                               tools=['hover'])
            * hv.Points(moved_points, label="affine points").opts(color='blue',
                                                                  size=POINT_SIZE,
                                                                  # alpha=.25,
                                                                  tools=['hover'])
        )

    def mri_with_affine_and_tps_overlay(self):
        tps = TpsAlgorithm(self.moving_image, self.fixed_image)
        moved = tps.warp_affine()

        moved_img = moved.change_landmarks_reference(Origin.BOTTOM_LEFT)
        pathology = moved_img()
        ph, pw = pathology.shape[0:2]
        moved_points = [(p.x, p.y) for p in moved_img.landmarks.points]

        fixed_img = self.fixed_image.change_landmarks_reference(
            Origin.BOTTOM_LEFT)
        mri = fixed_img()
        fh, fw = mri.shape
        fixed_points = [(p.x, p.y) for p in fixed_img.landmarks.points]

        tps = TpsAlgorithm(self.moving_image, self.fixed_image)
        tps_moved = tps.warp()

        tps_img = tps_moved.change_landmarks_reference(Origin.BOTTOM_LEFT)
        tps = tps_img()
        th, tw = tps.shape[0:2]
        tps_points = [(p.x, p.y) for p in tps_img.landmarks.points]

        return (
            hv.Image(mri, bounds=(0, 0, fw, fh)).opts(cmap='gray')
            * hv.RGB(pathology, bounds=(0, 0, pw, ph)).opts(alpha=.5)
            * hv.Points(fixed_points, label="mri points").opts(color='red',
                                                               size=POINT_SIZE,
                                                               alpha=.25,
                                                               tools=['hover'])
            * hv.Points(moved_points, label="affine points").opts(color='blue',
                                                                  size=POINT_SIZE,
                                                                  alpha=.25,
                                                                  tools=['hover'])
            * hv.Points(tps_points, label="tps points").opts(color='green',
                                                             size=POINT_SIZE,
                                                             alpha=.25,
                                                             tools=['hover'])
        )

    def mri_with_tps_overlay(self):
        tps = TpsAlgorithm(self.moving_image, self.fixed_image)
        moved = tps.warp()

        moved_img = moved.change_landmarks_reference(Origin.BOTTOM_LEFT)
        pathology = moved_img()
        ph, pw = pathology.shape[0:2]
        moved_points = [(p.x, p.y) for p in moved_img.landmarks.points]

        fixed_img = self.fixed_image.change_landmarks_reference(
            Origin.BOTTOM_LEFT)
        mri = fixed_img()
        fh, fw = mri.shape
        fixed_points = [(p.x, p.y) for p in fixed_img.landmarks.points]

        return (
            hv.Image(mri, bounds=(0, 0, fw, fh)).opts(cmap='gray')
            * hv.RGB(pathology, bounds=(0, 0, pw, ph)).opts(alpha=.5)
            * hv.Points(fixed_points, label="mri points").opts(color='red',
                                                               size=POINT_SIZE,
                                                               #    alpha=.25,
                                                               tools=['hover'])
            * hv.Points(moved_points, label="tps points").opts(color='blue',
                                                               size=POINT_SIZE,
                                                               #    alpha=.25,
                                                               tools=['hover'])
        )

    def panel(self):
        mri = self.mri_with_fixed_points()
        affined = self.pathology_with_affine_points()
        tps = self.pathology_with_tps_points()
        overlay_affine = self.mri_with_affine_overlay()
        overlay_tps = self.mri_with_tps_overlay()
        return (
            (mri
             + affined
             + tps
             + overlay_affine
             + overlay_tps
             ).opts(
                width=VISUAL_WIDTH,
                height=VISUAL_HEIGHT
            ).cols(2))
