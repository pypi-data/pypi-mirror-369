#!/usr/bin/python3
import numpy
import os
from fepydas.datatypes.Data import Data1D, Data2D, Data3D, Response
from fepydas.datatypes.Dataset import Spectrum, SpectrumSeries, PLE, SpectrumMap
import fepydas.datatypes as datatypes
from fepydas.constructors.datareaders.Generic import ASCII, ASCII_SpectrumRowSeries


def ASCII_RamanSeries(folder):
    """
    Reads Raman spectra from ASCII files in the specified folder.

    Args:
        folder (str): The path to the folder containing the .txt files.

    Returns:
        SpectrumSeries: A series of Raman spectra.
    """
    files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    num = len(files)
    ref = ASCII(os.path.join(folder, files[0])).T

    shape = (num, ref.shape[1])
    xAxis = Data1D(ref[0, :], datatypes.RS_cm)
    vals = numpy.ndarray(shape=shape)
    for i, file in enumerate(sorted(files)):
        spec = ASCII(os.path.join(folder, file)).T
        vals[i, :] = spec[1, :]

    values = Data2D(vals, datatypes.COUNTS)
    keys = Data1D(numpy.arange(num), datatypes.ANGLE_au)
    return SpectrumSeries(xAxis, keys, values)

    # data = ASCII(filename).T
    # ramanType = DataType("Raman Shift", "cm-1")
    # countType = DataType("Counts","#")
    # xAxis = Data1D


def ASCII_Spectrum(filename):
    """
    Reads a spectrum from an ASCII file.

    Args:
        filename (str): The path to the ASCII file.

    Returns:
        Spectrum: The spectrum read from the file.
    """
    data = ASCII(filename, skip_header=1).T
    xAxis = Data1D(data[0, :], datatypes.WL_nm)
    yAxis = Data1D(data[2, :], datatypes.COUNTS)
    return Spectrum(xAxis, yAxis)


def ASCII_TimeSeries(filename):
    """
    Reads a time series spectrum from an ASCII file.

    Args:
        filename (str): The path to the ASCII file.

    Returns:
        SpectrumSeries: The time series spectrum.
    """
    data = ASCII(filename).T
    xAxis = Data1D(data[0, 1:], datatypes.WL_nm)
    vals = Data2D(data[1:, 1:], datatypes.COUNTS)
    keys = Data1D(data[1:, 0], datatypes.TIME_s)
    return SpectrumSeries(xAxis, keys, vals)


def ASCII_Gelbes(filename):
    """
    Reads a spectrum from a specific ASCII file format (Gelbes).

    Args:
        filename (str): The path to the ASCII file.

    Returns:
        Spectrum: The spectrum read from the file.
    """
    data = ASCII(filename, skip_header=3).T
    xAxis = Data1D(data[0, :], datatypes.WL_nm)
    vals = Data1D(data[1, :], datatypes.COUNTS)
    return Spectrum(xAxis, vals)


def ASCII_TempSeries_Gelbes(filename):
    """
    Reads a temperature series spectrum from a specific ASCII file format (Gelbes).

    Args:
        filename (str): The path to the ASCII file.

    Returns:
        SpectrumSeries: The temperature series spectrum.
    """
    data = ASCII(filename, skip_header=3).T
    xAxis = Data1D(data[0, 1:], datatypes.WL_nm)
    vals = Data2D(data[1:, 1:], datatypes.COUNTS)
    keys = Data1D(data[1:, 0], datatypes.TEMP_K)
    return SpectrumSeries(xAxis, keys, vals)


def ASCII_TimeSeries_Gelbes(filename):
    """
    Reads a time series spectrum from a specific ASCII file format (Gelbes).

    Args:
        filename (str): The path to the ASCII file.

    Returns:
        SpectrumSeries: The time series spectrum.
    """
    data = ASCII(filename, skip_header=3).T
    xAxis = Data1D(data[0, :], datatypes.WL_nm)
    vals = Data2D(data[1:, :], datatypes.COUNTS)
    keys = Data1D(numpy.arange(vals.values.shape[0]), datatypes.TIME_s)
    return SpectrumSeries(xAxis, keys, vals)


def ASCII_SSTRPL(filename):
    """
    Reads a spectrum row series from an ASCII file.

    Args:
        filename (str): The path to the ASCII file.

    Returns:
        SpectrumSeries: The spectrum row series.
    """
    return ASCII_SpectrumRowSeries(
        filename, datatypes.TIME_ps, datatypes.NUMBER, datatypes.COUNTS
    )


def ASCII_EQE(filename):
    """
    Reads EQE data from an ASCII file.

    Args:
        filename (str): The path to the ASCII file.

    Returns:
        SpectrumSeries: The EQE data.
    """
    data = ASCII(filename)
    xAxis = Data1D(data[0, 3:], datatypes.WL_nm)
    keyAxis = Data1D(data[2:, 1] - data[1, 1], datatypes.I_mA)
    vals = Data2D(data[2:, 3:] - data[1, 3:], datatypes.COUNTS)
    return SpectrumSeries(xAxis, keyAxis, vals)


def ASCII_PLE(PLEFile, CalibrationFile=None, ResponseFile=None):
    """
    Reads PLE data from an ASCII file, optionally with calibration and response data.

    Args:
        PLEFile (str): The path to the PLE file.
        CalibrationFile (str, optional): The path to the calibration file.
        ResponseFile (str, optional): The path to the response file.

    Returns:
        PLE: The PLE data.
    """
    if CalibrationFile:
        data = ASCII(CalibrationFile, skip_header=3).T
        calX = Data1D(data[0, :], datatypes.WL_nm)
        calY = Data1D(data[1, :], datatypes.COUNTS)
    else:
        calY = None

    data = ASCII(PLEFile, skip_header=3).T
    pleX = Data1D(data[0, 1:], datatypes.WL_nm)
    pleKeys = Data1D(data[1:, 0], datatypes.WL_nm)
    pleVals = Data2D(data[1:, 1:], datatypes.COUNTS)

    if CalibrationFile:
        if numpy.sum(pleX.values - calX.values) > 0:
            print("Warning, PLE and Calibration Spectral Axes not compatible!!")

    data = ASCII(ResponseFile, skip_header=1).T
    responseX = Data1D(data[0, :], datatypes.WL_nm)
    responseY = Data1D(data[1, :], datatypes.P_mW)

    return PLE(pleX, pleKeys, pleVals, calY, Response(responseX, responseY))


def MapscanCommon(filename, ininame, format, CalibrationFile=None):
    """
    Common function to read map scan data from a binary file.

    Args:
        filename (str): The path to the binary data file.
        ininame (str): The path to the ini file with parameters.
        format (numpy.dtype): The data type of the binary file.
        CalibrationFile (str, optional): The path to the calibration file.

    Returns:
        SpectrumMap: The map scan data.
    """
    if CalibrationFile:
        data = ASCII(CalibrationFile, skip_header=3).T
        calX = Data1D(data[0, :], datatypes.WL_nm)
        calY = Data1D(data[1, :], datatypes.COUNTS)
    else:
        calY = None

    data = numpy.fromfile(filename, dtype=format)
    ini = open(ininame)
    inilines = ini.readlines()
    ini.close()
    xDim, yDim, xAmp, yAmp, center, dispersion = 0, 0, 0, 0, 0, 0
    for line in inilines:
        line = line.strip()
        print(line)
        line = line.split("=")
        if len(line) > 1:
            if line[0].startswith("x-dim"):
                xDim = int(line[1])
            if line[0].startswith("y-dim"):
                yDim = int(line[1])
            if line[0].startswith("x-amplitude"):
                xAmp = float(line[1].replace(",", "."))
            if line[0].startswith("y-amplitude"):
                yAmp = float(line[1].replace(",", "."))
            if line[0].startswith("center"):
                center = float(line[1].replace(",", "."))
            if line[0].startswith("dispersion"):
                dispersion = float(line[1].replace(",", "."))
    if (
        xDim == 0
        or yDim == 0
        or xAmp == 0
        or yAmp == 0
        or center == 0
        or dispersion == 0
    ):
        print("Error: some parameters are missing in ini file")
    print("Coordinates: {0}x{1} Size: {2}x{3}".format(xDim, yDim, xAmp, yAmp))
    print("Center: {0} Dispersion: {1}".format(center, dispersion))

    xData = numpy.arange(
        center + 1023.5 * dispersion, center - 1024.5 * dispersion, -dispersion
    )[:2048]

    axis = Data1D(xData, datatypes.WL_nm)

    yData = numpy.ndarray(shape=(xDim, yDim, 2048))

    mapping = numpy.ndarray(shape=(xDim, yDim, 2), dtype=numpy.float64)

    for x in range(xDim):
        for y in range(yDim):
            mapping[x, y, 0] = x / xDim * xAmp
            mapping[x, y, 1] = y / yDim * yAmp
            yData[x, y] = data[2048 * (x * yDim + y) : 2048 * (x * yDim + y + 1)]

    data = Data3D(yData, datatypes.COUNTS)
    mapping = Data3D(mapping, datatypes.POS_um)

    return SpectrumMap(axis, data, mapping, calY)


def Mapscan(filename, calibration=None):
    """
    Reads map scan data from a binary file.

    Args:
        filename (str): The path to the binary data file.
        calibration (str, optional): The path to the calibration file.

    Returns:
        SpectrumMap: The map scan data.
    """
    return MapscanCommon(filename, filename + "ini", numpy.dtype(">f8"), calibration)


def Mapscan2(filename, calibration=None):
    """
    Reads map scan data from a binary file with a different format.

    Args:
        filename (str): The path to the binary data file.
        calibration (str, optional): The path to the calibration file.

    Returns:
        SpectrumMap: The map scan data.
    """
    return MapscanCommon(
        filename, filename[: len(filename) - 1] + "ini", numpy.dtype(">u2"), calibration
    )
