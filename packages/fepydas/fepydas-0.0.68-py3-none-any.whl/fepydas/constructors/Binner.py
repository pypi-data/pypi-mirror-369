import numpy
from fepydas.datatypes.Data import Data1D, Data2D


class Binner:
    """
    A class for creating bins and binning data.
    """

    def __init__(self):
        """
        Initializes a Binner instance.

        Returns:
            None
        """
        return

    def createBins(self, axis, num_bins):
        """
        Creates bins based on the provided axis and number of bins.

        Args:
            axis (Data1D): The axis data to be binned.
            num_bins (int): The number of bins to create.

        Returns:
            Data1D: A Data1D object containing the bin averages and standard deviations.
        """
        values = self.transform(axis.values)
        empty_bins = True
        self.histogram, self.bin_edges = numpy.histogram(values, num_bins)
        self.digitized = numpy.digitize(values, self.bin_edges, right=True) - 1
        print(self.digitized)
        self.bin_centers = (self.bin_edges[:-1] + self.bin_edges[1:]) / 2
        self.bin_avgs = numpy.zeros_like(self.bin_centers)
        self.bin_stds = numpy.zeros_like(self.bin_centers)
        self.num_bins = num_bins

        for i in range(num_bins):
            idx = numpy.where(self.digitized == i)
            self.bin_avgs[i] = numpy.average(values[idx])
            self.bin_stds[i] = numpy.std(values[idx])

        return Data1D(self.bin_avgs, axis.datatype, self.bin_stds)

    def binData(self, data2D):
        """
        Bins the provided 2D data based on the previously created bins.

        Args:
            data2D (Data2D): The 2D data to be binned.

        Returns:
            tuple: A tuple containing a Data2D object of binned data and the histogram.
        """
        values2D = data2D.values
        originalShape = values2D.shape
        self.binned_data = numpy.ndarray(
            shape=(len(self.histogram), originalShape[1]), dtype=values2D.dtype
        )
        self.binned_std = numpy.zeros_like(self.binned_data)

        for i in range(self.num_bins):
            idx = numpy.where(self.digitized == i)
            self.binned_data[i, :] = numpy.average(values2D[idx[0], :], axis=0)
            self.binned_std[i, :] = numpy.std(values2D[idx[0], :], axis=0) / numpy.sqrt(
                self.histogram[i]
            )

        # Remove Empty Bins
        non_empty = numpy.where(self.histogram > 0)[0]
        self.histogram = self.histogram[non_empty]
        self.bin_centers = self.bin_centers[non_empty]
        self.bin_avgs = self.bin_avgs[non_empty]
        self.bin_stds = self.bin_stds[non_empty]
        self.binned_data = self.binned_data[non_empty, :]
        self.binned_std = self.binned_std[non_empty, :]

        return (
            Data2D(self.binned_data, data2D.datatype, self.binned_std),
            self.histogram,
        )


class LinearBinner(Binner):
    """
    A class for linear binning.
    """

    def __init__(self):
        """
        Initializes a LinearBinner instance.

        Returns:
            None
        """
        super().__init__()

    def transform(self, values):
        """
        Transforms the input values linearly.

        Args:
            values (numpy.ndarray): The values to transform.

        Returns:
            numpy.ndarray: The transformed values.
        """
        return values

    def inverseTransform(self, values):
        """
        Applies the inverse transformation to the input values.

        Args:
            values (numpy.ndarray): The values to inverse transform.

        Returns:
            numpy.ndarray: The inverse transformed values.
        """
        return values


class InverseBinner(Binner):
    """
    A class for inverse binning.
    """

    def __init__(self):
        """
        Initializes an InverseBinner instance.

        Returns:
            None
        """
        super().__init__()

    def transform(self, values):
        """
        Transforms the input values to their inverse.

        Args:
            values (numpy.ndarray): The values to transform.

        Returns:
            numpy.ndarray: The transformed values.
        """
        return 1 / values

    def inverseTransform(self, values):
        """
        Applies the inverse transformation to the input values.

        Args:
            values (numpy.ndarray): The values to inverse transform.

        Returns:
            numpy.ndarray: The inverse transformed values.
        """
        return 1 / values


class LogBinner(Binner):
    """
    A class for logarithmic binning.
    """

    def __init__(self):
        """
        Initializes a LogBinner instance.

        Returns:
            None
        """
        super().__init__()

    def transform(self, values):
        """
        Transforms the input values using a logarithmic scale.

        Args:
            values (numpy.ndarray): The values to transform.

        Returns:
            numpy.ndarray: The transformed values.
        """
        return numpy.log10(values)

    def inverseTransform(self, values):
        """
        Applies the inverse transformation to the input values.

        Args:
            values (numpy.ndarray): The values to inverse transform.

        Returns:
            numpy.ndarray: The inverse transformed values.
        """
        return numpy.power(10, values)
