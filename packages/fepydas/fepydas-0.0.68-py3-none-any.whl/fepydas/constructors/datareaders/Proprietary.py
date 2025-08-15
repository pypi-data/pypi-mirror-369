#!/usr/bin/python3
import numpy
from fepydas.libs.sdtfile import SdtFile


def PicoHarpHistogramIntegrationTime(filename):
    """
    Reads the integration time from a PicoHarp histogram file.

    Args:
        filename (str): The path to the PicoHarp histogram file.

    Returns:
        float: The integration time extracted from the file.
    """
    file = open(filename, "br")
    bytes = file.read(1000000000)
    from struct import unpack, calcsize

    skip = 0
    fmt_txtHdr = "8s8s"
    size_txtHdr = calcsize(fmt_txtHdr)
    data_txtHdr = unpack(fmt_txtHdr, bytes[skip : skip + size_txtHdr])
    skip += size_txtHdr
    fmt_Hdr = "32s3i1I"
    size_Hdr = calcsize(fmt_Hdr)
    NumberOfCurves = 0
    HistResDscr = {}
    while True:
        data_Hdr = unpack(fmt_Hdr, bytes[skip : skip + size_Hdr])
        skip += size_Hdr
        if data_Hdr[2] & 65535 == 65535:
            skip += data_Hdr[3]
        if data_Hdr[0] == b"HistResDscr_MDescStopAfter\x00\x00\x00\x00\x00\x00":
            # if data_Hdr[0] == b'MeasDesc_AcquisitionTime\x00\x00\x00\x00\x00\x00\x00\x00':
            time = data_Hdr[3]
            break
        if (
            data_Hdr[0]
            == b"Header_End\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ):
            break
    file.close()
    return time


def PicoHarpHistogram(filename):
    """
    Reads histogram data from a PicoHarp histogram file.

    Args:
        filename (str): The path to the PicoHarp histogram file.

    Returns:
        tuple: A tuple containing the time axis and histogram data as numpy arrays.
    """
    file = open(filename, "br")
    bytes = file.read(1000000000)
    from struct import unpack, calcsize

    skip = 0
    fmt_txtHdr = "8s8s"
    size_txtHdr = calcsize(fmt_txtHdr)
    data_txtHdr = unpack(fmt_txtHdr, bytes[skip : skip + size_txtHdr])
    skip += size_txtHdr
    fmt_Hdr = "32s3i1I"
    size_Hdr = calcsize(fmt_Hdr)
    NumberOfCurves = 0
    HistResDscr = {}
    while True:
        data_Hdr = unpack(fmt_Hdr, bytes[skip : skip + size_Hdr])
        skip += size_Hdr
        if data_Hdr[2] & 65535 == 65535:
            skip += data_Hdr[3]
        if (
            data_Hdr[0]
            == b"Header_End\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ):
            break
        if data_Hdr[0] == b"HistoResult_NumberOfCurves\x00\x00\x00\x00\x00\x00":
            NumberOfCurves = data_Hdr[3]
        if (
            data_Hdr[0]
            == b"HistResDscr_DataOffset\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ):
            curveId = data_Hdr[1]
            value = data_Hdr[3]
            if not curveId in HistResDscr.keys():
                HistResDscr[curveId] = {}
            HistResDscr[curveId]["DataOffset"] = value
        if data_Hdr[0] == b"HistResDscr_HistogramBins\x00\x00\x00\x00\x00\x00\x00":
            curveId = data_Hdr[1]
            value = data_Hdr[3]
            if not curveId in HistResDscr.keys():
                HistResDscr[curveId] = {}
            HistResDscr[curveId]["HistogramBins"] = value
        if data_Hdr[0] == b"HistResDscr_MDescResolution\x00\x00\x00\x00\x00":
            curveId = data_Hdr[1]
            fmt_Float = "1d"
            size_Float = calcsize(fmt_Float)
            data_Float = data_Hdr = unpack(fmt_Float, bytes[skip - size_Float : skip])
            value = data_Float[0]
            if not curveId in HistResDscr.keys():
                HistResDscr[curveId] = {}
            HistResDscr[curveId]["MDescResolution"] = value
    data = numpy.zeros(shape=(HistResDscr[0]["HistogramBins"]), dtype=numpy.int64)
    print("Number of Curves: {0}".format(NumberOfCurves))
    for i in range(NumberOfCurves):
        offset = HistResDscr[i]["DataOffset"]
        fmt_Histogram = "{0}I".format(HistResDscr[i]["HistogramBins"])
        size_Histogram = calcsize(fmt_Histogram)
        Histogram = unpack(fmt_Histogram, bytes[offset : offset + size_Histogram])
        data += Histogram
    print(
        "Bins: {0} Resolution: {1}".format(
            HistResDscr[0]["HistogramBins"], HistResDscr[0]["MDescResolution"]
        )
    )
    time = numpy.arange(
        0,
        (HistResDscr[0]["HistogramBins"]) * HistResDscr[0]["MDescResolution"] / 1e-9,
        HistResDscr[0]["MDescResolution"] / 1e-9,
    )
    file.close()
    return time, data


def TimeHarpHistogram(filename):
    """
    Reads histogram data from a TimeHarp histogram file.

    Args:
        filename (str): The path to the TimeHarp histogram file.

    Returns:
        tuple: A tuple containing the time axis and histogram data as numpy arrays.
    """
    file = open(filename, "br")
    bytes = file.read(100000000)
    from struct import unpack, calcsize

    skip = 0
    fmt_txtHdr = "16s6s18s12s18s2s256s"
    size_txtHdr = calcsize(fmt_txtHdr)
    skip += size_txtHdr

    fmt_binHdr = "6id2iI3i4I16i9f4i20s"
    size_binHdr = calcsize(fmt_binHdr)
    skip += size_binHdr

    fmt_mainHardwareHdr = "16s8s16s2id12i"
    size_mainHardwareHdr = calcsize(fmt_mainHardwareHdr)
    data_mainHardwareHdr = unpack(
        fmt_mainHardwareHdr, bytes[skip : skip + size_mainHardwareHdr]
    )
    inpChansPresent = data_mainHardwareHdr[7]
    skip += size_mainHardwareHdr

    fmt_inputChannelSettings = "4i"
    size_inputChannelsettings = inpChansPresent * calcsize(fmt_inputChannelSettings)
    skip += size_inputChannelsettings

    fmt_curveHdr = "iI16s8s16s2id20id4i3f3iQ2i"
    size_curveHdr = calcsize(fmt_curveHdr)
    data_curveHdr = unpack(fmt_curveHdr, bytes[skip : skip + size_curveHdr])
    bins = data_curveHdr[40]
    offset = data_curveHdr[41]
    resolution = data_curveHdr[28]
    print("Acquisition Time: {0}s".format(data_curveHdr[31] / 1000))
    print("Resolution: {0}ns".format(resolution / 1000))

    fmt_counts = "{0}I".format(bins)
    size_counts = calcsize(fmt_counts)
    data_counts = unpack(fmt_counts, bytes[offset : offset + size_counts])
    data = numpy.array(data_counts)
    time = numpy.arange(0, (bins) * resolution / 1000, resolution / 1000)

    return time, data


def BeckerHicklHistogram(filename):
    """
    Reads histogram data from a Becker & Hickl SDT file.

    Args:
        filename (str): The path to the Becker & Hickl SDT file.

    Returns:
        tuple: A tuple containing the time axis and histogram data as numpy arrays.
    """
    sdt = SdtFile(filename)
    x = numpy.ndarray(shape=(len(sdt.times[0][:])))
    y = numpy.ndarray(shape=(len(sdt.times[0][:])))
    print(len(sdt.times[0]))
    for i in range(len(sdt.times[0][:])):
        x[i] = numpy.abs(sdt.times[0][i] * 1000000000)
        y[i] = sdt.data[0][0][i]
    return x, y
