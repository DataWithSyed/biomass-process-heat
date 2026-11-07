# Scenario definitions

Scenarios combine a **process requirement** (what the industrial user needs) with a
**plant configuration** (which chain supplies it) and an **economic setting**. Values marked
*(assumption)* are illustrative screening values chosen by the author. Values marked *(to
be sourced)* will be replaced with cited data in the repo named in brackets. No value here is
a measured plant figure.

## 1. Process requirement scenarios

| ID | Illustrative application | Process / flue-gas exit temperature | Heat duty | Load profile | Gas-quality need |
|---|---|---|---|---|---|
| P1 | Drying, low-temperature process steam | 300 degC | 10 MW | continuous 8760 h | none beyond combustion stability |
| P2 | Metal heat treatment / reheating | 800 degC | 10 MW | two shifts, 5 days/week (16 h x 5) | stable flame, moderate T_ad |
| P3 | Ceramics / brick kiln | 1000 degC (**reference**) | 10 MW | continuous | T_ad well above process T |
| P4 | Very-high-temperature furnace | 1300 degC | 10 MW | continuous | T_ad and Wobbe close to natural gas (burner retrofit-free) |

All entries are *(assumption)*: temperatures and duties for screening, not data from a
specific site. Load profiles are generated synthetically and labelled as such. The gas
quality limits for "retrofit-free" use (Wobbe band, relative density, minimum CH4/maximum
H2) are *(to be sourced)* from public natural-gas quality rules, e.g. the DVGW G 260 gas
families in Germany [scenarios repo].

## 2. Plant configurations (implemented in `biomass-heat-plant-model`)

| Key | Gasifier | O2 supply | Methanation | H2 supply |
|---|---|---|---|---|
| `air` | air-blown, 850 degC | - | none | - |
| `oxy_none` | O2/steam, 850 degC | ASU | none | - |
| `oxy_partial` | O2/steam | electrolyser by-product (+ASU top-up) | partial (50 % of stoichiometric H2) | electrolyser |
| `oxy_full` | O2/steam | electrolyser by-product | full (100 %) | electrolyser |
| `oxy_none_elec` (variant) | O2/steam | electrolyser sized to O2 demand | none, surplus H2 blended | electrolyser |
| `steam_dfb` (variant) | allothermal steam, DFB | - | none | - |

## 3. Operating strategies [dispatch repo]

| ID | Strategy | Description |
|---|---|---|
| O1 | Follow demand | electrolyser runs exactly at the hourly H2/O2 need, no storage |
| O2 | Price threshold | full load below a price threshold, storage covers the rest |
| O3 | Optimised (perfect foresight) | LP minimising electricity cost with storage and capacity limits, as an upper bound |
| O4 | Optimised (rolling, day-ahead) | O3 re-solved daily with only day-ahead prices known |

Price data: real DE-LU day-ahead prices *(to be sourced, Energy-Charts / SMARD, with licence)*.

## 4. Economic scenarios [LCOH repo]

| Parameter | Low | Central | High | Status |
|---|---|---|---|---|
| Discount rate (real) | 5 % | 7 % | 10 % | assumption |
| Lifetime | 20 years | | | assumption |
| EU ETS CO2 price | 50 EUR/t | 76 EUR/t (DEHSt H1 2026) | 200 EUR/t | central cited, range assumption [LCOH repo] |
| Natural gas price (DE, band I4, excl. taxes) | 21.2 (2019-S2) | 44.1 (2026-S1) | 62.8 (2022-S2) EUR/MWh_GCV | Eurostat nrg_pc_203 [LCOH repo] |
| Wood chip price (net) | 24.1 | 30.3 | 41.0 EUR/MWh | Thunman 2019 (escalated) / C.A.R.M.E.N. 2025 DE / north [LCOH repo] |
| Electrolyser / gasifier / methanation CAPEX | | | | Schmidt 2017 / Thunman 2019 / Götz 2016, see LCOH repo docs/cost_basis.md |
| Electricity price | ×0.7 | DE-LU DA 2025-10-30 → 2026-10-30 (mean 110.8) | ×1.3 | Energy-Charts CC BY 4.0 [dispatch + LCOH repos] |

## 5. Outputs per scenario

LCOH (EUR/MWh_heat) per chain and strategy; gap to natural gas plus CO2; break-even CO2
price; biomass and electricity use per MWh_heat; avoided fossil CO2; feasibility flags (T_ad,
Wobbe, available heat at process temperature).
