"""
RMNLib Python wrappers

This module provides Python interfaces to the RMNLib library for
high-level analysis and computation tools.
"""

# Import wrapper classes when they're available
try:
    from .dimension import Dimension

    __all__ = ["Dimension"]
except ImportError:
    # Wrapper not yet built/available
    __all__ = []

# TODO: Add other wrappers when implemented
try:
    from .sparse_sampling import SparseSampling

    __all__.append("SparseSampling")
except ImportError:
    # SparseSampling wrapper not yet built/available
    pass

try:
    from .dependent_variable import DependentVariable, dependent_variable_from_dict

    __all__.extend(["DependentVariable", "dependent_variable_from_dict"])
except ImportError:
    # DependentVariable wrapper not yet built/available
    pass
