"""LCOH at a flue-exit temperature, reusing bhlcoh.

What is recomputed from the plant model at the case temperature
--------------------------------------------------------------
Biomass per MWh, fuel-gas capacity, ASU oxygen and the non-electrolyser
electricity all come from ``Plant.design_point`` at that flue temperature
(``bhlcoh.chain_inputs`` calls it). Natural-gas fuel and direct fossil CO2
come from ``bhlcoh.ng_lcoh`` / ``ng_design`` at the same temperature.
CAPEX and O&M are then rebuilt with the LCOH cost functions, so a smaller or
larger gasifier hits the Thunman scale exponents. That is not a rescaling of
the published 1000 degC LCOH.

What is scaled from the published 1000 degC dispatch, and why
-------------------------------------------------------------
``bhlcoh.dispatch.run_dispatch`` always calls ``bhed.design.design_point``
with the default 1000 degC, and the price file is not part of the installed
package. The day-ahead LP is not re-solved here.

For a continuous flat duty, electrolyser capacity (fixed multiple of the
design rating), storage (fixed hours of design demand) and the hourly demand
all scale with the plant-model throughput ratio. The LP is homogeneous in
that ratio, so electricity MWh and EUR per MWh of heat scale with it, and
the electrolyser full-load fraction does not. The published O4 point
(2.5 x, 24 h) is scaled that way. The capacity factor is not re-optimised.
The LCOH study describes that optimum as flat, which is why a modest
intensity change is unlikely to reorder the electrolyser chains, but the
EUR/MWh figures at temperatures other than 1000 degC remain a scaled estimate.

The two-shift load changes the hourly shape. Scaling does not represent a
re-optimised O4 schedule on that shape. Those rows stay in the table and are
marked provisional. Chains without an electrolyser do not use this snapshot.

Break-even CO2
--------------
``bhlcoh.breakeven_co2_price`` calls ``ng_design()`` with its default
1000 degC. It is not used. Break-even is recomputed from ``ng_design`` at
the case flue temperature.
"""
from __future__ import annotations

from bhlcoh.chains import chain_inputs, grouped, lcoh_breakdown
from bhlcoh.costs import CostInputs
from bhlcoh.reference import ng_design, ng_lcoh

from .assumptions import ELECTROLYSER_CONFIGS, REFERENCE_T_C
from .reference_dispatch import PUBLISHED_MEAN_DA_EUR_MWH, PUBLISHED_O4
from .technical import design_kpis, stack_co2_t_per_mwh, throughput_scale

_SCALE_KEYS = (
    "electrolyser_mw",
    "h2_storage_kg",
    "o2_storage_kg",
    "electricity_eur_per_mwh_heat",
    "electricity_mwh_per_mwh_heat",
    "o2_vent_kg_per_mwh_heat",
)


def scaled_dispatch(config: str, t_flue_c: float, heat_mw: float) -> dict:
    """Published O4 snapshot scaled by the plant-model throughput ratio."""
    scale = throughput_scale(config, t_flue_c, heat_mw)
    base = PUBLISHED_O4[config]
    out = dict(base)
    for key in _SCALE_KEYS:
        out[key] = base[key] * scale
    if abs(t_flue_c - REFERENCE_T_C) < 1e-9 and abs(heat_mw - 10.0) < 1e-9:
        out["strategy"] = base["strategy"]
    else:
        out["strategy"] = "O4_homogeneous_scale_of_1000C_continuous"
    return out


def electricity_cost_basis(config: str, load_id: str) -> str:
    if config not in ELECTROLYSER_CONFIGS:
        return "flat_mean_da"
    if load_id == "two_shift":
        return "o4_not_reoptimised_for_two_shift"
    return "o4_scaled_from_1000C_continuous"


def breakeven_co2_eur_t(lcoh_bio: float, costs: CostInputs, heat_mw: float, t_flue_c: float) -> float:
    """EUA price at which natural-gas heat matches ``lcoh_bio`` at this flue temperature.

    Biogenic CO2 is not priced. This is the same algebra as
    ``bhlcoh.breakeven_co2_price`` with the temperature passed through.
    """
    d = ng_design(heat_mw, t_flue_c)
    fuel = d["ng_mwh_lhv_per_mwh"] * d["gcv_over_ncv"] * costs.gas_eur_mwh_gcv
    return (lcoh_bio - fuel) / d["co2_t_per_mwh"]


def breakeven_gas_eur_mwh_gcv(lcoh_bio: float, costs: CostInputs, heat_mw: float,
                              t_flue_c: float) -> float:
    d = ng_design(heat_mw, t_flue_c)
    co2 = d["co2_t_per_mwh"] * costs.co2_eur_t
    return (lcoh_bio - co2) / (d["ng_mwh_lhv_per_mwh"] * d["gcv_over_ncv"])


def assert_ranked_temperatures_equal(t_process_c: float, t_flue_c: float) -> None:
    if abs(t_process_c - t_flue_c) > 1e-6:
        raise ValueError(
            "Ranked LCOH keeps flue exit equal to process temperature. "
            "bhlcoh.chain_inputs has no flue-exit approach, and a cooler flue "
            "without air preheat would be a recuperator the plant model does not close. "
            f"Got process {t_process_c} degC and flue {t_flue_c} degC."
        )


def evaluate_config(config: str, *, t_process_c: float, t_flue_c: float, heat_mw: float,
                    flh: float, load_id: str, costs: CostInputs | None = None,
                    mean_price: float = PUBLISHED_MEAN_DA_EUR_MWH) -> dict:
    """One chain at one case. Raises if process and flue temperatures differ."""
    assert_ranked_temperatures_equal(t_process_c, t_flue_c)
    costs = costs if costs is not None else CostInputs()
    case_costs = costs.with_(flh=flh)
    basis = electricity_cost_basis(config, load_id)
    dp = design_kpis(config, t_process_c, t_flue_c, heat_mw)
    if not dp["ok"]:
        return {
            "config": config,
            "ok": False,
            "error": dp["error"],
            "electricity_cost_basis": basis,
            "flue_exit_c_model": None,
        }
    dispatch = scaled_dispatch(config, t_flue_c, heat_mw) if config in ELECTROLYSER_CONFIGS else None
    chain = chain_inputs(config, mean_price, dispatch, heat_mw=heat_mw, t_process_c=t_flue_c)
    # chain_inputs just re-ran the same design point. Biomass must match.
    if abs(chain.biomass_mwh_per_mwh - dp["biomass_MWh_per_MWh"]) > 1e-9:
        raise RuntimeError(f"{config}: chain_inputs biomass drifted from design_point")
    if dispatch is not None:
        # Scaled electricity stays in a fixed ratio to the design-point electricity.
        ref = PUBLISHED_O4[config]["electricity_mwh_per_mwh_heat"]
        ref_dp = design_kpis(config, REFERENCE_T_C, REFERENCE_T_C, 10.0)
        ref_ratio = ref / ref_dp["electricity_MWh_per_MWh"]
        ratio = chain.electricity_mwh_per_mwh_heat / dp["electricity_MWh_per_MWh"]
        if abs(ratio - ref_ratio) > 1e-6:
            raise RuntimeError(
                f"{config}: scaled dispatch electricity is not consistent with the "
                f"plant-model electricity ratio ({ratio} vs {ref_ratio})"
            )
    breakdown = lcoh_breakdown(chain, case_costs)
    parts = grouped(breakdown)
    ng = ng_lcoh(case_costs, heat_mw, t_flue_c)
    biogenic = stack_co2_t_per_mwh(config, t_flue_c, heat_mw)
    fossil_direct = 0.0  # fuel carbon is biogenic; grid electricity is not counted
    return {
        "config": config,
        "ok": True,
        "label": chain.label,
        "electricity_cost_basis": basis,
        "strategy": chain.strategy,
        "capacity_factor": chain.capacity_factor,
        "storage_h": chain.storage_h,
        "flue_exit_c_model": dp["flue_exit_C"],
        "biomass_mwh_per_mwh": chain.biomass_mwh_per_mwh,
        "electricity_mwh_per_mwh": chain.electricity_mwh_per_mwh_heat,
        "fuel_lhv_mw": chain.fuel_lhv_mw,
        "available_heat_frac": dp["available_heat_frac"],
        "lcoh": breakdown["total"],
        "lcoh_capex": parts["CAPEX"],
        "lcoh_om": parts["O&M"],
        "lcoh_biomass": parts["Biomass"],
        "lcoh_electricity": parts["Electricity"],
        "capex_meur": breakdown["capex_total_meur"],
        "ng_lcoh": ng["total"],
        "ng_fuel": ng["fuel"],
        "ng_co2": ng["co2"],
        "gap_to_ng": breakdown["total"] - ng["total"],
        "breakeven_co2_eur_t": breakeven_co2_eur_t(breakdown["total"], case_costs, heat_mw, t_flue_c),
        "breakeven_gas_eur_mwh_gcv": breakeven_gas_eur_mwh_gcv(
            breakdown["total"], case_costs, heat_mw, t_flue_c),
        "direct_fossil_co2_t_per_mwh": fossil_direct,
        "biogenic_stack_co2_t_per_mwh": biogenic,
        "displaced_direct_fossil_co2_t_per_mwh": ng_design(heat_mw, t_flue_c)["co2_t_per_mwh"],
        # Not estimated. Do not treat biogenic stack CO2 or displaced fossil CO2 as lifecycle GHG.
        "lifecycle_ghg_t_per_mwh": None,
    }


def natural_gas_row(t_flue_c: float, heat_mw: float, costs: CostInputs | None = None) -> dict:
    costs = costs if costs is not None else CostInputs()
    ng = ng_lcoh(costs, heat_mw, t_flue_c)
    d = ng_design(heat_mw, t_flue_c)
    return {
        "lcoh": ng["total"],
        "ng_lcoh": ng["total"],
        "ng_fuel": ng["fuel"],
        "ng_co2": ng["co2"],
        "gap_to_ng": 0.0,
        "direct_fossil_co2_t_per_mwh": d["co2_t_per_mwh"],
        "biogenic_stack_co2_t_per_mwh": 0.0,
        "displaced_direct_fossil_co2_t_per_mwh": 0.0,
        "lifecycle_ghg_t_per_mwh": None,
        "ng_mwh_lhv_per_mwh": d["ng_mwh_lhv_per_mwh"],
        "available_heat_frac_ng": 1.0 / d["ng_mwh_lhv_per_mwh"],
    }
