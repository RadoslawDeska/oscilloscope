import logging
import matplotlib
from matplotlib import ticker
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
import numpy as np
from numpy.typing import NDArray
from matplotlib import transforms
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Polygon

from front_panel.custom_widgets.offset_indicators import VerticalOffsetIndicator
from signal_generator import N_TDIV, N_VDIV

matplotlib.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=180, **kwargs):
        self.parent = parent
        plt.style.use("dark_background")
        self.gridcolor = "#666666"

        self.xlim = kwargs["xlim"] if "xlim" in kwargs else (-1, 1)
        self.ylim1 = kwargs["ylim1"] if "ylim1" in kwargs else (-1, 1)
        self.ylim2 = kwargs["ylim2"] if "ylim2" in kwargs else (-1, 1)

        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        # Create axis for single channel
        self.axes1 = fig.add_subplot(111)
        self.axes1.set_xlim(self.xlim)
        self.axes1.set_ylim(self.ylim1)

        # Create a second y-axis for second channel
        self.axes2 = self.axes1.twinx()
        self.axes2.set_xlim(self.xlim)
        self.axes2.set_ylim(self.ylim2)

        # Do not autoscale
        self.axes1.set_autoscale_on(False)
        self.axes2.set_autoscale_on(False)

        # Enable grid lines
        # Update the grid
        self.update_grid()

        # Match the axes spines' color with color the grid
        for spine in self.axes1.spines.values():
            spine.set_color(self.gridcolor)
        for spine in self.axes2.spines.values():
            spine.set_color(self.gridcolor)

        # Draw the crosshair at the chart center
        # self.crosshair_h = self.axes1.axhline(self.axes_to_data(0.5, axis='y'), color='#CCCCCC', linewidth=0.5)
        # self.crosshair_v = self.axes1.axvline(self.axes_to_data(0.5, axis='x'), color='#CCCCCC', linewidth=0.5)

        # Hide the tick labels
        self.axes1.set_xticklabels([])
        self.axes1.set_yticklabels([])
        self.axes2.set_yticklabels([])

        # Format ticks (comment-out if should be invisible)
        # formatter = ticker.EngFormatter(places=1)  # Set places to 1 for one decimal place
        # self.axes1.xaxis.set_major_formatter(formatter)
        # self.axes1.xaxis.get_offset_text().set_fontsize(3)

        # Keep the tick marks but make them invisible
        self.axes1.tick_params(axis="both", which="both", length=0, labelsize=3)
        self.axes2.tick_params(axis="both", which="both", length=0, labelsize=3)

        # Draw trigger triangle
        self.draw_trigger_triangle()
        # Draw trigger line (it is zero time-point)
        self.axes1.axvline(color="lightblue", linewidth=0.5, linestyle="--")

        # Draw vertical offset indicators
        self.channel1_offset_indicator = VerticalOffsetIndicator(
            self.axes1,
            start_y=0.1,
            label="1",
            zorder=2,
            color="yellow",
            visible=self.parent.channel1.Enabled if self.parent is not None else False,
        )
        self.channel2_offset_indicator = VerticalOffsetIndicator(
            self.axes2,
            start_y=0.2,
            label="2",
            zorder=1,
            color="magenta",
            visible=self.parent.channel2.Enabled if self.parent is not None else False,
        )
        # Initialize plot lines for channels:
        (self.channel1_line,) = self.axes1.plot([], [], color="#ffff7b", linewidth=0.5)
        (self.channel2_line,) = self.axes2.plot([], [], color="#ee6bee", linewidth=0.5)

        super().__init__(fig)

    def draw_trigger_triangle(self):
        """Draws trigger position triangle using axes coordinates (independent of data)"""
        # Coordinates of the triangle vertices in axes coordinates
        base_y = 1  # Base of the triangle at the top of the axes
        h = 0.04  # Height of the triangle in axes coordinates
        apex_y = base_y - h
        self.half_base = h / (2 * np.sqrt(3) / 3)

        delay_position_axes = self.data_to_axes(0, axis="x")

        # Triangle vertices (apex pointing downwards) in axes coordinates
        self.vertices = np.array(
            [
                [delay_position_axes, apex_y],  # Apex at the bottom (centered horizontally and at the top of the axes)
                [delay_position_axes - self.half_base / 2, base_y],  # Left base
                [delay_position_axes + self.half_base / 2, base_y],  # Right base
            ]
        )

        # Create a transform to map the triangle to axes coordinates
        transform = transforms.blended_transform_factory(self.axes1.transAxes, self.axes1.transAxes)

        # Create the triangle patch using axes coordinates
        self.triangle = Polygon(self.vertices, closed=True, facecolor="lightblue", edgecolor="lightblue", transform=transform)

        # Add the triangle to the axes
        self.axes1.add_patch(self.triangle)

    def data_to_axes(self, data_coordinate: float, axis: str, axis_number: int = 1):
        """Return axes coordinates aware of y-axis offset"""
        if axis == "x":
            lim_min, lim_max = self.axes1.get_xlim()
        elif axis == "y":
            axes_map = {1: self.axes1, 2: self.axes2}
            if axis_number in axes_map:
                axis_instance: Axes = axes_map.get(axis_number)  # type: ignore
                if any(hasattr(self.parent, ch) for ch in ["channel1", "channel2"]) and self.parent:
                    offset_data = self.parent.channel1.Offset if axis_number == 1 else self.parent.channel2.Offset
                    lim_min, lim_max = axis_instance.get_ylim()
                    lim_min, lim_max = lim_min + float(offset_data), lim_max + float(offset_data)
                else:
                    logging.debug("MplCanvas parent is None.")
                    return
            else:
                logging.debug(f"Unsupported axis_number {axis_number}")
                return
        else:
            logging.debug(f"Unsupported axis {axis}")
            return

        return (data_coordinate - lim_min) / (lim_max - lim_min)

    def axes_to_data(self, axes_coordinate: float, axis: str, axis_number: int = 1):
        if axis == "x":
            lim_min, lim_max = self.axes1.get_xlim()
        elif axis == "y":
            axis_instance: Axes = {1: self.axes1, 2: self.axes2}.get(axis_number)  # type: ignore
            if not axis_instance:
                logging.debug(f"Unsupported axis_number {axis_number}")
                return
            lim_min, lim_max = axis_instance.get_ylim()
        else:
            logging.debug(f"Unsupported axis {axis}")
            return

        return axes_coordinate * (lim_max - lim_min) + lim_min

    def update_trigger_triangle_position(self):
        """Update the trigger triangle position with new time data x-coordinate"""
        # Update the data x coordinate
        x_position_axes = self.data_to_axes(0, axis="x")

        # Update the x-coordinates of the vertices
        self.vertices[0][0] = x_position_axes  # Apex
        self.vertices[1][0] = x_position_axes - self.half_base / 2  # Left base
        self.vertices[2][0] = x_position_axes + self.half_base / 2  # Right base

        # Set the new vertices to the polygon
        self.triangle.set_xy(self.vertices)

        self.draw_idle()

    def update_chart(self, xlim=None, ylim=None, axis_number=1):
        xlim = xlim if xlim is not None else self.xlim
        ylim = ylim if ylim is not None else self.ylim1

        self.axes1.set_xlim(xlim)
        self.xlim = self.axes1.get_xlim()

        if axis_number == 1:
            self.axes1.set_ylim(ylim)
            self.ylim1 = self.axes1.get_ylim()
        elif axis_number == 2:
            self.axes2.set_ylim(ylim)
            self.ylim2 = self.axes2.get_ylim()
        else:
            logging.debug(f"Unsupported axis_number {axis_number}")

        self.update_grid()
        self.draw()

    def update_grid(self):
        """The grid has to be determined only for one axis. No need to implement for self.axes2"""
        # Calculate fixed tick positions
        x_tick_positions: NDArray = self.calculate_fixed_positions(self.xlim, N_TDIV)
        y_tick_positions: NDArray = self.calculate_fixed_positions(self.ylim1, N_VDIV)

        # Set major tick locators with fixed positions
        major_Xlocator = FixedLocator(x_tick_positions.tolist())
        major_Ylocator = FixedLocator(y_tick_positions.tolist())
        self.axes1.xaxis.set_major_locator(major_Xlocator)
        self.axes1.yaxis.set_major_locator(major_Ylocator)

        # Update the grid
        self.axes1.grid(which="major", color=self.gridcolor, linewidth=0.5)

    def calculate_fixed_positions(self, axis_limits: tuple[float, float], num_ticks: int) -> NDArray:
        axis_min, axis_max = axis_limits
        return np.linspace(axis_min, axis_max, num_ticks + 1, endpoint=True)
