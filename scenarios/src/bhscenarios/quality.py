"""Fuel-gas screen against a published natural-gas quality band.

Membership of the band is a screening filter. It is not a determination that
a burner is compliant, certified, or safe to convert.
"""
from __future__ import annotations

from .assumptions import (
    DENSITY_MAX,
    DENSITY_MIN,
    H2_ELEVATED_VOL,
    H2_NOT_NEGLIGIBLE_VOL,
    TIGHT_MARGIN_K,
    WOBBE_MAX_MJ_NM3,
    WOBBE_MIN_MJ_NM3,
)


def band_failures(wobbe_mj_nm3: float, rel_density: float) -> list[str]:
    """Which cited EASEE-gas limits the gas misses. Empty list means inside both bands."""
    fails: list[str] = []
    if wobbe_mj_nm3 < WOBBE_MIN_MJ_NM3:
        fails.append("wobbe_below_band")
    elif wobbe_mj_nm3 > WOBBE_MAX_MJ_NM3:
        fails.append("wobbe_above_band")
    if rel_density < DENSITY_MIN:
        fails.append("density_below_band")
    elif rel_density > DENSITY_MAX:
        fails.append("density_above_band")
    return fails


def fuel_class(wobbe_mj_nm3: float, rel_density: float, h2_vol_dry: float) -> str:
    """Temperature-independent fuel class.

    ``band_low_h2`` is the only class treated as passing the interchangeability
    screen. Hydrogen cuts are screening assumptions S5 and S6, because the cited
    Wobbe band states that it applies at insignificant hydrogen and gives no
    numeric hydrogen limit.
    """
    inside = not band_failures(wobbe_mj_nm3, rel_density)
    if not inside:
        return "outside_published_band"
    if h2_vol_dry > H2_ELEVATED_VOL:
        return "band_h2_above_10vol"
    if h2_vol_dry > H2_NOT_NEGLIGIBLE_VOL:
        return "band_h2_not_negligible"
    return "band_low_h2"


def interchangeability_pass(fuel: str) -> bool:
    return fuel == "band_low_h2"


def thermal_assessment(t_ad_c: float, t_process_c: float, t_flue_c: float,
                       available_heat_frac: float | None) -> dict:
    """Separate the process temperature from the flue-gas exit temperature.

    Available heat is a function of the flue exit temperature. Heat can be
    delivered to a process only when the adiabatic flame temperature is above
    the process temperature. A cool flue does not by itself make a hotter
    process feasible.
    """
    margin_k = t_ad_c - t_process_c
    if available_heat_frac is None or available_heat_frac <= 0.0 or t_flue_c >= t_ad_c - 1e-6:
        feasible = False
        reason = "flue_exit_at_or_above_adiabatic_flame_temperature"
    elif margin_k <= 0.0:
        feasible = False
        reason = "adiabatic_flame_temperature_does_not_exceed_process_temperature"
    else:
        feasible = True
        reason = ""
    return {
        "thermally_feasible": feasible,
        "infeasibility_reason": reason,
        "margin_k": margin_k,
        "tight_margin": bool(feasible and margin_k < TIGHT_MARGIN_K),
    }
