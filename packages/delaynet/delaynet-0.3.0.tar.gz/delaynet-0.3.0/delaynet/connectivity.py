"""Module to provide a unified interface for all connectivity metrics."""

from collections.abc import Callable

from numpy import ndarray


from .connectivities import (
    __all_connectivity_metrics_names__,
    __all_connectivity_metrics_names_simple__,
)
from .decorators import connectivity as connectivity_decorator


Metric = str | Callable[[ndarray, ndarray, ...], tuple[float, int]]


def connectivity(
    ts1: ndarray,
    ts2: ndarray,
    /,
    metric: Metric,
    *args,
    lag_steps: int | list[int] | None = None,
    **kwargs,
) -> tuple[float, int]:
    """
    Calculate connectivity between two time series using a given metric.

    Keyword arguments are forwarded to the metric function.

    The metrics can be either a string or a function, implementing a connectivity
    metric.
    Find the metric string specifier using :func:`show_connectivity_metrics`.

    (Find all in submodule :mod:`delaynet.connectivities`, names are stored in
    :attr:`delaynet.connectivities.__all_connectivity_metrics__`)

    If a `callable` is given, it should take two time series as input and return a
    `tuple` of `float` and `int`.

    :param ts1: First time series. Positional only.
    :type ts1: numpy.ndarray
    :param ts2: Second time series. Positional only.
    :type ts2: numpy.ndarray
    :param metric: Metric to use.
    :type metric: str or Callable
    :param args: Positional arguments forwarded to the connectivity function, see
                 documentation.
    :type args: list
    :param lag_steps: The number of lag steps to consider. Required.
                      Can be integer for [1, ..., num], or a list of integers.
    :type lag_steps: int | list[int] | None
    :param kwargs: Keyword arguments forwarded to the connectivity function, see
                   documentation.
    :return: Connectivity value and lag.
    :rtype: tuple of float and int
    :raises ValueError: If the metric is unknown. Given as string.
    :raises ValueError: If the metric returns an invalid value. Given a Callable.
    :raises ValueError: If the metric is neither a string nor a Callable.
    """
    kwargs["lag_steps"] = lag_steps

    if isinstance(metric, str):
        metric = metric.lower()

        if metric not in __all_connectivity_metrics_names__:
            raise ValueError(f"Unknown metric: {metric}")

        return __all_connectivity_metrics_names__[metric](ts1, ts2, **kwargs)

    if not callable(metric):
        raise ValueError(
            f"Invalid connectivity metric: {metric}. Must be string or callable."
        )

    # connectivity metric is a callable,
    # add decorator to assure correct kwargs, type and shape
    return connectivity_decorator()(metric)(ts1, ts2, *args, **kwargs)


def show_connectivity_metrics():
    """Pretty print all available connectivity metrics."""
    print("Available connectivity metrics:")
    for metric, aliases in __all_connectivity_metrics_names_simple__.items():
        print(f"\nMetric: {metric}")
        print("Aliases:")
        for alias in aliases:
            print(f" - {alias}")
    print("\n")
