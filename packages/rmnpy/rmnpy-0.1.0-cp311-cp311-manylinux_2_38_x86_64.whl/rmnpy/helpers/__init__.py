"""
Helper functions for converting between Python types and OCTypes.

These are used internally by the SITypes and RMNLib wrappers.
They are not part of the public API.
"""

__all__ = [
    # String conversion functions
    "ocstring_to_pystring",
    "ocstring_create_from_pystring",
    "ocmutablestring_create_from_pystring",
    # Number conversion functions
    "ocnumber_create_from_pycomplex",
    "ocnumber_create_from_pynumber",
    "ocnumber_to_pynumber",
    # Boolean conversion functions
    "pybool_to_ocboolean",
    "ocboolean_to_pybool",
    # Data/NumPy conversion functions
    "ocdata_create_from_numpy_array",
    "ocdata_to_numpy_array",
    "ocmutabledata_create_from_numpy_array",
    # Array conversion functions
    "ocarray_create_from_pylist",
    "ocarray_to_pylist",
    "ocmutablearray_create_from_pylist",
    # Dictionary conversion functions
    "ocdict_create_from_pydict",
    "ocdict_to_pydict",
    "ocmutabledict_create_from_pydict",
    # Set conversion functions
    "ocset_create_from_pyset",
    "ocset_to_pyset",
    "ocmutableset_create_from_pyset",
    # Index array/set conversion functions
    "ocindexarray_create_from_pylist",
    "ocindexarray_to_pylist",
    "ocindexset_create_from_pyset",
    "ocindexset_to_pyset",
    "ocindexpairset_create_from_pydict",
    "ocindexpairset_to_pydict",
]

# Directly import the Cython‐built helpers.
from .octypes import (  # String conversion functions; Number conversion functions; Boolean conversion functions; Data/NumPy conversion functions; Array conversion functions; Dictionary conversion functions; Set conversion functions; Index array/set conversion functions
    ocarray_create_from_pylist,
    ocarray_to_pylist,
    ocboolean_to_pybool,
    ocdata_create_from_numpy_array,
    ocdata_to_numpy_array,
    ocdict_create_from_pydict,
    ocdict_to_pydict,
    ocindexarray_create_from_pylist,
    ocindexarray_to_pylist,
    ocindexpairset_create_from_pydict,
    ocindexpairset_to_pydict,
    ocindexset_create_from_pyset,
    ocindexset_to_pyset,
    ocmutablearray_create_from_pylist,
    ocmutabledata_create_from_numpy_array,
    ocmutabledict_create_from_pydict,
    ocmutableset_create_from_pyset,
    ocmutablestring_create_from_pystring,
    ocnumber_create_from_pycomplex,
    ocnumber_create_from_pynumber,
    ocnumber_to_pynumber,
    ocset_create_from_pyset,
    ocset_to_pyset,
    ocstring_create_from_pystring,
    ocstring_to_pystring,
    pybool_to_ocboolean,
)
