"""Some general purpose analysis routines otherwise defying categorization."""

import itertools
from collections import defaultdict

import numpy as np

import arpes.constants
import arpes.models.band
import arpes.utilities
import arpes.utilities.math
import xarray as xr
from arpes.provenance import update_provenance
from arpes.typing import DataType
from arpes.utilities import normalize_to_spectrum, lift_spectrum
from arpes.utilities.math import fermi_distribution

from .filters import gaussian_filter_arr

__all__ = (
    "normalize_by_fermi_distribution",
    "symmetrize_axis",
    "condense",
    "rebin",
    "fit_fermi_edge",
)


@update_provenance("Normalized by the 1/Fermi Dirac Distribution at sample temp")
def normalize_by_fermi_distribution(
    data: DataType,
    max_gain=None,
    rigid_shift=0,
    instrumental_broadening=None,
    total_broadening=None,
):
    """Normalizes a scan by 1/the fermi dirac distribution.

    You can control the maximum gain with ``clamp``, and whether
    the Fermi edge needs to be shifted (this is for those desperate situations where you want something that
    "just works") via ``rigid_shift``.

    Args:
        data: Input
        max_gain: Maximum value for the gain. By default the value used
            is the mean of the spectrum.
        rigid_shift: How much to shift the spectrum chemical potential.
        instrumental_broadening: Instrumental broadening to use for
            convolving the distribution
    Pass the nominal value for the chemical potential in the scan. I.e. if the chemical potential is at BE=0.1, pass
    rigid_shift=0.1.

    Returns:
        Normalized DataArray
    """
    data = normalize_to_spectrum(data)

    if total_broadening:
        distrib = fermi_distribution(
            data.coords["eV"].values - rigid_shift,
            total_broadening / arpes.constants.K_BOLTZMANN_EV_KELVIN,
        )
    else:
        distrib = fermi_distribution(
            data.coords["eV"].values - rigid_shift, data.S.temp
        )

    # don't boost by more than 90th percentile of input, by default
    if max_gain is None:
        max_gain = min(np.mean(data.values), np.percentile(data.values, 10))

    distrib[distrib < 1 / max_gain] = 1 / max_gain
    distrib_arr = xr.DataArray(distrib, {"eV": data.coords["eV"].values}, ["eV"])

    if instrumental_broadening is not None:
        distrib_arr = gaussian_filter_arr(
            distrib_arr, sigma={"eV": instrumental_broadening}
        )

    return data / distrib_arr


@update_provenance("Symmetrize about axis")
def symmetrize_axis(data, axis_name, flip_axes=None, shift_axis=True):
    """Symmetrizes data across an axis.

    It would be better ultimately to be able
    to implement an arbitrary symmetry (such as a mirror or rotational symmetry
    about a line or point) and to symmetrize data by that method.

    Args:
        data
        axis_name
        flip_axes
        shift_axis

    Returns:
        Data after symmetrization procedure.
    """
    data = data.copy(deep=True)  # slow but make sure we don't bork axis on original
    data.coords[axis_name].values = (
        data.coords[axis_name].values - data.coords[axis_name].values[0]
    )

    selector = {}
    selector[axis_name] = slice(None, None, -1)
    rev = data.sel(**selector).copy()

    rev.coords[axis_name].values = -rev.coords[axis_name].values

    if flip_axes is None:
        flip_axes = []

    for axis in flip_axes:
        selector = {}
        selector[axis] = slice(None, None, -1)
        rev = rev.sel(**selector)
        rev.coords[axis].values = -rev.coords[axis].values

    return rev.combine_first(data)


@update_provenance("Condensed array")
def condense(data: xr.DataArray):
    """Clips the data so that only regions where there is substantial weight are included.

    In practice this usually means selecting along the ``eV`` axis, although other selections
    might be made.

    Args:
        data: xarray.DataArray

    Returns:
        The clipped data.
    """
    if "eV" in data.dims:
        data = data.sel(eV=slice(None, 0.05))

    return data


# J: TODO - rebin coordinates instead of simply taking the nth element
@update_provenance("Rebinned array")
def rebin(
    data: DataType,
    shape: dict | None = None,
    reduction: int | dict | None = None,
    interpolate=False,
    **kwargs
):
    """Rebins the data onto a different (smaller) shape.

    By default the behavior is to
    split the data into chunks that are integrated over. An interpolation option is also
    available.

    Exactly one of ``shape`` or ``reduction`` should be supplied.

    Dimensions corresponding to missing entries in ``shape`` or ``reduction`` will not
    be changed.

    Args:
        data
        interpolate: Use interpolation instead of integration
        shape: Target shape
        reduction: Factor to reduce each dimension by

    Returns:
        The rebinned data.
    """
    if isinstance(data, xr.Dataset):
        new_vars = {
            datavar: rebin(
                data[datavar],
                shape=shape,
                reduction=reduction,
                interpolate=interpolate,
                **kwargs
            )
            for datavar in data.data_vars
        }
        new_coords = {}

        for var in new_vars.values():
            new_coords.update(var.coords)
        return xr.Dataset(data_vars=new_vars, coords=new_coords, attrs=data.attrs)

    data = arpes.utilities.normalize_to_spectrum(data)

    if any(d in kwargs for d in data.dims):
        reduction = kwargs

    if interpolate:
        raise NotImplementedError("The interpolation option has not been implemented")

    assert shape is None or reduction is None

    if isinstance(reduction, int):
        reduction = {d: reduction for d in data.dims}

    if reduction is None:
        reduction = {}

    # we standardize by computing reduction from shape is shape was supplied.
    if shape is not None:
        reduction = {k: len(data.coords[k]) // v for k, v in shape.items()}

    # since we are not interpolating, we need to clip each dimension so that the reduction
    # factor evenly divides the real shape of the input data.
    slices = defaultdict(lambda: slice(None))

    if not data.dims:
        return data

    for dim, reduction_factor in reduction.items():
        remainder = len(data.coords[dim]) % reduction_factor
        if remainder != 0:
            slices[dim] = slice(None, -remainder)

    trimmed_data = data.data[tuple(slices[d] for d in data.dims)]
    trimmed_coords = {d: coord[slices[d]] for d, coord in data.indexes.items()}

    temp_shape = [
        [trimmed_data.shape[i] // reduction.get(d, 1), reduction.get(d, 1)]
        for i, d in enumerate(data.dims)
    ]
    temp_shape = itertools.chain(*temp_shape)
    reduced_data = trimmed_data.reshape(*temp_shape)

    for i in range(len(data.dims)):
        reduced_data = reduced_data.mean(i + 1)

    reduced_coords = {
        d: coord[:: reduction.get(d, 1)] for d, coord in trimmed_coords.items()
    }
    reduced_coords.update(
        {c: data.coords[c] for c in data.coords.keys() if c not in trimmed_coords}
    )

    return xr.DataArray(reduced_data, reduced_coords, data.dims, attrs=data.attrs)


@lift_spectrum
def normalize(spectrum: xr.DataArray) -> xr.DataArray:
    """Normalize spectrum so its minimum value is 0 and maximum value is 1."""
    return (spectrum - spectrum.min()) / (spectrum.max() - spectrum.min())
