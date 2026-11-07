#!/usr/bin/env python3
"""Write screening tables and figures under scenarios/results and scenarios/figures."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhscenarios.plotting import plot_screening  # noqa: E402
from bhscenarios.reference_dispatch import PUBLISHED_LCOH_EUR_MWH  # noqa: E402
from bhscenarios.reporting import write_ranking  # noqa: E402
from bhscenarios.screen import run_screening  # noqa: E402
from bhscenarios.technical import available_heat_curve  # noqa: E402

import pandas as pd  # noqa: E402


def main() -> None:
    results = ROOT / "results"
    figures = ROOT / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    df = run_screening()
    df.to_csv(results / "screening_results.csv", index=False)
    pd.DataFrame(available_heat_curve()).to_csv(results / "available_heat_vs_flue_temperature.csv", index=False)
    write_ranking(df, results / "ranking.md")
    plot_screening(df, figures / "lcoh_and_available_heat.png")

    ref = df[df["case_id"] == "T1000_continuous"]
    worst = 0.0
    for config, published in PUBLISHED_LCOH_EUR_MWH.items():
        got = float(ref.loc[ref["config"] == config, "lcoh"].iloc[0])
        worst = max(worst, abs(got - published))
        print(f"{config:16s}  {got:10.3f}  published {published:10.3f}  d {got - published:+.4f}")
    if worst > 0.05:
        raise SystemExit(f"1000 degC LCOH drifted from the published study by {worst:.4f} EUR/MWh")
    print(f"wrote {results / 'screening_results.csv'}")
    print(f"max |difference| vs published 1000 degC LCOH: {worst:.4e} EUR/MWh")


if __name__ == "__main__":
    main()
