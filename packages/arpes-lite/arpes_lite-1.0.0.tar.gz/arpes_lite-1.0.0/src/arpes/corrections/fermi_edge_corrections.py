"""Automated utilities for calculating Fermi edge corrections."""

import lmfit as lf
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

import xarray as xr
from arpes.typing import DataType
from arpes.fits import (
    GStepBModel,
    LinearModel,
    QuadraticModel,
    AffineBroadenedFD,
    broadcast_model,
)
from arpes.provenance import provenance, update_provenance
from arpes.utilities.math import shift_by


def _exclude_from_set(excluded):
    def exclude(l):
        return list(set(l).difference(excluded))

    return exclude


exclude_hemisphere_axes = _exclude_from_set({"phi", "eV"})
exclude_hv_axes = _exclude_from_set({"hv", "eV"})


__all__ = (
    "build_quadratic_fermi_edge_correction",
    "build_photon_energy_fermi_edge_correction",
    "apply_photon_energy_fermi_edge_correction",
    "apply_quadratic_fermi_edge_correction",
    "build_direct_fermi_edge_correction",
    "apply_direct_fermi_edge_correction",
    "find_e_fermi_linear_dos",
    "fix_fermi_edge",
)


def find_e_fermi_linear_dos(edc, guess=None, plot=False, ax=None):
    """Estimate the Fermi level under the assumption of a linear density of states.

    Does a reasonable job of finding E_Fermi in-situ for graphene/graphite or other materials with a linear DOS near
    the chemical potential. You can provide an initial guess via guess, or one will be chosen half way through the EDC.

    The Fermi level is estimated as the location where the DoS crosses below an estimated background level

    Args:
        edc: Input data
        guess: Approximate location
        plot: Whether to plot the fit, useful for debugging.

    Returns:
        The Fermi edge position.
    """
    if guess is None:
        guess = edc.eV.values[len(edc.eV) // 2]

    edc = edc - np.percentile(edc.values, (20,))[0]
    mask = edc > np.percentile(edc.sel(eV=slice(None, guess)), 20)
    mod = LinearModel().guess_fit(edc[mask])

    chemical_potential = -mod.params["intercept"].value / mod.params["slope"].value

    if plot:
        if ax is None:
            fig, ax = plt.subplots()
        edc.plot(ax=ax)
        ax.axvline(chemical_potential, linestyle="--", color="red")
        ax.axvline(guess, linestyle="--", color="gray")

    return chemical_potential


def apply_direct_fermi_edge_correction(
    arr: xr.DataArray, correction=None, *args, **kwargs
):
    """Applies a direct fermi edge correction stencil."""
    if correction is None:
        correction = build_direct_fermi_edge_correction(arr, *args, **kwargs)

    shift_amount = (
        -correction / arr.G.stride(generic_dim_names=False)["eV"]
    )  # pylint: disable=invalid-unary-operand-type
    energy_axis = list(arr.dims).index("eV")

    correction_axis = list(arr.dims).index(correction.dims[0])

    corrected_arr = xr.DataArray(
        shift_by(
            arr.values, shift_amount, axis=energy_axis, by_axis=correction_axis, order=1
        ),
        arr.coords,
        arr.dims,
        attrs=arr.attrs,
    )

    if "id" in corrected_arr.attrs:
        del corrected_arr.attrs["id"]

    provenance(
        corrected_arr,
        arr,
        {
            "what": "Shifted Fermi edge to align at 0 along hv axis",
            "by": "apply_photon_energy_fermi_edge_correction",
            "correction": list(
                correction.values
                if isinstance(correction, xr.DataArray)
                else correction
            ),
        },
    )

    return corrected_arr


@update_provenance("Build direct Fermi edge correction")
def build_direct_fermi_edge_correction(
    arr: xr.DataArray, fit_limit=0.001, energy_range=None, plot=False, along="phi"
):
    """Builds a direct fermi edge correction stencil.

    This means that fits are performed at each value of the 'phi' coordinate
    to get a list of fits. Bad fits are thrown out to form a stencil.

    This can be used to shift coordinates by the nearest value in the stencil.

    Args:
        arr
        fit_limit
        energy_range
        plot
        along

    Returns:
        The array of fitted edge coordinates.
    """
    if energy_range is None:
        energy_range = slice(-0.1, 0.1)

    exclude_axes = ["eV", along]
    others = [d for d in arr.dims if d not in exclude_axes]
    edge_fit = broadcast_model(
        GStepBModel, arr.sum(others).sel(eV=energy_range), along
    ).results

    def sieve(c, v):
        return v.item().params["center"].stderr < 0.001

    corrections = edge_fit.G.filter_coord(along, sieve).G.map(
        lambda x: x.params["center"].value
    )

    if plot:
        corrections.plot()

    return corrections


def build_quadratic_fermi_edge_correction(
    arr: xr.DataArray, fit_limit=0.001, eV_slice=None, plot=False
) -> lf.model.ModelResult:
    """Calculates a quadratic Fermi edge correction by edge fitting and then quadratic fitting of edges."""
    # TODO improve robustness here by allowing passing in the location of the fermi edge guess
    # We could also do this automatically by using the same method we use for step detection to find the edge of the
    # spectrometer image

    if eV_slice is None:
        approximate_fermi_level = arr.S.find_spectrum_energy_edges().max()
        eV_slice = slice(approximate_fermi_level - 0.4, approximate_fermi_level + 0.4)
    else:
        approximate_fermi_level = 0
    sum_axes = exclude_hemisphere_axes(arr.dims)
    edge_fit = broadcast_model(
        GStepBModel,
        arr.sum(sum_axes).sel(eV=eV_slice),
        "phi",
        params={"center": {"value": approximate_fermi_level}},
    )

    size_phi = len(arr.coords["phi"])
    not_nanny = (np.logical_not(np.isnan(arr)) * 1).sum("eV") > size_phi * 0.30
    condition = np.logical_and(edge_fit.F.s("center") < fit_limit, not_nanny)

    quadratic_corr = QuadraticModel().guess_fit(
        edge_fit.F.p("center"), weights=condition * 1
    )
    if plot:
        edge_fit.F.p("center").plot()
        plt.plot(arr.coords["phi"], quadratic_corr.best_fit)

    return quadratic_corr


@update_provenance("Build photon energy Fermi edge correction")
def build_photon_energy_fermi_edge_correction(
    arr: xr.DataArray, plot=False, energy_window=0.2
):
    """Builds Fermi edge corrections across photon energy (corrects monochromator miscalibration)."""
    edge_fit = broadcast_model(
        GStepBModel,
        arr.sum(exclude_hv_axes(arr.dims)).sel(eV=slice(-energy_window, energy_window)),
        "hv",
    )

    return edge_fit


def apply_photon_energy_fermi_edge_correction(
    arr: xr.DataArray, correction=None, **kwargs
):
    """Applies Fermi edge corrections across photon energy (corrects monochromator miscalibration)."""
    if correction is None:
        correction = build_photon_energy_fermi_edge_correction(arr, **kwargs)

    correction_values = correction.G.map(lambda x: x.params["center"].value)
    if "corrections" not in arr.attrs:
        arr.attrs["corrections"] = {}

    arr.attrs["corrections"]["hv_correction"] = list(correction_values.values)

    shift_amount = -correction_values / arr.G.stride(generic_dim_names=False)["eV"]
    energy_axis = arr.dims.index("eV")
    hv_axis = arr.dims.index("hv")

    corrected_arr = xr.DataArray(
        shift_by(arr.values, shift_amount, axis=energy_axis, by_axis=hv_axis, order=1),
        arr.coords,
        arr.dims,
        attrs=arr.attrs,
    )

    if "id" in corrected_arr.attrs:
        del corrected_arr.attrs["id"]

    provenance(
        corrected_arr,
        arr,
        {
            "what": "Shifted Fermi edge to align at 0 along hv axis",
            "by": "apply_photon_energy_fermi_edge_correction",
            "correction": list(correction_values.values),
        },
    )

    return corrected_arr


def apply_quadratic_fermi_edge_correction(
    arr: xr.DataArray, correction: lf.model.ModelResult = None, offset=None
):
    """Applies a Fermi edge correction using a quadratic fit for the edge."""
    assert isinstance(arr, xr.DataArray)
    if correction is None:
        correction = build_quadratic_fermi_edge_correction(arr)

    if "corrections" not in arr.attrs:
        arr.attrs["corrections"] = {}

    arr.attrs["corrections"]["FE_Corr"] = correction.best_values

    delta_E = arr.coords["eV"].values[1] - arr.coords["eV"].values[0]
    dims = list(arr.dims)
    energy_axis = dims.index("eV")
    phi_axis = dims.index("phi")

    shift_amount_E = correction.eval(x=arr.coords["phi"].values)

    if offset is not None:
        shift_amount_E = shift_amount_E - offset

    shift_amount = -shift_amount_E / delta_E

    corrected_arr = xr.DataArray(
        shift_by(arr.values, shift_amount, axis=energy_axis, by_axis=phi_axis, order=1),
        arr.coords,
        arr.dims,
        attrs=arr.attrs,
    )

    if "id" in corrected_arr.attrs:
        del corrected_arr.attrs["id"]

    provenance(
        corrected_arr,
        arr,
        {
            "what": "Shifted Fermi edge to align at 0",
            "by": "apply_quadratic_fermi_edge_correction",
            "correction": correction.best_values,
        },
    )

    return corrected_arr


def fit_fermi_edge(cut: xr.DataArray) -> xr.DataArray:
    """
    Fits the curved Fermi edge of a cut to a quadratic model.
    """
    edge_region = cut.sel(eV=slice(-0.1, 0.1))

    edge_fits = broadcast_model(AffineBroadenedFD, edge_region, "phi", progress=False)
    quad_fit = QuadraticModel().guess_fit(edge_fits.F.p("fd_center"))
    return quad_fit.eval(x=edge_region["phi"])


def fix_fermi_edge(
    dataset: DataType,
    broadcast_fit: bool = True,
    edge_fit: xr.DataArray = None,
    smoothing_sigma: float = 1.0,
) -> DataType:
    """Automatically correct the Fermi edge in a dataset.

    If the measurement was done with a curved slit, the Fermi edge will only be shifted
    to 0. If the measurement was done with a straight slit, the Fermi edge will be
    shifted to 0 and the curved Fermi edge will be corrected (`slit_shape` attr needs to
    be set to `straight`).

    Args
    ----
    dataset : DataType
        The dataset to correct
    broadcast_fit : bool
        Whether to fit the Fermi edge of the summed spectrum and then broadcast to all
        cuts or fit each cut individually.
    edge_fit : DataArray
        A precomputed edge fit to use. Typically generated using `fit_fermi_edge` on
        metal reference data.
    smoothing_sigma : float
        The sigma value for the Gaussian filter used to smooth the integrated edc for
        Fermi edge detection. Increasing this can fix faulty edge detection in noisy
        data.

    Returns
    -------
        A new dataset with the Fermi edge corrected.
    """
    HEMISPHERE_DIMS = {"eV", "phi"}
    original_spectrum: xr.DataArray = (
        dataset.S.spectrum if isinstance(dataset, xr.Dataset) else dataset
    )
    # We want to be able to pass any dataset for convenience, but we only want to
    # correct the Fermi edge for hemisphere data.
    if not all(dim in original_spectrum.dims for dim in HEMISPHERE_DIMS):
        return dataset

    dataset = dataset.copy(deep=True)
    if edge_fit is None:
        integrated_edc = gaussian_filter1d(
            original_spectrum.sum(
                [dim for dim in original_spectrum.dims if dim != "eV"]
            ),
            sigma=smoothing_sigma,
        )
        dropoff_index = np.argmin(np.diff(integrated_edc))
        dataset.coords["eV"] = (
            dataset.coords["eV"] - dataset.coords["eV"].values[dropoff_index]
        )
        if dataset.attrs.get("slit_shape") != "straight":
            return dataset

    spectrum: xr.DataArray = (
        dataset.S.spectrum if isinstance(dataset, xr.Dataset) else dataset
    )

    scan_axes = [dim for dim in spectrum.dims if dim not in HEMISPHERE_DIMS]
    # we need to stack something
    if not scan_axes:
        spectrum = spectrum.expand_dims("temp")
        scan_axes = ["temp"]

    stacked = spectrum.stack(flattened=scan_axes)
    if edge_fit is None:
        edge_fit = (
            fit_fermi_edge(stacked.sum("flattened")) if broadcast_fit is True else None
        )

    def fix_one_fermi_edge(cut: xr.DataArray, edge_fit=None) -> xr.DataArray:
        edge_fit = edge_fit if edge_fit is not None else fit_fermi_edge(cut)
        return cut.G.shift_by(edge_fit, "eV")

    fixed_cuts = [
        fix_one_fermi_edge(cut, edge_fit) for cut in stacked.transpose("flattened", ...)
    ]
    fixed_stack: xr.DataArray = xr.concat(fixed_cuts, dim="flattened")
    # Have to replace only the values to unstack later
    stacked.values = fixed_stack.transpose(*stacked.dims)

    if isinstance(dataset, xr.Dataset):
        return dataset.update({dataset.S.spectrum_name: stacked.unstack("flattened")})
    return stacked.unstack("flattened")
