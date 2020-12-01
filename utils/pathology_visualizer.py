import panel.widgets as pnw
import panel as pn
from .helpers import scale_image_dim, default_factor, rotate_bound
import holoviews as hv
import param
import cv2
import numpy as np
from .primitives import Image

VISUAL_WIDTH = 600
VISUAL_HEIGHT = 600


class PathologyVisualizer(param.Parameterized):

    SCALE_MIN = 0.
    SCALE_MAX = 1.

    interpolation_map = {
        "INTER_LINEAR": cv2.INTER_LINEAR,
        "INTER_CUBIC": cv2.INTER_CUBIC,
        "INTER_AREA": cv2.INTER_AREA
    }

    def __init__(self, pathology_img: Image):
        self.pathology_img_source = pathology_img
        initial_scale = .01  # default_factor(self.pathology_img_source.shape)

        self.scale_wig = pnw.FloatSlider(name='scale factor', step=.01, value=initial_scale,
                                         start=PathologyVisualizer.SCALE_MIN,
                                         end=PathologyVisualizer.SCALE_MAX)
        self.aspect_wig = pn.widgets.StaticText(
            name='aspect ratio at 0 degrees (height x width)', value=(0, 0))
        self.angle_wig = pnw.IntSlider(name='angle', step=1, value=0,
                                       start=-180,
                                       end=180)

        self.flip_x_axis = pnw.Toggle(name="flip horizontally", width=100)
        self.flip_y_axis = pnw.Toggle(name="flip vertically", width=100)

        self.interpolation = pnw.Select(name='interpolation', options=[
                                        'INTER_AREA', 'INTER_CUBIC', 'INTER_LINEAR'], value='INTER_LINEAR')

    def load_pathology(self,
                       scale=.5,
                       interpolation=cv2.INTER_LINEAR,
                       angle=0.,
                       flip_x=False,
                       flip_y=False
                       ):
        img = self.moving_image()
        self.aspect_wig.value = img.shape[0:2]
        h, w = img.shape[0], img.shape[1]
        return hv.RGB(img, bounds=(0, 0, w, h)).opts(width=VISUAL_WIDTH, height=VISUAL_HEIGHT)

    @property
    def moving_image(self) -> Image:
        interpolation_ = PathologyVisualizer.interpolation_map.get(
            self.interpolation.value, 'INTER_LINEAR')
        return self.pathology_img_source.update(
            scale=self.scale_wig.value,
            angle=self.angle_wig.value,
            interpolation=self.interpolation.value,
            flip_x=self.flip_x_axis.value,
            flip_y=self.flip_y_axis.value
        )

    def panel(self):
        flips = pn.Row(self.flip_x_axis, self.flip_y_axis)
        transforms = pn.Column(
            self.scale_wig, self.aspect_wig, self.angle_wig, flips)
        widgets = pn.Column(transforms, self.interpolation)
        image_ = pn.Column()
        image_.append(pn.depends(self.scale_wig, self.interpolation,
                                 self.angle_wig, self.flip_x_axis, self.flip_y_axis)(self.load_pathology))
        image = pn.Row(image_, widgets)
        return image

    def side_by_side(self, annotated_source: Image):
        moving_img = self.moving_image
        annotated_img = annotated_source.copy_attributes(moving_img)
        moving = moving_img()
        annotated = annotated_img()
        view = (
            (hv.RGB(annotated) + hv.RGB(moving)) +
            (hv.RGB(moving) * hv.RGB(annotated).opts(alpha=.5))
        )
        return view.cols(2)
