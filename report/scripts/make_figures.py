"""Synthesis figures for the final report.

Reads only the result CSVs copied into report/data/ from the step repos (see
report/data/PROVENANCE.md). No numbers are typed in by hand.

    python report/scripts/make_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
FIG = HERE / "figures"


def levers_table() -> pd.DataFrame:
    """Cheapest chain (steam DFB) at 1000 degC: how far each lever closes the gap to gas."""
    lc = pd.read_csv(DATA / "lcoh_results.csv")
    sc = pd.read_csv(DATA / "lcoh_scale_sweep.csv")
    rk = pd.read_csv(DATA / "scenarios_ranking_best_feasible.csv")
    dfb = lc[lc.config == "steam_dfb"].set_index("scenario")
    p3r = rk[(rk.cost_case == "central") & (rk.process == "P3") & rk.recuperation].iloc[0]
    s100 = sc[(sc.heat_mw == 100) & (sc.config == "steam_dfb")].set_index("scenario")
    rows = [
        ("10 MW, central costs", dfb.loc["central", "lcoh"], dfb.loc["central", "ng_lcoh"],
         dfb.loc["central", "breakeven_co2_eur_t"]),
        ("10 MW, integrated site", dfb.loc["integrated", "lcoh"], dfb.loc["integrated", "ng_lcoh"],
         dfb.loc["integrated", "breakeven_co2_eur_t"]),
        ("10 MW, recuperative preheat", p3r.lcoh, p3r.ng_lcoh, p3r.breakeven_co2),
        ("100 MW, central costs", s100.loc["central", "lcoh"], dfb.loc["central", "ng_lcoh"],
         s100.loc["central", "breakeven_co2_eur_t"]),
        ("100 MW, integrated site", s100.loc["integrated", "lcoh"], dfb.loc["central", "ng_lcoh"],
         s100.loc["integrated", "breakeven_co2_eur_t"]),
    ]
    return pd.DataFrame(rows, columns=["case", "lcoh_dfb", "lcoh_ng", "breakeven_co2"])


def fig_levers(df: pd.DataFrame) -> Path:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6))
    y = range(len(df))[::-1]
    a1.barh(list(y), df.lcoh_dfb, color="#4c8c4a", label="steam DFB (cheapest biomass chain)")
    a1.scatter(df.lcoh_ng, list(y), color="black", marker="|", s=400, zorder=3,
               label="natural gas + EUA 76 EUR/t")
    a1.set_yticks(list(y))
    a1.set_yticklabels(df.case)
    a1.set_xlabel("LCOH, EUR per MWh heat (1000 degC process)")
    a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=8, frameon=False)
    a1.set_title("Levers on the cost gap")
    a2.barh(list(y), df.breakeven_co2, color="#c0504d")
    a2.axvline(76.02, color="black", ls="--", lw=1)
    a2.text(84, -0.45, "EUA 2026 H1: 76 EUR/t", fontsize=8, va="center")
    a2.set_yticks(list(y))
    a2.set_yticklabels([])
    a2.set_xlabel("break-even CO2 price, EUR/t")
    a2.set_title("CO2 price at which DFB beats gas")
    for yy, v in zip(y, df.breakeven_co2):
        a2.text(v + 8, yy, f"{v:.0f}", va="center", fontsize=8)
    fig.tight_layout()
    out = FIG / "00_levers_dfb_1000C.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def fig_chain_overview() -> Path:
    """Best feasible chain and break-even CO2 for P1-P4, central vs integrated costs."""
    rk = pd.read_csv(DATA / "scenarios_ranking_best_feasible.csv")
    rk = rk[~rk.recuperation]
    piv = rk.pivot(index="process", columns="cost_case", values="breakeven_co2")
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    piv.plot.bar(ax=ax, color=["#c0504d", "#e3a39f"], rot=0)
    ax.axhline(76.02, color="black", ls="--", lw=1, label="EUA 76 EUR/t")
    ax.set_ylabel("break-even CO2, EUR/t")
    ax.set_xlabel("process scenario (P1 300 / P2 800 two-shift / P3 1000 / P4 1300 degC)")
    ax.set_title("Best feasible chain per process, cold combustion air")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = FIG / "05c_breakeven_by_process.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


if __name__ == "__main__":
    t = levers_table()
    t.round(1).to_csv(DATA / "levers_dfb_1000C.csv", index=False)
    print(t.round(1).to_string(index=False))
    print(fig_levers(t))
    print(fig_chain_overview())
