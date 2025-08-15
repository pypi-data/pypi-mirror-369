"""
Module used to create an interactive graphic,
where slices are selected through scrolling.
"""

from typing import Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable


class IndexTracker:
    """
    Class defining a wrapper for allowing scrolling through different slices of a 3-D
    image when using plt.show().
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments
    def __init__(
        self,
        img_array,
        slice_axis: int = 0,
        fig: plt.Figure = None,
        ax: plt.Axes = None,  # pylint: disable=invalid-name
        **kwargs,
    ):
        """
        Description: Constructs an imshow object, defining the central portion
        of the 3-D image, and the axis that represents the slices. It uses the
        minimum (minv) and maximum value (maxv) to create a colorbar, and to
        define the colormap (cmap). An interactive image is created at the end,
        where scrolling through different slices is possible in the window plt.show().


        Args:
            fig: plt.Figure
                Figure object created from "fig, ax = plt.subplots()"
            ax: plt.Axes
                Axes object created from "fig, ax = plt.subplots()"
            img_array: Array, list, np.ndarray
                3-D array containing image
            overlay: A 3D array of the same shape as img_array to overlay atop
            slice_axis: int
                Axis where slices are located for a 3-D image (usually 0 or 2). Defaults to 0.
            overlay_args: Dictionary of arguments to pass to the overlay's imshow.
            **kwargs: any
                Arguments passed to matplotlib's imshow()
        """
        if fig is None and ax is None:
            fig, ax = plt.subplots()

        # Copy of matplotlib.axes.Axes object
        self.ax = ax  # pylint: disable=invalid-name
        # Axis of slice
        self._slice_axis = slice_axis
        # Define image array
        self.img_array = np.array(img_array)

        self.overlay_arrays = []
        self.overlay = []

        # Set shape of image array
        try:
            self.slices = self.img_array.shape[self._slice_axis]
        except IndexError as error:
            print(f"{error}: slice index must be 0, 1 or 2!")
        # Get the slice in the 'center' of stack
        self._ind = self.slices // 2

        # Construct an indexing tuple to have dynamic indexing
        # Avoids the use of slower <ndarray>.take()
        idx = [slice(None)] * self.img_array.ndim
        idx[self._slice_axis] = self._ind
        self.idx = idx

        # Define image object to show in Window
        # pylint: disable=invalid-name
        self.im = ax.imshow(self.img_array[tuple(idx)], **kwargs)

        # Define color-bar
        self.cb = plt.colorbar(self.im, extend="max")
        # Updates to center of 3-D image
        self._update()
        # Allows scrolling
        fig.canvas.mpl_connect("scroll_event", self._onscroll)

    def _onscroll(self, event):
        """
        Defines scrolling event.
        """
        if event.button == "up":
            self._ind = (self._ind + 1) % self.slices
        else:
            self._ind = (self._ind - 1) % self.slices
        self._update()

    def _update(self):
        """
        Updates image based on index self._ind.
        """
        idx = [slice(None)] * self.img_array.ndim
        idx[self._slice_axis] = self._ind

        self.im.set_data(self.img_array[tuple(idx)])
        if len(self.overlay) > 0:
            for overlay, overlay_array in zip(self.overlay, self.overlay_arrays):
                overlay.set_data(overlay_array[tuple(idx)])

        self.ax.set_ylabel(f"slice {self._ind}/{self.slices - 1}")
        self.im.axes.figure.canvas.draw()

    def add_overlay(self, overlay: np.ndarray, **kwargs) -> None:
        """
        method to add an overlay array on the main view.
        Pixels desired to be transparent should be set to numpy.NaN
        @param overlay: numpy array of the overlay
        @param kwargs: paramters for the imshow of the overlay
        """
        self.overlay_arrays.append(np.array(overlay))
        self.overlay.append(self.ax.imshow(overlay[tuple(self.idx)], **kwargs))

    @staticmethod
    def show():
        """
        Simple wrapper to open Window to show image.
        """
        plt.show()

    def colorbar(self, mappable: Union[ScalarMappable, None] = None, **kwargs):
        """
        Simple wrapper to define the colorbar.
        @param mappable: The matplotlib.cm.ScalarMappable
        (i.e., AxesImage, ContourSet, etc.) described by this colorbar
        """
        self.cb.remove()

        if mappable is None:
            mappable = self.im
        self.cb = plt.colorbar(mappable, **kwargs)
