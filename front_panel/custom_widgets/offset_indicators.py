from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import transforms
from matplotlib.colors import to_rgba


class VerticalOffsetIndicator:
    def __init__(self, ax, start_y=0.1, label="", label_fontsize=8, zorder=1, color="black", visible=False):
        self.ax: Axes = ax
        self.start_y = start_y
        self.start_y = start_y
        self.base_width = 0.02
        self.base_height = 0.05
        self.triangle_width = 0.01
        self.trans = transforms.blended_transform_factory(self.ax.transAxes, self.ax.transAxes)
        self.label = label
        self.scale = label_fontsize / 8
        # Compute the left offset in axes coordinates.
        self.left_of_y_axis = -self.base_width - self.triangle_width
        self.hut_coords = self._calculate_vertices()
        self.color: tuple | str = to_rgba(color)
        self.zorder = zorder

        # We'll save references to the drawn objects so they can be updated.
        self.patch = None
        self.text_artist = None

        # First draw to instantiate the patch and the text
        self.draw(visible)

    def hide(self):
        if self.patch is not None:
            self.patch.set_visible(False)
        if self.text_artist is not None:
            self.text_artist.set_visible(False)

    def show(self):
        if self.patch is not None:
            self.patch.set_visible(True)
        if self.text_artist is not None:
            self.text_artist.set_visible(True)

    def _calculate_vertices(self):
        # Combined vertices for the hut shape in axes coordinates
        self.left_of_y_axis = -self.base_width - self.triangle_width

        vertices = [
            (self.left_of_y_axis, self.start_y - self.base_height / 2),  # Bottom-left of base
            (self.left_of_y_axis, self.start_y + self.base_height / 2),  # Top-left of base
            (self.left_of_y_axis + self.base_width, self.start_y + self.base_height / 2),  # Top-right of base
            (self.left_of_y_axis + self.base_width + self.triangle_width, self.start_y),  # Triangle apex
            (self.left_of_y_axis + self.base_width, self.start_y - self.base_height / 2),  # Bottom-right of base
        ]
        
        if vertices[3][1] < 0:
            shift = -vertices[3][1]  # Calculate how much to shift upwards
            vertices = [(x, y + shift) for x, y in vertices]  # Shift all vertices
        elif vertices[3][1] > 1:
            shift = vertices[3][1] - 1  # Calculate how much to shift downwards
            vertices = [(x, y - shift) for x, y in vertices]  # Shift all vertices
        
        return vertices

    def draw(self, visible):
        # Recalculate vertices based on the latest self.start_y.
        self.hut_coords = self._calculate_vertices()

        # Update existing patch if available; otherwise, create a new one.
        if self.patch is None:
            self.patch = patches.Polygon(
                self.hut_coords,
                closed=True,
                facecolor=self.color,
                edgecolor="black",
                linewidth=0.5,
                transform=self.trans,
                zorder=self.zorder,
                clip_on=False,
            )
            # Exclude from layout calculations (prevent axes rescaling when indicator is at limits)
            self.patch.set_in_layout(False)
            # Add patch to axes
            self.ax.add_patch(self.patch)
        else:
            self.patch.set_xy(self.hut_coords)

        # Calculate the center of the rectangular base for the label.
        center_x = self.left_of_y_axis + self.base_width / 2
        # Adjusting the vertical center by hut's triangle apex
        center_y = self.hut_coords[3][1]

        # Update existing text if available; otherwise, create a new text artist.
        if self.text_artist is None:
            self.text_artist = self.ax.text(
                center_x,
                center_y,
                self.label,
                transform=self.trans,
                fontsize=4,
                color="black",
                weight="bold",
                ha="center",
                va="center",
                zorder=self.zorder + 0.1,
                clip_on=False,
            )
            # Exclude text from affecting layout (prevent axes rescaling when indicator is at limits)
            self.text_artist.set_in_layout(False)
        else:
            self.text_artist.set_position((center_x, center_y))
            self.text_artist.set_fontsize(4)
        
        # Decide about the visibility
        if visible:
            self.show()
        else:
            self.hide()

    def update_position(self, new_start_y, visible):
        """
        Update the vertical position of the indicator.
        This method changes the starting y-coordinate,
        recalculates the vertices, and updates the drawn patch and text.
        """
        self.start_y = float(new_start_y)
        # Recalculate the polygon vertices with the new y position.
        self.hut_coords = self._calculate_vertices()
        # Update the patch and text.
        self.draw(visible)
        # Optionally force a canvas redraw:
        if self.ax.figure:
            self.ax.figure.canvas.draw_idle()


class HorizontalOffsetIndicator:
    pass


if __name__ == "__main__":
    # Example usage:
    fig, ax = plt.subplots()

    hut1 = VerticalOffsetIndicator(ax, start_y=0.1, label="1", zorder=2, color="yellow", visible=True)
    hut2 = VerticalOffsetIndicator(ax, start_y=0.114, label="2", zorder=1, color="magenta", visible=True)

    plt.tight_layout(pad=2.0)
    # Set up the axes (the patches remain fixed in axes coordinates)
    ax.set_xlim(-1, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Hut-like Shape with Scaled Label (Combined Polygon)")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.grid(True)

    plt.show()
