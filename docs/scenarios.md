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
| EU ETS CO2 price | 50 EUR/t | 100 EUR/t | 200 EUR/t | assumption range; historical series to be sourced |
| Natural gas price (wholesale) | | | | to be sourced |
| Wood chip price | | | | to be sourced |
| Electrolyser / gasifier / methanation CAPEX | | | | to be sourced from published cost studies |
| Electricity price | historical day-ahead years | | | to be sourced |

## 5. Outputs per scenario

LCOH (EUR/MWh_heat) per chain and strategy; gap to natural gas plus CO2; break-even CO2
price; biomass and electricity use per MWh_heat; avoided fossil CO2; feasibility flags (T_ad,
Wobbe, available heat at process temperature).
