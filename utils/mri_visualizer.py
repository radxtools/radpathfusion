import panel.widgets as pnw
import panel as pn
from pathlib import Path
import holoviews as hv
from .helpers import scale_image_dim
import param
import cv2
import pydicom
from .primitives import Image


class MriVisualizer(param.Parameterized):

    VISUAL_WIDTH = 600
    VISUAL_HEIGHT = 600
    SCALE_MIN = 1
    SCALE_MAX = 10

    def __init__(self, mri_path: Path):
        p = Path(mri_path)

        # slice location better for sorting
        self.dcms = sorted([dcm for dcm in p.iterdir()])

        initial_scale = 1

        self.scale_wig = pnw.FloatSlider(name='scale factor',
                                         step=.1,
                                         value=initial_scale,
                                         start=MriVisualizer.SCALE_MIN,
                                         end=MriVisualizer.SCALE_MAX)
        self.index_wig = pnw.IntSlider(
            name='slice', value=1, start=1, end=len(self.dcms))
        self.interpolation = pnw.Select(name='interpolation', options=[
                                        'INTER_AREA', 'INTER_CUBIC', 'INTER_LINEAR'], value='INTER_CUBIC')
        w, h = 0, 0

        self.aspect_wig = pn.widgets.StaticText(
            name='aspect ratio', value=(w, h))

    def load_mri(self, i, scale, interpolation):
        dst = self.fixed_image()  # this should be a open cv image
        height, width = dst.shape[0], dst.shape[1]
        self.aspect_wig.value = dst.shape
        return (hv.Image(dst, bounds=(0, 0, width, height))
                  .opts(width=MriVisualizer.VISUAL_WIDTH,
                        height=MriVisualizer.VISUAL_HEIGHT,
                        cmap='gray'))

    @property
    def fixed_image(self) -> Image:
        path = self.dcms[self.index_wig.value]
        dataset = pydicom.dcmread(path)
        img = dataset.pixel_array
        return Image(img, scale=self.scale_wig.value, interpolation=self.interpolation.value)

    def panel(self):
        scaling = pn.Column(self.scale_wig, self.aspect_wig)
        widgets = pn.Column(scaling, self.index_wig, self.interpolation)
        image_ = pn.Column()
        image_.append(pn.depends(self.index_wig, self.scale_wig,
                                 self.interpolation)(self.load_mri))
        image = pn.Row(image_, widgets)
        return image
