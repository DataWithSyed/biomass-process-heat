"""Build the screening table: temperature x load x chain."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from bhlcoh.costs import CostInputs

from .assumptions import (
    CHAIN_ORDER,
    CONTINUOUS_FLH_H,
    HEAT_MW,
    P1_CALENDAR_FLH_H,
    TEMPERATURES_C,
    TWO_SHIFT_FLH_H,
)
from .economics import evaluate_config, natural_gas_row
from .quality import band_failures, fuel_class, interchangeability_pass, thermal_assessment
from .technical import available_heat_fraction, fuel_properties, stack_co2_t_per_mwh


@dataclass(frozen=True)
class Case:
    case_id: str
    named: str
    t_process_c: float
    t_flue_c: float
    heat_mw: float
    flh: float
    load_id: str
    load_note: str


def build_cases() -> list[Case]:
    """Temperature factorial at 8000 h and at the two-shift profile, plus P1 at 8760 h.

    P3 and P4 are the 1000 degC and 1300 degC rows of the 8000 h series.
    P2 is the 800 degC two-shift row. P1 keeps the 8760 h written in the
    umbrella scenario sheet, so the temperature comparison is not confounded
    with that calendar-year assumption.
    """
    cases: list[Case] = []
    for t in TEMPERATURES_C:
        named_c = {1000: "P3", 1300: "P4"}.get(t, "")
        cases.append(Case(
            f"T{t}_continuous", named_c, float(t), float(t), HEAT_MW, CONTINUOUS_FLH_H,
            "continuous",
            "8000 h/y at 10 MW. Thunman full-load hours used by the LCOH model. "
            "Flue exit equals process temperature.",
        ))
        named_s = "P2" if t == 800 else ""
        cases.append(Case(
            f"T{t}_two_shift", named_s, float(t), float(t), HEAT_MW, TWO_SHIFT_FLH_H,
            "two_shift",
            "4160 h/y = 16 h x 5 d x 52 wk at 10 MW peak. Synthetic profile, no holidays. "
            "Flue exit equals process temperature.",
        ))
    cases.append(Case(
        "P1", "P1", 300.0, 300.0, HEAT_MW, P1_CALENDAR_FLH_H, "continuous_8760",
        "300 degC, 8760 h/y, the continuous calendar year written for P1. "
        "No outage. Not used as the temperature-comparison basis.",
    ))
    return cases


def _naive_from_1000(row: pd.Series, base: pd.DataFrame) -> float | None:
    """Published-style mistake: scale the 1000 degC LCOH by the biomass-intensity ratio.

    Stored so the table can show that the recomputed LCOH is a different number.
    Only defined for continuous 8000 h rows, where FLH matches the reference.
    """
    if row["load_id"] != "continuous" or row["config"] == "natural_gas":
        return None
    if not row["thermally_feasible"]:
        return None
    ref = base.loc[row["config"]]
    if ref["lcoh_biomass"] == 0:
        return None
    return float(ref["lcoh"] * (row["lcoh_biomass"] / ref["lcoh_biomass"]))


def run_screening(costs: CostInputs | None = None) -> pd.DataFrame:
    """Rankable table. One row per case and chain, plus a natural-gas row per case."""
    costs = costs if costs is not None else CostInputs()
    props = {cfg: fuel_properties(cfg) for cfg in (*CHAIN_ORDER, "natural_gas")}
    rows: list[dict] = []
    for case in build_cases():
        ng = natural_gas_row(case.t_flue_c, case.heat_mw, costs)
        for config in (*CHAIN_ORDER, "natural_gas"):
            fuel = props[config]
            frac = available_heat_fraction(config, case.t_flue_c)
            thermal = thermal_assessment(fuel["t_ad_c"], case.t_process_c, case.t_flue_c, frac)
            fclass = fuel_class(fuel["wobbe_mj_nm3"], fuel["rel_density"], fuel["h2_vol_dry"])
            fails = band_failures(fuel["wobbe_mj_nm3"], fuel["rel_density"])
            row = {
                "case_id": case.case_id,
                "named": case.named,
                "load_id": case.load_id,
                "load_note": case.load_note,
                "t_process_c": case.t_process_c,
                "t_flue_c": case.t_flue_c,
                "flue_exit_approach_k": case.t_flue_c - case.t_process_c,
                "heat_mw": case.heat_mw,
                "flh": case.flh,
                "config": config,
                "label": fuel["label"],
                "lhv_mj_nm3": fuel["lhv_mj_nm3"],
                "wobbe_mj_nm3": fuel["wobbe_mj_nm3"],
                "rel_density": fuel["rel_density"],
                "h2_vol_dry": fuel["h2_vol_dry"],
                "ch4_vol_dry": fuel["ch4_vol_dry"],
                "t_ad_c": fuel["t_ad_c"],
                "available_heat_frac": frac,
                "fuel_class": fclass,
                "band_fail_reasons": "|".join(fails),
                "interchangeability_pass": interchangeability_pass(fclass) or config == "natural_gas",
                **thermal,
            }
            if config == "natural_gas":
                # Illustrative reference gas. direct fossil CO2 is the burner stack, not lifecycle.
                biogenic_check = stack_co2_t_per_mwh("natural_gas", case.t_flue_c, case.heat_mw)
                row.update({
                    "ok": True,
                    "electricity_cost_basis": "not_applicable",
                    "strategy": "",
                    "capacity_factor": None,
                    "storage_h": None,
                    "flue_exit_c_model": case.t_flue_c,
                    "biomass_mwh_per_mwh": None,
                    "electricity_mwh_per_mwh": None,
                    "fuel_lhv_mw": None,
                    "lcoh": ng["lcoh"],
                    "lcoh_capex": 0.0,
                    "lcoh_om": 0.0,
                    "lcoh_biomass": 0.0,
                    "lcoh_electricity": 0.0,
                    "capex_meur": 0.0,
                    "ng_lcoh": ng["ng_lcoh"],
                    "ng_fuel": ng["ng_fuel"],
                    "ng_co2": ng["ng_co2"],
                    "gap_to_ng": 0.0,
                    "breakeven_co2_eur_t": None,
                    "breakeven_gas_eur_mwh_gcv": None,
                    "direct_fossil_co2_t_per_mwh": ng["direct_fossil_co2_t_per_mwh"],
                    "biogenic_stack_co2_t_per_mwh": 0.0,
                    "displaced_direct_fossil_co2_t_per_mwh": 0.0,
                    "lifecycle_ghg_t_per_mwh": None,
                    "beats_natural_gas": False,
                })
                if biogenic_check is not None and abs(biogenic_check - ng["direct_fossil_co2_t_per_mwh"]) > 1e-9:
                    raise RuntimeError("natural-gas stack CO2 helpers disagree")
            elif not thermal["thermally_feasible"]:
                row.update({
                    "ok": False,
                    "electricity_cost_basis": "",
                    "strategy": "",
                    "capacity_factor": None,
                    "storage_h": None,
                    "flue_exit_c_model": None,
                    "biomass_mwh_per_mwh": None,
                    "electricity_mwh_per_mwh": None,
                    "fuel_lhv_mw": None,
                    "lcoh": None,
                    "lcoh_capex": None,
                    "lcoh_om": None,
                    "lcoh_biomass": None,
                    "lcoh_electricity": None,
                    "capex_meur": None,
                    "ng_lcoh": ng["ng_lcoh"],
                    "ng_fuel": ng["ng_fuel"],
                    "ng_co2": ng["ng_co2"],
                    "gap_to_ng": None,
                    "breakeven_co2_eur_t": None,
                    "breakeven_gas_eur_mwh_gcv": None,
                    "direct_fossil_co2_t_per_mwh": None,
                    "biogenic_stack_co2_t_per_mwh": None,
                    "displaced_direct_fossil_co2_t_per_mwh": ng["direct_fossil_co2_t_per_mwh"],
                    "lifecycle_ghg_t_per_mwh": None,
                    "beats_natural_gas": False,
                })
            else:
                econ = evaluate_config(
                    config,
                    t_process_c=case.t_process_c,
                    t_flue_c=case.t_flue_c,
                    heat_mw=case.heat_mw,
                    flh=case.flh,
                    load_id=case.load_id,
                    costs=costs,
                )
                row.update(econ)
                row["beats_natural_gas"] = bool(econ["lcoh"] < econ["ng_lcoh"])
                row["label"] = econ["label"]
            rows.append(row)

    df = pd.DataFrame(rows)
    base = df[(df["load_id"] == "continuous") & (df["t_process_c"] == 1000.0) & (df["config"] != "natural_gas")]
    base = base.set_index("config")
    df["lcoh_if_rescaled_from_1000C"] = df.apply(lambda r: _naive_from_1000(r, base), axis=1)
    return _assign_ranks(df)


def _assign_ranks(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rank"] = pd.NA
    df["rank_basis"] = ""
    for case_id in df["case_id"].unique():
        mask = (
            (df["case_id"] == case_id)
            & df["thermally_feasible"]
            & (df["config"] != "natural_gas")
        )
        order = df.loc[mask].sort_values(["lcoh", "config"], kind="mergesort")
        for i, idx in enumerate(order.index, start=1):
            df.loc[idx, "rank"] = i
            provisional = str(df.loc[idx, "electricity_cost_basis"]).startswith("o4_not_reoptimised")
            df.loc[idx, "rank_basis"] = "provisional_dispatch" if provisional else "full"
    df["rank"] = df["rank"].astype("Int64")
    return df.sort_values(["t_process_c", "load_id", "rank", "config"], kind="mergesort").reset_index(drop=True)
