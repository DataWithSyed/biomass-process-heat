# Scenario definitions

Scenarios combine a **process requirement** (what the industrial user needs) with a
**plant configuration** (which chain supplies it) and an **economic setting**. Values marked
*(assumption)* are illustrative screening values chosen by the author. No value here is
a measured plant figure.

The runnable screen is [`scenarios/`](../scenarios/) in this repository (import name
`bhscenarios`, distribution name `biomass-heat-scenarios`). The roadmap name is not a
separate repository. Results and the fuel-gas screen are in
[`scenarios/results/ranking.md`](../scenarios/results/ranking.md).

## 1. Process requirement scenarios

| ID | Illustrative application | Process / flue-gas exit temperature | Heat duty | Load profile | Gas-quality need |
|---|---|---|---|---|---|
| P1 | Drying, low-temperature process steam | 300 degC | 10 MW | continuous 8760 h | none beyond combustion stability |
| P2 | Metal heat treatment / reheating | 800 degC | 10 MW | two shifts, 5 days/week (16 h x 5) | stable flame, moderate T_ad |
| P3 | Ceramics / brick kiln | 1000 degC (**reference**) | 10 MW | continuous | T_ad well above process T |
| P4 | Very-high-temperature furnace | 1300 degC | 10 MW | continuous | T_ad and Wobbe close to natural gas (burner retrofit-free) |

All entries are *(assumption)*: temperatures and duties for screening, not data from a
specific site. Load profiles are generated synthetically and labelled as such.

The temperature comparison uses **8000 h/y** for every continuous case, the full-load
hours already fixed in the LCOH model. P1 is also run at the **8760 h** written in the
table above, so that calendar-year assumption is not mixed into the temperature comparison.
P2 uses **4160 h** = 16 h × 5 d × 52 wk, with no public holidays. P3 and P4 are the
1000 °C and 1300 °C rows of the 8000 h series.

The fuel-gas screen uses the published EASEE-gas CBP 2005-001/02 gross Wobbe band
(13.60–15.81 kWh/m³, combustion 25 °C, volume 0 °C) and relative density 0.555–0.700.
Hydrogen limits are screening assumptions: the CBP gives none. DVGW G 260 is not applied.
The screen is not a compliance check and not a burner certificate. See
[`scenarios/docs/assumptions.md`](../scenarios/docs/assumptions.md).

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

Price data: DE-LU day-ahead prices, Energy-Charts / SMARD, CC BY 4.0, used in the dispatch and LCOH repositories. The screening step does not re-solve that dispatch.

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

Produced by `scenarios/` (step 5), not by a separate repository.

LCOH (EUR/MWh_heat) per chain; gap to natural gas; break-even CO2 price at the same
flue-exit temperature; biomass and electricity per MWh_heat; direct fossil stack CO2
and biogenic stack CO2, reported separately from lifecycle emissions (lifecycle GHG is
not estimated); thermal feasibility (`T_ad` against process temperature, available heat
against flue-exit temperature) and the Wobbe / density screen. Electrolyser chains on
the two-shift load are marked provisional because the day-ahead dispatch was not
re-solved for that shape.
