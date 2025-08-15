#!/usr/bin/python3
from copy import deepcopy
import numpy
import pickle

from fepydas.datatypes.Data import (
    Data,
    Data1D,
    Data2D,
    Data3D,
    Response,
    VacuumCorrection,
)
from fepydas.datatypes import NUMBER
from fepydas.workers.Fit import (
    LimitedGaussianFit,
    GaussianFit,
    CalibrationFit,
    Fit,
    LinearFit,
    AutomaticCalibration,
)
from fepydas.workers.ASCIIWriter import MultiSpectrumWriter

from sklearn.decomposition import NMF, PCA, LatentDirichletAllocation
from sklearn.cluster import SpectralClustering

from scipy.interpolate import griddata


class BaseDataset:
    """
    A base class for datasets that provides common functionality.
    """

    def saveBinary(self, filename):
        """
        Saves the dataset to a binary file using pickle.

        Args:
            filename (str): The path to the file where the dataset will be saved.

        Returns:
            None
        """
        f = open(filename, "bw")
        pickle.dump(self, f)
        f.close()


class Dataset(BaseDataset):
    """
    A class representing a dataset with axis and data.
    """

    def __init__(self, axis: Data1D, data: Data, metadata=None):
        """
        Initializes a Dataset instance.

        Args:
            axis (Data1D): The axis data for the dataset.
            data (Data): The main data of the dataset.
            metadata (optional): Additional metadata for the dataset.

        Returns:
            None
        """
        self.metadata = metadata
        self.axis = axis
        self.data = data

    def applyAxisTransformation(self, transformation):
        """
        Applies a transformation to the axis of the dataset.

        Args:
            transformation: The transformation to apply to the axis.

        Returns:
            None
        """
        self.axis.values = transformation.apply(self.axis.values)
        print("Applied Axis Transformation")

    def applyVacuumCorrection(
        self, temperature=20, pressure=101325, humidity=0, co2=610
    ):
        """
        Applies vacuum correction to the axis values based on environmental parameters.

        Args:
            temperature (float, optional): The temperature in degrees Celsius. Defaults to 20.
            pressure (float, optional): The pressure in Pascals. Defaults to 101325.
            humidity (float, optional): The humidity as a fraction. Defaults to 0.
            co2 (float, optional): The CO2 concentration in ppm. Defaults to 610.

        Returns:
            None
        """
        vac = VacuumCorrection(temperature, pressure, humidity, co2)
        self.axis.values = vac.apply(self.axis.values)

    def convertToEnergy(self, unit="eV"):
        """
        Converts the axis values from wavelength to energy. Also applies Jacobian Transformation to the data.

        Args:
            unit (str, optional): The unit for energy. Defaults to "eV".

        Returns:
            None
        """
        self.axis.convertToEnergy(unit)
        self.data.applyJacobianTransformation(self.axis)

    def antiBloom(self, over, width=1, reverse=False):
        """
        Applies anti-blooming correction to the data values.

        Args:
            over (float): The threshold for the correction.
            width (int, optional): The width of the correction. Defaults to 1.
            reverse (bool, optional): If True, applies the correction in reverse. Defaults to False. The direction here refers to the direction the pixels are read out on the CCD.

        Returns:
            None
        """
        self.data.antiBloom(over, width=width, reverse=reverse)

    def cutAxis(self, minVal, maxVal):
        """
        Cuts the axis values to the specified range.

        Args:
            minVal (float): The minimum value for the cut.
            maxVal (float): The maximum value for the cut.

        Returns:
            None
        """
        idx1, idx2 = self.axis.cutAndGetIndexRange(minVal, maxVal)
        self.data.cut(idx1, idx2)

    def cutAxisByIdx(self, minIdx, maxIdx):
        """
        Cuts the axis and data values by specified indices.

        Args:
            minIdx (int): The minimum index for the cut.
            maxIdx (int): The maximum index for the cut.

        Returns:
            None
        """
        self.axis.cut(minIdx, maxIdx)
        self.data.cut(minIdx, maxIdx)

    def divideBySpectrum(self, spectrum):
        """
        Divides the data values by another spectrum's values.

        Args:
            spectrum (Spectrum): The spectrum to divide by.

        Returns:
            None
        """
        self.data.divideBy(spectrum.data.values)


class Spectrum(Dataset):
    """
    A class representing a spectrum dataset.
    """

    def __init__(self, axis: Data1D, data: Data1D, metadata=None):
        """
        Initializes a Spectrum instance.

        Args:
            axis (Data1D): The axis data for the spectrum.
            data (Data1D): The data values for the spectrum.
            metadata (optional): Additional metadata for the spectrum.

        Returns:
            None
        """
        super().__init__(axis, data, metadata)

    def export(self, filename):
        """
        Exports the spectrum to a file.

        Args:
            filename (str): The path to the file where the spectrum will be saved.

        Returns:
            None
        """
        msw = MultiSpectrumWriter(filename)
        msw.addSpectrum(self)
        msw.write()

    def identifyPeaks(self, threshold=10, width=10):
        """
        Identifies peaks in the spectrum data.

        Args:
            threshold (float, optional): The threshold for peak detection. Defaults to 10.
            width (int, optional): The width of the peak. Defaults to 10.

        Returns:
            list: A list of index ranges for the identified peaks.
        """
        derivative = numpy.diff(self.data.values)
        derivative.resize(self.data.values.shape)
        nonflat = derivative != 0
        zerocrossings = numpy.diff(numpy.sign(derivative)) != 0
        zerocrossings.resize(self.data.values.shape)
        noiseLevel = self.data.values > numpy.average(self.data.values) * threshold
        peaks = zerocrossings * noiseLevel * nonflat
        print("{0} peaks detected".format(numpy.sum(peaks)))
        indeces = numpy.where(peaks)[0]
        idxRanges = []
        for i, idx in enumerate(indeces):
            if idx + width > len(self.axis.values) or idx - width < 0:
                continue
            idxRanges.append([idx - width, idx + width])
        return idxRanges

    def normalize(self):
        """
        Normalizes the spectrum data.

        Returns:
            None
        """
        self.data.normalize()

    def toPlot(self):
        """
        Converts the spectrum to a plot object.

        Returns:
            SpectrumPlot: The plot object for the spectrum.
        """
        from fepydas.constructors.Plots import SpectrumPlot

        return SpectrumPlot(self)

    def toScatterPlot(self):
        """
        Converts the spectrum to a scatter plot object.

        Returns:
            SpectrumScatterPlot: The scatter plot object for the spectrum.
        """
        from fepydas.constructors.Plots import SpectrumScatterPlot

        return SpectrumScatterPlot(self)


class SpectrumSeries(Dataset):
    """
    A class representing a series of spectra.
    """

    def __init__(
        self, axis: Data1D, keys: Data1D, data: Data2D, metadata=None, infos=None
    ):
        """
        Initializes a SpectrumSeries instance.

        Args:
            axis (Data1D): The axis data for the series.
            keys (Data1D): The keys for the spectra.
            data (Data2D): The data for the spectra.
            metadata (optional): Additional metadata for the series.
            infos (optional): Additional information for the series.

        Returns:
            None
        """
        super().__init__(axis, data, metadata)
        self.keys = keys
        self.infos = infos
        if infos and "Power Track" in infos.keys():  # Legacy Direct Access to Power
            self.power = infos["Power Track"]
        else:
            self.power = None

    def average(self, despike_method=None, despike_cutoff=1):
        """
        Averages the spectra in the series.

        Args:
            despike_method (str, optional): The method to use for despiking. Defaults to None.
            despike_cutoff (float, optional): The cutoff value for despiking. Defaults to 1.

        Returns:
            Spectrum: The averaged spectrum.
        """
        return Spectrum(self.axis, self.data.average(despike_method, despike_cutoff))

    def collapse(self, filter=None):
        """
        Collapses the series into a single spectrum.

        Args:
            filter (optional): A filter to apply before collapsing.

        Returns:
            Spectrum: The collapsed spectrum.
        """
        return Spectrum(self.axis, self.data.collapse(filter))

    def collapseDominatingCluster(self, maxClusters=None):
        """
        Collapses the series to the dominating cluster based on clustering analysis.

        Args:
            maxClusters (int, optional): The maximum number of clusters to consider. Defaults to None.

        Returns:
            Spectrum: The collapsed spectrum of the dominating cluster.
        """
        averages, cluster, resp = self.performGMM(maxClusters=maxClusters)
        dominatingCluster = numpy.bincount(cluster).argmax()
        keep = numpy.where(cluster == dominatingCluster)
        return self.collapse(filter=keep)

    def cutKeys(self, min, max):
        """
        Cuts the keys and corresponding data values to the specified range.

        Args:
            min (float): The minimum value for the cut.
            max (float): The maximum value for the cut.

        Returns:
            None
        """
        keys = numpy.where((self.keys.values >= min) & (self.keys.values <= max))[0]
        self.keys.values = self.keys.values[keys]
        self.data.values = self.data.values[keys, :]

    def interpSpikes(self, despike_method=None, despike_cutoff=1, interp_method=None):
        """
        Interpolates spikes in the data values.

        Args:
            despike_method (str, optional): The method to use for despiking. Defaults to None.
            despike_cutoff (float, optional): The cutoff value for despiking. Defaults to 1.
            interp_method (str, optional): The method to use for interpolation. Defaults to None.

        Returns:
            None
        """
        self.data.interpSpikes(despike_method, despike_cutoff, interp_method)

    def export(self, filename):
        """
        Exports the spectrum series to a file.

        Args:
            filename (str): The path to the file where the series will be saved.

        Returns:
            None
        """
        writer = MultiSpectrumWriter(filename)
        writer.addSpectra(self)
        writer.write()

    def filterByIntegral(self, threshold=0.5):
        """
        Filters the spectra in the series based on their integral values.

        Args:
            threshold (float, optional): The threshold for filtering. Defaults to 0.5.

        Returns:
            None
        """
        integrals = self.data.integrate()
        max = numpy.amax(integrals.values)
        filter = numpy.where(integrals.values / max > threshold)[0]
        self.data.values = self.data.values[filter, :]
        self.keys.values = self.keys.values[filter]

    def findDominatingComponents(self, n=1, algo="NMF"):
        """
        Finds the dominating components in the spectrum series using specified algorithms.

        Args:
            n (int, optional): The number of components to find. Defaults to 1.
            algo (str, optional): The algorithm to use for component analysis. Defaults to "NMF".

        Returns:
            The dominating components.
        """
        if algo == "NMF":
            decomp = NMF(n_components=n)
        elif algo == "PCA":
            decomp = PCA(n_components=n)
        elif algo == "LDA":
            decomp = LatentDirichletAllocation(n_components=n)
        return self.fitDominatingComponents(decomp)

    def fit(self, fitter: Fit, log=False):
        """
        Fits the spectrum series using the provided fitter.

        Args:
            fitter (Fit): The fitter to use for fitting the data.
            log: Whether to use logarithmic residuals
        Returns:
            None
        """
        fitter.batchFit(self.axis.values, self.data.values, log=log)

    def fitDominatingComponents(self, decomp):
        """
        Fits the dominating components using the specified decomposition method.

        Args:
            decomp: The decomposition method to use.

        Returns:
            The fitted components.
        """
        decomp.fit(self.data.values)
        return decomp

    def getDataValues(self):
        """
        Retrieves the data values from the spectrum series.

        Returns:
            numpy.ndarray: The data values.
        """
        return self.data.values

    def fitMixture(self, n=2, nmf=None):
        """
        Fits a mixture model to the data values.

        Args:
            n (int, optional): The number of components in the mixture. Defaults to 2.
            nmf (optional): The NMF model to use for fitting. Defaults to None.

        Returns:
            The fitted mixture model.
        """
        data = self.getDataValues()

        if nmf is not None:
            # pcaWorker = NMF()
            # pcaWorker.fit(data)
            # np = numpy.where(pcaWorker.explained_variance_ratio_ > pca)[0][-1]
            data = NMF(n_components=nmf).fit_transform(data)
            # print("PCA reduced complexity to {0} components".format(len(pcaWorker.explained_variance_ratio_)))

        aff = numpy.zeros(shape=(data.shape[0], data.shape[0]))
        for i in range(data.shape[0]):
            for j in range(data.shape[0]):
                aff[i, j] = numpy.dot(data[i, :], data[j, :])

        gmm = SpectralClustering(
            affinity="precomputed", n_jobs=-1, eigen_solver="amg", n_clusters=n
        )
        gmm.fit(aff)

        return gmm

    def getDominatingComponent(self, algo="PCA"):
        """
        Retrieves the dominating component based on the specified algorithm.

        Args:
            algo (str, optional): The algorithm to use for component analysis. Defaults to "PCA".

        Returns:
            Spectrum: The dominating component as a Spectrum object.
        """
        decomp = self.findDominatingComponents(n=1, algo=algo)
        return Spectrum(self.axis, Data1D(decomp.components_[0], self.data.datatype))

    def getDominatingComponents(self, algo="PCA", n=2):
        """
        Retrieves the dominating components based on the specified algorithm.

        Args:
            algo (str, optional): The algorithm to use for component analysis. Defaults to "PCA".
            n (int, optional): The number of components to retrieve. Defaults to 2.

        Returns:
            tuple: A tuple containing the fitted components and a SpectrumSeries object.
        """
        decomp = self.findDominatingComponents(n=n, algo=algo)
        return decomp, SpectrumSeries(
            self.axis,
            Data1D(range(n), NUMBER),
            Data2D(decomp.components_, self.data.datatype),
        )

    def getProjection(self, decomp):
        """
        Projects the data values based on the specified decomposition method.

        Args:
            decomp: The decomposition method to use for projection.

        Returns:
            SpectrumSeries: The projected data as a SpectrumSeries object.
        """
        return SpectrumSeries(
            self.keys,
            Data1D(range(len(decomp.components_)), NUMBER),
            Data2D(decomp.transform(self.data.values).T, self.data.datatype),
        )

    def removeComponents(self, decomp):
        """
        Removes the specified components from the data values.

        Args:
            decomp: The decomposition method used to identify components to remove.

        Returns:
            None
        """
        self.data.values -= decomp.transform(self.data.values) @ decomp.components_

    def removeDominatingComponents(self, n=1, algo="NMF"):
        """
        Removes the dominating components from the data values.

        Args:
            n (int, optional): The number of components to remove. Defaults to 1.
            algo (str, optional): The algorithm to use for component analysis. Defaults to "NMF".

        Returns:
            The removed components.
        """
        decomp = self.findDominatingComponents(n=n, algo=algo)
        self.removeComponents(decomp)
        return decomp

    def highDynamicRange(self, max=0.99, zmin=None):
        """
        Applies high dynamic range processing to the data values.

        Args:
            max (float, optional): The maximum scaling factor. Defaults to 0.99.
            zmin (float, optional): The minimum value for scaling. Defaults to None.

        Returns:
            Spectrum: The processed spectrum as a Spectrum object.
        """
        if self.data.values.shape[0] == 1:
            # nothing to do here
            return Spectrum(
                deepcopy(self.axis),
                Data1D(self.data.values.flatten(), self.data.datatype),
            )
        # calculate weights
        zmax = numpy.amax(self.data.values) * max
        if zmin is None:
            zmin = numpy.amin(self.data.values)
        zfloor = numpy.full_like(self.data.values, zmin)
        zceil = numpy.full_like(self.data.values, zmax)
        zcenter, zrange = (zmax + zmin) / 2, (zmax - zmin) / 2
        weights = zrange - numpy.abs(
            (numpy.maximum(numpy.minimum(self.data.values, zceil), zfloor) - zcenter)
        )  # Low weight for low (under-exposed) or high (over-exposed) values, high weight for medium values

        # calculate mappings
        num = len(self.keys.values)
        crossweights = numpy.zeros((num, num, len(self.data.values[0, :])))
        for i in range(num):
            for j in range(num):
                crossweights[i, j, :] = numpy.multiply(weights[i, :], weights[j, :])
        integratedCWs = numpy.sum(crossweights, axis=2)
        idxs = numpy.flip(numpy.argsort(numpy.sum(integratedCWs, axis=1)))

        def linearProjection(dataIn, dataRef, crossweights):
            return dataIn * numpy.average(dataRef / dataIn, weights=crossweights)

        mapped = numpy.zeros((num))
        mapped[idxs[0]] = 1

        for i in range(len(idxs) - 1):
            idx = idxs[i + 1]
            usableCWs = numpy.multiply(integratedCWs[idx, :], mapped)
            best = numpy.argsort(usableCWs)[-1]
            self.data.values[idx, :] = linearProjection(
                self.data.values[idx, :],
                self.data.values[best, :],
                crossweights[idx, best, :],
            )
            print("mapped", idx, "to", best)
            mapped[idx] = 1

        return Spectrum(
            deepcopy(self.axis),
            Data1D(
                numpy.average(self.data.values, axis=0, weights=weights),
                self.data.datatype,
            ),
        )

    def integrate(self):
        """
        Integrates the data values along the spectal axis.

        Returns:
            Spectrum: The integrated spectrum.
        """
        return Spectrum(self.keys, self.data.integrate())

    def interpolate(self, newKeys):
        """
        Interpolates the data values to new keys.

        Args:
            newKeys (numpy.ndarray): The new keys for interpolation.

        Returns:
            None
        """
        oldPoints = numpy.ndarray(
            shape=(len(self.keys.values) * len(self.axis.values), 2)
        )
        values = numpy.ndarray(shape=(len(self.keys.values) * len(self.axis.values)))
        newPoints = numpy.ndarray(shape=(len(newKeys) * len(self.axis.values), 2))

        n = 0
        for it, t in enumerate(self.keys.values):
            for ix, x in enumerate(self.axis.values):
                oldPoints[n, :] = [t, x]
                values[n] = self.data.values[it, ix]
                n += 1
        n = 0
        for it, t in enumerate(newKeys):
            for ix, x in enumerate(self.axis.values):
                newPoints[n, :] = [t, x]
                n += 1
        self.data.values = griddata(
            oldPoints, values, newPoints, method="cubic"
        ).reshape(len(newKeys), len(self.axis.values))
        self.keys.values = newKeys

    def maximum(self):
        """
        Retrieves the maximum value from the data values in the spectrum series.

        Returns:
            Spectrum: A Spectrum object containing the keys and the maximum values.
        """
        return Spectrum(
            self.keys,
            Data1D(
                self.axis.values[numpy.argmax(self.data.values, axis=1)],
                self.axis.datatype,
            ),
        )

    def normalize(self, individual=False):
        """
        Normalizes the data values in the spectrum series.

        Args:
            individual (bool, optional): If True, normalizes each spectrum individually. Defaults to False.

        Returns:
            None
        """
        if individual:
            self.data.normalizeIndividual()
        else:
            self.data.normalize()

    def subtractBaseline(self):
        """
        Subtracts the baseline from the data values.

        This method removes the baseline by subtracting the minimum value from the data values.
        It should only be invoked if no dark spectrum is available.

        Returns:
            None
        """
        # Invoke only if no dark spectrum available!
        baseline = numpy.min(self.data.values) - 1
        self.data.values -= baseline
        print("Baseline removed: {0}".format(baseline))

    def toPlot(self, polar=False, cmap=None, norm=None):
        """
        Converts the spectrum series to a plot object.

        Args:
            polar (bool, optional): If True, creates a polar plot. Defaults to False.
            cmap (Colormap, optional): The colormap to use for the plot. Defaults to None.
            norm (Normalize, optional): The normalization to use for the plot. Defaults to None.

        Returns:
            SpectrumSeriesPlot: The plot object for the spectrum series.
        """
        from fepydas.constructors.Plots import SpectrumSeriesPlot

        return SpectrumSeriesPlot(self, polar=polar, cmap=cmap, norm=norm)


class BinnedSpectrumSeries(SpectrumSeries):
    """
    A class representing a binned spectrum series.
    """

    def __init__(self, spectrumSeries, binner, num_bins):
        """
        Initializes a BinnedSpectrumSeries instance.

        Args:
            spectrumSeries (SpectrumSeries): The original spectrum series to bin.
            binner: The binner object used for creating bins.
            num_bins (int): The number of bins to create.

        Returns:
            None
        """
        keys = binner.createBins(spectrumSeries.keys, num_bins)
        data, self.histogram = binner.binData(spectrumSeries.data)
        super().__init__(deepcopy(spectrumSeries.axis), keys, data)


class JoinSpectrumSeries(SpectrumSeries):
    """
    A class for joining multiple spectra into a SpectrumSeries.
    """

    def __init__(self, spectra, interpol=False, names=None):
        """
        Initializes a JoinSpectrumSeries instance.

        Args:
            spectra (list of Spectrum): The list of spectra to join.
            interpol (bool, optional): If True, performs interpolation on the data (if the axes are not identical). Defaults to False.
            names (list of str, optional): The names for the keys in the joined series. Defaults to None. Spectra will be numbered if None.

        Returns:
            None
        """
        if len(spectra) == 1:
            if names:
                keys = [names[0]]
            else:
                keys = [0]
            data = numpy.ndarray(
                shape=(1, len(spectra[0].data.values)),
                dtype=spectra[0].data.values.dtype,
            )
            data[0, :] = spectra[0].data.values
            super().__init__(
                spectra[0].axis,
                Data1D(keys, None),
                Data2D(data, spectra[0].data.datatype),
            )
            return
        if names:
            keys = Data1D(names, NUMBER)
        else:
            keys = Data1D(range(len(spectra)), NUMBER)
        if interpol:
            valmin, mins, maxs, res = [], [], [], []
            for i in range(len(spectra)):
                mins.append(numpy.amin(spectra[i].axis.values))
                maxs.append(numpy.amax(spectra[i].axis.values))
                res.append(numpy.average(numpy.diff(spectra[i].axis.values)))
                if res[i] < 0:  # axis must be ascending
                    spectra[i].axis.values = numpy.flip(spectra[i].axis.values)
                    spectra[i].data.values = numpy.flip(spectra[i].data.values)
                valmin.append(numpy.amin(spectra[i].data.values))
            resolution = numpy.abs(numpy.average(res))
            min, max = numpy.amin(mins), numpy.amax(maxs)
            valmin = numpy.amin(valmin)
            # Interpolation, set non-overlapping regions to minimum so weight will be 0
            newAxis = Data1D(
                numpy.linspace(min, max, int((max - min) / resolution)),
                spectra[0].axis.datatype,
            )
            data = Data2D(
                numpy.zeros((len(spectra), len(newAxis.values))),
                spectra[0].data.datatype,
            )
            for i in range(len(spectra)):
                data.values[i, :] = (
                    numpy.interp(
                        newAxis.values,
                        spectra[i].axis.values,
                        spectra[i].data.values,
                        left=valmin,
                        right=valmin,
                    )
                    - valmin
                    + 0.001
                )
            super().__init__(newAxis, keys, data)
        else:
            data = Data2D(
                numpy.zeros((len(spectra), len(spectra[0].data.values))),
                spectra[0].data.datatype,
            )
            for i in range(len(spectra)):
                data.values[i, :] = spectra[i].data.values
            # TODO check AXIS consistency
            super().__init__(spectra[0].axis, keys, data)
        # TODO default create keys in SS init


class MergeSpectraSeries(SpectrumSeries):
    """
    A class for merging multiple spectrum series into one.
    """

    def __init__(self, spectraSeries):
        """
        Initializes a MergeSpectraSeries instance.

        Args:
            spectraSeries (list of SpectrumSeries): The list of spectrum series to merge.

        Returns:
            None
        """
        first = True
        for spectrumSeries in spectraSeries:
            if first:
                super().__init__(
                    deepcopy(spectrumSeries.axis),
                    deepcopy(spectrumSeries.keys),
                    deepcopy(spectrumSeries.data),
                )
                first = False
            else:
                self.axis.append(spectrumSeries.axis.values)
                self.data.append(spectrumSeries.data.values)
                self.keys.append(spectrumSeries.keys.values)


class Map(BaseDataset):
    """
    A class representing a mapping of data in a 2D space.
    """

    def __init__(self, mapping: Data3D, data: Data2D):
        """
        Initializes a Map instance.

        Args:
            mapping (Data3D): The mapping data in 3D.
            data (Data2D): The 2D data associated with the mapping.

        Returns:
            None
        """
        self.mapping = mapping
        self.data = data

    def export(self, filename):
        """
        Exports the map data to a file.

        Args:
            filename (str): The path to the file where the map will be saved.

        Returns:
            None
        """
        writer = MultiSpectrumWriter(filename)
        x, y = self.mapping.extractAxes()
        writer.addX(x, "")
        for i in range(len(y.values)):
            writer.addY(self.data.getCrosssectionAt(i), "{0}".format(y.values[i]))
        writer.write()

    def insertFlatData(self, data):
        """
        Inserts flat data into the map.

        Args:
            data (numpy.ndarray): The flat data to insert.

        Returns:
            None
        """
        x, y = self.data.values.shape
        print(x, y, data.shape)
        self.data.values = data.reshape(x, y)

    def toPlot(self, log=False, zRange=None):
        """
        Converts the map to a plot object.

        Args:
            log (bool, optional): If True, uses a logarithmic scale for the plot. Defaults to False.
            zRange (tuple, optional): The range for the z-axis. Defaults to None.

        Returns:
            ContourMapPlot: The plot object for the map.
        """
        from fepydas.constructors.Plots import ContourMapPlot

        return ContourMapPlot(self, log=log, zRange=zRange)


class SpectrumSeriesWithCalibration(SpectrumSeries):
    """
    A class representing a spectrum series with calibration data.
    """

    def __init__(
        self, axis: Data1D, data: Data2D, calibration: Data1D, metadata=None, infos=None
    ):
        """
        Initializes a SpectrumSeriesWithCalibration instance.

        Args:
            axis (Data1D): The axis data for the series.
            data (Data2D): The data values for the series.
            calibration (Data1D): The calibration data for the series.
            metadata (optional): Additional metadata for the series.
            infos (optional): Additional information for the series.

        Returns:
            None
        """
        super().__init__(
            axis=axis, keys=None, data=data, metadata=metadata, infos=infos
        )
        self.calibrated = False
        self.calibration = calibration

    def getCalibrationSpectrum(self):
        """
        Retrieves the calibration spectrum.

        Returns:
            Spectrum: The calibration spectrum.
        """
        return Spectrum(self.axis, self.calibration)

    def calibrate(self, references, threshold=10, width=10):
        """
        Calibrates the spectrum series based on reference data.

        Args:
            references (numpy.ndarray): The reference values for calibration.
            threshold (float, optional): The threshold for peak detection. Defaults to 10.
            width (int, optional): The width for peak detection. Defaults to 10.

        Returns:
            None
        """

        self.applyAxisTransformation(
            AutomaticCalibration(
                self.getCalibrationSpectrum(),
                references,
                threshold=threshold,
                width=width,
            ).toTransformation()
        )
        self.calibrated = True
        print("Calibrated")


class BaseSpectrumMap(SpectrumSeriesWithCalibration):
    """
    A base class for spectrum maps with calibration data.
    """

    def __init__(
        self,
        axis: Data1D,
        data: Data2D,
        mapping: Data3D,
        calibration: Data1D,
        metadata=None,
        infos=None,
    ):
        """
        Initializes a BaseSpectrumMap instance.

        Args:
            axis (Data1D): The axis data for the map.
            data (Data2D): The data values for the map.
            mapping (Data3D): The mapping data in 3D.
            calibration (Data1D): The calibration data for the map.
            metadata (optional): Additional metadata for the map.
            infos (optional): Additional information for the map.

        Returns:
            None
        """
        super().__init__(axis, data, calibration, metadata, infos)
        self.mapping = mapping

    def average(self):
        """
        Averages the data values in the map.

        Returns:
            Spectrum: The averaged spectrum.
        """
        return Spectrum(self.axis, self.data.average())

    def getEmptyMap(self, datatype=NUMBER):
        """
        Creates an empty map with the specified data type.

        Args:
            datatype (DataType, optional): The data type for the empty map. Defaults to NUMBER.

        Returns:
            Map: An empty map object.
        """
        x, y, z = self.mapping.values.shape
        vals = numpy.ndarray(shape=(x, y))
        values = Data2D(vals, datatype)
        return Map(self.mapping, values)


class SparseSpectrumMap(BaseSpectrumMap):
    """
    A class representing a sparse spectrum map with calibration data. Sparse here means not all pixels in the mapping have a spectrum associated with them.
    """

    def __init__(
        self,
        axis: Data1D,
        data: Data2D,
        mapping: Data3D,
        mask: Data2D,
        calibration: Data1D,
        metadata=None,
        infos=None,
    ):
        """
        Initializes a SparseSpectrumMap instance.

        Args:
            axis (Data1D): The axis data for the sparse map.
            data (Data2D): The data values for the sparse map.
            mapping (Data3D): The mapping data in 3D.
            mask (Data2D): The mask indicating valid data points.
            calibration (Data1D): The calibration data for the sparse map.
            metadata (optional): Additional metadata for the sparse map.
            infos (optional): Additional information for the sparse map.

        Returns:
            None
        """
        super().__init__(axis, data, mapping, calibration, metadata, infos)
        self.mask = mask  # This contains the indexes of the data array where the invidiual spectra are stored or numpy.nan for empty pixels

    def cutMap(self, xMin, xMax, yMin, yMax):
        """
        Cuts the map data to the specified ranges.

        Args:
            xMin (float): The minimum x value for the cut.
            xMax (float): The maximum x value for the cut.
            yMin (float): The minimum y value for the cut.
            yMax (float): The maximum y value for the cut.

        Returns:
            None
        """
        i1, i2, i3, i4 = self.mapping.cutAndGetIndexRange(xMin, xMax, yMin, yMax)
        self.mask.cutMap(i1, i2, i3, i4)
        self.updateFromMask()
        # the spectra are still there, but they are not referenced anymore. this is okay for most plots, but should be fixed if fits are attempted?

    def fitParameterToMap(self, fitter, paramName, paramDatatype):
        """
        Fits a parameter to the map based on the provided fitter.

        Args:
            fitter: The fitter to use for fitting.
            paramName (str): The name of the parameter to fit.
            paramDatatype (DataType): The data type of the parameter.

        Returns:
            Map: The map with the fitted parameter values.
        """
        map = self.getEmptyMap(paramDatatype)
        x, y = map.data.values.shape
        for i in range(x):
            for j in range(y):
                idx = self.mask.values[i, j]
                result = fitter.results[idx]
                if result == 0:
                    val = 0
                else:
                    val = result.params[paramName].value
                map.data.values[i, j] = val
        return map

    def integrate(self):
        """
        Integrates the data values in the sparse map.

        Returns:
            Map: The integrated map.
        """
        return Map(self.mapping, self.data.integrate().to2D(self.mask))

    def maximum(self):
        """
        Retrieves the maximum value from the data values in the sparse map.

        Returns:
            Map: A Map object containing the maximum values.
        """
        return Map(
            self.mapping,
            Data1D(
                self.axis.values[numpy.argmax(self.data.values, axis=1)],
                self.axis.datatype,
            ).to2D(self.mask),
        )

    def updateFromMask(self):
        """
        Updates the sparse map based on the mask, removing spectra that are not referenced anymore.

        Returns:
            None
        """
        # This method removes spectra that are not part of the map anymore and updates the mask
        # TODO I probably need to check for NaN here?
        table = numpy.array(self.mask.values.flatten(), dtype=numpy.int64)
        self.data.values = self.data.values[table, :]
        coordinates = (
            []
        )  # I need to temp store this so I don't accidently "find" a value post-replacement
        for i, old in enumerate(table):
            coordinates.append(numpy.where(self.mask.values == old))
        for i, pos in enumerate(coordinates):
            self.mask.values[pos] = i
     
    def getSpectrumAt(self, x, y):
        if numpy.isnan(self.mask.values[x,y]):
            return None
        return Spectrum(self.axis,Data1D(self.data.values[int(self.mask.values[x,y]),:],self.data.datatype))

    def export(self, filename):
        """
        Exports the sparse spectrum map to a file.

        Args:
            filename (str): The path to the file where the map will be saved.

        Returns:
            None
        """
        writer = MultiSpectrumWriter(filename)
        writer.addX(self.axis, "Coordinates")
        for x in range(self.mapping.values.shape[0]):
            for y in range(self.mapping.values.shape[1]):
                if not numpy.isnan(self.mask.values[x, y]):
                    writer.addY(
                        Data1D(
                            self.data.values[int(self.mask.values[x, y]), :],
                            self.data.datatype,
                        ),
                        "{0}:{1}".format(
                            self.mapping.values[x, y, 0], self.mapping.values[x, y, 1]
                        ),
                    )
        writer.write()


class SpectrumMap(BaseSpectrumMap):
    """
    A class representing a mapping of data in a 2D space. This assumes a rectangular map with Spectra for all pixels.
    """

    def __init__(
        self, axis: Data1D, data: Data3D, mapping: Data3D, calibration: Data1D
    ):
        """
        Initializes a SpectrumMap instance.

        Args:
            axis (Data1D): The axis data for the map.
            data (Data3D): The data values for the map.
            mapping (Data3D): The mapping data in 3D.
            calibration (Data1D): The calibration data for the map.

        Returns:
            None
        """
        super().__init__(axis, data, mapping, calibration)

    def cutMap(self, xMin, xMax, yMin, yMax):
        """
        Cuts the map data to the specified ranges.

        Args:
            xMin (float): The minimum x value for the cut.
            xMax (float): The maximum x value for the cut.
            yMin (float): The minimum y value for the cut.
            yMax (float): The maximum y value for the cut.

        Returns:
            None
        """
        i1, i2, i3, i4 = self.mapping.cutAndGetIndexRange(xMin, xMax, yMin, yMax)
        self.data.cutMap(i1, i2, i3, i4)

    def getClusterMapIdx(self, gmm):
        """
        Retrieves the cluster map indices based on the provided Gaussian Mixture Model (GMM).

        Args:
            gmm: The Gaussian Mixture Model used for clustering.

        Returns:
            Map: A map object containing the cluster indices.
        """
        map = self.getEmptyMap()
        # map.insertFlatData(gmm.predict(self.getDataValues(pca)))
        map.insertFlatData(gmm.labels_)
        return map

    def getClusterIntegratedSpectra(self, gmm):
        """
        Integrates the spectra based on the cluster indices from the GMM.

        Args:
            gmm: The Gaussian Mixture Model used for clustering.

        Returns:
            SpectrumSeries: A SpectrumSeries object containing the integrated spectra for each cluster.
        """
        map = self.getClusterMapIdx(gmm)
        num = numpy.amax(map.data.values) + 1
        data = numpy.zeros(shape=(num, self.data.values.shape[2]))
        for i in range(num):
            cond = numpy.where(map.data.values == i)
            filtered = self.data.values[cond]
            data[i, :] = numpy.sum(filtered, axis=0)
        return SpectrumSeries(
            self.axis, Data1D(range(num), NUMBER), Data2D(data, self.data.datatype)
        )

    def export(self, filename):
        """
        Exports the spectrum map to a file.

        Args:
            filename (str): The path to the file where the map will be saved.

        Returns:
            None
        """
        writer = MultiSpectrumWriter(filename)
        writer.addX(self.axis, "Coordinates")
        for x in range(self.mapping.values.shape[0]):
            for y in range(self.mapping.values.shape[1]):
                writer.addY(
                    self.data.get1DAt(x, y),
                    "{0}:{1}".format(
                        self.mapping.values[x, y, 0], self.mapping.values[x, y, 1]
                    ),
                )
        writer.write()

    def fit(self, fitter: Fit, filter=None):
        """
        Fits the spectrum map using the provided fitter.

        Args:
            fitter (Fit): The fitter to use for fitting the data.
            filter (optional): A filter to apply during fitting.

        Returns:
            None
        """
        fitter.batchFit(self.axis.values, self.data.flatten(filter=filter))

    def fitDominatingComponents(self, decomp):
        """
        Fits the dominating components using the specified decomposition method.

        Args:
            decomp: The decomposition method to use.

        Returns:
            The fitted components.
        """
        decomp.fit(self.data.flatten())
        return decomp

    def fitParameterToMap(self, fitter, paramName, paramDatatype, filter=None):
        """
        Fits a parameter to the map based on the provided fitter.

        Args:
            fitter: The fitter to use for fitting.
            paramName (str): The name of the parameter to fit.
            paramDatatype (DataType): The data type of the parameter.
            filter (optional): A filter to apply during fitting.

        Returns:
            Map: The map with the fitted parameter values.
        """
        map = self.getEmptyMap(paramDatatype)
        x, y, z = self.data.values.shape
        if filter is not None:
            wasFitted = numpy.zeros_like(self.mapping.values[:, :, 0])
            print(wasFitted.shape)
            wasFitted[filter] = 1
            print(wasFitted.shape)
            wasFitted = wasFitted.reshape((x * y, 1))
            print(wasFitted.shape)
        vals = numpy.ndarray(shape=(x * y))
        i = 0
        for key in fitter.results.keys():
            if filter is not None:
                while wasFitted[i] == 0:
                    vals[i] = 0
                    i += 1
            result = fitter.results[key]
            if result == 0:
                vals[i] = 0
            else:
                vals[i] = result.params[paramName].value
            i += 1
        map.insertFlatData(vals)
        return map

    def getDataValues(self, pca=None):
        """
        Retrieves the data values from the spectrum series, optionally applying PCA transformation.

        Args:
            pca: The PCA model to use for transforming the data. Defaults to None.

        Returns:
            numpy.ndarray: The data values, transformed if PCA is provided.
        """
        if pca is not None:
            return pca.transform(self.data.flatten())
        return self.data.flatten()

    def integrate(self):
        """
        Integrates the data values along one axis.

        Returns:
            Map: The integrated spectrum as a Map object.
        """
        return Map(self.mapping, self.data.integrate())

    def maximum(self):
        """
        Retrieves the maximum value from the data values in the spectrum series.

        Returns:
            Map: A Map object containing the keys and the maximum values.
        """
        return Map(
            self.mapping,
            Data2D(
                self.axis.values[numpy.argmax(self.data.values, axis=2)],
                self.axis.datatype,
            ),
        )


class PLE(SpectrumSeriesWithCalibration):
    """
    A class representing a Photoluminescence Excitation (PLE) dataset.
    """

    def __init__(
        self,
        axis: Data1D,
        keys: Data1D,
        data: Data2D,
        calibration=None,
        response=None,
        metadata=None,
    ):
        """
        Initializes a PLE instance.

        Args:
            axis (Data1D): The axis data for the PLE.
            keys (Data1D): The keys for the PLE data.
            data (Data2D): The PLE data values.
            calibration (optional): The calibration data for the PLE.
            response (optional): The response data for the PLE.
            metadata (optional): Additional metadata for the PLE.

        Returns:
            None
        """
        super().__init__(axis, data, calibration, metadata)
        self.keys = keys
        self.response = response

    def applyLampResponseCorrection(self, zeroFloor=False):
        """
        Applies lamp response correction to the PLE data.

        Args:
            zeroFloor (bool, optional): If True, applies a zero floor correction. Defaults to False.

        Returns:
            None
        """
        interpolatedResponse = self.response.interpolateResponse(
            self.keys.values, zeroFloor
        )
        for i in range(len(self.keys.values)):
            self.data.values[i] /= interpolatedResponse[i]
        print("Lamp Response Correction made")

    def calibrateLamp(self, width=2, thresh=1):
        """
        Calibrates the lamp based on the PLE data.

        Args:
            width (int, optional): The width for peak detection. Defaults to 2.
            thresh (float, optional): The threshold for peak detection. Defaults to 1.

        Returns:
            The transformation applied during calibration.
        """
        # This assumes the lamp is present in some of the spectra and used to calibrate the entire excitation (keys) axis with a linear fit
        fit = LimitedGaussianFit()
        nominal = []
        fitted = []
        fittedErrs = []
        for i in range(len(self.keys.values)):
            x, y = fit.initializeAutoLimited(
                self.axis.values,
                self.data.values[i],
                self.keys.values[i],
                width,
                thresh,
            )
            if type(x) is numpy.ndarray and len(x) > 40:
                # print(x,y)
                fit.fit(x, y)
                nominal.append(self.keys.values[i])
                fitted.append(fit.result.params["x0"].value)
                fittedErrs.append(fit.result.params["x0"].stderr)
        nominal = numpy.array(nominal, dtype=numpy.float64)
        fitted = numpy.array(fitted, dtype=numpy.float64)
        calib = CalibrationFit()
        calib.initializeAuto()
        calib.fit(nominal, fitted)  # ,peakErrs)
        print(calib.result.params)
        transformation = calib.toTransformation()
        self.keys.values = transformation.apply(self.keys.values)
        print("Calibrated Lamp")
        return transformation

    def calibrateLampExplicit(self, width=2, thresh=1):
        """
        Explicitly calibrates the lamp based on the PLE data.

        Args:
            width (int, optional): The width for peak detection. Defaults to 2.
            thresh (float, optional): The threshold for peak detection. Defaults to 1.

        Returns:
            None
        """
        # This assumes the lamp is present in ALL spectra and is used to set the excitation (key) to the fitted value for each spectrum
        # The resulting axis may be used to calibrate another PLE measurement which used the same lamp parameters
        # USE WITH CAUTION AND CHECK RESULTS
        fit = GaussianFit()
        for i in range(len(self.keys.values)):
            idxs = numpy.where(
                numpy.abs(self.axis.values - self.keys.values[i]) <= width
            )[0]
            x, y = self.axis.values[idxs], self.data.values[i, idxs]
            fit.initializeAuto(x, y)
            fit.fit(x, y)
            self.keys.values[i] = fit.result.params["x0"].value
            # print(lamp.keys.values[i], fit.parameters["x0"])
        print("Calibrated Lamp")

    def export(self, filename):
        """
        Exports the PLE data to a file.

        Args:
            filename (str): The path to the file where the PLE data will be saved.

        Returns:
            None
        """
        writer = MultiSpectrumWriter(filename)
        writer.addSpectra(self)
        writer.write()

    def toPlot(self, log=True):
        """
        Converts the PLE data to a plot object.

        Args:
            log (bool, optional): If True, uses a logarithmic scale for the plot. Defaults to True.

        Returns:
            ContourPlot: The plot object for the PLE data.
        """
        from fepydas.constructors.Plots import ContourPlot

        return ContourPlot(self, log=log)


class SpectrumWithIRF(Spectrum):
    """
    A class representing a spectrum with an Instrument Response Function (IRF).
    """

    def __init__(self, axis: Data1D, data: Data, IRF: Data1D):
        """
        Initializes a SpectrumWithIRF instance.

        Args:
            axis (Data1D): The axis data for the spectrum.
            data (Data): The data values for the spectrum.
            IRF (Data1D): The Instrument Response Function data for the spectrum.

        Returns:
            None
        """
        super().__init__(axis, data)
        self.trimIRF(IRF)

    def evaluateConvolutionFit(self, fit):
        """
        Evaluates the fit using convolution with the IRF.

        Args:
            fit: The fit object to evaluate.

        Returns:
            Data1D: The evaluated convolution fit as a Data1D object.
        """
        return Data1D(
            fit.evaluateConvolution(self.axis.values, self.IRF.values),
            self.data.datatype,
        )

    def getExtendedIRF(self):
        """
        Retrieves the extended IRF for the spectrum.

        Returns:
            numpy.ndarray: The extended IRF values normalized to the maximum.
        """
        data = numpy.zeros(self.data.values.shape)
        for i, x in enumerate(self.IRF.values):
            data[self.IRFStart + i] = x
        return data / data.max()

    def trimIRF(self, IRF):
        """
        Trims the IRF data.

        Args:
            IRF (Data1D): The IRF data to trim.

        Returns:
            None
        """
        self.IRFStart = 0  # lastZero+1
        self.IRF = IRF
        self.IRF.trim()

    def deconvolve(self, eps=None):
        """
        Deconvolves the spectrum data using the IRF.

        Args:
            eps (optional): The epsilon value for deconvolution.

        Returns:
            None
        """
        self.data.deconvolve(self.IRF, eps)


class SpectraWithCommonIRF(SpectrumWithIRF):
    """
    A class representing multiple spectra with a common IRF.
    """

    def __init__(self, axis: Data1D, data: Data2D, IRF: Data1D, identifiers: Data1D):
        """
        Initializes a SpectraWithCommonIRF instance.

        Args:
            axis (Data1D): The axis data for the spectra.
            data (Data2D): The data values for the spectra.
            IRF (Data1D): The common IRF data for the spectra.
            identifiers (Data1D): The identifiers for the spectra.

        Returns:
            None
        """
        super().__init__(axis, data, IRF)
        self.keys = identifiers

    def normalize(self, individual=False):
        """
        Normalizes the spectra data.

        Args:
            individual (bool, optional): If True, normalizes each spectrum individually. Defaults to False.

        Returns:
            None
        """
        if individual:
            self.data.normalizeIndividual()
        else:
            self.data.normalize()
