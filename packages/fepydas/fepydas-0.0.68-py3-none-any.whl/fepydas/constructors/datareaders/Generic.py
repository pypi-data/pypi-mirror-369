#!/usr/bin/python3
import numpy
import pickle
from fepydas.datatypes.Data import Data1D, Data2D, DataType
import fepydas.datatypes as datatypes
from fepydas.datatypes.Dataset import (
    SpectraWithCommonIRF,
    Spectrum,
    SpectrumWithIRF,
    SpectrumSeries,
    PLE,
)
from fepydas.constructors.datareaders.Proprietary import (
    BeckerHicklHistogram,
    PicoHarpHistogram,
    TimeHarpHistogram,
)


def GenericXY(x, xname, xunit, y, yname, yunit):
    """
    Creates a Spectrum object from given x and y data.

    Args:
        x (numpy.ndarray): The x data values.
        xname (str): The name of the x data.
        xunit (str): The unit of the x data.
        y (numpy.ndarray): The y data values.
        yname (str): The name of the y data.
        yunit (str): The unit of the y data.

    Returns:
        Spectrum: A Spectrum object containing the x and y data.
    """
    return Spectrum(
        Data1D(x, datatypes.generateDataType(xname, xunit)), Data1D(x, datatypes.generateDataType(xname, xunit))
    )


def GenericXMultiY(x, xname, xunit, y, yname, yunit, keys, keyname, keyunit):
    """
    Creates a SpectrumSeries object from given x data and multiple y data sets.

    Args:
        x (numpy.ndarray): The x data values.
        xname (str): The name of the x data.
        xunit (str): The unit of the x data.
        y (numpy.ndarray): The y data values for multiple series.
        yname (str): The name of the y data.
        yunit (str): The unit of the y data.
        keys (numpy.ndarray): The keys for the y data series.
        keyname (str): The name of the keys.
        keyunit (str): The unit of the keys.

    Returns:
        SpectrumSeries: A SpectrumSeries object containing the x data and multiple y data sets.
    """
    return SpectrumSeries(
        Data1D(x, datatypes.generateDataType(xname, xunit)),
        Data1D(keys, datatypes.generateDataType(keyname, keyunit)),
        Data2D(y, datatypes.generateDataType(yname, yunit)),
    )


def ASCII(filename, delimiter="\t", missing_values="", skip_header=0):
    """
    Reads ASCII data from a file.

    Args:
        filename (str): The path to the ASCII file.
        delimiter (str, optional): The delimiter used in the file. Defaults to tab.
        missing_values (str, optional): The string representing missing values. Defaults to ''.
        skip_header (int, optional): The number of header lines to skip. Defaults to 0.

    Returns:
        numpy.ndarray: The data read from the ASCII file.
    """
    data = numpy.genfromtxt(
        filename,
        delimiter=delimiter,
        missing_values=missing_values,
        skip_header=skip_header,
        encoding="Latin-1",
    )
    print("ASCII File {0}. Shape:{1}".format(filename, data.shape))
    return data


def ASCII_SpectrumRowSeries(
    filename, xType: DataType, keyType: DataType, valueType: DataType
):
    """
    Reads a spectrum row series from an ASCII file.

    Args:
        filename (str): The path to the ASCII file.
        xType (DataType): The data type for the x-axis.
        keyType (DataType): The data type for the keys.
        valueType (DataType): The data type for the values.

    Returns:
        SpectrumSeries: The spectrum row series read from the file.
    """
    data = ASCII(filename)
    xAxis = Data1D(data[0, :], xType)
    keyAxis = Data1D(numpy.arange(len(data[:, 0]) - 1), keyType)
    vals = Data2D(data[1:, :], valueType)
    return SpectrumSeries(xAxis, keyAxis, vals)


def ASCII_Histogram(filename, resolution):
    """
    Reads histogram data from an ASCII file.

    Args:
        filename (str): The path to the ASCII file.
        resolution (float): The resolution for the histogram.

    Returns:
        Spectrum: The histogram spectrum.
    """
    data = ASCII(filename, delimiter=" ", skip_header=10)
    xAxis = Data1D(numpy.arange(len(data)) * resolution, datatypes.TIME_ns)
    yAxis = Data1D(data, datatypes.COUNTS)
    return Spectrum(xAxis, yAxis)


def Binary(filename):
    """
    Reads binary data from a file.

    Args:
        filename (str): The path to the binary file.

    Returns:
        object: The data read from the binary file.
    """
    return pickle.load(open(filename, "rb"))


def HistogramReader(filename):
    """
    Reads histogram data from a specified file based on its type.

    Args:
        filename (str): The path to the histogram file.

    Returns:
        tuple: A tuple containing the time axis and histogram data as Data1D objects.
    """
    print("Reading {0}".format(filename))
    filetype = filename[-3:]
    if filetype == "phu":
        time, data = PicoHarpHistogram(filename)
    elif filetype == "thi":
        time, data = TimeHarpHistogram(filename)
    elif filetype == "sdt":
        time, data = BeckerHicklHistogram(filename)
    else:
        print("Unsupported Histogram Type: .{0}".format(filetype))
    axis = Data1D(time, datatypes.TIME_ns)
    data = Data1D(data, datatypes.COUNTS)
    return axis, data


def Histogram(filename):
    """
    Reads a histogram and returns it as a Spectrum object.

    Args:
        filename (str): The path to the histogram file.

    Returns:
        Spectrum: The histogram as a Spectrum object.
    """
    axis, data = HistogramReader(filename)
    return Spectrum(axis, data)


def HistogramWithIRF(filename, filenameIRF):
    """
    Reads histogram data along with its Instrument Response Function (IRF).

    Args:
        filename (str): The path to the histogram file.
        filenameIRF (str): The path to the IRF file.

    Returns:
        SpectrumWithIRF: The histogram data with its IRF.
    """

    histoTime, histoData = HistogramReader(filename)
    IRFTime, IRFData = HistogramReader(filenameIRF)
    if numpy.sum(histoTime.values - IRFTime.values) > 0:
        print("Warning, IRF and Decay Histogram Time Axes not compatible!!")
    return SpectrumWithIRF(histoTime, histoData, IRFData)


def HistogramsWithCommonIRF(filenames, filenameIRF):
    """
    Reads multiple histograms and aligns them with a common IRF.

    Args:
        filenames (list of str): A list of paths to the histogram files.
        filenameIRF (str): The path to the IRF file.

    Returns:
        SpectraWithCommonIRF: The histograms aligned with the common IRF.
    """
    IRFTime, IRFData = HistogramReader(filenameIRF)
    data = numpy.ndarray(shape=(len(filenames), len(IRFTime.values)))
    for i, n in enumerate(filenames):
        histoTime, histoData = HistogramReader(n)
        if numpy.sum(histoTime.values - IRFTime.values) > 0:
            print(
                "Warning, IRF and Decay Histogram Time Axes not compatible for {0}!!".format(
                    n
                )
            )
        data[i, :] = histoData.values
        filenames[i] = filenames[i].split("/")[-1]
    CombinedData = Data2D(data, IRFData.datatype)
    return SpectraWithCommonIRF(
        IRFTime, CombinedData, IRFData, Data1D(filenames, DataType("Filename", ""))
    )
