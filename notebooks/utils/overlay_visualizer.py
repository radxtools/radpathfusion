import panel.widgets as pnw
import panel as pn
import holoviews as hv
import param
import cv2
import numpy as np
from .primitives import Image, Origin
from .tps import TpsAlgorithm

VISUAL_WIDTH = 800
VISUAL_HEIGHT = 800


class TpsOverlayVisualizer():

    def __init__(self,
                 fixed: Image,
                 warped: Image,
                 annotated: Image = None):

        self.fixed_alpha_wig = pnw.FloatSlider(
            name='fixed_alpha', value=1, start=0, end=1)
        self.moving_alpha_wig = pnw.FloatSlider(
            name='moving_alpha', value=.5, start=0, end=1)
        self.annotated_alpha_wig = pnw.FloatSlider(
            name='annotated_alpha', value=.5, start=0, end=1)

        self.fixed = fixed
        self.warped = warped
        self.annotated = annotated

    def visualize_images(self, fixed_alpha, moving_alpha, annotated_alpha):
        fixed: Image = self.fixed()
        height, width = fixed.shape

        tps_pathology = TpsAlgorithm(
            moving_img=self.warped, fixed_img=self.fixed)
        warped: Image = tps_pathology.warp()

        f = hv.Image(fixed, bounds=(0, 0, width, height)
                     ).opts(cmap='gray', alpha=fixed_alpha)
        m = hv.RGB(warped(), bounds=(0, 0, width, height)
                   ).opts(alpha=moving_alpha)
        graphs = f * m
        if self.annotated is not None:
            tps_annotated = TpsAlgorithm(
                moving_img=self.annotated, fixed_img=self.fixed)
            annotated: Image = tps_annotated.warp()

            a = hv.RGB(annotated(), bounds=(0, 0, width, height)
                       ).opts(alpha=annotated_alpha)
            graphs = graphs * a
        return (graphs).opts(width=VISUAL_WIDTH, height=VISUAL_HEIGHT,
                             title="MRI, pathology, and annotated pathology overlay")

    def panel(self):
        cols = pn.Column()
        if self.annotated is not None:
            wigs = pn.Row(self.fixed_alpha_wig,
                          self.moving_alpha_wig, self.annotated_alpha_wig)
        else:
            wigs = pn.Row(self.fixed_alpha_wig, self.moving_alpha_wig)
        cols.append(pn.depends(self.fixed_alpha_wig, self.moving_alpha_wig,
                               self.annotated_alpha_wig)(self.visualize_images))
        cols.append(wigs)
        return cols
