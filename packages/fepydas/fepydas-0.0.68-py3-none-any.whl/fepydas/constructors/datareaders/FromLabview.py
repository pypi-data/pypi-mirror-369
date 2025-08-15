import numpy
import os
from fepydas.datatypes.Dataset import Spectrum, PLE, SpectrumSeries, SparseSpectrumMap
from fepydas.constructors.datareaders.Generic import ASCII
from fepydas.datatypes.Data import Data1D, Data2D, Data3D, DataType
import fepydas.datatypes as datatypes
import sympy.physics.units as u

def Automatic(filename):
    """
    Automatically reads data from a specified file and processes the headers.

    Args:
        filename (str): The path to the file to be read.

    Returns:
        None
    """
    file = open(filename, encoding="Latin-1")
    done = False
    headers = {}
    while not done:
        line = file.readline().strip().split(" = ")
        # print(line)
        if line[0] == "HEADER":
            done = True
        else:
            headers[line[0]] = line[1:]
    # Header Done
    if "Header Version" in headers.keys() and int(headers["Header Version"][0]) == 2:
        # New Header
        if "Series Mode" in headers.keys():
            is_map = headers["Series Mode"][0] == "Mapscan Cube"
            is_ple = headers["Series Mode"][0] == "PLE"
            is_series = True
            series_mode = headers["Series Mode"][0]
        else:
            is_map = False
            is_ple = False
            is_series = False
        # These use the old header currently
        is_ple_response = False
        is_histogram = False
        if "Measurement Mode" in headers.keys():
            print("Measurement Mode: "+headers["Measurement Mode"][0])
            if headers["Measurement Mode"][0]=="TRPL":
                is_histogram = True

        def read_units(file):
            """
            Reads unit information from a file.

            Args:
                file: The file object to read from.

            Returns:
                tuple: A tuple containing the names, units, and information dictionary, along with the length of the read data.
            """
            length = 0
            done = False
            infos = {}
            while not done:
                line = file.readline().strip()
                length += 1
                if line == "---":
                    done = True
                else:
                    line = line.split("\t")
                    infos[line[0]] = Data1D(
                        numpy.array(line[2:], dtype=numpy.float64),
                        datatypes.generateDataType(line[0], line[1]),
                    )
            names = file.readline().strip().split("\t")
            units = file.readline().strip().split("\t")
            length += 2
            return names, units, infos, length

    else:
        # Old Header
        is_map = headers["Measurement Type"][0] == "Mapscan Cube"
        is_series = headers["Measurement Type"][0] == "Series"
        if is_series:
          series_mode = headers["Measurement Type"][1]
        is_ple = is_series and headers["Measurement Type"][1] == "PLE Xe Arc Lamp"
        is_ple_response = headers["Measurement Type"][0] == "PLE Response"
        is_histogram = headers["Measurement Type"][0] == "Histogram"

        def read_units(file):
            names = file.readline().strip().split("\t")
            units = file.readline().strip().split("\t")
            infos = {}
            if len(units) > 2:
                # In the legacy file, the powers are appended after the units in the units row, unless it is a Time Series (no param), where they start in column 3..
                if headers["Measurement Type"][1] == "Time Series":
                    fields = units[3:]
                elif headers["Measurement Type"][1] == "Power":
                    fields = names[3:]                 
                else:                 
                    fields = units[1 + int(len(units) / 2) :]  
                try:
                    values = numpy.array(fields, dtype=numpy.float64)        
                    infos["Power Track"] = Data1D(values, datatypes.P_mW)
                except ValueError as e:
                    print("Invalid Power in tracked power:", e)
            return names, units, infos, 2  # in the old format, these are always 2 lines

    if is_map:
        print("Mapscan detected")
        # For Mapscans, the Header is followed by a section showing the mapping using X and O.
        map_x = int(headers["Map Dimension X"][0])
        map_y = int(headers["Map Dimension Y"][0])
        map_x0 = float(headers["Map Edge Position X (µm)"][0])
        map_y0 = float(headers["Map Edge Position Y (µm)"][0])
        map_pitch = float(headers["Map Pitch (µm)"][0])
        file.readline()  # ---
        mapping = numpy.ndarray(shape=(map_x, map_y, 2), dtype=numpy.float64)
        bool_mask = numpy.ndarray(shape=(map_x, map_y), dtype=bool)
        mask = numpy.ndarray(shape=(map_x, map_y), dtype=numpy.float64)
        num = 0
        for i in range(map_y):
            line = file.readline()
            for j in range(map_x):
                mapping[j, map_y - 1 - i] = [
                    map_x0 + j * map_pitch,
                    map_y0 + (map_y - 1 - i) * map_pitch,
                ]
                if line[j] == "X":
                    bool_mask[j, map_y - 1 - i] = True
                    num += 1
                else:
                    bool_mask[j, map_y - 1 - i] = False
        file.readline()  # ---

        names, units, infos, length = read_units(file)

        endOfAxis = False
        axisData = []
        while not endOfAxis:
            value = file.readline().strip()
            if value == "---":
                break
            axisData.append(float(value.split("\t")[0]))
        axis = Data1D(numpy.array(axisData), datatypes.generateDataType(names[0], units[0]))

        raw = numpy.fromfile(file, dtype=numpy.dtype(">u8"))[
            1:
        ]  # 64bit uint big-endian
        actual_num = int(numpy.floor(len(raw) / len(axis.values)))
        data = numpy.ndarray(shape=(actual_num, len(axis.values)))
        # It seems that this array is transposed?
        data = raw.reshape((len(axis.values), actual_num)).T
        n = 0
        for i in range(map_x):
            for j in range(map_y):
                if bool_mask[i, j]:
                    if n < actual_num:  # Ignore missing pixels
                        mask[i, j] = n
                    else:
                        mask[i, j] = numpy.nan
                    n += 1
                else:
                    mask[i, j] = numpy.nan
        sparsemap = SparseSpectrumMap(
            axis,
            Data2D(data.astype(numpy.float64), datatypes.COUNTS),
            Data3D(mapping, datatypes.POS_um),
            Data2D(mask, datatypes.NUMBER),
            None,
            headers,
            infos,
        )
        if int(headers["Dark Frames"][0]) > 0:
            # Has been corrected and is offset by 1000
            if "Dark Offset" in headers.keys():
                sparsemap.data.values -= int(headers["Dark Offset"][0])
            else:
                sparsemap.data.values -= 1000
        return sparsemap
    else:
        names, units, infos, hlength = read_units(file)
        length = hlength + len(headers) + 1
        file.close()
        data = ASCII(filename, skip_header=length).T
        if data[0, 0] == numpy.inf or data[0, 0] == -numpy.inf:
            axis = Data1D(data[1, :], datatypes.generateDataType(names[1], units[1]))
        else:
            axis = Data1D(data[0, :], datatypes.generateDataType(names[0], units[0]))
        if is_series:
            # 2D
            values = Data2D(data[2:, :], datatypes.COUNTS)
            if int(headers["Dark Frames"][0]) > 0:
                # Has been corrected and is offset by 1000
                if "Dark Offset" in headers.keys():
                    values.values -= int(headers["Dark Offset"][0])
                else:
                    values.values -= 1000
            if is_ple:
                dtype = datatypes.generateDataType("Excitation Wavelength", "nm")
            else:
                if len(units) > 2:
                    dtype = datatypes.generateDataType(series_mode, units[2])  # TODO
                else:
                    dtype = datatypes.generateDataType(series_mode, "a.u.")  # TODO
            keys = Data1D(
                numpy.array(names[2 : 2 + values.values.shape[0]]).astype(
                    numpy.float64
                ),
                dtype,
            )
            if (
                int(headers["Dark Frames"][0]) > 0
                and values.values.shape[0] == int(headers["Dark Frames"][0])+1 
                and len(keys.values) == 0
            ):
                # This is a Time Series of Dark Spectra, the last Dark Spectrum is the AVG used for correct
                keyvals = numpy.arange(1, int(headers["Dark Frames"][0]) + 2)
                keys.values = keyvals.astype(str)
                keys.values[-1] = "Average"
            if is_ple:
                return PLE(axis, keys, values, None, None, headers)
            else:
                return SpectrumSeries(axis, keys, values, headers, infos)
        elif is_ple_response:
            values = Data1D(data[1, :], datatypes.generateDataType(names[1], units[1]))
            return Spectrum(axis, values, headers)
        elif is_histogram:
            values = Data1D(data[1, :], datatypes.COUNTS)
            return Spectrum(axis, values, headers)
        else:
            # 1D
            values = Data1D(data[2, :], datatypes.COUNTS)
            return Spectrum(axis, values, headers)
