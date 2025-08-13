"""Specialized type annotations for use in PyARPES.

In particular, we frequently allow using the `DataType` annotation,
which refers to either an xarray.DataArray or xarray.Dataset.

Additionally, we often use `NormalizableDataType` which
means essentially anything that can be turned into a dataset,
for instance by loading from the cache using an ID, or which is
literally already data.
"""

import uuid

import xarray as xr
import numpy as np

__all__ = ["DTypeLike", "DataType", "NormalizableDataType", "xr_types"]

DTypeLike = np.dtype | None | type | str

DataType = xr.DataArray | xr.Dataset
NormalizableDataType = DataType | str | uuid.UUID

xr_types = (xr.DataArray, xr.Dataset)
