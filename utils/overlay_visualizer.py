import panel.widgets as pnw
import panel as pn
import holoviews as hv
import param
import cv2

VISUAL_WIDTH = 800
VISUAL_HEIGHT = 800


class OverlayVisualizer():

    def __init__(self, fixed, warped, annotated=None):

        self.fixed_alpha_wig = pnw.FloatSlider(
            name='fixed_alpha', value=1, start=0, end=1)
        self.moving_alpha_wig = pnw.FloatSlider(
            name='moving_alpha', value=.5, start=0, end=1)
        self.annotated_alpha_wig = pnw.FloatSlider(
            name='annotated_alpha', value=.5, start=0, end=1)

        self.fixed = fixed
        self.warped = warped
        self.annotated = annotated
        menu_items = [('Download', 'a')]

        self.download_button = pn.widgets.MenuButton(
            name='Download', items=menu_items, button_type='primary')

        def download(event):
            f'Clicked menu item: "{event.new}"'
        self.download_button.on_click(download)

    def visualize_images(self, fixed_alpha, moving_alpha, annotated_alpha):
        width, height = self.fixed.shape
        f = hv.Image(self.fixed, bounds=(0, 0, width, height)
                     ).opts(cmap='gray', alpha=fixed_alpha)
        m = hv.RGB(self.warped, bounds=(0, 0, width, height)
                   ).opts(alpha=moving_alpha)
        graphs = f * m
        if self.annotated is not None:
            a = hv.RGB(self.annotated, bounds=(0, 0, width, height)
                       ).opts(alpha=annotated_alpha)
            graphs = graphs * a
        return (graphs).opts(width=VISUAL_WIDTH, height=VISUAL_HEIGHT)

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
        cols.append(self.download_button)
        return cols
