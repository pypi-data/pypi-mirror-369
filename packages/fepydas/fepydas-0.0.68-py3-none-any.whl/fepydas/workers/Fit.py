#!/usr/bin/python3
import sys
from os.path import dirname, realpath, join
import numpy
from multiprocessing.pool import Pool
from pathos.multiprocessing import ProcessPool
import pickle
from inspect import getsource
from datetime import datetime
from lmfit import Parameters, minimize, fit_report, Model
from lmfit.model import ModelResult
from lmfit.models import LinearModel
from fepydas.libs.fit_functions import (
    BiExponential,
    BiExponentialTail,
    Exponential,
    Gaussian,
    Lorentzian,
    Linear,
    TriExponential,
    Quadratic,
)
from fepydas.datatypes.Data import Transformation
from scipy.signal import convolve
from typing import List, Dict, Union, Optional
import matplotlib.pyplot as plt
import copy
from tqdm import tqdm


class Fit:
    """
    A class for fitting data using various fitting functions.
    """

    def __init__(self, function):
        """
        Initializes a Fit instance.

        Args:
            function: The fitting function to use.

        Returns:
            None
        """
        self.function = function

    def saveBinary(self, filename):
        """
        Saves the fit object to a binary file using pickle.

        Args:
            filename (str): The path to the file where the fit object will be saved.

        Returns:
            None
        """
        f = open(filename, "bw")
        pickle.dump(self, f)
        f.close()

    def toTransformation(self):
        """
        Converts the fit results to a Transformation object.

        Returns:
            Transformation: The transformation based on the fit results.
        """
        return Transformation(self.function, self.result.params.valuesdict())

    def initializeParameters(self, parameters: Parameters):
        """
        Initializes the parameters for the fit.

        Args:
            parameters (Parameters): The parameters to initialize.

        Returns:
            None
        """
        self.parameters = parameters

    def residual(self, params, x, data=None, eps=None):
        """
        Calculates the residuals between the fit and the data.

        Args:
            params: The parameters for the fit.
            x (numpy.ndarray): The x values.
            data (optional): The data values to fit. Defaults to None.
            eps (optional): The error values. Defaults to None.

        Returns:
            numpy.ndarray: The calculated residuals.
        """
        parvals = params.valuesdict()
        if eps is not None:
            return (data - self.function(x, **parvals)) * eps
        else:
            return data - self.function(x, **parvals)

    def residualLog(self, params, x, data=None, eps=None):
        """
        Calculates the log residuals between the fit and the data.

        Args:
            params: The parameters for the fit.
            x (numpy.ndarray): The x values.
            data (optional): The data values to fit. Defaults to None.
            eps (optional): The error values. Defaults to None.

        Returns:
            numpy.ndarray: The calculated log residuals.
        """
        parvals = params.valuesdict()
        vals = self.function(x, **parvals)
        vals = numpy.maximum(vals, numpy.full_like(vals, 1e-9))
        if eps is not None:
            return (numpy.log(data) - numpy.log(vals)) * eps
        else:
            return numpy.log(data) - numpy.log(vals)

    def convolve(self, signal, ref):
        """
        Convolves the signal with a reference function.

        Args:
            signal (numpy.ndarray): The signal to convolve.
            ref (numpy.ndarray): The reference function.

        Returns:
            numpy.ndarray: The convolved signal.
        """
        return convolve(signal, ref, mode="full")[: len(signal)]

    def convolutedResidual(self, params, x, data=None, irf=None):
        """
        Calculates the residuals for a convoluted fit.

        Args:
            params: The parameters for the fit.
            x (numpy.ndarray): The x values.
            data (optional): The data values to fit. Defaults to None.
            irf (optional): The instrument response function. Defaults to None.

        Returns:
            numpy.ndarray: The calculated convoluted residuals.
        """
        parvals = params.valuesdict()
        return data - self.convolve(self.function(x, **parvals), irf)

    def fit(self, x, y, eps=None, nan_policy="raise", log=False):
        """
        Fits the data using the specified fitting method.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.
            eps (optional): The error values. Defaults to None.
            nan_policy (str, optional): The policy for handling NaN values. Defaults to "raise".
            log (bool, optional): If True, uses log fitting. Defaults to False.

        Returns:
            The result of the fitting process.
        """
        if log:
            self.result = minimize(
                self.residualLog,
                self.parameters,
                args=(x, y, eps),
                method="leastsq",
                nan_policy=nan_policy,
            )
        else:
            self.result = minimize(
                self.residual,
                self.parameters,
                args=(x, y, eps),
                method="leastsq",
                nan_policy=nan_policy,
            )
        return self.result

    def fitSpectrum(self, spectrum):
        """
        Fits a spectrum using the fitting method.

        Args:
            spectrum: The spectrum to fit.

        Returns:
            The result of the fitting process.
        """
        return self.fit(spectrum.axis.values, spectrum.data.values)

    def batchFit(self, x, y, log=False):
        """
        Fits a batch of data.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.
            log: whether to use logarighmic residuals
        Returns:
            None
        """
        print("BatchFit", x.shape, y.shape)
        args = {}
        for i in range(y.shape[0]):
            args[i] = [x, y[i]]
        self.executeBatchFit(self.fit, args=args, kwds={"log": log})

    def convolutedFit(self, x, y, irf):
        """
        Fits the data using a convoluted fitting method.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.
            irf (numpy.ndarray): The instrument response function.

        Returns:
            The result of the fitting process.
        """
        self.result = minimize(
            self.convolutedResidual, self.parameters, args=(x, y, irf)
        )
        return self.result

    def convolutedBatchFit(self, x, y, irf):
        """
        Fits a batch of data using a convoluted fitting method.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.
            irf (numpy.ndarray): The instrument response function.

        Returns:
            None
        """
        args = {}
        for i in range(y.shape[0]):
            args[i] = [x, y[i], irf]
        self.executeBatchFit(self.convolutedFit, args, log=log)

    def executeBatchFit(self, func, args, **kwargs):
        """
        Executes batch fitting using multiprocessing.

        Args:
            func: The fitting function to execute.
            args (dict): The arguments for the fitting function.

        Returns:
            None
        """
        pool = Pool()
        jobs = {}
        for key in args.keys():
            jobs[key] = pool.apply_async(func, args[key], **kwargs)
        results = {}
        for key in args.keys():
            results[key] = jobs[key].get(1000)
        self.results = results

    def batchEvaluate(self, x):
        """
        Evaluates the fitted model for a batch of x values.

        Args:
            x (numpy.ndarray): The x values to evaluate.

        Returns:
            numpy.ndarray: The evaluated data.
        """
        data = numpy.ndarray(shape=(len(self.results.keys()), len(x)))
        for key in self.results.keys():
            pars = self.results[key].params.valuesdict()
            data[key, :] = self.function(x, **pars)
        return data

    def batchEvaluateConvolution(self, x, irf):
        """
        Evaluates the fitted model for a batch of x values with convolution.

        Args:
            x (numpy.ndarray): The x values to evaluate.
            irf (numpy.ndarray): The instrument response function.

        Returns:
            numpy.ndarray: The evaluated convolved data.
        """
        data = self.batchEvaluate(x)
        for i in range(data.shape[0]):
            data[i, :] = self.convolve(data[i, :], irf)
        return data

    def evaluate(self, x):
        """
        Evaluates the fitted model for the given x values.

        Args:
            x (numpy.ndarray): The x values to evaluate.

        Returns:
            numpy.ndarray: The evaluated data based on the fitted parameters.
        """
        parvals = self.result.params.valuesdict()
        return self.function(x, **parvals)

    def evaluateInput(self, x):
        """
        Evaluates the model using the input parameters.

        Args:
            x (numpy.ndarray): The x values to evaluate.

        Returns:
            numpy.ndarray: The evaluated data based on the input parameters.
        """
        parvals = self.parameters.valuesdict()
        return self.function(x, **parvals)

    def evaluateConvolution(self, x, irf):
        """
        Evaluates the convolution of the fitted model with the IRF.

        Args:
            x (numpy.ndarray): The x values to evaluate.
            irf (numpy.ndarray): The instrument response function.

        Returns:
            numpy.ndarray: The convolved data.
        """
        return self.convolve(self.evaluate(x), irf)

    def startReport(self, filename):
        """
        Starts a report for the fitting process.

        Args:
            filename (str): The path to the file where the report will be saved.

        Returns:
            file object: The opened file object for writing the report.
        """
        f = open(filename, "w")
        f.write("Generated by Fit: {0}\n".format(self.__class__.__name__))
        f.write("Time: {0}\n".format(datetime.now()))
        f.write("Model: {0}\n".format(self.function.__name__))
        f.write("{0}\n".format("\n".join(getsource(self.function).split("\n")[1:-1])))
        f.write("Input Parameters: \n")
        for p in self.parameters.keys():
            f.write(
                "  {0}:\t{1}\t[{2}:{3}]\n".format(
                    p,
                    self.parameters[p].value,
                    self.parameters[p].min,
                    self.parameters[p].max,
                )
            )
        f.write("---\n")
        return f

    def saveReport(self, filename):
        """
        Saves the fitting report to a file.

        Args:
            filename (str): The path to the file where the report will be saved.

        Returns:
            None
        """
        f = self.startReport(filename)
        params = self.parameters.keys()
        f.write("Parameter\tValue\tError\n")
        for p in params:
            f.write(
                "{0}\t{1}\t{2}\n".format(
                    p, self.result.params[p].value, self.result.params[p].stderr
                )
            )
        f.write(
            "\nnfev\t{0}\tchisqr\t{1}\tredchi\t{2}\n".format(
                self.result.nfev, self.result.chisqr, self.result.redchi
            )
        )
        f.close()

    def batchSaveReport(self, filename, labels):
        """
        Saves a batch report of fitting results to a file.

        Args:
            filename (str): The path to the file where the report will be saved.
            labels (list): The labels for the datasets in the report.

        Returns:
            None
        """
        f = self.startReport(filename)
        keys = self.results.keys()
        params = self.parameters.keys()
        f.write("Dataset")
        for p in params:
            f.write("\t{0}\t{0}Error".format(p))
        f.write("\tnfev\tchisqr\tredchi")
        f.write("\n")
        for k in keys:
            f.write("{0}".format(labels[k]))
            for p in params:
                f.write(
                    "\t{0}\t{1}".format(
                        self.results[k].params[p].value,
                        self.results[k].params[p].stderr,
                    )
                )
            f.write(
                "\t{0}\t{1}\t{2}".format(
                    self.results[k].nfev, self.results[k].chisqr, self.results[k].redchi
                )
            )
            f.write("\n")
        f.close()

    def initializeAutoFromSpectrum(self, spectrum):
        """
        Initializes the fitting parameters automatically from a spectrum.

        Args:
            spectrum: The spectrum object to initialize from.

        Returns:
            None
        """
        self.initializeAuto(spectrum.axis.values, spectrum.data.values)

    def saveLMfitReport(self, filepath):
        """
        Saves the fit report generated by the lmfit result object to a file.

        Args:
            filepath: The file path where the fit report will be written.

        Returns:
            None
        """
        with open(filepath, "w") as f:
            f.write(fit_report(self.result))


def fit_simple_pool_helper(args: tuple) -> Union[ModelResult, Exception]:
    """
    Do a single fit. Wrapper for pathos.ProcessPool.
    """
    model, x, y, p0s, fit_kwargs = args
    try:
        if numpy.all(numpy.isnan(y)):
            result = ModelResult(model, p0s)
            result.success = False
            result.message = "Input data contains only NaNs."
            return result

        y_err = fit_kwargs.pop("y_err", None)
        if y_err is not None:
            return model.fit(data=y, x=x, params=p0s, weights=1 / y_err, **fit_kwargs)
        else:
            return model.fit(data=y, x=x, params=p0s, **fit_kwargs)
    except Exception as e:
        # An exception is returned, instead of crashing the process
        return e


class FitSimple:
    """A class for fitting data using a simple lmfit pipeline.

    This class provides a streamlined workflow for fitting one-dimensional (a single
    spectrum) or two-dimensional (a collection of spectra) datasets using
    `lmfit` models. It handles parameter guessing, fitting, evaluation, and
    saving of results.

    Attributes:
        function (lmfit.model.Model): The lmfit Model instance used for fitting.
        spectrumdataset (Spectrum, ...): The input data object containing axis and data values.
        ydims (int): The number of dimensions of the y-data (1 for a single
            spectrum, 2 for a collection).
        params (Union[Parameters, List[Parameters]]): The parameters for the model.
            This can be a single `Parameters` object (for 1D data) or a list of
            `Parameters` objects (for 2D data). It is initialized by `initguess`
            or can be set manually with `setinitparams`.
        results (Union[ModelResult, List[ModelResult]]): The fit results.
            This will be a single `ModelResult` object or a list of them, populated
            after the `fit` method is called.
    """

    def __init__(self, function: Model, spectrum):
        """Initializes the FitSimple instance.

        Sets up the fitting object with a specified `lmfit` model and the dataset
        to be analyzed.

        Args:
            function (lmfit.model.Model): The `lmfit` model to be used for the
                fitting procedure (e.g., `models.GaussianModel()`).
            spectrum (Spectrum, ...): An object containing the spectral data. It must
                have an `axis.values` attribute (1D NumPy array for the
                x-axis) and a `data.values` attribute (1D or 2D NumPy array
                for the y-axis data).
        """
        self.function: Model = function
        self.spectrumdataset = spectrum
        self.ydims: int = spectrum.data.values.ndim
        self.params: Optional[Union[Parameters, List[Parameters]]] = None
        self.results: Optional[Union[ModelResult, List[ModelResult]]] = None

    def initguess(self):
        """Generates initial parameter guesses from the data.

        This method uses the `guess()` function of the provided `lmfit` model
        to automatically estimate starting parameters. For 1D data, it creates a
        single `Parameters` object. For 2D data, it iterates through each
        spectrum to create a list of `Parameters` objects.

        The guessed parameters are stored in the `self.params` attribute.

        Raises:
            ValueError: If the dimension of the data is not 1 or 2.
        """
        if self.ydims == 1:
            self.params = self.function.guess(
                x=self.spectrumdataset.axis.values,
                data=self.spectrumdataset.data.values,
            )
        elif self.ydims == 2:
            self.params = []
            for singlespectrum in self.spectrumdataset.data.values:
                self.params.append(
                    self.function.guess(
                        x=self.spectrumdataset.axis.values, data=singlespectrum
                    )
                )
        else:
            raise ValueError("Data dimension must be 1 or 2 for initial guess.")

    def setinitparams(self, parameters: Union[Parameters, List[Parameters]]):
        """Sets the initial parameters for the fit manually.

        This method allows the user to override the automatic parameter guessing
        and provide their own initial `Parameters`.

        Args:
            parameters (Union[Parameters, List[Parameters]]): For a 1D fit, this
                should be a single `lmfit.Parameters` object. For a 2D fit, this
                should be a list of `lmfit.Parameters` objects, one for each
                spectrum in the dataset.
        """
        self.params = parameters

    def fitxy(
        self,
        x: numpy.ndarray,
        y: numpy.ndarray,
        p0s: Parameters,
        y_err: Optional[numpy.ndarray] = None,
        **kwargs,
    ) -> ModelResult:
        """Performs a single fit on a given x-y dataset.

        This is a low-level fitting method that takes explicit x, y, and parameter
        data. It can optionally perform a weighted fit if y-errors are provided.

        Args:
            x (numpy.ndarray): The independent variable (x-axis data).
            y (numpy.ndarray): The dependent variable (y-axis data).
            p0s (Parameters): An `lmfit.Parameters` object with initial values.
            y_err (Optional[numpy.ndarray]): Optional array of standard deviations
                for y. If provided, the fit will be weighted by `1 / y_err`.
            **kwargs: Additional keyword arguments to be passed directly to the
                `lmfit.model.Model.fit()` method.

        Returns:
            ModelResult: The `lmfit` result object for this single fit.
        """
        if y_err is not None:
            return self.function.fit(
                data=y, x=x, params=p0s, weights=1 / y_err, **kwargs
            )
        else:
            return self.function.fit(data=y, x=x, params=p0s, **kwargs)

    def saveBinary(self, filename: str):
        """Saves the entire FitSimple object to a binary file using pickle.

        Serializes the current state of the object, including the model, data,
        parameters, and results, allowing for later restoration.

        Warning:
            The pickle protocol is specific to Python and may not be compatible
            across different versions. Loading a pickled object from an
            untrusted source can be a security risk.

        Args:
            filename (str): The path to the file where the object will be saved.
                A '.pkl' extension is recommended.
        """
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    def _apply_dynamic_bounds(
        self,
        params: Parameters,
        bounds_tol: Dict[str, float],
        respect_initial_bounds: bool = False,
    ) -> Parameters:
        for name, rel_tol in bounds_tol.items():
            if name in params:
                p = params[name]
                value = p.value

                new_min = value * (1 - abs(rel_tol))
                new_max = value * (1 + abs(rel_tol))

                if respect_initial_bounds:
                    final_min = max(p.min, new_min)
                    final_max = min(p.max, new_max)
                    p.set(min=final_min, max=final_max)
                else:
                    p.set(min=new_min, max=new_max)
        return params

    def fit(
        self,
        multiprocessing: bool = True,
        chunksize: int = 5,
        bounds_tolerance: Optional[Dict[str, float]] = None,
        respect_initial_bounds: bool = False,
        cores: Optional[int] = None,
        print_report: bool = False,
        **kwargs,
    ):
        """
        Performs fitting for the entire dataset.

        This method implements different strategies for 2D data, depending on whether
        `self.params` is a list or a single object, and whether multiprocessing is enabled.

        Args:
            multiprocessing (bool): If True, uses `pathos.multiprocessing.ProcessPool`
            for parallel fitting.
            chunksize (int): Only relevant when `multiprocessing=True` and
            `self.params` is a single object. Determines the size of the
            blocks processed in parallel.
            bounds_tolerance (Optional[Dict[str, float]]): If `self.params` is a
            single object, this can be used to pass tolerances for dynamic
            adjustment of parameter bounds. Example: `{'center': 0.1}` for +/-10%.
            respect_initial_bounds (bool): If True and `bounds_tolerance` is used,
            the dynamically generated bounds will not extend beyond any initial
            bounds already set on the parameters. Defaults to False.
            cores (Optional[int]): Number of CPU cores to use for pathos.
            By default, all available cores are used.
            print_report (bool): If True, prints the lmfit report for each fit.
            **kwargs: Additional arguments passed to `lmfit.model.fit`.
        """
        if self.params is None:
            raise TypeError(
                "Initial parameters not set. Call 'initguess()' or 'setinitparams()' first."
            )

        # Case 1: 1D-data
        if self.ydims == 1:
            self.results = self.fitxy(
                x=self.spectrumdataset.axis.values,
                y=self.spectrumdataset.data.values,
                p0s=self.params,
                **kwargs,
            )
            if print_report:
                print(self.results.fit_report())
            return
        # Case 2: 2D-data
        elif self.ydims == 2:
            y_data = self.spectrumdataset.data.values
            num_spectra = len(y_data)
            self.results = []

            # One parameter set per spectrum (default)
            if isinstance(self.params, list):
                if len(self.params) != num_spectra:
                    raise ValueError(
                        f"Mismatch: Got {len(self.params)} parameter sets for {num_spectra} spectra."
                    )

                if not multiprocessing:
                    pbar = tqdm(
                        range(num_spectra),
                        desc="Standard Sequential Fitting",
                        colour="green",
                    )
                    self.results = []
                    for i in pbar:
                        result = self.fitxy(
                            x=self.spectrumdataset.axis.values,
                            y=y_data[i],
                            p0s=self.params[i],
                            **kwargs,
                        )
                        self.results.append(result)
                else:
                    args_list = [
                        (
                            self.function,
                            self.spectrumdataset.axis.values,
                            y_data[i],
                            self.params[i],
                            copy.deepcopy(kwargs),
                        )
                        for i in range(num_spectra)
                    ]
                    with ProcessPool(nodes=cores) as pool:
                        self.results = list(
                            tqdm(
                                pool.imap(fit_simple_pool_helper, args_list),
                                total=num_spectra,
                                desc="Fully Parallel Fitting",
                                colour="green",
                            )
                        )

            # One set of Parameters for all fits
            elif isinstance(self.params, Parameters):
                current_p0s = copy.deepcopy(self.params)

                if not multiprocessing:
                    pbar = tqdm(
                        range(num_spectra),
                        desc="Sequential Propagation Fitting",
                        colour="green",
                    )
                    self.results = []
                    for i in pbar:
                        if i > 0 and bounds_tolerance:
                            current_p0s = self._apply_dynamic_bounds(
                                current_p0s,
                                bounds_tolerance,
                                respect_initial_bounds=respect_initial_bounds,
                            )

                        result = self.fitxy(
                            x=self.spectrumdataset.axis.values,
                            y=y_data[i],
                            p0s=current_p0s,
                            **kwargs,
                        )
                        self.results.append(result)

                        if isinstance(result, ModelResult) and result.success:
                            current_p0s = result.params

                else:
                    num_chunks = int(numpy.ceil(num_spectra / chunksize))
                    self.results = []
                    with ProcessPool(nodes=cores) as pool:
                        for i in range(num_chunks):
                            if i > 0 and bounds_tolerance:
                                current_p0s = self._apply_dynamic_bounds(
                                    current_p0s,
                                    bounds_tolerance,
                                    respect_initial_bounds=respect_initial_bounds,
                                )

                            start_idx = i * chunksize
                            end_idx = min((i + 1) * chunksize, num_spectra)

                            args_list = [
                                (
                                    self.function,
                                    self.spectrumdataset.axis.values,
                                    y_data[j],
                                    current_p0s,
                                    copy.deepcopy(kwargs),
                                )
                                for j in range(start_idx, end_idx)
                            ]

                            pbar_desc = f"Fitting Chunk {i+1}/{num_chunks}"
                            chunk_results = list(
                                tqdm(
                                    pool.imap(fit_simple_pool_helper, args_list),
                                    total=len(args_list),
                                    desc=pbar_desc,
                                    colour="green",
                                )
                            )
                            self.results.extend(chunk_results)

                            for res in chunk_results:
                                if isinstance(res, ModelResult) and res.success:
                                    current_p0s = res.params
                                    break
            else:
                raise TypeError(
                    f"self.params must be of type 'Parameters' or 'list', but got {type(self.params)}"
                )

            if print_report:
                for i, result in enumerate(self.results):
                    print(f"\n--- Fit Report for Spectrum {i} ---")
                    if isinstance(result, ModelResult):
                        print(result.fit_report())
                    else:
                        print(f"Fit failed with an exception: {result}")

    def evaluate(self, x: numpy.ndarray, i: Optional[int] = None) -> numpy.ndarray:
        """Evaluates the fitted model at given x-values.

        Uses the best-fit parameters stored in `self.results` to generate the
        model's curve.

        Args:
            x (numpy.ndarray): The x-values at which to evaluate the model.
            i (Optional[int]): For 2D datasets, this is the index of the fit result
                to use for the evaluation. This argument is ignored for 1D data.

        Returns:
            numpy.ndarray: The calculated y-values of the model.

        Raises:
            TypeError: If the model has not been fitted yet (`self.results` is None).
            ValueError: If the data is 2D but the index `i` is not provided.
        """
        if self.results is None:
            raise TypeError(
                "Fit has not been performed yet. Call the 'fit()' method first."
            )

        if self.ydims == 1:
            return self.function.eval(self.results.params, x=x)
        elif self.ydims == 2:
            if i is None:
                raise ValueError(
                    "For 2D data, the index 'i' of the spectrum to evaluate must be provided."
                )
            return self.function.eval(self.results[i].params, x=x)
        else:
            raise ValueError(f"Unsupported data dimension: {self.ydims}")

    def saveLMfitReport(self, filepath: str):
        """Saves the text-based fit report(s) to a file.

        For 1D data, a single report is saved. For 2D data, a separate report
        is saved for each fit, with the index appended to the filename.

        Args:
            filepath (str): The base path for the output file(s). The file
                extension '.txt' will be added automatically. For 2D data,
                the filename will be 'filepath_0.txt', 'filepath_1.txt', etc.

        Raises:
            TypeError: If the model has not been fitted yet (`self.results` is None).
        """
        if self.results is None:
            raise TypeError(
                "Fit has not been performed yet. Call the 'fit()' method first."
            )

        if self.ydims == 1:
            with open(f"{filepath}.txt", "w") as f:
                f.write(self.results.fit_report())
        elif self.ydims == 2:
            for i, result in enumerate(self.results):
                with open(f"{filepath}_{i}.txt", "w") as f:
                    f.write(result.fit_report())

    def plot(self, baseplot, i=None):
        if self.ydims == 1:
            plot = baseplot
            plot.bottom.plot(
                self.spectrumdataset.axis.values, self.spectrumdataset.data.values
            )
            plot.bottom.plot(
                self.spectrumdataset.axis.values,
                self.evaluate(self.spectrumdataset.axis.values),
                label="fit",
            )
            plot.bottom.legend()
            return plot
        elif self.ydims == 2:
            if i is None:
                plots = []
                for i in range(len(self.spectrumdataset.data.values)):
                    plot = copy.deepcopy(baseplot)
                    plot.bottom.plot(
                        self.spectrumdataset.axis.values,
                        self.spectrumdataset.data.values[i],
                    )
                    plot.bottom.plot(
                        self.spectrumdataset.axis.values,
                        self.evaluate(self.spectrumdataset.axis.values, i),
                        label="fit",
                    )
                    plot.bottom.legend()
                    plot.bottom.set_title(
                        f"{i} - {self.spectrumdataset.keys.values[i]}"
                    )
                    plots.append(plot)
                return plots
            elif isinstance(i, int):
                plot = baseplot
                plot.bottom.plot(
                    self.spectrumdataset.axis.values,
                    self.spectrumdataset.data.values[i],
                )
                plot.bottom.plot(
                    self.spectrumdataset.axis.values,
                    self.evaluate(self.spectrumdataset.axis.values, i),
                    label="fit",
                )
                plot.bottom.legend()
                return (
                    plot,
                    self.spectrumdataset.keys.values[i],
                    self.spectrumdataset.keys.datatype,
                )


class LorentzianFit(Fit):
    """
    A class for fitting data using a Lorentzian function.
    """

    def __init__(self):
        """
        Initializes a LorentzianFit instance.

        Returns:
            None
        """
        super().__init__(Lorentzian)


class SpectralLine(LorentzianFit):
    """
    A class for fitting spectral lines using a Lorentzian function.
    """

    def __init__(self):
        """
        Initializes a SpectralLine instance.

        Returns:
            None
        """
        super().__init__()

    def initializeAuto(self, x, y):
        """
        Initializes fitting parameters automatically based on provided x and y data.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.

        Returns:
            None
        """
        bg = (y[0] + y[-1]) / 2
        I = numpy.max(y) - bg
        x0 = x[numpy.argmax(y)]
        idx = numpy.where(y > bg + I / 2)[0]
        fwhm = numpy.abs(x[idx[-1]] - x[idx[0]])
        params = Parameters()
        params.add("bg", value=bg)
        params.add("I", value=I)
        params.add("x0", value=x0)
        params.add("fwhm", value=fwhm)
        self.initializeParameters(params)


class GaussianFit(Fit):
    """
    A class for fitting data using a Gaussian function.
    """

    def __init__(self):
        """
        Initializes a GaussianFit instance.

        Returns:
            None
        """
        super().__init__(Gaussian)

    def initializeAuto(self, x, y):
        """
        Initializes fitting parameters automatically based on provided x and y data.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.

        Returns:
            None
        """
        bg = (y[0] + y[-1]) / 2
        I = numpy.max(y) - bg
        x0 = x[numpy.argmax(y)]
        idx = numpy.where(y > bg + I / 2)[0]
        fwhm = numpy.abs(x[idx[-1]] - x[idx[0]])
        params = Parameters()
        params.add("bg", value=bg)
        params.add("I", value=I)
        params.add("x0", value=x0)
        params.add("fwhm", value=fwhm + x0 / 1000)
        self.initializeParameters(params)


class LimitedGaussianFit(GaussianFit):
    """
    A class for fitting data using a limited Gaussian function.
    """

    def __init__(self):
        """
        Initializes a LimitedGaussianFit instance.

        Returns:
            None
        """
        super().__init__()

    def initializeAutoLimited(self, x, y, center, range, thresh=1):
        """
        Initializes fitting parameters for a limited Gaussian fit based on provided x and y data.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.
            center (float): The center value for the fit.
            range (float): The range around the center to consider for fitting.
            thresh (float, optional): The threshold for peak detection. Defaults to 1.

        Returns:
            tuple: A tuple containing the x and y values used for fitting, or False if fitting is not possible.
        """
        if (len(numpy.where(y == numpy.max(y))[0])) > 1:
            return False, False
        lowerIdx = (numpy.abs(x - (center - range))).argmin()
        higherIdx = (numpy.abs(x - (center + range))).argmin()
        if numpy.abs(higherIdx - lowerIdx) < 15:
            return False, False
        if higherIdx < lowerIdx:
            t = lowerIdx
            lowerIdx = higherIdx
            higherIdx = t
        x = x[lowerIdx:higherIdx]
        y = y[lowerIdx:higherIdx]
        if numpy.amax(y) <= thresh:
            return False, False
        self.initializeAuto(x, y)
        return x, y


class LinearFit(Fit):
    """
    A class for fitting data using a linear function.
    """

    def __init__(self):
        """
        Initializes a LinearFit instance.

        Returns:
            None
        """
        super().__init__(Linear)


class CalibrationFit(LinearFit):
    """
    A class for fitting calibration data using a linear function.
    """

    def __init__(self):
        """
        Initializes a CalibrationFit instance.

        Returns:
            None
        """
        super().__init__()

    def initializeAuto(self):
        """
        Initializes fitting parameters automatically for calibration.

        Returns:
            None
        """
        params = Parameters()
        params.add("a", value=1)
        params.add("b", value=0)
        self.initializeParameters(params)


class QuadraticFit(Fit):
    """
    A class for fitting data using a quadratic function.
    """

    def __init__(self):
        """
        Initializes a QuadraticFit instance.

        Returns:
            None
        """
        super().__init__(Quadratic)


class QuadraticCalibrationFit(QuadraticFit):
    """
    A class for fitting calibration data using a quadratic function.
    """

    def __init__(self):
        """
        Initializes a QuadraticCalibrationFit instance.

        Returns:
            None
        """
        super().__init__()

    def initializeAuto(self):
        """
        Initializes fitting parameters automatically for quadratic calibration.

        Returns:
            None
        """
        params = Parameters()
        params.add("a", value=0)
        params.add("b", value=1)
        params.add("c", value=0)
        self.initializeParameters(params)


class AutomaticCalibration(QuadraticCalibrationFit):
    """
    A class for performing automatic calibration based on a spectrum and reference data.
    """

    def __init__(self, spectrum, references, threshold=10, width=10):
        """
        Initializes an AutomaticCalibration instance.

        Args:
            spectrum (Spectrum): The spectrum to calibrate.
            references (numpy.ndarray): The reference values for calibration.
            threshold (float, optional): The threshold for peak detection. Defaults to 10.
            width (int, optional): The width for peak detection. Defaults to 10.

        Returns:
            None
        """
        super().__init__()
        peaks = spectrum.identifyPeaks(threshold=threshold, width=width)
        SpectralFit = SpectralLine()
        peakVals = []
        peakErrs = []
        for peak in peaks:
            x, y = (
                spectrum.axis.values[peak[0] : peak[1]],
                spectrum.data.values[peak[0] : peak[1]],
            )
            SpectralFit.initializeAuto(x, y)
            SpectralFit.fit(x, y)
            peakVals.append(SpectralFit.result.params["x0"].value)
            peakErrs.append(SpectralFit.result.params["x0"].stderr)
        references = numpy.array(references, dtype=numpy.float64)
        peakVals = numpy.array(peakVals, dtype=numpy.float64)
        peakErrs = numpy.array(peakErrs, dtype=numpy.float64)
        idx = numpy.where(~numpy.isnan(references))[0]
        print("Calibration with ", references, peakVals, idx)
        self.initializeAuto()
        self.fit(peakVals[idx], references[idx])


class ExponentialFit(Fit):
    """
    A class for fitting data using an exponential function.
    """

    def __init__(self):
        """
        Initializes an ExponentialFit instance.

        Returns:
            None
        """
        super().__init__(Exponential)

    def initialize(self, bg, I, x0, tau, rise):
        """
        Initializes the parameters for the exponential fit.

        Args:
            bg (float): The background level.
            I (float): The peak intensity.
            x0 (float): The position of the peak.
            tau (float): The decay constant.
            rise (float): The rise time.

        Returns:
            None
        """
        params = Parameters()
        params.add("bg", value=bg)
        params.add("I", value=I, min=0)
        params.add("x0", value=x0)
        params.add("tau", value=tau, min=0)
        params.add("rise", value=rise, min=0)
        self.initializeParameters(params)

    def initializeAuto(self, x, y):
        """
        Initializes fitting parameters automatically based on provided x and y data.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.

        Returns:
            None
        """
        params = Parameters()
        params.add("bg", value=y[0])
        params.add("I", value=numpy.max(y) - y[0], min=0)
        # params.add("I_rise",value=numpy.max(y)-y[0],min=0)
        params.add("x0", value=x[numpy.argmax(y)])
        params.add("tau", value=1, min=0)
        params.add("rise", value=0.001, min=0)
        self.initializeParameters(params)


class BiExponentialFit(Fit):
    """
    A class for fitting data using a bi-exponential function.
    """

    def __init__(self):
        """
        Initializes a BiExponentialFit instance.

        Returns:
            None
        """
        super().__init__(BiExponential)

    def initializeAuto(self, x, y):
        """
        Initializes fitting parameters automatically based on provided x and y data.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.

        Returns:
            None
        """
        params = Parameters()
        params.add("bg", value=y[0])
        params.add("I_1", value=(numpy.max(y) - y[0]) / 2, min=0)
        params.add("I_2", value=(numpy.max(y) - y[0]) / 2, min=0)
        params.add("x0", value=x[numpy.argmax(y)])
        params.add("tau_1", value=5, min=0)
        params.add("tau_2", value=50, min=0)
        params.add("rise", value=0.001, min=0)
        self.initializeParameters(params)

    def initialize(self, I_1, I_2, tau_1, tau_2, x0=0, rise=0.001):
        """
        Initializes the parameters for the bi-exponential fit.

        Args:
            I_1 (float): The intensity of the first exponential.
            I_2 (float): The intensity of the second exponential.
            tau_1 (float): The decay constant for the first exponential.
            tau_2 (float): The decay constant for the second exponential.
            x0 (float, optional): The position of the peak. Defaults to 0.
            rise (float, optional): The rise time. Defaults to 0.001.

        Returns:
            None
        """
        params = Parameters()
        params.add("bg", value=0)
        params.add("I_1", value=I_1, min=0)
        params.add("I_2", value=I_2, min=0)
        params.add("x0", value=x0)
        params.add("tau_1", value=tau_1, min=0)
        params.add("tau_2", value=tau_2, min=0)
        params.add("rise", value=rise, min=0)
        self.initializeParameters(params)


class TriExponentialFit(Fit):
    """
    A class for fitting data using a tri-exponential function.
    """

    def __init__(self):
        """
        Initializes a TriExponentialFit instance.

        Returns:
            None
        """
        super().__init__(TriExponential)

    def initializeAuto(self, x, y):
        """
        Initializes fitting parameters automatically based on provided x and y data.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.

        Returns:
            None
        """
        params = Parameters()
        params.add("bg", value=y[0])
        params.add("I_1", value=(numpy.max(y) - y[0]) / 3, min=0)
        params.add("I_2", value=(numpy.max(y) - y[0]) / 3, min=0)
        params.add("I_3", value=(numpy.max(y) - y[0]) / 3, min=0)
        params.add("x0", value=x[numpy.argmax(y)])
        params.add("tau_1", value=5, min=0)
        params.add("tau_2", value=50, min=0)
        params.add("tau_3", value=500, min=0)
        params.add("rise", value=0.001, min=0)
        self.initializeParameters(params)

    def initialize(self, I_1, I_2, I_3, tau_1, tau_2, tau_3, x0=0, rise=0.001):
        """
        Initializes the parameters for the tri-exponential fit.

        Args:
            I_1 (float): The intensity of the first exponential.
            I_2 (float): The intensity of the second exponential.
            I_3 (float): The intensity of the third exponential.
            tau_1 (float): The decay constant for the first exponential.
            tau_2 (float): The decay constant for the second exponential.
            tau_3 (float): The decay constant for the third exponential.
            x0 (float, optional): The position of the peak. Defaults to 0.
            rise (float, optional): The rise time. Defaults to 0.001.

        Returns:
            None
        """
        params = Parameters()
        params.add("bg", value=0)
        params.add("I_1", value=I_1, min=0)
        params.add("I_2", value=I_2, min=0)
        params.add("I_3", value=I_3, min=0)
        params.add("x0", value=x0)
        params.add("tau_1", value=tau_1, min=0)
        params.add("tau_2", value=tau_2, min=0)
        params.add("tau_3", value=tau_3, min=0)
        params.add("rise", value=rise, min=0)
        self.initializeParameters(params)


class BiExponentialTailFit(Fit):
    """
    A class for fitting data using a bi-exponential tail function.
    """

    def __init__(self):
        """
        Initializes a BiExponentialTailFit instance.

        Returns:
            None
        """
        super().__init__(BiExponentialTail)

    def initializeAuto(self, x, y):
        """
        Initializes fitting parameters automatically based on provided x and y data.

        Args:
            x (numpy.ndarray): The x values for fitting.
            y (numpy.ndarray): The y values for fitting.

        Returns:
            None
        """
        params = Parameters()
        params.add("bg", value=y[-1])
        params.add("I_1", value=(numpy.max(y) - y[-1]) / 2, min=0)
        params.add("I_2", value=(numpy.max(y) - y[-1]) / 2, min=0)
        params.add("tau_1", value=5, min=0)
        params.add("tau_2", value=50, min=0)
        self.initializeParameters(params)

    def initialize(self, I_1, I_2, tau_1, tau_2):
        """
        Initializes the parameters for the bi-exponential tail fit.

        Args:
            I_1 (float): The intensity of the first exponential.
            I_2 (float): The intensity of the second exponential.
            tau_1 (float): The decay constant for the first exponential.
            tau_2 (float): The decay constant for the second exponential.

        Returns:
            None
        """
        params = Parameters()
        params.add("bg", value=0)
        params.add("I_1", value=I_1, min=0)
        params.add("I_2", value=I_2, min=0)
        params.add("tau_1", value=tau_1, min=0)
        params.add("tau_2", value=tau_2, min=0)
        self.initializeParameters(params)


def get_current_dir_path():
    """Return the current script directory

    Returns:
        str: path of the current script directory
    """
    return dirname(realpath(sys.argv[0]))


class Calibration:
    """Manages spectral calibration by fitting measured data to reference data.

    This class provides a workflow for calibrating spectral data. It takes measured
    spectral line positions and their corresponding known reference values (e.g., from NIST)
    to establish a calibration function. The calibration is performed using the `lmfit`
    library, allowing for various fitting models (linear by default).

    Once an instance is calibrated, it can be used to apply the transformation
    to any other spectral data.

    Attributes:
        spectral_lines (list): The measured spectral line positions provided during initialization.
        NIST_spectral_lines (list): The reference spectral line positions (e.g., from NIST)
            provided during initialization.
        model (lmfit.model.Model): The `lmfit` model used for the calibration fit.
        unit (str): The unit for the spectral data (e.g., 'nm'), used for plotting.
        fitted_p0s (lmfit.parameter.Parameters): The collection of fitted parameters
            determined by the calibration process.
    """

    def __init__(self, spectral_lines, NIST_spectral_lines, **kwargs):
        """Initializes the Calibration object and performs the calibration.

        This method immediately calls `get_spectral_calibration` with the
        provided arguments, running the entire calibration process upon object
        creation.

        Args:
            spectral_lines (list): A list of measured spectral line positions.
            NIST_spectral_lines (list): A list of corresponding reference spectral
                line positions.
            **kwargs: Arbitrary keyword arguments passed directly to the
                `get_spectral_calibration` method. See its docstring for details
                on available options like `model`, `name`, `show`, etc.
        """
        self.get_spectral_calibration(spectral_lines, NIST_spectral_lines, **kwargs)

    def get_spectral_calibration(
        self,
        spectral_lines,
        NIST_spectral_lines,
        model=LinearModel(),
        name="calibration",
        unit="nm",
        show=False,
        save=True,
        savepath=get_current_dir_path(),
        savetype="pdf",
    ):
        """Calculates and visualizes the spectral calibration.

        This method fits the measured `spectral_lines` to the `NIST_spectral_lines`
        using a specified `lmfit` model. It generates a plot of the fit, which
        can be optionally displayed or saved to a file. The fit results and
        configuration are stored as instance attributes for later use.

        Args:
            spectral_lines (list): Measured spectral lines to calibrate.
            NIST_spectral_lines (list): Corresponding spectral lines from a
                reference source (e.g., NIST).
            model (lmfit.model.Model, optional): `lmfit` model for the calibration
                fit. Defaults to LinearModel().
            name (str, optional): The base name for the saved plot file.
                Defaults to "calibration".
            unit (str, optional): The unit to display in the plot labels.
                Defaults to "nm".
            show (bool, optional): If True, displays the plot after fitting.
                Defaults to False.
            save (bool, optional): If True, saves the plot after fitting.
                Defaults to True.
            savepath (str, optional): The directory path where the plot will be
                saved. Defaults to the current script's directory.
            savetype (str, optional): The file format for the saved plot (e.g.,
                "pdf", "png"). Defaults to "pdf".

        Returns:
            tuple[lmfit.model.Model, lmfit.parameter.Parameters]: A tuple containing
            the `lmfit` model used and the fitted parameters.
        """

        self.spectral_lines = spectral_lines
        self.NIST_spectral_lines = NIST_spectral_lines
        self.model = model
        self.unit = unit

        p0s = model.guess(NIST_spectral_lines, x=spectral_lines)
        out = model.fit(NIST_spectral_lines, x=spectral_lines, params=p0s)

        self.fitted_p0s = out.params

        x_fine = numpy.linspace(
            min(spectral_lines),
            max(spectral_lines),
            endpoint=True,
            num=1000,
        )
        y_fine = model.eval(out.params, x=x_fine)

        plt.plot(spectral_lines, NIST_spectral_lines, "x")
        plt.plot(
            x_fine,
            y_fine,
        )
        plt.xlabel(f"Measured spectral line positions [{unit}]")
        plt.ylabel(f"NIST spectral line positions [{unit}]")

        if save:
            plt.savefig(join(savepath, f"{name}.{savetype}"), bbox_inches="tight")
        if show:
            plt.show()

        plt.close("all")

        print(out.fit_report())

        return model, out.params

    def calculate_calibration(self, x, model=None, params=None):
        """Applies the calculated calibration to a new set of data points.

        Uses the model and fitted parameters stored in the instance to transform
        an array of input values `x` into their calibrated equivalents. The model
        and parameters can be overridden by providing them as arguments.

        Args:
            x (list | numpy.ndarray): The input data axis to be calibrated.
            model (lmfit.model.Model, optional): An `lmfit` model to use for the
                calculation. If None, defaults to the instance's `self.model`.
            params (lmfit.parameter.Parameters, optional): `lmfit` parameters to
                use for the calculation. If None, defaults to the instance's
                `self.fitted_p0s`.

        Returns:
            numpy.ndarray: An array containing the calibrated values corresponding to `x`.
        """
        if model is None:
            model = self.model
        if params is None:
            params = self.fitted_p0s

        return model.eval(params, x=x)

    def apply(self, x, model=None, params=None):
        """A convenience alias for the `calculate_calibration` method.

        This method is a simple wrapper around `calculate_calibration`. It provides
        a shorter, more intuitive name for applying the calibration to data.

        Args:
            x (list | numpy.ndarray): The input data axis to be calibrated.
            model (lmfit.model.Model, optional): An `lmfit` model to use.
                Passed to `calculate_calibration`. Defaults to None.
            params (lmfit.parameter.Parameters, optional): `lmfit` parameters to use.
                Passed to `calculate_calibration`. Defaults to None.

        Returns:
            numpy.ndarray: An array containing the calibrated values.
        """
        return self.calculate_calibration(x, model, params)
