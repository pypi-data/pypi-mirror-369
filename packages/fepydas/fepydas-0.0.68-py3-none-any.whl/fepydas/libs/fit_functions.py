import numpy
from lmfit import Parameters


def Lorentzian(x, bg=0, I=1, x0=0, fwhm=1):
    """
    Calculates the Lorentzian function.

    Args:
        x (numpy.ndarray): The input values.
        bg (float, optional): The background level. Defaults to 0.
        I (float, optional): The peak intensity. Defaults to 1.
        x0 (float, optional): The position of the peak. Defaults to 0.
        fwhm (float, optional): The full width at half maximum. Defaults to 1.

    Returns:
        numpy.ndarray: The calculated Lorentzian values.
    """
    if I == 0:
        return 0
    t = (x - x0) / (fwhm / 2)
    return bg + I / (1 + t * t)


def Gaussian(x, bg=0, I=1, x0=0, fwhm=1):
    """
    Calculates the Gaussian function.

    Args:
        x (numpy.ndarray): The input values.
        bg (float, optional): The background level. Defaults to 0.
        I (float, optional): The peak intensity. Defaults to 1.
        x0 (float, optional): The position of the peak. Defaults to 0.
        fwhm (float, optional): The full width at half maximum. Defaults to 1.

    Returns:
        numpy.ndarray: The calculated Gaussian values.
    """
    if I == 0:
        return 0
    return I * numpy.exp(-numpy.log(2) * ((x - x0) / (fwhm / 2)) ** 2)


def Linear(x, a=1, b=0):
    """
    Calculates the linear function.

    Args:
        x (numpy.ndarray): The input values.
        a (float, optional): The slope of the line. Defaults to 1.
        b (float, optional): The y-intercept of the line. Defaults to 0.

    Returns:
        numpy.ndarray: The calculated linear values.
    """
    return a * x + b


def Quadratic(x, a=0, b=1, c=0):
    """
    Calculates the quadratic function.

    Args:
        x (numpy.ndarray): The input values.
        a (float, optional): The coefficient for x^2. Defaults to 0.
        b (float, optional): The coefficient for x. Defaults to 1.
        c (float, optional): The constant term. Defaults to 0.

    Returns:
        numpy.ndarray: The calculated quadratic values.
    """
    return a * x**2 + b * x + c


def Exponential(x, bg=0, I=1, x0=0, tau=1, rise=0.001):
    """
    Calculates the exponential function.

    Args:
        x (numpy.ndarray): The input values.
        bg (float, optional): The background level. Defaults to 0.
        I (float, optional): The peak intensity. Defaults to 1.
        x0 (float, optional): The position of the peak. Defaults to 0.
        tau (float, optional): The decay constant. Defaults to 1.
        rise (float, optional): The rise time. Defaults to 0.001.

    Returns:
        numpy.ndarray: The calculated exponential values.
    """
    y = numpy.zeros_like(x)
    y += bg
    decay = numpy.where(x >= x0)

    y[decay] += (
        I * numpy.exp(-(x[decay] - x0) / tau) * (1 - numpy.exp(-(x[decay] - x0) / rise))
    )
    #  notDecay = numpy.where(x<x0)
    #  y[decay]+= I*numpy.exp(-(x[decay]-x0)/tau)
    #  y[notDecay]+= I*numpy.exp(-(x0-x[notDecay])/rise)
    return y


def BiExponential(x, bg=0, x0=0, I_1=1, tau_1=1, I_2=1, tau_2=1, rise=0.001):
    """
    Calculates the bi-exponential function.

    Args:
        x (numpy.ndarray): The input values.
        bg (float, optional): The background level. Defaults to 0.
        x0 (float, optional): The position of the peak. Defaults to 0.
        I_1 (float, optional): The intensity of the first exponential. Defaults to 1.
        tau_1 (float, optional): The decay constant for the first exponential. Defaults to 1.
        I_2 (float, optional): The intensity of the second exponential. Defaults to 1.
        tau_2 (float, optional): The decay constant for the second exponential. Defaults to 1.
        rise (float, optional): The rise time. Defaults to 0.001.

    Returns:
        numpy.ndarray: The calculated bi-exponential values.
    """
    y = numpy.zeros_like(x)
    y += bg
    decay = numpy.where(x >= x0)
    y[decay] += (
        I_1 * numpy.exp(-(x[decay] - x0) / tau_1)
        + I_2 * numpy.exp(-(x[decay] - x0) / tau_2)
    ) * (1 - numpy.exp(-(x[decay] - x0) / rise))
    # notDecay = numpy.where(x<x0)
    # y[decay]+= I_1*numpy.exp(-(x[decay]-x0)/tau_1)+I_2*numpy.exp(-(x[decay]-x0)/tau_2)
    # y[notDecay]+= (I_1+I_2)*numpy.exp(-(x0-x[notDecay])/rise)
    return y


def TriExponential(
    x, bg=0, x0=0, I_1=1, tau_1=1, I_2=1, tau_2=1, I_3=1, tau_3=1, rise=0.001
):
    """
    Calculates the tri-exponential function.

    Args:
        x (numpy.ndarray): The input values.
        bg (float, optional): The background level. Defaults to 0.
        x0 (float, optional): The position of the peak. Defaults to 0.
        I_1 (float, optional): The intensity of the first exponential. Defaults to 1.
        tau_1 (float, optional): The decay constant for the first exponential. Defaults to 1.
        I_2 (float, optional): The intensity of the second exponential. Defaults to 1.
        tau_2 (float, optional): The decay constant for the second exponential. Defaults to 1.
        I_3 (float, optional): The intensity of the third exponential. Defaults to 1.
        tau_3 (float, optional): The decay constant for the third exponential. Defaults to 1.
        rise (float, optional): The rise time. Defaults to 0.001.

    Returns:
        numpy.ndarray: The calculated tri-exponential values.
    """
    y = numpy.zeros_like(x)
    y += bg
    decay = numpy.where(x >= x0)
    notDecay = numpy.where(x < x0)
    y[decay] += (
        I_1 * numpy.exp(-(x[decay] - x0) / tau_1)
        + I_2 * numpy.exp(-(x[decay] - x0) / tau_2)
        + I_3 * numpy.exp(-(x[decay] - x0) / tau_3)
    )
    y[notDecay] += (I_1 + I_2 + I_3) * numpy.exp(-(x0 - x[notDecay]) / rise)
    return y


def BiExponentialTail(x, bg=0, I_1=1, tau_1=1, I_2=1, tau_2=1):
    """
    Calculates the bi-exponential tail function.

    Args:
        x (numpy.ndarray): The input values.
        bg (float, optional): The background level. Defaults to 0.
        I_1 (float, optional): The intensity of the first exponential. Defaults to 1.
        tau_1 (float, optional): The decay constant for the first exponential. Defaults to 1.
        I_2 (float, optional): The intensity of the second exponential. Defaults to 1.
        tau_2 (float, optional): The decay constant for the second exponential. Defaults to 1.

    Returns:
        numpy.ndarray: The calculated bi-exponential tail values.
    """
    y = bg + I_1 * numpy.exp(-(x) / tau_1) + I_2 * numpy.exp(-(x) / tau_2)
    return y
