"""Screening tests. Temperature dependence is checked against the plant model, not against a rescale."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from bhscenarios.assumptions import (
    KWH_TO_MJ,
    TWO_SHIFT_FLH_H,
    WOBBE_MAX_MJ_NM3,
    WOBBE_MIN_MJ_NM3,
    EASEE_WOBBE_KWH_MAX,
    EASEE_WOBBE_KWH_MIN,
)
from bhscenarios.economics import evaluate_config
from bhscenarios.quality import fuel_class, thermal_assessment
from bhscenarios.reference_dispatch import PUBLISHED_LCOH_EUR_MWH
from bhscenarios.screen import run_screening
from bhscenarios.technical import (
    available_heat_fraction,
    fuel_properties,
    synthetic_two_shift_week,
    throughput_scale,
)
from biomass_heat import Plant

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def table() -> pd.DataFrame:
    return run_screening()


def _cont(table: pd.DataFrame, config: str, t: float) -> pd.Series:
    m = table[(table["load_id"] == "continuous") & (table["config"] == config) & (table["t_process_c"] == t)]
    assert len(m) == 1
    return m.iloc[0]


def test_wobbe_band_is_the_cited_kwh_range_times_3_6():
    assert WOBBE_MIN_MJ_NM3 == pytest.approx(EASEE_WOBBE_KWH_MIN * KWH_TO_MJ)
    assert WOBBE_MAX_MJ_NM3 == pytest.approx(EASEE_WOBBE_KWH_MAX * KWH_TO_MJ)
    assert KWH_TO_MJ == 3.6


def test_illustrative_natural_gas_sits_inside_the_published_band():
    ng = fuel_properties("natural_gas")
    assert fuel_class(ng["wobbe_mj_nm3"], ng["rel_density"], ng["h2_vol_dry"]) == "band_low_h2"
    assert WOBBE_MIN_MJ_NM3 < ng["wobbe_mj_nm3"] < WOBBE_MAX_MJ_NM3


def test_wobbe_and_flame_temperature_do_not_depend_on_process_temperature():
    a = fuel_properties("air")
    b = fuel_properties("air")
    assert a["wobbe_mj_nm3"] == pytest.approx(b["wobbe_mj_nm3"])
    # design-point Wobbe at two flue temperatures is the same composition
    from bhscenarios.technical import design_kpis
    lo = design_kpis("oxy_full", 300, 300)
    hi = design_kpis("oxy_full", 1300, 1300)
    assert lo["fuel_wobbe_MJ_Nm3"] == pytest.approx(hi["fuel_wobbe_MJ_Nm3"])
    assert lo["adiabatic_flame_C"] == pytest.approx(hi["adiabatic_flame_C"])


def test_available_heat_depends_on_flue_exit_not_on_a_single_rescale():
    air_300 = available_heat_fraction("air", 300)
    air_1300 = available_heat_fraction("air", 1300)
    dfb_300 = available_heat_fraction("steam_dfb", 300)
    dfb_1300 = available_heat_fraction("steam_dfb", 1300)
    assert air_300 > air_1300
    assert dfb_300 > dfb_1300
    air_ratio = air_1300 / air_300
    dfb_ratio = dfb_1300 / dfb_300
    assert abs(air_ratio - dfb_ratio) > 0.01


def test_cool_flue_does_not_make_a_hotter_process_feasible():
    props = fuel_properties("air")
    frac = available_heat_fraction("air", 800)
    assert frac is not None and frac > 0
    hot = thermal_assessment(props["t_ad_c"], t_process_c=1600, t_flue_c=800, available_heat_frac=frac)
    assert hot["thermally_feasible"] is False
    assert hot["infeasibility_reason"] == "adiabatic_flame_temperature_does_not_exceed_process_temperature"
    ok = thermal_assessment(props["t_ad_c"], t_process_c=800, t_flue_c=800, available_heat_frac=frac)
    assert ok["thermally_feasible"] is True


def test_ranked_lcoh_rejects_unequal_process_and_flue_temperatures():
    with pytest.raises(ValueError, match="flue exit"):
        evaluate_config("steam_dfb", t_process_c=1000, t_flue_c=800, heat_mw=10, flh=8000, load_id="continuous")


def test_biomass_intensity_tracks_available_heat_and_ratios_differ():
    from bhscenarios.technical import design_kpis
    ratios = {}
    for config in ("air", "steam_dfb", "oxy_full"):
        lo = design_kpis(config, 300, 300)
        hi = design_kpis(config, 1300, 1300)
        # biomass per MWh heat * available-heat fraction is invariant in temperature
        assert lo["biomass_MWh_per_MWh"] * lo["available_heat_frac"] == pytest.approx(
            hi["biomass_MWh_per_MWh"] * hi["available_heat_frac"], rel=1e-9)
        ratios[config] = hi["biomass_MWh_per_MWh"] / lo["biomass_MWh_per_MWh"]
    assert abs(ratios["air"] - ratios["steam_dfb"]) > 0.02
    assert abs(ratios["air"] - ratios["oxy_full"]) > 0.02


def test_1000c_continuous_reproduces_published_lcoh(table: pd.DataFrame):
    for config, published in PUBLISHED_LCOH_EUR_MWH.items():
        got = float(_cont(table, config, 1000)["lcoh"])
        assert got == pytest.approx(published, abs=0.05)


def test_rescaling_1000c_lcoh_does_not_match_the_recomputed_value(table: pd.DataFrame):
    for config, t in (("air", 300), ("air", 1300), ("steam_dfb", 1300), ("oxy_full", 300)):
        row = _cont(table, config, t)
        assert abs(row["lcoh"] - row["lcoh_if_rescaled_from_1000C"]) > 5.0


def test_using_another_chains_ratio_is_a_different_number(table: pd.DataFrame):
    air_1000 = _cont(table, "air", 1000)
    air_1300 = _cont(table, "air", 1300)
    dfb_1000 = _cont(table, "steam_dfb", 1000)
    dfb_1300 = _cont(table, "steam_dfb", 1300)
    air_ratio = air_1300["lcoh_biomass"] / air_1000["lcoh_biomass"]
    mistaken = dfb_1000["lcoh"] * air_ratio
    assert abs(mistaken - dfb_1300["lcoh"]) > 5.0


def test_lcoh_and_natural_gas_rise_with_flue_temperature(table: pd.DataFrame):
    for config in ("air", "steam_dfb", "oxy_none", "oxy_full", "natural_gas"):
        vals = [float(_cont(table, config, t)["lcoh"]) for t in (300, 800, 1000, 1300)]
        assert vals == sorted(vals)
        assert vals[-1] - vals[0] > 10.0


def test_break_even_uses_the_case_temperature_not_the_1000c_helper(table: pd.DataFrame):
    from bhlcoh.reference import breakeven_co2_price
    from bhlcoh.costs import CostInputs
    costs = CostInputs()
    row = _cont(table, "steam_dfb", 1000)
    helper = breakeven_co2_price(float(row["lcoh"]), costs)
    assert float(row["breakeven_co2_eur_t"]) == pytest.approx(helper, abs=0.05)
    hot = _cont(table, "steam_dfb", 1300)
    # The library helper ignores flue temperature. The screening value must move.
    assert abs(float(hot["breakeven_co2_eur_t"]) - helper) > 1.0
    assert float(hot["direct_fossil_co2_t_per_mwh"]) == 0.0
    assert float(_cont(table, "natural_gas", 1300)["direct_fossil_co2_t_per_mwh"]) > float(
        _cont(table, "natural_gas", 300)["direct_fossil_co2_t_per_mwh"])


def test_emissions_are_split_and_lifecycle_is_not_estimated(table: pd.DataFrame):
    dfb = _cont(table, "steam_dfb", 1000)
    ng = _cont(table, "natural_gas", 1000)
    assert float(dfb["direct_fossil_co2_t_per_mwh"]) == 0.0
    assert float(dfb["biogenic_stack_co2_t_per_mwh"]) > 0.2
    assert float(ng["biogenic_stack_co2_t_per_mwh"]) == 0.0
    assert float(ng["direct_fossil_co2_t_per_mwh"]) == pytest.approx(float(dfb["displaced_direct_fossil_co2_t_per_mwh"]))
    assert pd.isna(dfb["lifecycle_ghg_t_per_mwh"])
    assert pd.isna(ng["lifecycle_ghg_t_per_mwh"])


def test_two_shift_raises_capital_recovery_and_does_not_change_biomass(table: pd.DataFrame):
    for config in ("steam_dfb", "air", "oxy_none"):
        a = table[(table["config"] == config) & (table["t_process_c"] == 1000) & (table["load_id"] == "continuous")].iloc[0]
        b = table[(table["config"] == config) & (table["t_process_c"] == 1000) & (table["load_id"] == "two_shift")].iloc[0]
        assert b["flh"] == TWO_SHIFT_FLH_H
        assert float(b["lcoh_biomass"]) == pytest.approx(float(a["lcoh_biomass"]))
        assert float(b["lcoh"]) > float(a["lcoh"]) + 10.0
        assert b["rank_basis"] == "full"
    elec = table[(table["config"] == "oxy_full") & (table["t_process_c"] == 800) & (table["load_id"] == "two_shift")].iloc[0]
    assert elec["rank_basis"] == "provisional_dispatch"
    assert elec["electricity_cost_basis"] == "o4_not_reoptimised_for_two_shift"


def test_p1_8760h_is_cheaper_than_300c_at_8000h_for_the_same_chain(table: pd.DataFrame):
    p1 = table[(table["case_id"] == "P1") & (table["config"] == "steam_dfb")].iloc[0]
    base = _cont(table, "steam_dfb", 300)
    assert p1["flh"] == 8760
    assert float(p1["lcoh_biomass"]) == pytest.approx(float(base["lcoh_biomass"]))
    assert float(p1["lcoh"]) < float(base["lcoh"])


def test_reference_dispatch_scale_is_one_at_the_published_point():
    assert throughput_scale("oxy_full", 1000, 10) == pytest.approx(1.0, abs=1e-12)
    assert throughput_scale("oxy_full", 1000, 20) == pytest.approx(2.0, rel=1e-9)


def test_follow_demand_cost_scales_with_plant_electricity():
    """Hourly plant simulation, flat price. Not the O4 LP."""
    prices = [80.0] * 24
    demand = [10e6] * 24
    costs = {}
    intensity = {}
    for t in (300, 1000, 1300):
        df = Plant("oxy_full").simulate(demand, prices, T_process=t + 273.15)
        heat = float(df["heat_MW"].sum())
        costs[t] = float(df["electricity_cost_eur"].sum()) / heat
        intensity[t] = float(df["electricity_MW"].sum()) / heat
    ratio_cost = costs[1300] / costs[1000]
    ratio_el = intensity[1300] / intensity[1000]
    assert ratio_cost == pytest.approx(ratio_el, rel=1e-6)
    assert ratio_el == pytest.approx(throughput_scale("oxy_full", 1300, 10), rel=1e-6)
    # Air's throughput ratio is a different number, so one rescale would miss it.
    assert abs(throughput_scale("air", 1300, 10) - ratio_el) > 0.02


def test_two_shift_week_matches_the_design_point_integral():
    hours = synthetic_two_shift_week(10e6)
    assert sum(1 for h in hours if h > 0) == 80
    df = Plant("steam_dfb").simulate(hours, [0.0] * len(hours), T_process=800 + 273.15)
    dp = Plant("steam_dfb").design_point(10e6, 800 + 273.15)
    expected = dp["biomass_lhv_MW"] * 80
    assert float(df["biomass_MW"].sum()) == pytest.approx(expected, rel=1e-6)


def test_full_methanation_misses_the_band_on_density_not_on_wobbe():
    from bhscenarios.quality import band_failures
    fuel = fuel_properties("oxy_full")
    assert band_failures(fuel["wobbe_mj_nm3"], fuel["rel_density"]) == ["density_below_band"]
    assert fuel["h2_vol_dry"] > 1.0
    assert fuel_class(fuel["wobbe_mj_nm3"], fuel["rel_density"], fuel["h2_vol_dry"]) == "outside_published_band"


def test_air_and_electrolyser_blend_swap_rank_as_temperature_rises(table: pd.DataFrame):
    def order(t: float) -> list[str]:
        g = table[(table["load_id"] == "continuous") & (table["t_process_c"] == t) & table["rank"].notna()]
        return g.sort_values("rank")["config"].tolist()
    assert order(300)[:4] == ["steam_dfb", "oxy_none", "air", "oxy_none_elec"]
    assert order(1000)[:4] == ["steam_dfb", "oxy_none", "oxy_none_elec", "air"]
    assert order(1300)[3] == "air"


def test_euro_gap_and_break_even_co2_move_differently(table: pd.DataFrame):
    low = _cont(table, "steam_dfb", 300)
    high = _cont(table, "steam_dfb", 1300)
    assert float(high["gap_to_ng"]) > float(low["gap_to_ng"])
    assert float(high["breakeven_co2_eur_t"]) < float(low["breakeven_co2_eur_t"])


def test_air_at_1300c_has_the_smallest_positive_margin(table: pd.DataFrame):
    cont = table[table["load_id"] == "continuous"]
    margins = cont[cont["config"] != "natural_gas"].groupby("config")["margin_k"].min()
    assert margins.idxmin() == "air"
    air = float(_cont(table, "air", 1300)["margin_k"])
    assert 200 < air < 250
    assert bool(_cont(table, "air", 1300)["thermally_feasible"]) is True


def test_published_rank_order_at_1000c(table: pd.DataFrame):
    g = table[(table["case_id"] == "T1000_continuous") & table["rank"].notna()].sort_values("rank")
    assert g["config"].tolist() == [
        "steam_dfb", "oxy_none", "oxy_none_elec", "air", "oxy_partial", "oxy_full",
    ]
    assert bool(g["beats_natural_gas"].any()) is False


def test_infeasible_process_is_unranked_when_flame_temperature_is_too_low():
    props = fuel_properties("air")
    # Above the adiabatic flame temperature the design point itself fails.
    from bhscenarios.technical import design_kpis
    failed = design_kpis("air", props["t_ad_c"] + 50, props["t_ad_c"] + 50)
    assert failed["ok"] is False


def test_economics_module_does_not_call_the_1000c_helpers():
    import inspect
    import bhscenarios.economics as econ
    src = inspect.getsource(econ)
    assert "run_dispatch(" not in src
    assert "breakeven_co2_price(" not in src


def test_plot_writes_a_figure(table: pd.DataFrame, tmp_path: Path):
    from bhscenarios.plotting import plot_screening
    path = plot_screening(table, tmp_path / "screen.png")
    assert path.is_file()
    assert path.stat().st_size > 10_000


def test_committed_table_matches_a_fresh_run(table: pd.DataFrame):
    committed = pd.read_csv(ROOT / "results" / "screening_results.csv")
    keys = ["case_id", "config"]
    cols = ["lcoh", "breakeven_co2_eur_t", "biomass_mwh_per_mwh", "gap_to_ng", "biogenic_stack_co2_t_per_mwh"]
    merged = committed.merge(table, on=keys, suffixes=("_c", "_f"))
    assert len(merged) == len(table)
    for col in cols:
        both = merged[[f"{col}_c", f"{col}_f"]].dropna()
        if both.empty:
            continue
        assert (both[f"{col}_c"] - both[f"{col}_f"]).abs().max() < 1e-6
