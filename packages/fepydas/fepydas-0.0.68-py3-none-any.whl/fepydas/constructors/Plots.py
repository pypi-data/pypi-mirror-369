#!/usr/bin/python3
import numpy
from pylab import *
from matplotlib.colors import *
from fepydas.datatypes.Data import Data, Data1D, Data2D, Data3D
from fepydas.datatypes.Dataset import Spectrum, SpectrumWithIRF, SpectrumSeries, Map
from fepydas.workers.Fit import Fit


class BasePlot:
    """
    A base class for creating plots.
    """

    def __init__(self, polar=False):
        """
        Initializes a BasePlot instance.

        Args:
            polar (bool, optional): If True, creates a polar plot. Defaults to False.

        Returns:
            None
        """
        self.figure = figure()
        self.bottom = self.figure.add_subplot(111, polar=polar)

    def legend(self):
        """
        Displays the legend for the plot.

        Returns:
            None
        """
        self.bottom.legend()

    def show(self):
        """
        Displays the plot.

        Returns:
            None
        """
        show()

    def save(self, filename, **kwargs):
        """
        Saves the plot to a file.

        Args:
            filename (str): The path to the file where the plot will be saved.
            **kwargs: Additional keyword arguments passed to `matplotlib.figure.Figure.savefig()`.

        Returns:
            None
        """
        self.figure.savefig(filename, **kwargs)

    def setXAxis(self, axis: Data1D):
        """
        Sets the x-axis label and unit.

        Args:
            axis (Data1D): The axis data to set.

        Returns:
            None
        """
        self.bottom.set_xlabel(
            "{0} ({1})".format(axis.datatype.name, axis.datatype.unit)
        )

    def setXRange(self, xmin, xmax):
        """
        Sets the range for the x-axis.

        Args:
            xmin (float): The minimum value for the x-axis.
            xmax (float): The maximum value for the x-axis.

        Returns:
            None
        """
        self.bottom.set_xlim(xmin, xmax)

    def setYRange(self, ymin, ymax):
        """
        Sets the range for the y-axis.

        Args:
            ymin (float): The minimum value for the y-axis.
            ymax (float): The maximum value for the y-axis.

        Returns:
            None
        """
        self.bottom.set_ylim(ymin, ymax)

    def setXLog(self):
        """
        Sets the x-axis to a logarithmic scale.

        Returns:
            None
        """
        self.bottom.set_xscale("log")

    def setYLog(self):
        """
        Sets the y-axis to a logarithmic scale.

        Returns:
            None
        """
        self.bottom.set_yscale("log")

    def setYAxis(self, data: Data):
        """
        Sets the y-axis label and unit.

        Args:
            data (Data): The data to set for the y-axis.

        Returns:
            None
        """
        self.bottom.set_ylabel(
            "{0} ({1})".format(data.datatype.name, data.datatype.unit)
        )


class Plot1D(BasePlot):
    """
    A class for creating 1D plots.
    """

    def __init__(self, axis: Data1D, polar=False):
        """
        Initializes a Plot1D instance.

        Args:
            axis (Data1D): The axis data for the plot.
            polar (bool, optional): If True, creates a polar plot. Defaults to False.

        Returns:
            None
        """
        super().__init__(polar=polar)
        if polar:
            axis.values = axis.values / 360 * 2 * numpy.pi
        self.setXAxis(axis)

    def plotLine(self, x, y, label=None, linewidth=2, color=None):
        """
        Plots a line on the graph.

        Args:
            x (numpy.ndarray): The x data values.
            y (numpy.ndarray): The y data values.
            label (str, optional): The label for the line. Defaults to None.
            linewidth (int, optional): The width of the line. Defaults to 2.
            color (str, optional): The color of the line. Defaults to None.

        Returns:
            None
        """
        self.bottom.plot(x, y, label=label, linewidth=linewidth, color=color)

    def plotPoints(self, x, y, xerr=None, yerr=None, label=None, color=None):
        """
        Plots points on the graph with error bars.

        Args:
            x (numpy.ndarray): The x data values.
            y (numpy.ndarray): The y data values.
            xerr (numpy.ndarray, optional): The error in the x data. Defaults to None.
            yerr (numpy.ndarray, optional): The error in the y data. Defaults to None.
            label (str, optional): The label for the points. Defaults to None.
            color (str, optional): The color of the points. Defaults to None.

        Returns:
            None
        """
        self.bottom.errorbar(
            x,
            y,
            xerr=xerr,
            yerr=yerr,
            label=label,
            fmt="o",
            alpha=0.2,
            color=color,
            zorder=1,
        )


class Plot1DSingleAxis(Plot1D):
    """
    A class for creating single-axis 1D plots.
    """

    def __init__(self, axis: Data1D, polar=False):
        """
        Initializes a Plot1DSingleAxis instance.

        Args:
            axis (Data1D): The axis data for the plot.
            polar (bool, optional): If True, creates a polar plot. Defaults to False.

        Returns:
            None
        """
        super().__init__(axis, polar=polar)
        self.axis = axis

    def addLine(self, data: ndarray, label=None, linewidth=2, color=None):
        """
        Adds a line to the plot.

        Args:
            data (ndarray): The data values for the line.
            label (str, optional): The label for the line. Defaults to None.
            linewidth (int, optional): The width of the line. Defaults to 2.
            color (str, optional): The color of the line. Defaults to None.

        Returns:
            None
        """
        self.plotLine(
            self.axis.values[0 : len(data)],
            data,
            label=label,
            linewidth=linewidth,
            color=color,
        )

    def addPoints(self, data: ndarray, errors=None, label=None, color=None):
        """
        Adds points to the plot.

        Args:
            data (ndarray): The data values for the points.
            errors (ndarray, optional): The error values for the points. Defaults to None.
            label (str, optional): The label for the points. Defaults to None.
            color (str, optional): The color of the points. Defaults to None.

        Returns:
            None
        """
        self.plotPoints(
            self.axis.values, data, self.axis.errors, errors, label=label, color=color
        )

    def addLines(self, data, labels):
        """
        Adds multiple lines to the plot.

        Args:
            data (ndarray): The data values for the lines.
            labels (list of str): The labels for the lines.

        Returns:
            None
        """
        for i in range(data.shape[0]):
            self.plotLine(self.axis.values, data[i], label=labels[i])


class Plot1DMultiAxis(Plot1D):
    """
    A class for creating multi-axis 1D plots.
    """

    def __init__(self, axis: Data1D, data: Data1D):
        """
        Initializes a Plot1DMultiAxis instance.

        Args:
            axis (Data1D): The axis data for the plot.
            data (Data1D): The data for the y-axis.

        Returns:
            None
        """
        super().__init__(axis)
        self.setYAxis(data)

    def addLine(self, axis: Data1D, data: Data1D, label=None):
        """
        Adds a line to the plot using specified axis data.

        Args:
            axis (Data1D): The axis data for the line.
            data (Data1D): The data values for the line.
            label (str, optional): The label for the line. Defaults to None.

        Returns:
            None
        """
        # TODO: Compare Units
        self.plotLine(axis.values, data.values, label=label)

    def addPoints(self, axis: Data1D, data: Data1D, label=None):
        """
        Adds points to the plot using specified axis data.

        Args:
            axis (Data1D): The axis data for the points.
            data (Data1D): The data values for the points.
            label (str, optional): The label for the points. Defaults to None.

        Returns:
            None
        """
        # TODO: Compare Units
        self.plotPoints(axis.values, data.values, label=label)


class MultiSpectrumScatterPlot(Plot1DMultiAxis):
    """
    A class for creating scatter plots of multiple spectra.
    """

    def __init__(self, spectra, labels):
        """
        Initializes a MultiSpectrumScatterPlot instance.

        Args:
            spectra: The spectra data for the plot.
            labels: The labels for the spectra.

        Returns:
            None
        """
        super().__init__(spectra[0].axis, spectra[0].data)
        for i, spectrum in enumerate(spectra):
            self.addPoints(spectrum.axis, spectrum.data, labels[i])


class Plot1DSingleLine(Plot1DSingleAxis):
    """
    A class for creating a single line plot.
    """

    def __init__(self, axis: Data1D, data: Data1D, label=None):
        """
        Initializes a Plot1DSingleLine instance.

        Args:
            axis (Data1D): The axis data for the plot.
            data (Data1D): The data for the line.
            label (str, optional): The label for the line. Defaults to None.

        Returns:
            None
        """
        super().__init__(axis)
        self.setYAxis(data)
        self.addLine(data.values, label=label)


class Plot1DSingleScatter(Plot1DSingleAxis):
    """
    A class for creating a single scatter plot.
    """

    def __init__(self, axis: Data1D, data: Data1D):
        """
        Initializes a Plot1DSingleScatter instance.

        Args:
            axis (Data1D): The axis data for the plot.
            data (Data1D): The data for the scatter points.

        Returns:
            None
        """
        super().__init__(axis)
        self.setYAxis(data)
        self.addPoints(data.values, data.errors)


class Plot1DMultiLineSingleAxis(Plot1DSingleAxis):
    """
    A class for creating multi-line plots on a single axis.
    """

    def __init__(
        self,
        axis: Data1D,
        keys: Data1D,
        data: Data2D,
        polar=False,
        cmap=None,
        norm=None,
    ):
        """
        Initializes a Plot1DMultiLineSingleAxis instance.

        Args:
            axis (Data1D): The axis data for the plot.
            keys (Data1D): The keys for the data series.
            data (Data2D): The data for the lines.
            polar (bool, optional): If True, creates a polar plot. Defaults to False.
            cmap (Colormap, optional): The colormap to use. Defaults to None.
            norm (Normalize, optional): The normalization to use. Defaults to None.

        Returns:
            None
        """
        super().__init__(axis, polar=polar)
        self.setYAxis(data)
        for i, key in enumerate(keys.values):
            if cmap and norm:
                self.addLine(data.values[i], key, color=cmap(norm(float(key))))
            else:
                self.addLine(data.values[i], key)


class Plot1DMultiScatterSingleAxis(Plot1DSingleAxis):
    """
    A class for creating multi-scatter plots on a single axis.
    """

    def __init__(
        self,
        axis: Data1D,
        keys: Data1D,
        data: Data2D,
        polar=False,
        cmap=None,
        norm=None,
    ):
        """
        Initializes a Plot1DMultiScatterSingleAxis instance.

        Args:
            axis (Data1D): The axis data for the plot.
            keys (Data1D): The keys for the data series.
            data (Data2D): The data for the scatter points.
            polar (bool, optional): If True, creates a polar plot. Defaults to False.
            cmap (Colormap, optional): The colormap to use. Defaults to None.
            norm (Normalize, optional): The normalization to use. Defaults to None.

        Returns:
            None
        """
        super().__init__(axis, polar=polar)
        self.setYAxis(data)
        for i, key in enumerate(keys.values):
            if cmap and norm:
                self.addPoints(data.values[i], key, color=cmap(norm(float(key))))
            else:
                self.addPoints(data.values[i], key)


class SpectrumPlot(Plot1DSingleLine):
    """
    A class for plotting a spectrum as a single line.
    """

    def __init__(self, spectrum: Spectrum, label=None):
        """
        Initializes a SpectrumPlot instance.

        Args:
            spectrum (Spectrum): The spectrum data for the plot.
            label (str, optional): The label for the plot. Defaults to None.

        Returns:
            None
        """
        super().__init__(spectrum.axis, spectrum.data, label=label)

    def addSpectrum(self, spectrum, label=None):
        """
        Adds a spectrum to the plot.

        Args:
            spectrum (Spectrum): The spectrum to add.
            label (str, optional): The label for the spectrum. Defaults to None.

        Returns:
            None
        """
        self.addLine(spectrum.data.values, label=label)


class HistoPlot(Plot1D):
    """
    A class for creating histogram plots.
    """

    def __init__(self, spectrum: Spectrum, label=None, n=100, bins=None):
        """
        Initializes a HistoPlot instance.

        Args:
            spectrum (Spectrum): The spectrum data for the histogram.
            label (str, optional): The label for the histogram. Defaults to None.
            n (int, optional): The number of bins. Defaults to 100.
            bins (array-like, optional): The bin edges. Defaults to None.

        Returns:
            None
        """
        super().__init__(spectrum.data)  # In a histogram, the data values form the axis
        if bins is not None:
            n, bins, patches = hist(spectrum.data.values.flatten(), bins=bins)
        else:
            n, bins, patches = hist(spectrum.data.values.flatten(), n)
        self.data = n


class SpectrumScatterPlot(Plot1DSingleScatter):
    """
    A class for creating scatter plots of a spectrum.
    """

    def __init__(self, spectrum: Spectrum):
        """
        Initializes a SpectrumScatterPlot instance.

        Args:
            spectrum (Spectrum): The spectrum data for the scatter plot.

        Returns:
            None
        """
        super().__init__(spectrum.axis, spectrum.data)


class SpectrumScatterPlotWithFit(SpectrumScatterPlot):
    """
    A class for creating scatter plots of a spectrum with a fit line.
    """

    def __init__(self, spectrum: Spectrum, fit: Fit):
        """
        Initializes a SpectrumScatterPlotWithFit instance.

        Args:
            spectrum (Spectrum): The spectrum data for the scatter plot.
            fit (Fit): The fit object to overlay on the plot.

        Returns:
            None
        """
        super().__init__(spectrum)
        self.addLine(fit.evaluate(spectrum.axis.values))


class SpectrumWithIRFPlot(Plot1DSingleScatter):
    """
    A class for creating scatter plots of a spectrum with an IRF.
    """

    def __init__(self, spectrum: SpectrumWithIRF):
        """
        Initializes a SpectrumWithIRFPlot instance.

        Args:
            spectrum (SpectrumWithIRF): The spectrum data with IRF for the scatter plot.

        Returns:
            None
        """
        super().__init__(spectrum.axis, spectrum.data)
        self.addLine(spectrum.getExtendedIRF())


class SpectrumSeriesPlot(Plot1DMultiLineSingleAxis):
    """
    A class for plotting a series of spectra.
    """

    def __init__(self, spectra: SpectrumSeries, polar=False, cmap=None, norm=None):
        """
        Initializes a SpectrumSeriesPlot instance.

        Args:
            spectra (SpectrumSeries): The series of spectra to plot.
            polar (bool, optional): If True, creates a polar plot. Defaults to False.
            cmap (Colormap, optional): The colormap to use. Defaults to None.
            norm (Normalize, optional): The normalization to use. Defaults to None.

        Returns:
            None
        """
        if (cmap and not norm) or norm == "Default":
            # The default norm is [min,max] -> [0,1]
            norm = Normalize(
                vmin=numpy.amin(spectra.keys.values),
                vmax=numpy.amax(spectra.keys.values),
            )
        if norm and not cmap:
            # The default cmap
            cmap = LinearSegmentedColormap.from_list(
                "my_colormap", ["black", "red", "green", "blue", "white"], 1000
            )
        super().__init__(
            spectra.axis, spectra.keys, spectra.data, polar=polar, cmap=cmap, norm=norm
        )


class SpectrumSeriesScatterPlot(Plot1DMultiScatterSingleAxis):
    """
    A class for creating scatter plots of a series of spectra.
    """

    def __init__(self, spectra: SpectrumSeries, polar=False, cmap=None, norm=None):
        """
        Initializes a SpectrumSeriesScatterPlot instance.

        Args:
            spectra (SpectrumSeries): The series of spectra to plot.
            polar (bool, optional): If True, creates a polar plot. Defaults to False.
            cmap (Colormap, optional): The colormap to use. Defaults to None.
            norm (Normalize, optional): The normalization to use. Defaults to None.

        Returns:
            None
        """
        if (cmap and not norm) or norm == "Default":
            # The default norm is [min,max] -> [0,1]
            norm = Normalize(
                vmin=numpy.amin(spectra.keys.values),
                vmax=numpy.amax(spectra.keys.values),
            )
        if norm and not cmap:
            # The default cmap
            cmap = LinearSegmentedColormap.from_list(
                "my_colormap", ["black", "red", "green", "blue", "white"], 1000
            )
        super().__init__(
            spectra.axis, spectra.keys, spectra.data, polar=polar, cmap=cmap, norm=norm
        )


class Plot2D(BasePlot):
    """
    A class for creating 2D plots.
    """

    def __init__(self, axis, keys):
        """
        Initializes a Plot2D instance.

        Args:
            axis: The axis data for the plot.
            keys: The keys for the data.

        Returns:
            None
        """
        super().__init__()
        self.setXAxis(axis)
        self.setYAxis(keys)

    def setZAxis(self, data: Data):
        """
        Sets the z-axis label and unit.

        Args:
            data (Data): The data to set for the z-axis.

        Returns:
            None
        """
        self.colorbar.set_label(
            "{0} ({1})".format(data.datatype.name, data.datatype.unit)
        )
        self.colorbar.minorticks_on()


class ContourPlot(Plot2D):
    """
    A class for creating contour plots.
    """

    def __init__(self, spectra: SpectrumSeries, log=False):
        """
        Initializes a ContourPlot instance.

        Args:
            spectra (SpectrumSeries): The spectra data for the contour plot.
            log (bool, optional): If True, uses a logarithmic scale for the plot. Defaults to False.

        Returns:
            None
        """
        super().__init__(spectra.axis, spectra.keys)
        cmap = LinearSegmentedColormap.from_list(
            "my_colormap", ["black", "red", "green", "blue", "white"], 1000
        )
        extent = [
            spectra.axis.values[0],
            spectra.axis.values[-1],
            spectra.keys.values[0],
            spectra.keys.values[-1],
        ]
        if log:
            values = numpy.log10(spectra.data.values + 0.001)
        else:
            values = spectra.data.values
        image = imshow(
            values,
            interpolation="none",
            cmap=cmap,
            origin="lower",
            aspect="auto",
            extent=extent,
        )


class ContourMapPlot(Plot2D):
    """
    A class for creating contour map plots.
    """

    def __init__(
        self,
        map: Map,
        log=False,
        colors=["black", "red", "orange", "yellow", "green", "blue", "white"],
        zRange=None,
    ):
        """
        Initializes a ContourMapPlot instance.

        Args:
            map (Map): The map data for the contour plot.
            log (bool, optional): If True, uses a logarithmic scale for the plot. Defaults to False.
            colors (list of str, optional): The colors to use for the contour plot. Defaults to a predefined list.
            zRange (tuple, optional): The range for the z-axis. Defaults to None.

        Returns:
            None
        """

        x, y = map.mapping.extractAxes()
        super().__init__(x, y)
        cmap = LinearSegmentedColormap.from_list("my_colormap", colors, 1000)
        cmap.set_over("white")
        cmap.set_under("black")
        cmap.set_bad("violet")
        extent = [x.values[0], x.values[-1], y.values[0], y.values[-1]]
        if log:
            values = numpy.log10(map.data.values.T + 0.001)
        else:
            values = map.data.values.T
        if zRange:
            zmin = zRange[0]
            zmax = zRange[1]
        else:
            zmin = None
            zmax = None
        image = imshow(
            values,
            interpolation="none",
            cmap=cmap,
            origin="lower",
            aspect="auto",
            extent=extent,
            vmin=zmin,
            vmax=zmax,
        )
        self.colorbar = self.figure.colorbar(
            image, cmap=cmap
        )  # ,  ticks=range(len(colors)))
        self.setZAxis(map.data)
