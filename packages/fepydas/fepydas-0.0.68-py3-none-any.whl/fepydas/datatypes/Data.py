#!/usr/bin/python3
import numpy
import sympy.physics.units as u
from sympy.core.numbers import Rational

class Unit:
    """
    A class representing a physical unit
    """
    def __init__(self, unit):
        """
        Initializes a Unit instance.
        
        Args:
            unit (str): The unit as understood by sympy (e.g. "nm","ps" or "eV".
        """
        
        self.unit = unit
        
    def __str__(self):
        """
        This overrides the default __str__ method inserting SI prefixes for powers of 1000 where necessary and outputting only abbreviations
        """
        if hasattr(self.unit,"abbrev"):
            return str(self.unit.abbrev) 
        else:
            factors = []
            for arg in self.unit.args:
                if hasattr(arg, "abbrev"):
                    factors.append(str(arg.abbrev))
                else:
                    if str(arg)=="1/1000":
                        factors.append("m")
                    if str(arg)=="1/1000000":
                        factors.append("µ")
                    if str(arg)=="1/1000000000":
                        factors.append("n")
                    if str(arg)=="1/1000000000000":
                        factors.append("p")
            return "".join(factors)
    
    def __getattr__(self,name):
        """
        This overrides the default __getattr__ method in order to pass method calls down to the sympy Unit class
        """
        return getattr(object.__getattribute__(self,'unit'), name) #call __getattribute__ to avoid _getattr_ loop that happens if self.unit is here
        
    def _getDimension(self):
        """
        A helper function to construct the dimension of a unit expression, which can be used for comparison with other units
        """
        def get_expr_dimension(expr):
            # Build up the total dimension manually
            if hasattr(expr, 'dimension'):  # Single quantity
                return expr.dimension
            elif isinstance(expr, (int,float,Rational)): #dimensionless
                return u.dimensions.Dimension(1)
            elif expr.func.__name__ == 'Mul':
                base_dim = u.dimensions.Dimension(1)  # dimensionless
                for arg in expr.args:
                    arg_dim = get_expr_dimension(arg)
                    base_dim *= arg_dim
                return base_dim
            elif expr.func.__name__ == 'Pow':
                base, exp = expr.args
                return get_expr_dimension(base) ** exp
            else:
                raise TypeError("Unsupported expression type: ",expr,type(expr))
        return get_expr_dimension(self.unit)        

    def compareDimensionWith(self, otherUnit):
        """
        Compares the dimension with a different unit
        
        Args:
            otherUnit (Unit): the Unit to compare with
            
        Returns:
            True if they have the same Dimension (for example Energy)
        """
        return u.systems.si.dimsys_SI.equivalent_dims(self._getDimension(),otherUnit._getDimension())       

    def isWavelength(self):
        """
        Is the dimension a Length?
        
        Returns:
            True if it is a Length
        """
        
        return u.systems.si.dimsys_SI.equivalent_dims(self._getDimension(),u.m.dimension)
        
    def isEnergy(self):
        """
        Is the dimension an Energy?
        
        Returns:
            True if it is an Energy
        """
        
        return u.systems.si.dimsys_SI.equivalent_dims(self._getDimension(),u.J.dimension)
     
    def getTransformationTo(self, newUnit):
        """ 
        Build a Transformation to a different Unit. This works for units of the same Dimension and implented special other cases
        Currently, Wavelength <-> Energy. A TypeError will be raised if an invalid conversion is attempted.
        
        Args:
            newUnit (Unit): The new Unit that the values should be converted to

        Returns:
            Transformation object with the correct transformation function. (Transformation.apply())
        """
        if not self.compareDimensionWith(newUnit):
            if self.isWavelength() and newUnit.isEnergy() or self.isEnergy() and newUnit.isWavelength():
                def y(x):
                    return u.planck*u.c/(x*self.unit)
            else:
                raise TypeError(self._getDimension(),' to ',newUnit._getDimension(),' Transformation not known.')
        else:
            def y(x):
                return x*self.unit
        def transform(x):                    
            if type(x) is numpy.ndarray:
                x = numpy.array(x,dtype=numpy.float64)
                for i,xi in enumerate(x):
                    x[i] = float(u.convert_to(y(xi),newUnit.unit)/newUnit.unit)
                return x
            else:
                return float(u.convert_to(y(x),newUnit.unit)/newUnit.unit)

        return Transformation(transform,{})


class DataType:
    """
    A class representing the data type with a name and unit.
    """

    def __init__(self, name: str, unit):
        """
        Initializes a DataType instance.

        Args:
            name (str): The name of the data type.
            unit (Unit/str): The unit of the data type.

        Returns:
            None
        """
        self.name = name
        self.unit = unit

class Data:
    """
    A base class for handling data with associated values and errors.
    """

    def __init__(self, values: numpy.ndarray, datatype: DataType, errors=None):
        """
        Initializes a Data instance.

        Args:
            values (numpy.ndarray): The data values.
            datatype (DataType): The data type associated with the values.
            errors (optional): The associated errors for the values.

        Returns:
            None
        """
        self.values = values
        self.datatype = datatype
        self.errors = errors

    def normalize(self):
        """
        Normalizes the data values to the maximum value.

        Returns:
            None
        """
        self.values = self.values / numpy.max(self.values)

    def divideBy(self, data):
        """
        Divides the data values by another set of values.

        Args:
            data (numpy.ndarray): The values to divide by.

        Returns:
            None
        """
        self.values = self.values / data

    def append(self, dataToAppend):
        """
        Appends additional data to the existing values.

        Args:
            dataToAppend (numpy.ndarray): The data to append.

        Returns:
            None
        """
        self.values = numpy.concatenate((self.values, dataToAppend), axis=0)

    def applyJacobianTransformation(self, axis):
        """
        Applies a Jacobian transformation to the data values based on the provided axis.

        Args:
            axis (Data): The axis to use for the transformation.

        Returns:
            None
        """
        jacobian = axis.getJacobian()
        total_pre = numpy.sum(self.values)
        self.values = self.values * jacobian
        total_post = numpy.sum(self.values)
        self.values = self.values / total_post * total_pre #Keep integrated counts identical

    def linearAntiBloom(self, values, over, width=1, reverse=False):
        """
        Applies a linear anti-blooming correction to the data values.

        Args:
            values (numpy.ndarray): The values to apply the correction to.
            over (float): The threshold for the correction.
            width (int, optional): The width of the correction. Defaults to 1.
            reverse (bool, optional): If True, applies the correction in reverse. Defaults to False.

        Returns:
            numpy.ndarray: The corrected values.
        """
        max = numpy.max(values)
        length = len(values)
        if reverse:
            for j in range(length - 1, 0, -1):
                if j - width > 0:
                    if values[j - width] > over:
                        values[j] = max
        else:
            for j in range(length - 1):
                if j + width < length:
                    if values[j + width] > over:
                        values[j] = max
        return values


class Data1D(Data):
    """
    A class representing one-dimensional data.
    """

    def __init__(self, values: numpy.ndarray, datatype: DataType, errors=None):
        """
        Initializes a Data1D instance.

        Args:
            values (numpy.ndarray): The data values.
            datatype (DataType): The data type associated with the values.
            errors (optional): The associated errors for the values.

        Returns:
            None
        """
        super().__init__(values, datatype, errors=errors)

    def antiBloom(self, over, width=1, reverse=False):
        """
        Applies anti-blooming correction to the data values.

        Args:
            over (float): The threshold for the correction.
            width (int, optional): The width of the correction. Defaults to 1.
            reverse (bool, optional): If True, applies the correction in reverse. Defaults to False.

        Returns:
            None
        """
        self.values = self.linearAntiBloom(self.values, over, width, reverse)

    def cutAndGetIndexRange(self, min, max):
        """
        Cuts the data to the specified range and returns the index range.

        Args:
            min (float): The minimum value of the range.
            max (float): The maximum value of the range.

        Returns:
            tuple: A tuple containing the start and end indices of the cut data.
        """
        idx1, idx2 = self.getIndexRange(min, max)
        self.cut(idx1, idx2)
        return idx1, idx2

    def getIndexRange(self, min, max):
        """
        Gets the indices of the data values that fall within the specified range.

        Args:
            min (float): The minimum value of the range.
            max (float): The maximum value of the range.

        Returns:
            tuple: A tuple containing the start and end indices of the range.
        """
        idx1 = (numpy.abs(self.values - min)).argmin()
        idx2 = (numpy.abs(self.values - max)).argmin()
        if idx2 < idx1:
            temp = idx2
            idx2 = idx1
            idx1 = temp
        return idx1, idx2

    def convertToEnergy(self, unit="eV"):
        """
        Converts the data values from wavelength to energy.

        Args:
            unit (str, optional): The unit for energy. Defaults to "eV".

        Returns:
            None
        """
        self.transformTo(DataType("Energy",Unit(u.eV)))

    def getJacobian(self):
        """
        Calculates the Jacobian for the data values based on their data type.

        Returns:
            numpy.ndarray: The Jacobian values.
        """
        conversionUnit = u.nm * u.eV
        factor = float(u.convert_to(u.planck * u.c, conversionUnit)/conversionUnit) #eV s * m/s = eV m
        print(factor)
        return factor / ((self.values) ** 2)

    def cut(self, idx1, idx2):
        """
        Cuts the data values to the specified index range.

        Args:
            idx1 (int): The start index for the cut.
            idx2 (int): The end index for the cut.

        Returns:
            None
        """
        self.values = self.values[idx1:idx2]
        if self.errors is not None:
            self.errors = self.errors[idx1:idx2]

    def shiftValues(self, amount):
        """
        Shifts the data values by a specified amount.

        Args:
            amount (float): The amount to shift the values.

        Returns:
            None
        """
        self.values += amount

    def transformTo(self, newDataType):
        """
        Transform the values from the current unit to a different unit
        
        Args:
            newDataType (DataType): The new datatype
            
        Returns:
            None
        """
        print(self.datatype.unit)
        transformation = self.datatype.unit.getTransformationTo(newDataType.unit)
        self.values = transformation.apply(self.values)
        self.datatype=newDataType

    def trim(self):
        """
        Trims the data values to remove leading and trailing zeros.

        Returns:
            None
        """
        maxIdx = numpy.argmax(self.values)
        zeroes = numpy.where(self.values == 0)[0]
        start = 0
        end = zeroes[numpy.where(zeroes > maxIdx)[0][-1]]
        self.values = self.values[start:end]
        self.values = numpy.array(self.values, dtype=numpy.float64)
        self.values /= self.values.sum()

    def to2D(self, mask):
        """
        Converts the 1D data values to a 2D format based on a mask.

        Args:
            mask (Data2D): The mask to use for conversion.

        Returns:
            Data2D: The converted 2D data.
        """
        newValues = numpy.full_like(mask.values, numpy.nan, dtype=numpy.float64)
        x, y = mask.values.shape
        for i in range(x):
            for j in range(y):
                if not numpy.isnan(mask.values[i, j]):
                    idx = int(mask.values[i, j])
                    newValues[i, j] = self.values[idx]
        return Data2D(newValues, self.datatype)


class Data2D(Data):
    """
    A class representing two-dimensional data.
    """

    def __init__(self, values: numpy.ndarray, datatype: DataType, errors=None):
        """
        Initializes a Data2D instance.

        Args:
            values (numpy.ndarray): The data values.
            datatype (DataType): The data type associated with the values.
            errors (optional): The associated errors for the values.

        Returns:
            None
        """
        super().__init__(values, datatype, errors=errors)

    def antiBloom(self, over, width=1, reverse=False):
        """
        Applies anti-blooming correction to each row of the data values.

        Args:
            over (float): The threshold for the correction.
            width (int, optional): The width of the correction. Defaults to 1.
            reverse (bool, optional): If True, applies the correction in reverse. Defaults to False.

        Returns:
            None
        """
        for i in range(self.values.shape[0]):
            self.values[i, :] = self.linearAntiBloom(
                self.values[i, :], over, width, reverse
            )

    def average(self, despike_method=None, despike_cutoff=1):
        """
        Averages the data values, optionally applying a despiking method.

        Args:
            despike_method (str, optional): The method to use for despiking. Defaults to None. "median" filters outlies by value <= despike_cutoff * median.
            despike_cutoff (float, optional): The cutoff value for despiking. Defaults to 1.

        Returns:
            Data1D: The averaged data as a Data1D object.
        """
        if despike_method == "median":
            median = numpy.median(self.values, axis=0)
            no_spikes = (self.values <= despike_cutoff * median).astype(int)
            return Data1D(
                numpy.average(self.values, axis=0, weights=no_spikes), self.datatype
            )
        else:
            return Data1D(numpy.average(self.values, axis=0), self.datatype)

    def collapse(self, filter=None):
        """
        Collapses the 2D data into a 1D array by summing along the first axis, i.e. along the keys. (this integrates a time series to get a spectrum for example)

        Args:
            filter (optional): A filter to apply to the data before collapsing.

        Returns:
            Data1D: The collapsed data as a Data1D object.
        """
        if filter:
            return Data1D(numpy.sum(self.values[filter], axis=0), self.datatype)
        else:
            return Data1D(numpy.sum(self.values, axis=0), self.datatype)

    def interpSpikes(self, despike_method=None, despike_cutoff=1, interp_method=None):
        """
        Interpolates spikes in the data values based on specified methods.

        Args:
            despike_method (str, optional): The method to use for despiking. Defaults to None.
            despike_cutoff (float, optional): The cutoff value for despiking. Defaults to 1.
            interp_method (str, optional): The method to use for interpolation. Defaults to None.

        Returns:
            None
        """
        if despike_method == "diff":
            diff = numpy.diff(self.values, axis=0, prepend=self.values[0, 0])
            filter = numpy.abs(diff) > despike_cutoff
        if interp_method == "avg_0":
            for i in range(self.values.shape[0]):
                for j in range(self.values.shape[1]):
                    if filter[i, j]:
                        self.values[i, j] = (
                            self.values[i - 1, j] + self.values[i + 1, j]
                        ) / 2

    def integrate(self):
        """
        Integrates the 2D data values along the second (spectral) axis. For a time series, this gives the temporal evolution of integrated intensity.

        Returns:
            Data1D: The integrated data as a Data1D object.
        """
        if self.errors is None:
            errors = None
        else:
            errors = numpy.sum(self.errors, axis=1)
        return Data1D(numpy.sum(self.values, axis=1), self.datatype, errors)

    def normalizeIndividual(self):
        """
        Normalizes each row of the data individually.

        Returns:
            None
        """
        maxima = numpy.max(self.values, axis=1)
        self.values = (self.values.T / maxima).T

    def cut(self, idx1, idx2):
        """
        Cuts the data values to the specified index range along the second dimension.

        Args:
            idx1 (int): The start index for the cut.
            idx2 (int): The end index for the cut.

        Returns:
            None
        """
        self.values = self.values[:, idx1:idx2]
        if self.errors is not None:
            self.errors = self.errors[:, idx1:idx2]

    def cutMap(self, idx1, idx2, idx3, idx4):
        """
        Cuts the 2D data values to the specified index ranges along both dimensions.

        Args:
            idx1 (int): The start index for the first dimension.
            idx2 (int): The end index for the first dimension.
            idx3 (int): The start index for the second dimension.
            idx4 (int): The end index for the second dimension.

        Returns:
            None
        """
        self.values = self.values[idx1:idx2, idx3:idx4]

    def getCrosssectionAt(self, idx):
        """
        Retrieves the cross-section of the 2D data at a specified index.

        Args:
            idx (int): The index at which to retrieve the cross-section.

        Returns:
            Data1D: The cross-section data as a Data1D object.
        """
        return Data1D(self.values[:, idx], self.datatype)


class Data3D(Data):
    """
    A class representing three-dimensional data.
    """

    def __init__(self, values: numpy.ndarray, datatype: DataType):
        """
        Initializes a Data3D instance.

        Args:
            values (numpy.ndarray): The data values.
            datatype (DataType): The data type associated with the values.

        Returns:
            None
        """
        super().__init__(values, datatype)

    def collapse(self, filter=None):
        """
        Collapses the 3D data into a 1D array by summing along the first and second axis - i.e. across the map.

        Args:
            filter (optional): A filter to apply to the data before collapsing.

        Returns:
            Data1D: The collapsed data as a Data1D object.
        """
        print(filter)
        if filter is not None:
            return Data1D(numpy.sum(self.flatten()[filter], axis=0), self.datatype)
        else:
            return Data1D(numpy.sum(self.flatten(), axis=0), self.datatype)

    def cutMap(self, xMin, xMax, yMin, yMax):
        """
        Cuts the 3D data values to the specified index ranges along the first two dimensions.

        Args:
            xMin (int): The minimum index for the x-dimension.
            xMax (int): The maximum index for the x-dimension.
            yMin (int): The minimum index for the y-dimension.
            yMax (int): The maximum index for the y-dimension.

        Returns:
            None
        """
        self.values = self.values[xMin:xMax, yMin:yMax, :]

    def flatten(self, filter=None):
        """
        Flattens the 3D data into a 2D array.

        Args:
            filter (optional): A filter to apply to the data before flattening.

        Returns:
            numpy.ndarray: The flattened data.
        """
        if filter is None:
            x, y, z = self.values.shape
            return self.values.reshape(x * y, z)
        else:
            return self.values[filter].reshape(len(filter[0]), self.values.shape[2])

    def getIndexRange(self, xMin, xMax, yMin, yMax):
        """
        Gets the indices of the data values that fall within the specified ranges.

        Args:
            xMin (float): The minimum value for the x-dimension.
            xMax (float): The maximum value for the x-dimension.
            yMin (float): The minimum value for the y-dimension.
            yMax (float): The maximum value for the y-dimension.

        Returns:
            tuple: A tuple containing the indices for the specified ranges.
        """
        idx1 = (numpy.abs(self.values[:, 0, 0] - xMin)).argmin(axis=0)
        idx2 = (numpy.abs(self.values[:, 0, 0] - xMax)).argmin(axis=0)
        idx3 = (numpy.abs(self.values[0, :, 1] - yMin)).argmin(axis=0)
        idx4 = (numpy.abs(self.values[0, :, 1] - yMax)).argmin(axis=0)
        return idx1, idx2, idx3, idx4

    def get1DAt(self, x, y):
        """
        Retrieves a 1D slice of the 3D data at specified x and y indices.

        Args:
            x (int): The x index.
            y (int): The y index.

        Returns:
            Data1D: The 1D data slice as a Data1D object.
        """
        return Data1D(self.values[x, y, :], self.datatype)

    def cutAndGetIndexRange(self, xMin, xMax, yMin, yMax):
        """
        Cuts the 3D data to the specified ranges and returns the index ranges.

        Args:
            xMin (float): The minimum value for the x-dimension.
            xMax (float): The maximum value for the x-dimension.
            yMin (float): The minimum value for the y-dimension.
            yMax (float): The maximum value for the y-dimension.

        Returns:
            tuple: A tuple containing the indices for the specified ranges.
        """
        i1, i2, i3, i4 = self.getIndexRange(xMin, xMax, yMin, yMax)
        self.cutMap(i1, i2, i3, i4)
        return i1, i2, i3, i4

    def integrate(self):
        """
        Integrates the 3D data values along one axis.

        Returns:
            Data2D: The integrated data as a Data2D object.
        """
        return Data2D(numpy.sum(self.values, axis=2), self.datatype)

    def average(self):
        """
        Averages the 3D data values across the first two dimensions.

        Returns:
            Data1D: The averaged data as a Data1D object.
        """
        return Data1D(numpy.average(self.values, axis=(0, 1)), self.datatype)

    def extractAxes(self):
        """
        Extracts the axes from the 3D data.

        Returns:
            tuple: A tuple containing the x and y axes as Data1D objects.
        """
        y = self.values[0, :, 1]
        x = self.values[:, 0, 0]
        return Data1D(x, self.datatype), Data1D(y, self.datatype)

    def cut(self, idx1, idx2):
        """
        Cuts the data values to the specified index range along the second dimension.

        Args:
            idx1 (int): The start index for the cut.
            idx2 (int): The end index for the cut.

        Returns:
            None
        """
        self.values = self.values[:, :, idx1:idx2]

    def normalizeIndividual(self):
        """
        Normalizes each row of the 3D data individually by dividing by the maximum value in that row.

        This method calculates the maximum value along the last axis (depth) for each row and then
        divides each element in the row by its corresponding maximum value. This ensures that the
        values in each row are scaled between 0 and 1.

        Returns:
            None
        """
        maxima = numpy.max(self.values, axis=2)
        self.values = (self.values.T / maxima.T).T


class DataTransformation:
    """
    A class for applying transformations to data.
    """

    def __init__(self, transformation, newUnit):
        """
        Initializes a DataTransformation instance.

        Args:
            transformation: The transformation function to apply.
            newUnit (str): The new unit for the transformed data.

        Returns:
            None
        """
        self.transformation = transformation
        self.newUnit = newUnit

    def apply(self, oldAxis):
        """
        Applies the transformation to the given data axis.

        Args:
            oldAxis (Data1D): The data axis to transform.

        Returns:
            Data1D: The transformed data as a Data1D object.
        """
        newValues = self.transformation.apply(oldAxis.values)
        if oldAxis.errors is not None:
            errors = oldAxis.errors / oldAxis.values * newValues
        else:
            errors = None
        return Data1D(newValues, self.newUnit, errors)


class ArrheniusTransformation(DataTransformation):
    """
    A class for applying Arrhenius transformations to data.
    """

    def __init__(self):
        """
        Initializes an ArrheniusTransformation instance.

        Returns:
            None
        """
        super().__init__(Transformation(self.reciprocal, {}), DataType("1/T", "1/K"))

    def reciprocal(self, values):
        """
        Calculates the reciprocal of the given values.

        Args:
            values (numpy.ndarray): The values to calculate the reciprocal for.

        Returns:
            numpy.ndarray: The reciprocal values.
        """
        return 1 / values


class Transformation:
    """
    A class for defining a transformation function.
    """

    def __init__(self, function, parameterDict):
        """
        Initializes a Transformation instance.

        Args:
            function: The transformation function to apply.
            parameterDict (dict): The parameters for the transformation function.

        Returns:
            None
        """
        self.function = function
        self.params = parameterDict

    def apply(self, values):
        """
        Applies the transformation function to the given values.

        Args:
            values (numpy.ndarray): The values to transform.

        Returns:
            numpy.ndarray: The transformed values.
        """
        if values is None:
            return None
        return self.function(values, **self.params)


class WavelengthToEnergy(Transformation):
    """
    This should not be used anymore!
    Use axis.transformTo(E_eV) or Dataset.convertToEnergy or similar
    """

    def __init__(self):
        """
        Initializes a WavelengthToEnergy instance.

        Args:
            unit (str, optional): The unit for energy. Defaults to "eV".

        Returns:
            None
        """
        from fepydas.datatypes import WL_nm, E_eV 
        super().__init__(WL_nm.getTransformationTo(E_eV).function)

class VacuumCorrection(Transformation):
    """
    A class for applying vacuum corrections to wavelength values.
    """

    def __init__(self, temperature=20, pressure=101325, humidity=0, co2=610):
        """
        Initializes a VacuumCorrection instance.

        Args:
            temperature (float, optional): The temperature in degrees Celsius. Defaults to 20.
            pressure (float, optional): The pressure in Pascals. Defaults to 101325.
            humidity (float, optional): The humidity as a fraction. Defaults to 0.
            co2 (float, optional): The CO2 concentration in ppm. Defaults to 610.

        Returns:
            None
        """
        params = {}
        params["temperature"] = temperature
        params["pressure"] = pressure
        params["humidity"] = humidity
        params["co2"] = co2
        super().__init__(self.convertWavelength, params)

    def convertWavelength(self, values, temperature, pressure, humidity, co2):
        """
        Applies the vacuum correction to the given wavelength values.

        Args:
            values (numpy.ndarray): The wavelength values to correct.
            temperature (float): The temperature in degrees Celsius.
            pressure (float): The pressure in Pascals.
            humidity (float): The humidity as a fraction.
            co2 (float): The CO2 concentration in ppm.

        Returns:
            numpy.ndarray: The corrected wavelength values.
        """
        return values * self.n(values / 1000, temperature, pressure, humidity, co2)

    def Z(self, T, p, xw):  # compressibility
        """
        Calculates the compressibility factor.

        Args:
            T (float): The temperature in Kelvin.
            p (float): The pressure in Pascals.
            xw (float): The molar fraction of water vapor.

        Returns:
            float: The compressibility factor.
        """
        t = T - 273.15
        a0 = 1.58123e-6  # K·Pa^-1
        a1 = -2.9331e-8  # Pa^-1
        a2 = 1.1043e-10  # K^-1·Pa^-1
        b0 = 5.707e-6  # K·Pa^-1
        b1 = -2.051e-8  # Pa^-1
        c0 = 1.9898e-4  # K·Pa^-1
        c1 = -2.376e-6  # Pa^-1
        d = 1.83e-11  # K^2·Pa^-2
        e = -0.765e-8  # K^2·Pa^-2
        return (
            1
            - (p / T)
            * (a0 + a1 * t + a2 * t**2 + (b0 + b1 * t) * xw + (c0 + c1 * t) * xw**2)
            + (p / T) ** 2 * (d + e * xw**2)
        )

    def n(self, λ, t, p, h, xc):
        """
        Calculates the refractive index of moist air.

        Args:
            λ (float): The wavelength in micrometers.
            t (float): The temperature in degrees Celsius.
            p (float): The pressure in Pascals.
            h (float): The fractional humidity.
            xc (float): The CO2 concentration in ppm.

        Returns:
            float: The refractive index of moist air.
        """
        # λ: wavelength, 0.3 to 1.69 μm
        # t: temperature, -40 to +100 °C
        # p: pressure, 80000 to 120000 Pa
        # h: fractional humidity, 0 to 1
        # xc: CO2 concentration, 0 to 2000 ppm
        σ = 1 / λ  # μm^-1
        T = t + 273.15  # Temperature °C -> K
        R = 8.314510  # gas constant, J/(mol·K)
        k0 = 238.0185  # μm^-2
        k1 = 5792105  # μm^-2
        k2 = 57.362  # μm^-2
        k3 = 167917  # μm^-2
        w0 = 295.235  # μm^-2
        w1 = 2.6422  # μm^-2
        w2 = -0.032380  # μm^-4
        w3 = 0.004028  # μm^-6
        A = 1.2378847e-5  # K^-2
        B = -1.9121316e-2  # K^-1
        C = 33.93711047
        D = -6.3431645e3  # K
        α = 1.00062
        β = 3.14e-8  # Pa^-1,
        γ = 5.6e-7  # °C^-2
        # saturation vapor pressure of water vapor in air at temperature T
        if t >= 0:
            svp = numpy.exp(A * T**2 + B * T + C + D / T)  # Pa
        else:
            svp = 10 ** (-2663.5 / T + 12.537)
        # enhancement factor of water vapor in air
        f = α + β * p + γ * t**2
        # molar fraction of water vapor in moist air
        xw = f * h * svp / p
        # refractive index of standard air at 15 °C, 101325 Pa, 0% humidity, 450 ppm CO2
        nas = 1 + (k1 / (k0 - σ**2) + k3 / (k2 - σ**2)) * 1e-8
        # refractive index of standard air at 15 °C, 101325 Pa, 0% humidity, xc ppm CO2
        naxs = 1 + (nas - 1) * (1 + 0.534e-6 * (xc - 450))
        # refractive index of water vapor at standard conditions (20 °C, 1333 Pa)
        nws = 1 + 1.022 * (w0 + w1 * σ**2 + w2 * σ**4 + w3 * σ**6) * 1e-8
        Ma = 1e-3 * (28.9635 + 12.011e-6 * (xc - 400))  # molar mass of dry air, kg/mol
        Mw = 0.018015  # molar mass of water vapor, kg/mol
        Za = self.Z(288.15, 101325, 0)  # compressibility of dry air
        Zw = self.Z(293.15, 1333, 1)  # compressibility of pure water vapor
        # Eq.4 with (T,P,xw) = (288.15, 101325, 0)
        ρaxs = 101325 * Ma / (Za * R * 288.15)  # density of standard air
        # Eq 4 with (T,P,xw) = (293.15, 1333, 1)
        ρws = 1333 * Mw / (Zw * R * 293.15)  # density of standard water vapor
        # two parts of Eq.4: ρ=ρa+ρw
        ρa = (
            p * Ma / (self.Z(T, p, xw) * R * T) * (1 - xw)
        )  # density of the dry component of the moist air
        ρw = (
            p * Mw / (self.Z(T, p, xw) * R * T) * xw
        )  # density of the water vapor component
        nprop = 1 + (ρa / ρaxs) * (naxs - 1) + (ρw / ρws) * (nws - 1)
        return nprop


class Response:
    """
    A class representing a response function.
    """

    def __init__(self, input: Data1D, values: Data1D):
        """
        Initializes a Response instance.

        Args:
            input (Data1D): The input data for the response.
            values (Data1D): The response values.

        Returns:
            None
        """
        self.input = input
        self.values = values

    def interpolateResponse(self, inputValues: numpy.ndarray, zeroFloor=False):
        """
        Interpolates the response values based on the input values.

        Args:
            inputValues (numpy.ndarray): The input values for interpolation.
            zeroFloor (bool, optional): If True, applies a zero floor correction. Defaults to False.

        Returns:
            numpy.ndarray: The interpolated response values.
        """
        if zeroFloor:
            self.values.values -= numpy.amin(self.values.values) * 0.9
        return numpy.interp(inputValues, self.input.values, self.values.values)
