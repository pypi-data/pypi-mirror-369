"""Implements data loading for the Lanzara group "Main Chamber"."""

import numpy as np
import xarray as xr

from arpes.endstations import FITSEndstation, HemisphericalEndstation
from arpes.constants import pi

__all__ = ("ALGMainChamber",)


class ALGMainChamber(HemisphericalEndstation, FITSEndstation):
    """Implements data loading for the Lanzara group "Main Chamber"."""

    PRINCIPAL_NAME = "ALG-Main"
    ALIASES = [
        "MC",
        "ALG-Main",
        "ALG-MC",
        "ALG-Hemisphere",
        "ALG-Main Chamber",
    ]
    ATTR_TRANSFORMS = {
        "START_T": lambda l: {
            "time": " ".join(l.split(" ")[1:]).lower(),
            "date": l.split(" ")[0],
        },
    }

    RENAME_KEYS = {
        "Phi": "chi",
        "Beta": "beta",
        "Theta": "theta",
        "Azimuth": "chi",
        "Alpha": "alpha",
        "Pump_energy_uJcm2": "pump_fluence",
        "T0_ps": "t0_nominal",
        "W_func": "workfunction",
        "Slit": "slit",
        "LMOTOR0": "x",
        "LMOTOR1": "y",
        "LMOTOR2": "z",
        "LMOTOR3": "theta",
        "LMOTOR4": "beta",
        "LMOTOR5": "chi",
        "LMOTOR6": "delay",
        "SFLNM0": "lens_mode_name",
        "SFFR_0": "frames_per_slice",
        "SFBA_0": "phi_prebinning",
        "SFBE0": "eV_prebinning",
        "null": "cycle",
        "X": "x",
        "Y": "y",
    }

    MERGE_ATTRS = {
        "analyzer": "Specs PHOIBOS 150",
        "analyzer_name": "Specs PHOIBOS 150",
        "parallel_deflectors": False,
        "perpendicular_deflectors": False,
        "analyzer_radius": 150,
        "analyzer_type": "hemispherical",
        "mcp_voltage": None,
        "probe_linewidth": 0.015,
    }

    RAD_PER_PIXEL = (1 / 10) * (pi / 180)

    def postprocess_frame(self, frame: xr.Dataset):
        frame = super().postprocess_frame(frame)

        if "pixel" in frame.coords:
            phi_axis = frame.coords["pixel"].values * self.RAD_PER_PIXEL

            if "pixel" in frame.coords:
                frame = frame.rename(pixel="phi")

            frame = frame.assign_coords(phi=phi_axis)
        return frame

    def postprocess_scan(self, data: xr.Dataset, scan_desc: dict = None):
        """Performs final normalization of scan data.

        For the Lanzaa group main chamber, this means:

        1. Associating the fixex UV laser energy.
        2. Adding missing coordinates.
        3. Using a standard approximate set of coordinate offsets.
        4. Converting relevant angular coordinates to radians.
        """
        data.attrs["hv"] = 5.93
        data.attrs["alpha"] = 0
        data.attrs["psi"] = 0
        # by default we use this value since this isnear the center of the spectrometer window
        data.attrs["phi_offset"] = 0.405

        data = super().postprocess_scan(data, scan_desc)

        if "beta" in data.coords:
            data = data.assign_coords(beta=data.beta.values * np.pi / 180)

        return data
