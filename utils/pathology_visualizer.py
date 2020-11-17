import panel.widgets as pnw
import panel as pn
from .helpers import scale_image_dim, default_factor, rotate_bound
import holoviews as hv
import param
import cv2

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

    def __init__(self, pathology_img):
        self.pathology_img_scaled = pathology_img.copy()
        initial_scale = default_factor(self.pathology_img_scaled.shape)

        self.scale_wig = pnw.FloatSlider(name='scale factor', step=.01, value=initial_scale,
                                         start=PathologyVisualizer.SCALE_MIN,
                                         end=PathologyVisualizer.SCALE_MAX)
        self.aspect_wig = pn.widgets.StaticText(
            name='aspect ratio (height x width)', value=self.pathology_img_scaled.shape[0:2])
        self.angle_wig = pnw.IntSlider(name='angle', step=1, value=0,
                                       start=-180,
                                       end=180)

        self.rotate_left = pnw.Button(name='rotate left', width=50)
        self.rotate_left.on_click(self.rotate_counter_clockwise_fn)
        self.rotate_right = pnw.Button(name='rotate right', width=50)
        self.rotate_right.on_click(self.rotate_clockwise_fn)
        self.interpolation = pnw.Select(name='interpolation', options=[
                                        'INTER_AREA', 'INTER_CUBIC', 'INTER_LINEAR'], value='INTER_LINEAR')

    def rotate_clockwise_fn(self, event):
        self.pathology_img_scaled = cv2.rotate(
            self.pathology_img_scaled, cv2.ROTATE_90_CLOCKWISE)
        self.image_.pop(0)
        self.image_.append(pn.depends(
            self.scale_wig, self.interpolation, self.angle_wig)(self.load_pathology))

    def rotate_counter_clockwise_fn(self, event):
        self.pathology_img_scaled = cv2.rotate(
            self.pathology_img_scaled, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.image_.pop(0)
        self.image_.append(pn.depends(
            self.scale_wig, self.interpolation, self.angle_wig)(self.load_pathology))

    def load_pathology(self, scale=.5, interpolation=cv2.INTER_LINEAR, angle=0):
        # Update label of aspect ratio of original image without rotation
        # print("lp inital", self.pathology_img_scaled.shape)
        img = self.pathology_img_scaled
        factor = self.scale_wig.value
        h, w = int(factor*img.shape[0]), int(factor*img.shape[1])
        self.aspect_wig.value = (h, w)
        dst = self.moving_image
        h, w = dst.shape[0], dst.shape[1]
        return hv.RGB(dst, bounds=(0, 0, w, h)).opts(width=VISUAL_WIDTH, height=VISUAL_HEIGHT)

    @property
    def moving_image(self):
        interpolation_ = PathologyVisualizer.interpolation_map.get(
            self.interpolation.value, 'INTER_LINEAR')
        img = scale_image_dim(self.pathology_img_scaled,
                              self.scale_wig.value, interpolation_)
        return rotate_bound(img, self.angle_wig.value)

    def transform_annotation_image(self, annotated_img):
        interpolation_ = cv2.INTER_AREA
        img = scale_image_dim(
            annotated_img, self.scale_wig.value, interpolation_)
        return rotate_bound(img, self.angle_wig.value)

    def panel(self):
        transforms = pn.Column(self.scale_wig, self.aspect_wig, self.angle_wig)
        rotation = pn.Row(self.rotate_left, self.rotate_right)
        widgets = pn.Column(transforms, rotation, self.interpolation)
        image_ = pn.Column()
        self.image_ = image_
        image_.append(pn.depends(self.scale_wig, self.interpolation,
                                 self.angle_wig)(self.load_pathology))
        image = pn.Row(image_, widgets)
        return image
