"""Plant-model queries. Temperature dependence comes from fresh design points.

Fuel composition, Wobbe index and adiabatic flame temperature do not depend on
the process temperature: the gasifier outlet temperature is fixed in the plant
model. Specific biomass and electricity use do depend on the flue-gas exit
temperature, through the burner available-heat calculation, and they do not
share one ratio across chains.
"""
from __future__ import annotations

from typing import Iterable

from biomass_heat import Burner, Plant, natural_gas

from .assumptions import CHAIN_ORDER, HEAT_MW, REFERENCE_T_C


def plant_for(config: str) -> Plant:
    return Plant(config)


def fuel_properties(config: str) -> dict:
    """Composition-side properties. Independent of process and flue temperature."""
    if config == "natural_gas":
        fuel = natural_gas()
        burner = Burner()
        label = "Natural gas (illustrative composition)"
    else:
        plant = plant_for(config)
        fuel = plant.chain(1.0)["fuel"]
        burner = plant.burner
        label = plant.config.label
    return {
        "config": config,
        "label": label,
        "lhv_mj_nm3": fuel.lhv_volumetric(),
        "hhv_mj_nm3": fuel.hhv_volumetric(),
        "wobbe_mj_nm3": fuel.wobbe_index(),
        "rel_density": fuel.relative_density(),
        "h2_vol_dry": fuel.x(dry=True).get("H2", 0.0) * 100.0,
        "ch4_vol_dry": fuel.x(dry=True).get("CH4", 0.0) * 100.0,
        "t_ad_c": burner.adiabatic_flame_temperature(fuel) - 273.15,
    }


def available_heat_fraction(config: str, t_flue_c: float) -> float | None:
    """Fraction of fuel LHV available when flue gas leaves at ``t_flue_c``.

    This does not use the process temperature. None means the flue exit is at
    or above the adiabatic flame temperature, so available heat is not positive.
    """
    if config == "natural_gas":
        fuel = natural_gas()
        burner = Burner()
    else:
        plant = plant_for(config)
        fuel = plant.chain(1.0)["fuel"]
        burner = plant.burner
    if t_flue_c >= burner.adiabatic_flame_temperature(fuel) - 273.15 - 1e-6:
        return None
    return float(burner.available_heat_fraction(fuel, t_flue_c + 273.15))


def design_kpis(config: str, t_process_c: float, t_flue_c: float, heat_mw: float = HEAT_MW) -> dict:
    """Design point with an explicit flue-exit approach.

    ``Plant.design_point`` takes the process temperature plus
    ``flue_exit_approach_K``. The ranked study uses approach 0. A non-zero
    approach is available for checks and is not passed to the LCOH helper,
    which has no approach argument.
    """
    if config == "natural_gas":
        raise ValueError("natural gas has no biomass design point")
    approach = t_flue_c - t_process_c
    plant = plant_for(config)
    try:
        dp = plant.design_point(heat_mw * 1e6, t_process_c + 273.15, approach)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "config": config}
    return {"ok": True, "config": config, **dp}


def stack_co2_t_per_mwh(config: str, t_flue_c: float, heat_mw: float = HEAT_MW) -> float | None:
    """Flue CO2 from the carbon in the fuel, t per MWh of process heat.

    For a biomass chain this carbon is biogenic. For the illustrative natural
    gas it is fossil. The split is applied by the caller. Upstream biomass
    supply-chain emissions and grid-electricity emissions are not in this number.
    """
    if config == "natural_gas":
        # Same quantity the plant model reports as ng_avoided_co2 on any chain.
        dp = plant_for("air").design_point(heat_mw * 1e6, t_flue_c + 273.15, 0.0)
        return float(dp["ng_avoided_co2_t_per_MWh"])
    plant = plant_for(config)
    t_exit = t_flue_c + 273.15
    ref = plant.chain(1.0)
    q = plant.burner.available_heat(ref["fuel"], t_exit)
    if q <= 0.0:
        return None
    fuel = ref["fuel"].scaled((heat_mw * 1e6) / q)
    kg_s = plant.burner.co2_kg_s(fuel)
    return float(kg_s * 3.6 / heat_mw)


def throughput_scale(config: str, t_flue_c: float, heat_mw: float) -> float:
    """Chain size relative to the published 10 MW / 1000 degC design point.

    Fuel LHV capacity is proportional to biomass feed because the plant model
    is linear in throughput. The ratio differs by fuel because flue enthalpy
    differs. It is not a single factor for every chain.
    """
    dp = design_kpis(config, t_flue_c, t_flue_c, heat_mw)
    ref = design_kpis(config, REFERENCE_T_C, REFERENCE_T_C, 10.0)
    if not dp["ok"] or not ref["ok"]:
        raise ValueError(f"{config} has no positive available heat at {t_flue_c} degC")
    return float(dp["fuel_lhv_MW"] / ref["fuel_lhv_MW"])


def available_heat_curve(configs: Iterable[str] = CHAIN_ORDER,
                         t_min: int = 200, t_max: int = 1500, step: int = 25):
    """Available-heat fraction against flue-exit temperature, one row per point."""
    rows = []
    temps = list(range(t_min, t_max + 1, step))
    for config in (*configs, "natural_gas"):
        props = fuel_properties(config)
        for t in temps:
            frac = available_heat_fraction(config, float(t))
            rows.append({
                "config": config,
                "label": props["label"],
                "t_flue_c": t,
                "t_ad_c": props["t_ad_c"],
                "available_heat_frac": frac,
            })
    return rows


def synthetic_two_shift_week(peak_w: float, hours_per_day: int = 16) -> list[float]:
    """One synthetic week: ``hours_per_day`` on-hours on five weekdays, else zero.

    The profile is generated here. It is not a measured site load.
    """
    out: list[float] = []
    for day in range(7):
        weekday = day < 5
        for hour in range(24):
            out.append(peak_w if weekday and hour < hours_per_day else 0.0)
    return out
