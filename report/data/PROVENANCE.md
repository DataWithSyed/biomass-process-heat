# Provenance of report data and figures

Nothing in this folder was typed in by hand. Each file is a copy of a result produced by the
code of one step repository, at the commit given below (copied on 2026-11-10).

| File(s) in `report/` | Source repo | Source path | Commit |
|---|---|---|---|
| `data/plant_results_table.csv`, `figures/02a_*`, `figures/02b_*` | biomass-heat-plant-model | `results/results_table.csv`, `results/fuel_quality_vs_natural_gas.png`, `results/inputs_per_mwh_heat.png` | `4dc13cb` |
| `data/dispatch_summary.csv`, `figures/03a_*`, `figures/03b_*` | biomass-heat-electrolysis-dispatch | `results/dispatch_summary.csv`, `figures/01_dispatch_cost_and_storage.png`, `figures/03_capacity_oversizing.png` | `b0624d4` |
| `data/lcoh_results.csv`, `data/lcoh_scale_sweep.csv`, `data/lcoh_monte_carlo_summary.csv`, `figures/04a-04d_*` | biomass-heat-lcoh | `results/lcoh_results.csv`, `results/scale_sweep.csv`, `results/monte_carlo_summary.csv`, `figures/01,03,04,06_*.png` | `b4d6853` |
| `data/scenarios_ranking_best_feasible.csv`, `figures/05a_*`, `figures/05b_*` | biomass-heat-scenarios | `results/ranking_best_feasible.csv`, `figures/01_lcoh_by_process.png`, `figures/03_gas_quality.png` | `6d4711f` |
| `data/dashboard_temperature_sweep.csv`, `figures/06a_*`, `figures/06b_*` | biomass-heat-dashboard | `results/temperature_sweep.csv`, `figures/00_dashboard_screenshot.png`, `figures/03_temperature_sweep.png` | `2e492d4` |

Derived in this repo by `scripts/make_figures.py` (reads only the CSVs above):

* `data/levers_dfb_1000C.csv` and `figures/00_levers_dfb_1000C.png`
* `figures/05c_breakeven_by_process.png`

Regenerate: `pip install pandas matplotlib && python report/scripts/make_figures.py`.

The day-ahead prices behind steps 3-6 are Energy-Charts.info (Fraunhofer ISE) DE-LU data,
CC BY 4.0, underlying source Bundesnetzagentur | SMARD.de.
