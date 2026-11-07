# Scenario screening results

Costs are model estimates on the LCOH central cost basis (EUR 2025).
They are not measured heat prices and not a quote. No chain is certified
for a burner, and no figure here is a lifecycle greenhouse-gas result.

Flue-gas exit temperature equals the process temperature in every ranked
row (plant-model assumption of no recuperation). The two temperatures are
different inputs. Available heat uses the flue exit. Thermal feasibility
uses the adiabatic flame temperature against the process temperature.

## Reproduction of the 1000 °C / 8000 h LCOH

Pinned to biomass-heat-lcoh commit `b4d68537751ef8ca6cb618679497e1c71a44d13e`.

| Chain | This screening | Published LCOH | Difference |
|---|---:|---:|---:|
| `steam_dfb` | 268.24 | 268.24 | 0.000 |
| `oxy_none` | 282.32 | 282.32 | 0.000 |
| `oxy_none_elec` | 328.78 | 328.78 | 0.000 |
| `air` | 329.79 | 329.79 | 0.000 |
| `oxy_partial` | 555.36 | 555.36 | 0.000 |
| `oxy_full` | 575.32 | 575.32 | 0.000 |
| `natural_gas` | 122.74 | 122.74 | 0.000 |

## Named scenarios

P1 is 300 °C at 8760 h. P2 is 800 °C on the two-shift profile (4160 h).
P3 and P4 are 1000 °C and 1300 °C at 8000 h. Electrolyser rows on P2 are
provisional: the O4 schedule was not re-solved for a two-shift shape.
Steam DFB, oxyfuel-ASU and air gasification do not use that schedule.

### P1 — 300 °C, continuous_8760, 8760 h

Natural gas in the same furnace: **73.2 EUR/MWh** (fuel 55.7 + direct fossil CO2 17.5).

| Rank | Chain | LCOH | Gap to gas | Break-even CO2 | Fuel screen | Margin K | Rank basis |
|---:|---|---:|---:|---:|---|---:|---|
| 1 | Steam gasification (DFB) | 180.4 | 107.2 | 541 | `outside_published_band` | 1565 | `full` |
| 2 | Oxyfuel, O2 from ASU | 184.6 | 111.4 | 560 | `outside_published_band` | 1507 | `full` |
| 3 | Air gasification | 188.3 | 115.1 | 576 | `outside_published_band` | 1230 | `full` |
| 4 | Oxyfuel, O2 from electrolyser, H2 blended | 212.0 | 138.8 | 679 | `outside_published_band` | 1582 | `full` |
| 5 | Oxyfuel + partial methanation | 348.6 | 275.4 | 1272 | `outside_published_band` | 1522 | `full` |
| 6 | Oxyfuel + full methanation | 368.0 | 294.8 | 1356 | `outside_published_band` | 1616 | `full` |

### P2 — 800 °C, two_shift, 4160 h

Natural gas in the same furnace: **102.0 EUR/MWh** (fuel 77.6 + direct fossil CO2 24.4).

| Rank | Chain | LCOH | Gap to gas | Break-even CO2 | Fuel screen | Margin K | Rank basis |
|---:|---|---:|---:|---:|---|---:|---|
| 1 | Steam gasification (DFB) | 390.9 | 288.9 | 977 | `outside_published_band` | 1065 | `full` |
| 2 | Oxyfuel, O2 from ASU | 405.8 | 303.8 | 1024 | `outside_published_band` | 1007 | `full` |
| 3 | Air gasification | 438.4 | 336.5 | 1125 | `outside_published_band` | 730 | `full` |
| 4 | Oxyfuel, O2 from electrolyser, H2 blended | 458.2 | 356.2 | 1187 | `outside_published_band` | 1082 | `provisional_dispatch` |
| 5 | Oxyfuel + partial methanation | 774.3 | 672.3 | 2173 | `outside_published_band` | 1022 | `provisional_dispatch` |
| 6 | Oxyfuel + full methanation | 801.4 | 699.4 | 2257 | `outside_published_band` | 1116 | `provisional_dispatch` |

### P3 — 1000 °C, continuous, 8000 h

Natural gas in the same furnace: **122.7 EUR/MWh** (fuel 93.4 + direct fossil CO2 29.3).

| Rank | Chain | LCOH | Gap to gas | Break-even CO2 | Fuel screen | Margin K | Rank basis |
|---:|---|---:|---:|---:|---|---:|---|
| 1 | Steam gasification (DFB) | 268.2 | 145.5 | 453 | `outside_published_band` | 865 | `full` |
| 2 | Oxyfuel, O2 from ASU | 282.3 | 159.6 | 489 | `outside_published_band` | 807 | `full` |
| 3 | Oxyfuel, O2 from electrolyser, H2 blended | 328.8 | 206.0 | 610 | `outside_published_band` | 882 | `full` |
| 4 | Air gasification | 329.8 | 207.0 | 612 | `outside_published_band` | 530 | `full` |
| 5 | Oxyfuel + partial methanation | 555.4 | 432.6 | 1197 | `outside_published_band` | 822 | `full` |
| 6 | Oxyfuel + full methanation | 575.3 | 452.6 | 1249 | `outside_published_band` | 916 | `full` |

### P4 — 1300 °C, continuous, 8000 h

Natural gas in the same furnace: **179.6 EUR/MWh** (fuel 136.7 + direct fossil CO2 42.9).

| Rank | Chain | LCOH | Gap to gas | Break-even CO2 | Fuel screen | Margin K | Rank basis |
|---:|---|---:|---:|---:|---|---:|---|
| 1 | Steam gasification (DFB) | 350.8 | 171.2 | 379 | `outside_published_band` | 565 | `full` |
| 2 | Oxyfuel, O2 from ASU | 382.0 | 202.4 | 434 | `outside_published_band` | 507 | `full` |
| 3 | Oxyfuel, O2 from electrolyser, H2 blended | 444.5 | 264.9 | 545 | `outside_published_band` | 582 | `full` |
| 4 | Air gasification | 583.9 | 404.3 | 792 | `outside_published_band` | 230 | `full` |
| 5 | Oxyfuel + partial methanation | 775.3 | 595.7 | 1131 | `outside_published_band` | 522 | `full` |
| 6 | Oxyfuel + full methanation | 777.1 | 597.4 | 1134 | `outside_published_band` | 616 | `full` |

## Temperature comparison at 8000 h

Same full-load hours as the LCOH step, so the change is the flue-exit
balance (and the natural-gas balance at that same flue exit), not the load.
`rescaled` multiplies the 1000 °C LCOH by the biomass-intensity ratio.
It is shown because that shortcut does not reproduce the recomputed cost:
CAPEX meets a scale exponent below 1, and the natural-gas reference moves too.

| Chain | 300 °C | 800 °C | 1000 °C | 1300 °C | 1300 rescaled from 1000 | 1300 recomputed |
|---|---:|---:|---:|---:|---:|---:|
| Steam gasification (DFB) | 192.7 | 237.3 | 268.2 | 350.8 | 404.3 | 350.8 |
| Oxyfuel, O2 from ASU | 197.3 | 246.8 | 282.3 | 382.0 | 442.5 | 382.0 |
| Oxyfuel, O2 from electrolyser, H2 blended | 225.4 | 286.0 | 328.8 | 444.5 | 490.4 | 444.5 |
| Air gasification | 201.0 | 270.0 | 329.8 | 583.9 | 747.2 | 583.9 |
| Oxyfuel + partial methanation | 371.3 | 477.8 | 555.4 | 775.3 | 861.4 | 775.3 |
| Oxyfuel + full methanation | 391.2 | 499.5 | 575.3 | 777.1 | 843.1 | 777.1 |
| Natural gas | 73.2 | 102.0 | 122.7 | 179.6 |  |  |

## Direct stack CO2 at 8000 h, t per MWh of heat

Biomass rows: biogenic carbon in the fuel gas. Natural gas: fossil carbon
in the fuel gas. Neither column is a lifecycle emission. Electricity-grid
emissions and biomass supply-chain emissions are not estimated.

| Chain | 300 °C biogenic or fossil | 1000 °C | 1300 °C |
|---|---:|---:|---:|
| Steam gasification (DFB) (biogenic) | 0.366 | 0.627 | 0.945 |
| Oxyfuel, O2 from ASU (biogenic) | 0.501 | 0.888 | 1.391 |
| Oxyfuel, O2 from electrolyser, H2 blended (biogenic) | 0.361 | 0.614 | 0.915 |
| Air gasification (biogenic) | 0.544 | 1.194 | 2.705 |
| Oxyfuel + partial methanation (biogenic) | 0.330 | 0.580 | 0.899 |
| Oxyfuel + full methanation (biogenic) | 0.224 | 0.377 | 0.552 |
| Natural gas (illustrative composition) (fossil) | 0.230 | 0.386 | 0.565 |

## Fuel screen (independent of temperature)

Upper Wobbe index and relative density are compared with EASEE-gas CBP
2005-001/02 (13.60–15.81 kWh/m³ at 25 °C combustion / 0 °C volume,
relative density 0.555–0.700). The plant-model Wobbe uses the same
reference temperatures on an ideal-gas basis, not a real-gas ISO 6976 value.
Passing the band is not a burner certificate. The CBP itself limits the band
to insignificant hydrogen and gives no hydrogen number; the 1 vol-% and
10 vol-% flags are screening assumptions.

| Chain | LHV MJ/Nm³ | Wobbe MJ/Nm³ | rel. density | H2 vol-% dry | Class | Band misses | T_ad °C |
|---|---:|---:|---:|---:|---|---|---:|
| Steam gasification (DFB) | 10.79 | 15.69 | 0.595 | 51.00 | `outside_published_band` | `wobbe_below_band` | 1865 |
| Oxyfuel, O2 from ASU | 9.72 | 12.47 | 0.743 | 39.65 | `outside_published_band` | `wobbe_below_band|density_above_band` | 1807 |
| Oxyfuel, O2 from electrolyser, H2 blended | 10.00 | 14.90 | 0.571 | 55.07 | `outside_published_band` | `wobbe_below_band` | 1882 |
| Air gasification | 5.53 | 6.43 | 0.869 | 17.64 | `outside_published_band` | `wobbe_below_band|density_above_band` | 1530 |
| Oxyfuel + partial methanation | 24.06 | 29.05 | 0.846 | 2.02 | `outside_published_band` | `wobbe_below_band|density_above_band` | 1822 |
| Oxyfuel + full methanation | 33.49 | 50.65 | 0.540 | 6.51 | `outside_published_band` | `density_below_band` | 1916 |
| Natural gas (illustrative composition) | 36.76 | 52.72 | 0.597 | 0.00 | `band_low_h2` | `—` | 1919 |

Full methanation is the near miss: Wobbe 50.65 MJ/Nm³ is inside the cited band, and relative density 0.540 is below the 0.555 floor. Dry hydrogen is 6.51 vol-%, above the 1 vol-% screening cut, so a density pass would still not be `band_low_h2`.

Interchangeability screen (`band_low_h2` only): no biomass chain passes.
Inside the published Wobbe and density window, including hydrogen flags: none.
Chains outside that window would need a purpose-designed burner. This screen does not design or certify one.

