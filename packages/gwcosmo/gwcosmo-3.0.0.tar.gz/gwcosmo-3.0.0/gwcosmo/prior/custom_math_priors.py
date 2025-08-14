"""
This module collects analytical and numerical probability density functions.
"""

import copy as _copy
import json as _json

import numpy as _np
from scipy.interpolate import interp1d as _interp1d
from scipy.special import erf as _erf
from scipy.special import logsumexp as _logsumexp
from scipy.stats import truncnorm as _truncnorm

from scipy.integrate import cumulative_trapezoid as _cumtrapz
from scipy.integrate import trapezoid as _trapz


def high_pass_filter(mass, mmin, delta_m):
    """
    This function return the value of the window function defined as Eqs B6 and B7 of https://arxiv.org/pdf/2010.14533.pdf

    Parameters
    ----------
    mass: np.array or float
        array of x or masses values
    mmin: float or np.array (in this case len(mmin) == len(mass))
        minimum value of window function
    delta_m: float or np.array (in this case len(delta_m) == len(mass))
        width of the window function

    Returns
    -------
    Values of the window function
    """

    if not isinstance(mass, _np.ndarray):
        mass = _np.array([mass])

    to_ret = _np.ones_like(mass)
    if delta_m == 0:
        return to_ret

    mprime = mass - mmin

    # Defines the different regions of the window function ad in Eq. B6 of  https://arxiv.org/pdf/2010.14533.pdf
    select_window = (mass > mmin) & (mass < (delta_m + mmin))
    select_one = mass >= (delta_m + mmin)
    select_zero = mass <= mmin

    effe_prime = _np.ones_like(mass)

    # Definethe f function as in Eq. B7 of https://arxiv.org/pdf/2010.14533.pdf
    effe_prime[select_window] = _np.exp(
        _np.nan_to_num(
            (delta_m / mprime[select_window]) + (delta_m / (mprime[select_window] - delta_m))
        )
    )
    to_ret = 1.0 / (effe_prime + 1)
    to_ret[select_zero] = 0.0
    to_ret[select_one] = 1.0
    return to_ret


def low_pass_filter(mass, mmax, delta_m):
    """
    Parameters
    ----------
    mass: np.array or float
        array of x or masses values
    mmax: float or np.array (in this case len(mmin) == len(mass))
        maximum value of window function
    delta_m: float or np.array (in this case len(delta_m) == len(mass))
        width of the window function

    Returns
    -------
    Values of the window function
    """

    if not isinstance(mass, _np.ndarray):
        mass = _np.array([mass])

    to_ret = _np.ones_like(mass)
    if delta_m == 0:
        return to_ret

    mprime = mmax - mass

    # Defines the different regions of thw window function ad in Eq. B6 of  https://arxiv.org/pdf/2010.14533.pdf
    select_window = (mass < mmax) & (mass > (mmax - delta_m))
    select_one = mass <= (mmax - delta_m)
    select_zero = mass >= mmax

    effe_prime = _np.ones_like(mass)

    # Definethe f function as in Eq. B7 of https://arxiv.org/pdf/2010.14533.pdf
    effe_prime[select_window] = _np.exp(
        _np.nan_to_num(
            (delta_m / mprime[select_window]) + (delta_m / (mprime[select_window] - delta_m))
        )
    )
    to_ret = 1.0 / (effe_prime + 1)
    to_ret[select_zero] = 0.0
    to_ret[select_one] = 1.0
    return to_ret


def notch_filter(mass, notch_right, right_smooth, notch_left, left_smooth, A):
    """
    This function returns a notch filter based on the one defined in eq. (4) of https://arxiv.org/pdf/2111.03498.pdf, but using the

    Parameters
    ----------
    mass: np.array or float
        array of x or masses values in solar masses
    high_pass_min,low_pass_max: float
        maximum value of window function (maximum credible mass of the spectrum)
    right_smooth, right_smooth: float
        width of the high or low pass window function
    A: float
        Fraction of the signal to substract

    Returns
    -------
    Values of the notch filter
    """

    filter = 1 - A * high_pass_filter(mass, notch_left, left_smooth) * low_pass_filter(
        mass, notch_right, right_smooth
    )
    return filter


def get_PL_norm(alpha, minv, maxv):
    """
    This function returns the powerlaw normalization factor

    Parameters
    ----------
    alpha: float
        Powerlaw slope
    min_pl: float
        lower cutoff
    max_pl: float
        low_pass_max cutoff
    """

    # Get the PL norm as in Eq. 24 on the tex document
    if alpha == -1:
        return _np.log(maxv / minv)
    else:
        return (_np.power(maxv, alpha + 1) - _np.power(minv, alpha + 1)) / (alpha + 1)


def get_gaussian_norm(mu, sigma, min, max):
    """
    This function returns the gaussian normalization factor

    Parameters
    ----------
    mu: float
        mu of the gaussian
    sigma: float
        standard deviation of the gaussian
    min_pl: float
        lower cutoff
    max_pl: float
        low_pass_max cutoff
    """

    # Get the gaussian norm as in Eq. 28 on the tex document
    max_point = (max - mu) / (sigma * _np.sqrt(2.0))
    min_point = (min - mu) / (sigma * _np.sqrt(2.0))
    return 0.5 * _erf(max_point) - 0.5 * _erf(min_point)


class SmoothedProb(object):
    """
    Class for smoothing the low part of a PDF. The smoothing follows Eq. B7 of
    2010.14533.

    Parameters
    ----------
    origin_prob: class
        Original prior class to smooth from this module
    high_pass_min: float
        minimum cut-off. Below this, the window is 0.
    high_pass_smooth: float
        smooth factor. The smoothing acts between high_pass_min and high_pass_min+high_pass_smooth
    """

    def __init__(self, origin_prob, high_pass_min, high_pass_smooth):

        self.origin_prob = _copy.deepcopy(origin_prob)
        self.high_pass_smooth = high_pass_smooth
        self.high_pass_min = high_pass_min
        self.maximum = self.origin_prob.maximum
        self.minimum = self.origin_prob.minimum

        # Find the values of the integrals in the region of the window function before and after the smoothing
        int_array = _np.linspace(high_pass_min, high_pass_min + high_pass_smooth, 1000)
        integral_before = _trapz(self.origin_prob.prob(int_array), x=int_array)
        integral_now = _trapz(self.prob(int_array), x=int_array)

        self.integral_before = integral_before
        self.integral_now = integral_now
        # Renormalize the the smoother function.
        self.norm = 1 - integral_before + integral_now - self.origin_prob.cdf(high_pass_min)

        x_eval = _np.logspace(
            _np.log10(high_pass_min), _np.log10(high_pass_min + high_pass_smooth), 1000
        )
        cdf_numeric = _cumtrapz(self.prob(x_eval), x_eval)
        self.cached_cdf_window = _interp1d(
            x_eval[:-1:], cdf_numeric, fill_value="extrapolate", bounds_error=False, kind="linear"
        )

    def prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        return _np.exp(self.log_prob(x))

    def log_prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Return the window function
        window = high_pass_filter(x, self.high_pass_min, self.high_pass_smooth)

        if hasattr(self, "norm"):
            prob_ret = self.origin_prob.log_prob(x) + _np.log(window) - _np.log(self.norm)
        else:
            prob_ret = self.origin_prob.log_prob(x) + _np.log(window)

        return prob_ret

    def log_conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array
            Value at which compute the probability
        a: np.array
            New lower boundary
        b: np.array
            New low_pass_max boundary
        """

        to_ret = self.log_prob(x)
        # Find the new normalization in the new interval
        new_norm = self.cdf(b) - self.cdf(a)
        # Apply the new normalization and put to zero all the values above/below the interval
        wok = _np.where(new_norm > 0)[0]
        if len(wok) > 0:  # the pdf can be normalized
            to_ret[wok] -= _np.log(new_norm[wok])
        wnull = _np.where(new_norm <= 0)[0]
        if len(wnull) > 0:
            to_ret[wnull] = -_np.inf

        to_ret[(x < a) | (x > b)] = -_np.inf

        return to_ret

    def cdf(self, x):
        """
        Returns the cumulative density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the cumulative
        """

        to_ret = _np.ones_like(x)
        to_ret[x < self.high_pass_min] = 0.0
        to_ret[(x >= self.high_pass_min) & (x <= (self.high_pass_min + self.high_pass_smooth))] = (
            self.cached_cdf_window(
                x[(x >= self.high_pass_min) & (x <= (self.high_pass_min + self.high_pass_smooth))]
            )
        )
        to_ret[x >= (self.high_pass_min + self.high_pass_smooth)] = (
            self.integral_now
            + self.origin_prob.cdf(x[x >= (self.high_pass_min + self.high_pass_smooth)])
            - self.origin_prob.cdf(self.high_pass_min + self.high_pass_smooth)
        ) / self.norm

        return to_ret

    def conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array
            Value at which compute the probability
        a: np.array
            New lower boundary
        b: np.array
            New low_pass_max boundary
        """

        return _np.exp(self.log_conditioned_prob(x, a, b))


class SmoothedDipProb(object):
    """
    Class for low pass and high pass smoothing of a PDF, and adding a dip. The smoothing follows Eq. B7 of
    2010.14533.

    Parameters
    ----------
    origin_prob: class
        Original probability
    right_smooth: float
        high pass window
    left_smooth: float
        low pass window
    notch_lower: float
        Where to find the start of the dip
    notch_upper: float
        Where to find the end of the dip
    notch_lower_smooth: float
        The window size for the left part of the smooth
    notch_upper_smooth: float
        The window size for the right part of the smooth
    A: float
        The fraction of pdf to suppress in the dip.
    """

    def __init__(
        self,
        origin_prob,
        right_smooth,
        left_smooth,
        A,
        notch_lower,
        notch_lower_smooth,
        notch_upper,
        notch_upper_smooth,
    ):

        self.origin_prob = _copy.deepcopy(origin_prob)
        self.right_smooth = right_smooth
        self.high_pass_min = self.origin_prob.minimum
        self.left_smooth = left_smooth
        self.low_pass_max = self.origin_prob.maximum
        self.A = A
        self.notch_lower = notch_lower
        self.notch_lower_smooth = notch_lower_smooth
        self.notch_upper = notch_upper
        self.notch_upper_smooth = notch_upper_smooth
        self.maximum = self.origin_prob.maximum
        self.minimum = self.origin_prob.minimum

        # Find the values of the integrals in the region of the window function before and after the smoothing
        int_points = 1500

        # high pass
        int_array = _np.linspace(self.minimum, self.minimum + self.right_smooth, int_points)
        self.integral_before_1 = _np.trapz(self.origin_prob.prob(int_array), int_array)
        self.integral_now_1 = _np.trapz(self.prob(int_array), int_array)

        # notch filter
        int_array = _np.linspace(self.notch_lower, notch_upper, int_points)
        self.integral_before_2 = _np.trapz(self.origin_prob.prob(int_array), int_array)
        self.integral_now_2 = _np.trapz(self.prob(int_array), int_array)

        # low pass
        int_array = _np.linspace(self.maximum - self.left_smooth, self.maximum, int_points)
        self.integral_before_3 = _np.trapz(self.origin_prob.prob(int_array), int_array)
        self.integral_now_3 = _np.trapz(self.prob(int_array), int_array)

        # compute norm
        self.integral_before = (
            self.integral_before_1 + self.integral_before_2 + self.integral_before_3
        )
        self.integral_now = self.integral_now_1 + self.integral_now_2 + self.integral_now_3

        self.norm = 1 - self.integral_before + self.integral_now

        # create and compute cdf ranges

        self.x_eval_1 = _np.linspace(self.minimum, self.minimum + self.right_smooth, int_points)
        self.cdf_numeric_1 = _np.cumsum(
            self.prob((self.x_eval_1[:-1:] + self.x_eval_1[1::]) * 0.5)
        ) * (self.x_eval_1[1::] - self.x_eval_1[:-1:])

        self.x_eval_2 = _np.linspace(self.notch_lower, notch_upper, int_points)
        self.cdf_numeric_2 = (
            self.integral_now_1
            + self.origin_prob.cdf(_np.array([self.notch_lower]))
            - self.integral_before_1
        ) / (self.norm) + _np.cumsum(
            self.prob((self.x_eval_2[:-1:] + self.x_eval_2[1::]) * 0.5)
        ) * (
            self.x_eval_2[1::] - self.x_eval_2[:-1:]
        )

        self.x_eval_3 = _np.linspace(self.maximum - self.left_smooth, self.maximum, int_points)
        self.cdf_numeric_3 = (
            self.integral_now_1
            + self.integral_now_2
            + self.origin_prob.cdf(_np.array([self.maximum - self.left_smooth]))
            - self.integral_before_1
            - self.integral_before_2
        ) / self.norm + _np.cumsum(self.prob((self.x_eval_3[:-1:] + self.x_eval_3[1::]) * 0.5)) * (
            self.x_eval_3[1::] - self.x_eval_3[:-1:]
        )

        self.cached_cdf_window_1 = _interp1d(
            self.x_eval_1[:-1:],
            self.cdf_numeric_1,
            fill_value="extrapolate",
            bounds_error=False,
            kind="linear",
        )
        self.cached_cdf_window_2 = _interp1d(
            self.x_eval_2[:-1:],
            self.cdf_numeric_2,
            fill_value="extrapolate",
            bounds_error=False,
            kind="linear",
        )
        self.cached_cdf_window_3 = _interp1d(
            self.x_eval_3[:-1:],
            self.cdf_numeric_3,
            fill_value="extrapolate",
            bounds_error=False,
            kind="linear",
        )

    def prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        return _np.exp(self.log_prob(x))

    def log_prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Return the window function
        window_high_pass = high_pass_filter(x, self.high_pass_min, self.right_smooth)
        window_low_pass = low_pass_filter(x, self.low_pass_max, self.left_smooth)
        notch = notch_filter(
            x,
            self.notch_upper,
            self.notch_upper_smooth,
            self.notch_lower,
            self.notch_lower_smooth,
            self.A,
        )

        if hasattr(self, "norm"):
            prob_ret = (
                self.origin_prob.log_prob(x)
                + _np.log(window_high_pass)
                + _np.log(window_low_pass)
                + _np.log(notch)
                - _np.log(self.norm)
            )
        else:
            prob_ret = (
                self.origin_prob.log_prob(x)
                + _np.log(window_high_pass)
                + _np.log(window_low_pass)
                + _np.log(notch)
            )
        return prob_ret

    def log_conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array
            Value at which compute the probability
        a: np.array
            New lower boundary
        b: np.array
            New low_pass_max boundary
        """

        to_ret = self.log_prob(x)
        # Find the new normalization in the new interval
        new_norm = self.cdf(b) - self.cdf(a)
        # Apply the new normalization and put to zero all the values above/below the interval
        wok = _np.where(new_norm > 0)[0]
        if len(wok) > 0:  # the pdf can be normalized
            to_ret[wok] -= _np.log(new_norm[wok])
        wnull = _np.where(new_norm <= 0)[0]
        if len(wnull) > 0:
            to_ret[wnull] = -_np.inf

        to_ret[(x < a) | (x > b)] = -_np.inf

        return to_ret

    def cdf(self, x):
        """
        Returns the cumulative density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the cumulative
        """

        to_ret = _np.ones_like(x)
        to_ret[x < self.high_pass_min] = 0.0
        to_ret[(x >= self.high_pass_min) & (x < (self.high_pass_min + self.right_smooth))] = (
            self.cached_cdf_window_1(
                x[(x >= self.high_pass_min) & (x <= (self.high_pass_min + self.right_smooth))]
            )
        )
        to_ret[(x >= (self.high_pass_min + self.right_smooth)) & (x < self.notch_lower)] = (
            self.integral_now_1
            - self.integral_before_1
            + self.origin_prob.cdf(
                x[(x >= (self.high_pass_min + self.right_smooth)) & (x < self.notch_lower)]
            )
        ) / self.norm
        to_ret[(x >= self.notch_lower) & (x < self.notch_upper)] = self.cached_cdf_window_2(
            x[(x >= self.notch_lower) & (x < self.notch_upper)]
        )
        to_ret[(x >= self.notch_upper) & (x < self.low_pass_max - self.left_smooth)] = (
            self.integral_now_1
            - self.integral_before_1
            + self.integral_now_2
            - self.integral_before_2
            + self.origin_prob.cdf(
                x[(x >= self.notch_upper) & (x < (self.low_pass_max - self.left_smooth))]
            )
        ) / self.norm
        to_ret[x >= (self.low_pass_max - self.left_smooth)] = self.cached_cdf_window_3(
            x[x >= (self.low_pass_max - self.left_smooth)]
        )
        return to_ret

    def conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array
            Value at which compute the probability
        a: np.array
            New lower boundary
        b: np.array
            New low_pass_max boundary
        """

        return _np.exp(self.log_conditioned_prob(x, a, b))


class PowerLaw_math(object):
    """
    Class for a powerlaw probability :math:`p(x) \\propto x^{\\alpha}` defined in
    [a,b]

    Parameters
    ----------
    alpha: float
        Powerlaw slope
    min_pl: float
        lower cutoff
    max_pl: float
        low_pass_max cutoff
    """

    def __init__(self, alpha, min_pl, max_pl):

        self.minimum = min_pl
        self.maximum = max_pl
        self.min_pl = min_pl
        self.max_pl = max_pl
        self.alpha = alpha

        # Get the PL norm and as Eq. 24 on the paper
        self.norm = get_PL_norm(alpha, min_pl, max_pl)

    def prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        return _np.exp(self.log_prob(x))

    def log_prob(self, x):
        """
        Returns the logarithm of the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        to_ret = self.alpha * _np.log(x) - _np.log(self.norm)
        to_ret[(x < self.min_pl) | (x > self.max_pl)] = -_np.inf

        return to_ret

    def log_conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        norms = get_PL_norm(self.alpha, a, b)
        to_ret = self.alpha * _np.log(x) - _np.log(norms)
        to_ret[(x < a) | (x > b)] = -_np.inf

        return to_ret

    def cdf(self, x):
        """
        Returns the cumulative density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the cumulative
        """

        # Define the cumulative density function, see  Eq. 24 to see the integral form

        if self.alpha == -1:
            to_ret = _np.log(x / self.min_pl) / self.norm
        else:
            to_ret = (
                (_np.power(x, self.alpha + 1) - _np.power(self.min_pl, self.alpha + 1))
                / (self.alpha + 1)
            ) / self.norm

        to_ret *= x >= self.min_pl

        if hasattr(x, "__len__"):
            to_ret[x > self.max_pl] = 1.0
        else:
            if x > self.max_pl:
                to_ret = 1.0

        return to_ret

    def conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        return _np.exp(self.log_conditioned_prob(x, a, b))


class Truncated_Gaussian_math(object):
    """
    Class for a truncated gaussian in
    [a,b]

    Parameters
    ----------
    mu: float
        mean of the gaussian
    sigma: float
        standard deviation of the gaussian
    min_g: float
        lower cutoff
    max_g: float
        low_pass_max cutoff
    """

    def __init__(self, mu, sigma, min_g, max_g):

        self.minimum = min_g
        self.maximum = max_g
        self.max_g = max_g
        self.min_g = min_g
        self.mu = mu
        self.sigma = sigma

        # Find the gaussian normalization as in Eq. 28 in the tex document
        self.norm = get_gaussian_norm(mu, sigma, min_g, max_g)

    def prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        return _np.exp(self.log_prob(x))

    def log_prob(self, x):
        """
        Returns the logarithm of the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        to_ret = (
            -_np.log(self.sigma)
            - 0.5 * _np.log(2 * _np.pi)
            - 0.5 * _np.power((x - self.mu) / self.sigma, 2.0)
            - _np.log(self.norm)
        )
        to_ret[(x < self.min_g) | (x > self.max_g)] = -_np.inf

        return to_ret

    def log_conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        norms = get_gaussian_norm(self.mu, self.sigma, a, b)
        to_ret = (
            -_np.log(self.sigma)
            - 0.5 * _np.log(2 * _np.pi)
            - 0.5 * _np.power((x - self.mu) / self.sigma, 2.0)
            - _np.log(norms)
        )
        to_ret[(x < a) | (x > b)] = -_np.inf

        return to_ret

    def cdf(self, x):
        """
        Returns the cumulative density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the cumulative
        """

        # Define the cumulative density function as in Eq. 28 on the paper to see the integral form

        max_point = (x - self.mu) / (self.sigma * _np.sqrt(2.0))
        min_point = (self.min_g - self.mu) / (self.sigma * _np.sqrt(2.0))

        to_ret = (0.5 * _erf(max_point) - 0.5 * _erf(min_point)) / self.norm

        to_ret *= x >= self.min_g

        if hasattr(x, "__len__"):
            to_ret[x > self.max_g] = 1.0
        else:
            if x > self.max_g:
                to_ret = 1.0

        return to_ret

    def conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        return _np.exp(self.log_conditioned_prob(x, a, b))


class PowerLawGaussian_math(object):
    """
    Class for a powerlaw probability plus gausian peak
    :math:`p(x) \\propto (1-\\lambda)x^{\\alpha}+\\lambda \\mathcal{N}(\\mu,\\sigma)`. Each component is defined in
    a different interval

    Parameters
    ----------
    alpha: float
        Powerlaw slope
    min_pl: float
        lower cutoff
    max_pl: float
        low_pass_max cutoff
    lambda_g: float
        fraction of prob coming from gaussian peak
    mu_g: float
        mean for the gaussian
    sigma_g: float
        standard deviation for the gaussian
    min_g: float
        minimum for the gaussian component
    max_g: float
        maximim for the gaussian component
    """

    def __init__(self, alpha, min_pl, max_pl, lambda_g, mu_g, sigma_g, min_g, max_g):

        self.minimum = _np.min([min_pl, min_g])
        self.maximum = _np.max([max_pl, max_g])

        self.lambda_g = lambda_g

        self.pl = PowerLaw_math(alpha, min_pl, max_pl)
        self.gg = Truncated_Gaussian_math(mu_g, sigma_g, min_g, max_g)

    def prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Define the PDF as in Eq. 36-37-38 on on the tex document
        return _np.exp(self.log_prob(x))

    def cdf(self, x):
        """
        Returns the cumulative density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the cumulative
        """

        return (1 - self.lambda_g) * self.pl.cdf(x) + self.lambda_g * self.gg.cdf(x)

    def conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        return _np.exp(self.log_conditioned_prob(x, a, b))

    def log_prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Define the PDF as in Eq. 36-37-38 on on the tex document
        return _np.logaddexp(
            _np.log1p(-self.lambda_g) + self.pl.log_prob(x),
            _np.log(self.lambda_g) + self.gg.log_prob(x),
        )

    def log_conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        return _np.logaddexp(
            _np.log1p(-self.lambda_g) + self.pl.log_conditioned_prob(x, a, b),
            _np.log(self.lambda_g) + self.gg.log_conditioned_prob(x, a, b),
        )


class PowerLawDoubleGaussian_math(object):
    """
    Class for a powerlaw probability plus gausian peak
    :math:`p(x) \\propto (1-\\lambda)x^{\\alpha}+\\lambda \\lambda_1 \\mathcal{N}(\\mu_1,\\sigma_1)+\\lambda (1-\\lambda_1) \\mathcal{N}(\\mu_2,\\sigma_2)`.
    Each component is defined ina different interval

    Parameters
    ----------
    alpha: float
        Powerlaw slope
    min_pl: float
        lower cutoff
    max_pl: float
        low_pass_max cutoff
    lambda_g: float
        fraction of prob coming in both gaussian peaks
    lambda_g_low: float
        fraction of prob in lower gaussian peak
    mu_g_low: float
        mean for the lower gaussian peak
    sigma_g_low: float
        standard deviation for the gaussian # Define the PDF as in Eq. 37 on on the tex document
    mu_g_high: float
        mean for the higher gaussian peak
    sigma_g_high: float
        standard deviation for the lower gaussian peak
    min_g: float
        minimum for the gaussian components
    max_g: float
        maximum for the gaussian components
    """

    def __init__(
        self,
        alpha,
        min_pl,
        max_pl,
        lambda_g,
        lambda_g_low,
        mu_g_low,
        sigma_g_low,
        mu_g_high,
        sigma_g_high,
        min_g,
        max_g,
    ):

        self.minimum = _np.min([min_pl, min_g])
        self.maximum = _np.max([max_pl, max_g])

        self.lambda_g = lambda_g
        self.lambda_g_low = lambda_g_low

        self.pl = PowerLaw_math(alpha, min_pl, max_pl)
        self.gg_low = Truncated_Gaussian_math(mu_g_low, sigma_g_low, min_g, max_g)
        self.gg_high = Truncated_Gaussian_math(mu_g_high, sigma_g_high, min_g, max_g)

    def prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        return _np.exp(self.log_prob(x))

    def log_prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Define the PDF as in Eq. 44-45-46 on the tex document

        pl_part = _np.log1p(-self.lambda_g) + self.pl.log_prob(x)
        g_low = self.gg_low.log_prob(x) + _np.log(self.lambda_g) + _np.log(self.lambda_g_low)
        g_high = self.gg_high.log_prob(x) + _np.log(self.lambda_g) + _np.log1p(-self.lambda_g_low)

        return _logsumexp(_np.stack([pl_part, g_low, g_high]), axis=0)

    def log_conditioned_prob(self, x, a, b):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Define the PDF as in Eq.  44-45-46  on the tex document

        pl_part = _np.log1p(-self.lambda_g) + self.pl.log_conditioned_prob(x, a, b)
        g_low = (
            self.gg_low.log_conditioned_prob(x, a, b)
            + _np.log(self.lambda_g)
            + _np.log(self.lambda_g_low)
        )
        g_high = (
            self.gg_high.log_conditioned_prob(x, a, b)
            + _np.log(self.lambda_g)
            + _np.log1p(-self.lambda_g_low)
        )

        return _logsumexp(_np.stack([pl_part, g_low, g_high]), axis=0)

    def cdf(self, x):
        """
        Returns the cumulative density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the cumulative
        """

        pl_part = (1 - self.lambda_g) * self.pl.cdf(x)
        g_part = self.gg_low.cdf(x) * self.lambda_g * self.lambda_g_low + self.gg_high.cdf(
            x
        ) * self.lambda_g * (1 - self.lambda_g_low)

        return pl_part + g_part

    def conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        return _np.exp(self.log_conditioned_prob(x, a, b))


class BrokenPowerLaw_math(object):
    """
    Class for a broken powerlaw probability
    :math:`p(x) \\propto x^{\\alpha}` if :math:`min<x<b(max-min)`, :math:`p(x) \\propto x^{\\beta}` if :math:`b(max-min)<x<max`.

    Parameters
    ----------
    alpha_1: float
        Powerlaw slope for first component
    alpha_2: float
        Powerlaw slope for second component
    min_pl: float
        lower cutoff
    max_pl: float
        low_pass_max cutoff
    b: float
        fraction in [0,1] at which the powerlaw breaks
    """

    def __init__(self, alpha_1, alpha_2, min_pl, max_pl, b):

        self.minimum = min_pl
        self.maximum = max_pl

        self.min_pl = min_pl
        self.max_pl = max_pl

        self.alpha_1 = alpha_1
        self.alpha_2 = alpha_2

        # Define the breaking point
        self.break_point = min_pl + b * (max_pl - min_pl)
        self.b = b

        # Initialize the single powerlaws
        self.pl1 = PowerLaw_math(alpha_1, min_pl, self.break_point)
        self.pl2 = PowerLaw_math(alpha_2, self.break_point, max_pl)

        # Define the broken powerlaw as in Eq. 39-40-41 on the tex document
        self.new_norm = 1 + self.pl1.prob(_np.array([self.break_point])) / self.pl2.prob(
            _np.array([self.break_point])
        )

    def prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Define the PDF as in Eq. 39-40-41 on the tex document
        return _np.exp(self.log_prob(x))

    def log_prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Define the PDF as in Eq. 39-40-41 on the tex document

        to_ret = _np.logaddexp(
            self.pl1.log_prob(x),
            self.pl2.log_prob(x)
            + self.pl1.log_prob(_np.array([self.break_point]))
            - self.pl2.log_prob(_np.array([self.break_point])),
        ) - _np.log(self.new_norm)
        return to_ret

    def log_conditioned_prob(self, x, a, b):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Define the PDF as in Eq. 39-40-41 on the tex document

        to_ret = _np.logaddexp(
            self.pl1.log_conditioned_prob(x, a, b),
            self.pl2.log_conditioned_prob(x, a, b)
            + self.pl1.log_prob(_np.array([self.break_point]))
            - self.pl2.log_prob(_np.array([self.break_point])),
        ) - _np.log(self.new_norm)

        return to_ret

    def cdf(self, x):
        """
        Returns the cumulative density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the cumulative
        """

        return (
            self.pl1.cdf(x)
            + self.pl2.cdf(x)
            * (
                self.pl1.prob(_np.array([self.break_point]))
                / self.pl2.prob(_np.array([self.break_point]))
            )
        ) / self.new_norm

    def conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        return _np.exp(self.log_conditioned_prob(x, a, b))


class BrokenPowerLawDoubleGaussian_math(object):
    """
    Class for a broken powerlaw probability with two gaussian peaks
    :math:`p(x) \\propto x^{\\alpha_1}` if :math:`min<x<b(max-min)`, :math:`p(x) \\propto x^{\\alpha_2}` if :math:`b(max-min)<x<max`. This is added to two gaussians to give
    :math: `(1-\\lambda) BPL(\\alpha_1,\\alpha_2,b)+\\lambda \\lambda_1 \\mathcal{N}(\\mu_1,\\sigma_1)+\\lambda (1-\\lambda_1) \\mathcal{N}(\\mu_2,\\sigma_2)` where BPL is the above powerlaw function.

    Parameters
    ----------
    alpha_1: float
        Powerlaw slope for first component
    alpha_2: float
        Powerlaw slope for second component
    min_pl: float
        lower cutoff
    max_pl: float
        low_pass_max cutoff
    b: float
        fraction in [0,1] at which the powerlaw breaks
    lambda_g: float
        fraction of prob coming in both gaussian peaks
    lambda_g_low: float
        fraction of prob in lower gaussian peak
    mu_g_low: float
        mean for the lower gaussian peak
    sigma_g_low: float
        standard deviation for the gaussian # Define the PDF as in Eq. 37 on on the tex document
    mu_g_high: float
        mean for the higher gaussian peak
    sigma_g_high: float
        standard deviation for the lower gaussian peak
    min_g: float
        minimum for the gaussian components
    max_g: float
        maximum for the gaussian components
    """

    def __init__(
        self,
        min_pl,
        max_pl,
        lambda_g,
        lambda_g_low,
        mu_g_low,
        sigma_g_low,
        mu_g_high,
        sigma_g_high,
        min_g,
        max_g,
        alpha_1,
        alpha_2,
        break_point,
    ):

        self.minimum = _np.min([min_pl, min_g])
        self.maximum = _np.max([max_pl, max_g])

        self.lambda_g = lambda_g
        self.lambda_g_low = lambda_g_low

        self.break_point = break_point

        self.pl1 = PowerLaw_math(alpha_1, min_pl, self.break_point)
        self.pl2 = PowerLaw_math(alpha_2, self.break_point, max_pl)
        self.gg_low = Truncated_Gaussian_math(mu_g_low, sigma_g_low, min_g, max_g)
        self.gg_high = Truncated_Gaussian_math(mu_g_high, sigma_g_high, min_g, max_g)

        self.new_norm = 1 + self.pl1.prob(_np.array([self.break_point])) / self.pl2.prob(
            _np.array([self.break_point])
        )

    def prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """

        # Define the PDF as in Eq. 39-40-41 on the tex document
        return _np.exp(self.log_prob(x))

    def log_prob(self, x):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """
        pl1_part = self.pl1.log_prob(x)
        pl2_part = (
            self.pl2.log_prob(x)
            + self.pl1.log_prob(_np.array([self.break_point]))
            - self.pl2.log_prob(_np.array([self.break_point]))
        )
        pl_part = (
            _np.log1p(-self.lambda_g) + _np.logaddexp(pl1_part, pl2_part) - _np.log(self.new_norm)
        )
        g_low = self.gg_low.log_prob(x) + _np.log(self.lambda_g) + _np.log(self.lambda_g_low)
        g_high = self.gg_high.log_prob(x) + _np.log(self.lambda_g) + _np.log1p(-self.lambda_g_low)

        return _logsumexp(_np.stack([pl_part, g_low, g_high]), axis=0)

    def log_conditioned_prob(self, x, a, b):
        """
        Returns the probability density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        """
        pl1_part = self.pl1.log_conditioned_prob(x, a, b)
        pl2_part = (
            self.pl2.log_conditioned_prob(x, a, b)
            + self.pl1.log_prob(_np.array([self.break_point]))
            - self.pl2.log_prob(_np.array([self.break_point]))
        )
        pl_part = (
            _np.log1p(-self.lambda_g) + _np.logaddexp(pl1_part, pl2_part) - _np.log(self.new_norm)
        )
        g_low = (
            self.gg_low.log_conditioned_prob(x, a, b)
            + _np.log(self.lambda_g)
            + _np.log(self.lambda_g_low)
        )
        g_high = (
            self.gg_high.log_conditioned_prob(x, a, b)
            + _np.log(self.lambda_g)
            + _np.log1p(-self.lambda_g_low)
        )

        return _logsumexp(_np.stack([pl_part, g_low, g_high]), axis=0)

    def conditioned_prob(self, x, a, b):
        """
        Returns the conditional probability between two new boundaries [a,b]

        Parameters
        ----------
        x: np.array or float
            Value at which compute the probability
        a: np.array or float
            New lower boundary
        b: np.array or float
            New low_pass_max boundary
        """

        return _np.exp(self.log_conditioned_prob(x, a, b))

    def cdf(self, x):
        """
        Returns the cumulative density function normalized

        Parameters
        ----------
        x: np.array or float
            Value at which compute the cumulative
        """
        pl_part = (
            (1 - self.lambda_g)
            * (
                self.pl1.cdf(x)
                + self.pl2.cdf(x)
                * (
                    self.pl1.prob(_np.array([self.break_point]))
                    / self.pl2.prob(_np.array([self.break_point]))
                )
            )
            / self.new_norm
        )
        g_part = self.gg_low.cdf(x) * self.lambda_g * self.lambda_g_low + self.gg_high.cdf(
            x
        ) * self.lambda_g * (1 - self.lambda_g_low)
        return pl_part + g_part


class PairingFunc(object):
    """
    Class to add pairing function to mass distributions.

    Parameters
    ----------
    origin_prob : object
        original probability distribution
    pairing_function : callable
        pairing function for m1 and m2 distributions
    """

    def __init__(self, origin_dist, pairing_function, m1_samps, m2_samps):

        self.origin_dist = origin_dist
        self.pairing_function = pairing_function
        self.m1_samps, self.m2_samps = m1_samps, m2_samps

        self.norm = self.calc_norm()

    def calc_norm(self):
        """
        Uses monte carlo sum to calculate new normalisation after addition of pairing function

        """

        self.new_norm = _np.mean(self.pairing_function(self.m1_samps, self.m2_samps))

    def log_prob(self, x1, x2):
        """
        Calculate the log probability of a pair of values (x1, x2).

        Parameters
        ----------
        x1 : array-like
            First set of values for which to calculate log probability.
        x2 : array-like
            Second set of values for which to calculate log probability.

        Returns
        -------
        toret : array-like
            Normalised log probabilities.
        """
        toret = (
            self.origin_dist["mass_1"].log_prob(x1)
            + self.origin_dist["mass_2"].log_prob(x2)
            + _np.log(self.pairing_function(x1, x2))
            - _np.log(self.new_norm)
        )
        toret[_np.isnan(toret)] = -_np.inf
        return toret

    def prob(self, x1, x2):
        """
        Calculate the probability of a pair of values (x1, x2).

        Parameters
        ----------
        x1 : array-like
            First set of values for which to calculate probability.
        x2 : array-like
            Second set of values for which to calculate probability.

        Returns
        -------
        array-like
            Normalised probabilities.
        """
        return _np.exp(self.log_prob(x1, x2))

    def sample(self, Nsample):
        """
        Generate samples from the probability density function.

        Parameters
        ----------
        Nsample : int
            Number of samples to generate.

        Returns
        -------
        tuple of np.array
           arrays of m1 and m2 samples.
        """
        x1 = _np.random.uniform(
            self.origin_dist["mass_1"].minimum,
            self.origin_dist["mass_1"].maximum,
            size=10 * Nsample,
        )
        x2 = _np.random.uniform(
            self.origin_dist["mass_2"].minimum,
            self.origin_dist["mass_2"].maximum,
            size=10 * Nsample,
        )
        probs = self.prob(x1, x2)
        idx = _np.random.choice(len(x1), size=Nsample, replace=True, p=probs / _np.sum(probs))
        return x1[idx], x2[idx]
