#!/usr/bin/python3
import numpy


class BaseWriter:
    """
    A base class for writing data to a binary file.
    """

    def __init__(self, filename):
        """
        Initializes a BaseWriter instance.

        Args:
            filename (str): The path to the file where data will be written.

        Returns:
            None
        """
        self.f = open(filename, "wb")


class MultiSpectrumWriter(BaseWriter):
    """
    A class for writing multiple spectra to a binary file.
    """

    def __init__(self, filename):
        """
        Initializes a MultiSpectrumWriter instance.

        Args:
            filename (str): The path to the file where multiple spectra will be written.

        Returns:
            None
        """
        super().__init__(filename)
        self.data = []
        self.names = []
        self.units = []
        self.identifiers = []

    def addX(self, data, identifier):
        """
        Adds x-axis data to the spectrum writer.

        Args:
            data (Data): The data object containing x-axis values.
            identifier (str): The identifier for the x-axis data.

        Returns:
            None
        """
        self.data.append(data.values)
        self.names.append(data.datatype.name)
        self.units.append(str(data.datatype.unit))
        self.identifiers.append(identifier)
        if data.errors is not None:
            self.data.append(data.errors)
            self.names.append(data.datatype.name)
            self.units.append(str(data.datatype.unit))
            self.identifiers.append(identifier + "_Error")

    def addY(self, data, identifier):
        """
        Adds y-axis data to the spectrum writer.

        Args:
            data (Data): The data object containing y-axis values.
            identifier (str): The identifier for the y-axis data.

        Returns:
            None
        """
        if len(data.values) < len(self.data[0]):
            vals = numpy.zeros(self.data[0].shape)
            vals[0 : len(data.values)] = data.values
        else:
            vals = data.values
        self.data.append(vals)
        self.names.append(data.datatype.name)
        self.units.append(str(data.datatype.unit))
        self.identifiers.append(identifier)
        if data.errors is not None:
            self.data.append(data.errors)
            self.names.append(data.datatype.name)
            self.units.append(str(data.datatype.unit))
            self.identifiers.append(identifier + "_Error")

    def addMultiY(self, Ys, labels, commonlabel=""):
        """
        Adds multiple y-axis data sets to the spectrum writer.

        Args:
            Ys (list of Data): The list of data objects containing y-axis values.
            labels (list of str): The labels for each y-axis data set.
            commonlabel (str, optional): A common label to append to each identifier. Defaults to "".

        Returns:
            None
        """
        for i, Y in enumerate(Ys):
            self.data.append(Y)
            self.identifiers.append("{0}".format(labels[i]) + commonlabel)

    def addSpectrum(self, spectrum, identifier="Y"):
        """
        Adds a spectrum to the writer.

        Args:
            spectrum (Spectrum): The spectrum object to add.
            identifier (str, optional): The identifier for the spectrum. Defaults to "Y".

        Returns:
            None
        """
        self.addX(spectrum.axis, "X")
        self.addY(spectrum.data, identifier)

    def addSpectra(self, spectra):
        """
        Adds multiple spectra to the writer.

        Args:
            spectra (SpectrumSeries): The series of spectra to add.

        Returns:
            None
        """
        self.addX(spectra.axis, "X")
        self.addMultiY(spectra.data.values, spectra.keys.values)

    def addFit(self, spectrum, fit, convolve=False):
        """
        Adds a fit to the spectrum writer.

        Args:
            spectrum (Spectrum): The spectrum object to which the fit is applied.
            fit (Fit): The fit object to add.
            convolve (bool, optional): If True, convolves the fit with the spectrum. Defaults to False.

        Returns:
            None
        """
        if convolve:
            y = spectrum.evaluateConvolutionFit(fit)
        else:
            y = fit.evaluate(self.data[0])
        self.addY(y, fit.__class__.__name__)

    def addFits(self, fit):
        """
        Adds multiple fits to the spectrum writer.

        Args:
            fit (Fit): The fit object containing multiple fits to add.

        Returns:
            None
        """
        self.addMultiY(
            fit.batchEvaluate(self.data[0]), self.headers[1:], fit.__class__.__name__
        )

    def write(self, fmt="%4f"):
        """
        Writes the collected data to the binary file.

        Args:
            fmt (str, optional): The format for the data values. Defaults to "%4f".

        Returns:
            None
        """
        data = numpy.array(self.data).T
        self.f.write(("\t".join(self.identifiers) + "\n").encode("utf-8"))
        self.f.write(("\t".join(self.names) + "\n").encode("utf-8"))
        self.f.write(("\t".join(self.units) + "\n").encode("utf-8"))
        numpy.savetxt(self.f, data, fmt=fmt, delimiter="\t")
        self.f.close()


class SpectrumWithFitWriter(MultiSpectrumWriter):
    """
    A class for writing a spectrum along with its fit to a binary file.
    """

    def __init__(self, filename, spectrum, fit, withIRF=False):
        """
        Initializes a SpectrumWithFitWriter instance.

        Args:
            filename (str): The path to the file where the spectrum and fit will be written.
            spectrum (Spectrum): The spectrum object to write.
            fit (Fit): The fit object to write.
            withIRF (bool, optional): If True, includes the IRF in the output. Defaults to False.

        Returns:
            None
        """
        super().__init__(filename)
        self.addSpectrum(spectrum, identifier="Data")
        if withIRF:
            self.addY(spectrum.IRF, identifier="IRF")
        self.addFit(spectrum, fit, withIRF)
        self.write()
