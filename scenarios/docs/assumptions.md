# Screening assumptions

Numerical limits are either copied from a public document or marked as a screening
assumption. Nothing here is a measured plant result, a regulatory determination,
or a burner certificate.

Plant-model assumptions A1–A23 and LCOH assumptions L-A1–L-A18 still apply.
This file only adds the choices made for the screen.

## Cited

| Item | Value | Source |
|---|---|---|
| Gross Wobbe band | 13.60–15.81 kWh/m³ | EASEE-gas CBP 2005-001/02, section 4. Combustion reference 25 °C, volume at 0 °C and 1.01325 bar (section 3). The lower end is written `[13.60]`; the CBP recommends starting implementation at 13.76 because data below that were sparse. This screen uses the stated 13.60–15.81 range as a filter, not as a legal limit. |
| Same band in MJ/m³ | 48.96–56.916 | 1 kWh = 3.6 MJ |
| Relative density | 0.555–0.700 | Same CBP |
| Continuous full-load hours used for the temperature comparison | 8000 h/y | Thunman et al. 2019, already L-A3 in the LCOH model |
| Cost basis | central `CostInputs` | biomass-heat-lcoh: Eurostat gas, DEHSt EUA, C.A.R.M.E.N. wood chips, GoBiGas / Schmidt / Götz CAPEX. Assumption-based where that repo says so |
| Electrolyser dispatch anchor | O4, 2.5×, 24 h, 10 MW, 1000 °C | Public `sizing_grid_O4.csv` at commit `b4d6853`. Not re-solved here |

The plant-model upper Wobbe index is HHV at 25 °C over an ideal-gas normal cubic metre (0 °C, 1.01325 bar). That matches the CBP reference temperatures. It is not an ISO 6976 real-gas calculation. A sub-percent difference is possible and is not treated as compliance margin.

The CBP says the band was drawn for insignificant hydrogen and that hydrogen can cause flashback. It gives no numeric hydrogen limit. DVGW G 260 is the German grid-gas worksheet. Its tables are not reproduced here, and this screen is not a G 260 check.

## Screening assumptions

| ID | Choice | Why it is not a cited limit |
|---|---|---|
| S1 | Ranked rows set flue-gas exit temperature equal to process temperature | Plant-model A20 (no recuperation). The code keeps the two temperatures as separate fields. A cooler flue without air preheat is not ranked, because that would be a recuperator the plant model does not close. |
| S2 | Temperature comparison uses 8000 h, not 8760 h | So the comparison sits on the same full-load hours as the LCOH step. |
| S3 | P1 is also reported at 8760 h | That is the calendar year written in the umbrella scenario sheet. It assumes no outage. |
| S4 | Two-shift year = 16 h × 5 d × 52 wk = 4160 h | Synthetic. No public holidays, no measured load. |
| S5 | Hydrogen above 1 vol-% dry is "not negligible" | The CBP gives no number. Only `band_low_h2` (inside the band and at or below 1 vol-%) passes the interchangeability screen. |
| S6 | Hydrogen above 10 vol-% dry is a second flag | A round screening cut of the same order as figures discussed for appliances. Not a certificate, and not applied to industrial furnaces as a rule. |
| S7 | Margin `T_ad − T_process` below 200 K is "tight" and still ranked. Margin at or below 0 K is infeasible | Below 0 K there is no driving force. 200 K is a round warning, not a heat-transfer design. |
| S8 | Electrolyser EUR/MWh at other temperatures scales the published 1000 °C O4 cost by the plant-model throughput ratio | Valid for a continuous flat duty if capacity stays 2.5× design and storage stays 24 h of design demand. The optimum is not re-searched. Invalid for the two-shift shape; those rows are marked provisional. |
| S9 | No burner-retrofit CAPEX | Same gap as LCOH L-A14. |
| S10 | Direct fossil CO2 of a biomass chain is 0. Biogenic stack CO2 is the carbon in the fuel gas. Lifecycle GHG is not estimated | EU ETS zero-rating of biogenic CO2 is an accounting choice already in L-A15. It is not a lifecycle result. Grid electricity and biomass supply-chain emissions are omitted. |
| S11 | 10 MW heat duty | The duty in the umbrella scenario sheet. |
| S12 | Ideal-gas Wobbe compared with the CBP band | See above. |

## Temperatures

300, 800, 1000 and 1300 °C are the screening temperatures in the umbrella scenario sheet. They are illustrative process temperatures, not measurements from a site. Naegler et al. (2015) and Madeddu et al. (2020) are the background for splitting industrial heat by temperature level. Those papers are not the source of these four round numbers.

## What "feasible" means here

A chain is thermally feasible when the adiabatic flame temperature is above the process temperature and the flue exit is below the adiabatic flame temperature, so available heat is positive. Fuel class is separate. A chain outside the Wobbe band can still be ranked on cost. The rank is a cost order of thermally feasible options. It is not a permit and not a burner approval.
