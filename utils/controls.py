from matplotlib import pyplot as plt
import cv2
import holoviews as hv
from holoviews import opts
import pydicom
import param
import panel.widgets as pnw
import panel as pn
from pathlib import Path
import numpy as np
import holoviews as hv
from holoviews import opts
from PIL import Image
import numpy as np
from holoviews import streams
from holoviews.streams import Pipe, Buffer
from holoviews.plotting.links import DataLink
import pandas as pd


class tps_intermediate_states_viewer():
    def __init__(self, tps, fixed_image, fixed_landmarks, moving_image, moving_landmarks):
        pass

    def mri_and_fixed_points(self):
        pass

    def pathology_and_affine_points(self):
        pass

    def both_mri_pathology_with_fixed_and_affined_points(self):
        pass

    def both_mri_pathology_with_fixed_and_tps_points(self):
        pass

    def all_view():
        z = (
            hv.Image(mv.fixed_image, bounds=(
                0, 0, mv.fixed_image.shape[0], mv.fixed_image.shape[1])).opts(cmap='gray')
            * hv.RGB(m, bounds=(0, 0, m.shape[1], m.shape[0])).opts(alpha=.5)
            * hv.Points(tps.display_moving_landmarks[0]).opts(color='red', size=25, alpha=.25)
            * hv.Points(fixed_pts).opts(color='blue', size=25, alpha=.25)
        )
        z.opts(width=800, height=800)
        return z
