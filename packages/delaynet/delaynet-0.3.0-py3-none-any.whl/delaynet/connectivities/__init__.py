"""Connectivities init, subpackage of delaynet."""

# Import all connectivity metrics
from .continuous_ordinal_patterns import random_patterns
from .granger import gt_multi_lag
from .gravity import gravity
from .linear_correlation import linear_correlation
from .mutual_information import mutual_information
from .rank_correlation import rank_correlation
from .transfer_entropy import transfer_entropy

from ..utils.dict_lookup import dict_lookup

# Named connectivity metrics
__all_connectivity_metrics_names__ = {
    "continuous ordinal patterns": random_patterns,
    "cop": random_patterns,
    "granger causality": gt_multi_lag,
    "gc": gt_multi_lag,
    "gravity": gravity,
    "gv": gravity,
    "linear correlation": linear_correlation,
    "lc": linear_correlation,
    "mutual information": mutual_information,
    "mi": mutual_information,
    "rank correlation": rank_correlation,
    "rc": rank_correlation,
    "transfer entropy": transfer_entropy,
    "te": transfer_entropy,
}

# List of all available metrics
__all_connectivity_metrics__ = set(__all_connectivity_metrics_names__.values())

# Extend named connectivity metrics with the function name
# e.g. adds "gt_multi_lag": gt_multi_lag
for metric in __all_connectivity_metrics__:
    __all_connectivity_metrics_names__[metric.__name__] = metric

# Convenient name dict: "metric.__name__": ["metric", "metric short", ...]
# shows all names that point to the same metric
__all_connectivity_metrics_names_simple__ = dict_lookup(
    __all_connectivity_metrics_names__
)
__all_connectivity_metrics_names_simple__ = {
    metric.__name__: names
    for metric, names in __all_connectivity_metrics_names_simple__.items()
}
