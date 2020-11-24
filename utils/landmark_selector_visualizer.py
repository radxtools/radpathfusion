import panel.widgets as pnw
import panel as pn
from pathlib import Path
import param
import cv2
import holoviews as hv
from holoviews import opts
from holoviews import streams
from holoviews.streams import Pipe, Buffer
from holoviews.plotting.links import DataLink
import pandas as pd
from typing import Tuple, List
import typing
import enum
import numpy as np
from .primitives import Origin, Frame, Point, Image, translate_vertical_reference_frames


LANDMARK_COLOR_CYCLE = ['green', 'blue',  'red', 'yellow', 'pink',
                        'gray', 'orange', 'black', 'purple', 'brown']

LANDMARK_COLOR_DEFAULT = 'white'


class LandmarkSelectorVisualizer():

    def __init__(self, fixed_img: Image, moving_img: Image):
        self.fixed_img = fixed_img
        self.moving_img = moving_img
        self.fixed_stream = None
        self.moving_stream = None

    def _landmark_moving_wig(self, arr):
        points_source = hv.Points([])

        points_source_stream = streams.PointDraw(data=points_source.columns(),
                                                 num_objects=10,
                                                 source=points_source,
                                                 empty_value=LANDMARK_COLOR_DEFAULT,
                                                 styles={
                                                     'fill_color': LANDMARK_COLOR_CYCLE
        })

        height, width, _ = arr.shape
        image = hv.RGB(arr, bounds=(0, 0, width, height))

        table = hv.Table(points_source, ['x', 'y'])
        DataLink(points_source, table)

        wig = ((image * points_source) + table).opts(
            opts.Points(active_tools=['point_draw'], show_grid=True,
                        marker='s', size=10, tools=['hover', 'crosshair', 'undo']),
            opts.Table(editable=True)
        )

        self.moving_stream = points_source_stream

        return wig

    def _landmark_fixed_wig(self, arr):
        points_source = hv.Points([])
        points_source_stream = streams.PointDraw(data=points_source.columns(),
                                                 num_objects=10,
                                                 source=points_source,
                                                 empty_value=LANDMARK_COLOR_DEFAULT,
                                                 styles={
                                                     'fill_color': LANDMARK_COLOR_CYCLE
        })

        height, width = arr.shape
        image = hv.Image(arr, bounds=(0, 0, width, height)).opts(cmap='gray')

        table = hv.Table(points_source, ['x', 'y'])
        DataLink(points_source, table)

        self.fixed_stream = points_source_stream

        wig = ((image * points_source) + table).opts(
            opts.Points(active_tools=['point_draw'], show_grid=True,
                        marker='s', size=10, tools=['hover', 'crosshair', 'undo']),
            opts.Table(editable=True)
        )

        return wig

    def fixed_image(self, in_origin: Origin) -> Image:
        xs = self.fixed_stream.data['x']
        ys = self.fixed_stream.data['y']
        points = list([Point(x, y) for x, y in zip(xs, ys)])
        if in_origin.value == Origin.TOP_LEFT.value:
            frame = Frame()
            h = self.fixed_img().shape[0]
            frame.points = translate_vertical_reference_frames(
                origin=Point(0, h), points=points)
            frame.origin = Origin.TOP_LEFT
        else:
            frame = Frame()
            frame.points = points
            frame.origin = Origin.BOTTOM_LEFT

        return self.fixed_img.update(
            landmarks=frame
        )

    def moving_image(self, in_origin: Origin) -> Frame:
        xs = self.moving_stream.data['x']
        ys = self.moving_stream.data['y']
        points = list([Point(x, y) for x, y in zip(xs, ys)])

        if in_origin.value == Origin.TOP_LEFT.value:
            f = Frame()
            h = self.moving_img().shape[0]
            f.points = translate_vertical_reference_frames(
                origin=Point(0, h), points=points)
            f.origin = Origin.TOP_LEFT

        else:
            f = Frame()
            f.points = points
            f.origin = Origin.BOTTOM_LEFT
        return self.moving_img.update(
            landmarks=f
        )

    def associated_points_to_DF(self):
        df = pd.DataFrame(
            {
                "moving_x": map(int, self.moving_stream.data['x']),
                "moving_y": map(int, self.moving_stream.data['y']),
                "fixed_x": map(int, self.fixed_stream.data['x']),
                "fixed_y": map(int, self.fixed_stream.data['y'])
            }
        )
        return df

    def panel(self):
        fixed = self._landmark_fixed_wig(self.fixed_img())
        moving = self._landmark_moving_wig(self.moving_img())
        layout = (fixed + moving).opts(merge_tools=False, shared_axes=False)
        layout.cols(2)
        return layout
