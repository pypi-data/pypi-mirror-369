from pyqtgraph import QtGui, QtCore
import pyqtgraph as pg
from abc import abstractmethod
import numpy as np
from .style import DEFAULT_STYLE, LINE_DEFAULT_STYLE
from .data_handler import ChildDataFrame, PricesDataFrame, VolumeDataFrame


def get_plot_item(data_frame: ChildDataFrame, style=DEFAULT_STYLE):
    """
    Returns a plot item based on the type of data frame.

    Parameters:
    data_frame (ChildDataFrame): The data frame to create the plot item for.
    style (str, optional): The style of the plot item. Defaults to DEFAULT_STYLE.

    Returns:
    PlotItem: The plot item based on the type of data frame.

    Raises:
    TypeError: If the data frame is not of type PricesDataFrame.
    """
    if isinstance(data_frame, PricesDataFrame):
        return CandlestickPricesItem(data_frame, style=style)
    elif isinstance(data_frame, VolumeDataFrame):
        return CandlestickVolumeItem(data_frame, style=style)
    else:
        raise TypeError("data_frame must be PricesDataFrame")


class AdaptiveGraphObject(pg.GraphicsObject):
    """
    A base class for adaptive graph objects in the plotter.
    """

    def __init__(self):
        super().__init__()
        self.style = None

    @abstractmethod
    def get_local_plot_range(self, x_start, x_end):
        """
        Abstract method to get the local plot range for the graph object.

        Args:
            x_start (float): The starting x-coordinate of the plot range.
            x_end (float): The ending x-coordinate of the plot range.

        Returns:
            tuple: A tuple containing the local plot range.
        """
        raise NotImplementedError

    @abstractmethod
    def get_x_ticks(self):
        """
        Abstract method to get the x-axis ticks for the graph object.

        Returns:
            list: A list of x-axis ticks.
        """
        raise NotImplementedError

    @abstractmethod
    def get_feature_value(self, key):
        """
        Abstract method to get the value of a specific feature for the graph object.

        Args:
            key (str): The key of the feature.

        Returns:
            Any: The value of the feature.
        """
        raise NotImplementedError


class CandlestickPricesItem(AdaptiveGraphObject):
    """
    A class representing a candlestick plot item for displaying prices.

    Attributes:
        data (PricesDataFrame): The data containing the prices.
        style (Style, optional): The style of the candlestick plot item. Defaults to DEFAULT_STYLE.
        value_key (str, optional): The key representing the value to be used for plotting. Defaults to "close".
    """

    def __init__(self, data: PricesDataFrame, style=DEFAULT_STYLE):
        """
        Initializes a CandlestickPricesItem object.

        Args:
            data (PricesDataFrame): The data containing the prices.
            style (Style, optional): The style of the candlestick plot item. Defaults to DEFAULT_STYLE.
        """
        super().__init__()
        self.data = data
        self.style = style
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        w = style.bar_width
        for t, open_price, close_price, high_price, low_price in self.data:
            if close_price > open_price:
                p.setBrush(pg.mkBrush(self.style.positive_color))
                p.setPen(pg.mkPen(self.style.positive_color))
                p.drawRect(QtCore.QRectF(t - w, open_price, w * 2, close_price - open_price))
            else:
                p.setBrush(pg.mkBrush(self.style.negative_color))
                p.setPen(pg.mkPen(self.style.negative_color))
                p.drawRect(QtCore.QRectF(t - w, close_price, w * 2, open_price - close_price))
            p.drawRect(QtCore.QRectF(t - style.shadow_width / 2, low_price, style.shadow_width, high_price - low_price))
        p.end()

    def paint(self, p, *args):
        """
        Paints the candlestick plot item.

        Args:
            p (QPainter): The painter object used for painting.
            *args: Additional arguments.
        """
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        """
        Returns the bounding rectangle of the candlestick plot item.

        Returns:
            QRectF: The bounding rectangle.
        """
        return QtCore.QRectF(self.picture.boundingRect())

    def get_local_plot_range(self, x_start, x_end):
        """
        Returns the local plot range based on the given x-axis start and end values.

        Args:
            x_start (float): The start value of the x-axis.
            x_end (float): The end value of the x-axis.

        Returns:
            PricesDataFrame: The local plot range.
        """
        return self.data.get_local_range(x_start, x_end)

    def get_x_ticks(self):
        """
        Returns the x-axis ticks.

        Returns:
            list: The x-axis ticks.
        """
        return self.data.get_x_ticks()

    def get_feature_value(self, key="close"):
        """
        Returns the feature values based on the given key.

        Args:
            key (str, optional): The key representing the feature value. Defaults to "close".

        Returns:
            ndarray: The feature values.

        Raises:
            ValueError: If the key is not one of 'open', 'close', 'high', 'low'.
        """
        available_keys = ["open", "close", "high", "low"]
        if key not in available_keys:
            raise ValueError("value_key must be one of 'open','close','high','low'")
        index = available_keys.index(key) + 1
        return np.asarray([data[index] for data in self.data])


class CandlestickVolumeItem(AdaptiveGraphObject):
    """
    A class representing a candlestick volume item for plotting.

    Attributes:
        data (VolumeDataFrame): The volume data to be plotted. Must have fields: time, open, close, min, max.
        style (Style, optional): The style configuration for the plot item. Defaults to DEFAULT_STYLE.
    """

    def __init__(self, data: VolumeDataFrame, style=DEFAULT_STYLE):
        super().__init__()
        self.data = data
        self.style = style
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setBrush(pg.mkBrush(self.style.volume_color))
        p.setPen(pg.mkPen(self.style.volume_color))
        w = style.bar_width
        for t, volume in self.data:
            p.drawRect(QtCore.QRectF(t - w, 0, w * 2, volume / 1e8))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

    def get_local_plot_range(self, x_start, x_end):
        """
        Get the local plot range for the volume item.

        Args:
            x_start (float): The starting x-coordinate of the plot range.
            x_end (float): The ending x-coordinate of the plot range.

        Returns:
            tuple: A tuple containing the minimum and maximum volume values within the plot range.
        """
        min_v, max_v = self.data.get_local_range(x_start, x_end)
        return 0, max_v / 1e8

    def get_x_ticks(self):
        """
        Get the x-axis ticks for the volume item.

        Returns:
            list: A list of x-axis tick values.
        """
        return self.data.get_x_ticks()

    def get_feature_value(self, key=None):
        """
        Get the feature values for the volume item.

        Returns:
            numpy.ndarray: An array of feature values.
        """
        return np.asarray([data[1] / 1e8 for data in self.data])


def draw_circle_marker(p, canvas_pt, marker_size):
    """
    Draws a circle marker at the specified canvas point.

    Args:
        p (QPainter): The painter object used for drawing.
        canvas_pt (QPointF): The point where the marker should be drawn.
        marker_size (float): The size of the marker.
    """
    p.drawEllipse(canvas_pt, marker_size, marker_size)


class LinePlotItem(AdaptiveGraphObject):
    """
    A class representing a line plot item for displaying data.

    Attributes:
        data (ChildDataFrame): The data containing the values to be plotted.
        style (Style, optional): The style of the line plot item. Defaults to DEFAULT_STYLE.
    """

    MARKER_DRAWER = {"circle": draw_circle_marker, "o": draw_circle_marker}

    def __init__(self, data: ChildDataFrame, style=LINE_DEFAULT_STYLE, marker=None):
        super().__init__()
        self.data = data
        self.style = style
        self.marker_drawer = self.MARKER_DRAWER.get(marker, None)
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen(self.style.line_color, width=self.style.line_width))
        x = data.data_frame.index.to_numpy()
        for data_key in data.data_keys:
            if data_key not in data.data_frame.columns:
                raise ValueError(f"Data key '{data_key}' not found in data frame.")
            y = data.data_frame[data_key].to_numpy()
            p.drawPolyline(QtGui.QPolygonF([QtCore.QPointF(x[i], y[i]) for i in range(len(x))]))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
        if self.marker_drawer is not None:
            transform = p.transform()
            # Set marker color
            p.setPen(pg.mkPen(self.style.marker_color, width=self.style.line_width))
            p.setBrush(pg.mkBrush(self.style.marker_color))
            marker_size = self.style.marker_size / 2
            x = self.data.data_frame.index.to_numpy()
            # Reset transformation to canvas transform, so marker is unaffected by data scaling.
            p.resetTransform()
            for data_key in self.data.data_keys:
                if data_key not in self.data.data_frame.columns:
                    continue
                y = self.data.data_frame[data_key].to_numpy()
                for i in range(len(x)):
                    # Map data point to canvas coordinate.
                    data_pt = QtCore.QPointF(x[i], y[i])
                    canvas_pt = transform.map(data_pt)
                    self.marker_drawer(p, canvas_pt, marker_size)
            # Restore the original transformation
            p.setTransform(transform)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

    def get_local_plot_range(self, x_start, x_end):
        return self.data.get_local_range(x_start, x_end)

    def get_x_ticks(self):
        return self.data.get_x_ticks()

    def get_feature_value(self, key=None):
        return self.data.get_feature_value(key)
