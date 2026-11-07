"""Markdown tables written next to the CSV. Numbers come from the screening frame."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .assumptions import CHAIN_ORDER
from .reference_dispatch import PUBLISHED_COMMIT, PUBLISHED_LCOH_EUR_MWH


def _fmt(value, digits=1) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return f"{float(value):.{digits}f}"


def _ranked(df: pd.DataFrame, case_id: str) -> pd.DataFrame:
    g = df[(df["case_id"] == case_id) & (df["config"] != "natural_gas") & df["rank"].notna()]
    return g.sort_values("rank")


def write_ranking(df: pd.DataFrame, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Scenario screening results")
    lines.append("")
    lines.append("Costs are model estimates on the LCOH central cost basis (EUR 2025).")
    lines.append("They are not measured heat prices and not a quote. No chain is certified")
    lines.append("for a burner, and no figure here is a lifecycle greenhouse-gas result.")
    lines.append("")
    lines.append("Flue-gas exit temperature equals the process temperature in every ranked")
    lines.append("row (plant-model assumption of no recuperation). The two temperatures are")
    lines.append("different inputs. Available heat uses the flue exit. Thermal feasibility")
    lines.append("uses the adiabatic flame temperature against the process temperature.")
    lines.append("")
    lines.append("## Reproduction of the 1000 °C / 8000 h LCOH")
    lines.append("")
    lines.append(f"Pinned to biomass-heat-lcoh commit `{PUBLISHED_COMMIT}`.")
    lines.append("")
    lines.append("| Chain | This screening | Published LCOH | Difference |")
    lines.append("|---|---:|---:|---:|")
    ref = df[(df["case_id"] == "T1000_continuous")]
    for config in (*CHAIN_ORDER, "natural_gas"):
        got = float(ref.loc[ref["config"] == config, "lcoh"].iloc[0])
        pub = PUBLISHED_LCOH_EUR_MWH[config]
        lines.append(f"| `{config}` | {_fmt(got, 2)} | {_fmt(pub, 2)} | {_fmt(got - pub, 3)} |")
    lines.append("")
    lines.append("## Named scenarios")
    lines.append("")
    lines.append("P1 is 300 °C at 8760 h. P2 is 800 °C on the two-shift profile (4160 h).")
    lines.append("P3 and P4 are 1000 °C and 1300 °C at 8000 h. Electrolyser rows on P2 are")
    lines.append("provisional: the O4 schedule was not re-solved for a two-shift shape.")
    lines.append("Steam DFB, oxyfuel-ASU and air gasification do not use that schedule.")
    lines.append("")
    for named in ("P1", "P2", "P3", "P4"):
        block = df[df["named"] == named]
        case_id = block["case_id"].iloc[0]
        head = block.iloc[0]
        ng = float(block.loc[block["config"] == "natural_gas", "lcoh"].iloc[0])
        lines.append(f"### {named} — {head['t_process_c']:.0f} °C, {head['load_id']}, {head['flh']:.0f} h")
        lines.append("")
        lines.append(f"Natural gas in the same furnace: **{_fmt(ng)} EUR/MWh** "
                     f"(fuel {_fmt(float(block['ng_fuel'].iloc[0]))} + direct fossil CO2 "
                     f"{_fmt(float(block['ng_co2'].iloc[0]))}).")
        lines.append("")
        lines.append("| Rank | Chain | LCOH | Gap to gas | Break-even CO2 | Fuel screen | Margin K | Rank basis |")
        lines.append("|---:|---|---:|---:|---:|---|---:|---|")
        for _, r in _ranked(df, case_id).iterrows():
            lines.append(
                f"| {int(r['rank'])} | {r['label']} | {_fmt(r['lcoh'])} | {_fmt(r['gap_to_ng'])} | "
                f"{_fmt(r['breakeven_co2_eur_t'], 0)} | `{r['fuel_class']}` | {_fmt(r['margin_k'], 0)} | "
                f"`{r['rank_basis']}` |"
            )
        lines.append("")

    lines.append("## Temperature comparison at 8000 h")
    lines.append("")
    lines.append("Same full-load hours as the LCOH step, so the change is the flue-exit")
    lines.append("balance (and the natural-gas balance at that same flue exit), not the load.")
    lines.append("`rescaled` multiplies the 1000 °C LCOH by the biomass-intensity ratio.")
    lines.append("It is shown because that shortcut does not reproduce the recomputed cost:")
    lines.append("CAPEX meets a scale exponent below 1, and the natural-gas reference moves too.")
    lines.append("")
    header = "| Chain | 300 °C | 800 °C | 1000 °C | 1300 °C | 1300 rescaled from 1000 | 1300 recomputed |"
    lines.append(header)
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    cont = df[df["load_id"] == "continuous"]
    for config in CHAIN_ORDER:
        g = cont[cont["config"] == config].set_index("t_process_c")
        naive = g.loc[1300, "lcoh_if_rescaled_from_1000C"]
        lines.append(
            f"| {g.loc[1000, 'label']} | {_fmt(g.loc[300, 'lcoh'])} | {_fmt(g.loc[800, 'lcoh'])} | "
            f"{_fmt(g.loc[1000, 'lcoh'])} | {_fmt(g.loc[1300, 'lcoh'])} | {_fmt(naive)} | "
            f"{_fmt(g.loc[1300, 'lcoh'])} |"
        )
    ng = cont[cont["config"] == "natural_gas"].set_index("t_process_c")
    lines.append(
        f"| Natural gas | {_fmt(ng.loc[300, 'lcoh'])} | {_fmt(ng.loc[800, 'lcoh'])} | "
        f"{_fmt(ng.loc[1000, 'lcoh'])} | {_fmt(ng.loc[1300, 'lcoh'])} |  |  |"
    )
    lines.append("")
    lines.append("## Direct stack CO2 at 8000 h, t per MWh of heat")
    lines.append("")
    lines.append("Biomass rows: biogenic carbon in the fuel gas. Natural gas: fossil carbon")
    lines.append("in the fuel gas. Neither column is a lifecycle emission. Electricity-grid")
    lines.append("emissions and biomass supply-chain emissions are not estimated.")
    lines.append("")
    lines.append("| Chain | 300 °C biogenic or fossil | 1000 °C | 1300 °C |")
    lines.append("|---|---:|---:|---:|")
    for config in (*CHAIN_ORDER, "natural_gas"):
        g = cont[cont["config"] == config].set_index("t_process_c")
        col = "direct_fossil_co2_t_per_mwh" if config == "natural_gas" else "biogenic_stack_co2_t_per_mwh"
        label = g.loc[1000, "label"]
        kind = "fossil" if config == "natural_gas" else "biogenic"
        lines.append(
            f"| {label} ({kind}) | {_fmt(g.loc[300, col], 3)} | {_fmt(g.loc[1000, col], 3)} | "
            f"{_fmt(g.loc[1300, col], 3)} |"
        )
    lines.append("")
    lines.append("## Fuel screen (independent of temperature)")
    lines.append("")
    lines.append("Upper Wobbe index and relative density are compared with EASEE-gas CBP")
    lines.append("2005-001/02 (13.60–15.81 kWh/m³ at 25 °C combustion / 0 °C volume,")
    lines.append("relative density 0.555–0.700). The plant-model Wobbe uses the same")
    lines.append("reference temperatures on an ideal-gas basis, not a real-gas ISO 6976 value.")
    lines.append("Passing the band is not a burner certificate. The CBP itself limits the band")
    lines.append("to insignificant hydrogen and gives no hydrogen number; the 1 vol-% and")
    lines.append("10 vol-% flags are screening assumptions.")
    lines.append("")
    lines.append("| Chain | LHV MJ/Nm³ | Wobbe MJ/Nm³ | rel. density | H2 vol-% dry | Class | Band misses | T_ad °C |")
    lines.append("|---|---:|---:|---:|---:|---|---|---:|")
    seen = df.drop_duplicates("config")
    for config in (*CHAIN_ORDER, "natural_gas"):
        r = seen[seen["config"] == config].iloc[0]
        misses = r["band_fail_reasons"] or "—"
        lines.append(
            f"| {r['label']} | {_fmt(r['lhv_mj_nm3'], 2)} | {_fmt(r['wobbe_mj_nm3'], 2)} | "
            f"{_fmt(r['rel_density'], 3)} | {_fmt(r['h2_vol_dry'], 2)} | `{r['fuel_class']}` | "
            f"`{misses}` | {_fmt(r['t_ad_c'], 0)} |"
        )
    lines.append("")
    full = seen[seen["config"] == "oxy_full"].iloc[0]
    if (
        "density_below_band" in str(full["band_fail_reasons"])
        and "wobbe_" not in str(full["band_fail_reasons"])
    ):
        lines.append(
            f"Full methanation is the near miss: Wobbe {_fmt(full['wobbe_mj_nm3'], 2)} MJ/Nm³ "
            f"is inside the cited band, and relative density {_fmt(full['rel_density'], 3)} "
            f"is below the 0.555 floor. Dry hydrogen is {_fmt(full['h2_vol_dry'], 2)} vol-%, "
            "above the 1 vol-% screening cut, so a density pass would still not be "
            "`band_low_h2`."
        )
        lines.append("")
    bio = seen[seen["config"] != "natural_gas"].drop_duplicates("config")
    low = bio.loc[bio["fuel_class"] == "band_low_h2", "label"].tolist()
    inside = bio.loc[bio["fuel_class"].str.startswith("band_"), "label"].tolist()
    lines.append(
        "Interchangeability screen (`band_low_h2` only): "
        + (", ".join(low) if low else "no biomass chain passes.")
    )
    lines.append(
        "Inside the published Wobbe and density window, including hydrogen flags: "
        + (", ".join(inside) if inside else "none.")
    )
    lines.append(
        "Chains outside that window would need a purpose-designed burner. "
        "This screen does not design or certify one."
    )
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
