# Biomass Process Heat

**Agent-based simulation and economic assessment of biomass-based process chains for
industrial high-temperature process heat.** This independent open-source project looks at
how biogenic syngas from thermochemical biomass gasification can replace natural gas in
industrial furnaces and burners. It covers air gasification, oxyfuel gasification with
partial or full methanation, oxygen and hydrogen supply via electrolysis and H2/O2 storage,
and electricity-price-dependent operation. Each chain is compared with natural gas plus the
EU ETS CO2 price on a **levelised cost of heat (LCOH)** basis.

The project is a **series of public repositories**, built step by step. This umbrella repo
holds the overview, architecture, roadmap, methods notes, scenario definitions and the
final write-up.

## Why

Most industrial heat above ~500 degC still comes from burning natural gas. Electrification
is hard at very high temperatures and in existing furnaces. Gasified biomass is a renewable
gas fuel that can, with the right conditioning, come close to natural gas. The open question
is which process chain gives the cheapest heat for a given process. Air-blown gas is cheap
but N2-diluted. Oxyfuel needs O2. Methanation needs H2. Electrolysis produces both and can
follow electricity prices.

## Architecture

```mermaid
flowchart LR
    subgraph Market
        GM[GridMarket<br/>day-ahead price, CO2 price]
    end
    BF[BiomassFeed] --> GZ[Gasifier<br/>air / oxyfuel / steam DFB]
    GZ --> GC[GasCleaning<br/>cooling, tar/dust, condensate]
    GC --> ME[Methanation<br/>none / partial / full]
    ME --> BU[Burner / furnace]
    BU --> PD[ProcessHeatDemand<br/>T level, load profile]
    GM -- price --> ST{Operating<br/>strategy}
    ST --> EL[Electrolyser]
    EL -- H2 --> H2S[(H2 storage)] -- H2 --> ME
    EL -- O2 --> O2S[(O2 storage)] -- O2 --> GZ
    ASU[Air separation unit] -. O2 top-up .-> GZ
    EL & ASU & ME -- electricity --> GM
    PD -- heat duty --> BF
    BU --> LC[LCOH and comparison<br/>vs natural gas + EU ETS]
    LC --> UI[Streamlit dashboard]
```

The plant model is **agent-based**: every unit is an agent with its own parameters, state
and ledger. A scheduler passes messages between them each time step: heat demand, gas
streams, H2/O2 flows and electricity. Operating strategies are pluggable agents too.

## Roadmap

| # | Repository | Content | Status |
|---|---|---|---|
| 1 | [biomass-process-heat](https://github.com/DataWithSyed/biomass-process-heat) (this repo) | overview, architecture, roadmap, [methods notes](docs/methods.md), [scenarios](docs/scenarios.md), final report | in progress |
| 2 | [biomass-heat-plant-model](https://github.com/DataWithSyed/biomass-heat-plant-model) | modular agent-based plant model, mass and energy balances, gas quality, O2/H2 demand | v0.1 done |
| 3 | [biomass-heat-electrolysis-dispatch](https://github.com/DataWithSyed/biomass-heat-electrolysis-dispatch) | price-dependent electrolysis and H2/O2 storage strategies on real German day-ahead prices | v0.1 done |
| 4 | [biomass-heat-lcoh](https://github.com/DataWithSyed/biomass-heat-lcoh) | LCOH, natural gas + EU ETS comparison, break-even CO2, sensitivity, Monte Carlo, tornado charts | v0.1 done |
| 5 | [biomass-heat-scenarios](https://github.com/DataWithSyed/biomass-heat-scenarios) | process scenarios P1–P4 (300–1300 degC, load profiles), recuperative air preheat, gas-quality feasibility filter, ranking | v0.1 done |
| 6 | [biomass-heat-dashboard](https://github.com/DataWithSyed/biomass-heat-dashboard) | interactive Streamlit UI: process requirement → feasible chains → LCOH / break-even CO2 vs natural gas, precomputed or live recompute | v0.1 done |
| 7 | this repo, `report/` | final write-up of results | planned |

- [x] **1. Umbrella repo**: README, architecture, roadmap, methods/literature notes, scenario definitions (2026-11-05)
- [x] **2. Plant model** [`biomass-heat-plant-model`](https://github.com/DataWithSyed/biomass-heat-plant-model): agents, gasifier (air/oxyfuel/steam), cleaning, methanation (none/partial/full), electrolyser, H2/O2 storage, ASU, burner, market; design-point and hourly simulation; 33 tests (2026-11-05)
- [x] **3. Electrolysis dispatch** [`biomass-heat-electrolysis-dispatch`](https://github.com/DataWithSyed/biomass-heat-electrolysis-dispatch): real DE-LU day-ahead prices (Energy-Charts / SMARD, CC BY 4.0), O1 follow-demand / O2 price-threshold / O3 perfect-foresight LP / O4 rolling day-ahead; at 1.5× electrolyser + 24 h storage O3 cuts electricity cost ~23 % vs O1 (oxy_full 268 → 206 EUR/MWh_heat; O4 recovers 93–98 %); oversizing is the main lever (1× barely helps); 9 tests (2026-11-06)
- [x] **4. LCOH** [`biomass-heat-lcoh`](https://github.com/DataWithSyed/biomass-heat-lcoh): CAPEX/O&M scaled from GoBiGas cost data (Thunman 2019), electrolyser (Schmidt 2017), storage/methanation (Götz 2016), EUR 2025 via HICP; annuity LCOH vs natural gas (Eurostat DE I4) + EUA (DEHSt); break-even CO2/gas price, LCOH-optimal electrolyser sizing, tornado, 10k Monte Carlo, scale sweep; at 10 MW the cheapest chain (DFB) is 268 vs 123 EUR/MWh for gas, break-even CO2 ≈ 450 EUR/t; 19 tests (2026-11-07)
- [x] **5. Scenarios and screening** [`biomass-heat-scenarios`](https://github.com/DataWithSyed/biomass-heat-scenarios): P1–P4 (300/800/1000/1300 degC, continuous or two-shift), with and without recuperative air preheat; rolling day-ahead electrolyser LP for time-varying demand; ASU cost and power now sourced (VTT Technology 91); DVGW G 260 H-gas limits as a gas-quality filter; DFB is cheapest wherever a burner retrofit is allowed, 1000 degC continuous is the best case (453 EUR/t), two-shift operation pushes break-even CO2 above 1,000 EUR/t, only full methanation suits a retrofit-free 1300 degC furnace; 25 tests (2026-11-08)
- [x] **6. Dashboard** [`biomass-heat-dashboard`](https://github.com/DataWithSyed/biomass-heat-dashboard): Streamlit app; pick P1–P4 or any temperature 300–1300 degC, load profile, burner retrofit yes/no, air preheat, cost case and price sliders; feasibility via the step-5 filter, LCOH breakdown and LCOH-vs-CO2 chart; live recompute reproduces the step-5 matrix to 1e-9; new temperature sweep: without a burner retrofit only full methanation is feasible at any temperature (about 2× the LCOH), with a retrofit break-even CO2 falls from 595 (300 degC) to 379 EUR/t (1300 degC); 20 tests incl. Streamlit AppTest (2026-11-09)
- [ ] **7. Final report** in this repo (`report/`)
- [ ] Plant-model enhancements: DFB flue-gas heat recovery, tar/C2+ species, part-load behaviour, flame dissociation (recuperative air preheat is now covered via the burner's air temperature in step 5)

## First results (from the plant model, 10 MW of heat at 1000 degC)

| Chain | Fuel LHV (MJ/Nm3) | Wobbe (MJ/Nm3) | Biomass MWh/MWh_heat | Electricity MWh/MWh_heat | H2 kg/MWh_heat |
|---|---|---|---|---|---|
| Air gasification | 5.5 | 6.4 | 3.49 | 0.02 | 0 |
| Oxyfuel, no methanation | 9.7 | 12.5 | 2.54 | 0.05 | 0 |
| Oxyfuel + partial methanation | 24.1 | 29.0 | 1.66 | 1.90 | 33 |
| Oxyfuel + full methanation | 33.5 | 50.6 | 1.08 | 2.42 | 43 |
| Natural gas (reference) | 36.8 | 52.7 | 1.91 (NG) | - | - |

With full methanation the fuel comes close to natural gas. The electrolyser then produces
4.4 times the O2 the gasifier needs. See the
[plant-model README](https://github.com/DataWithSyed/biomass-heat-plant-model) for the
assumptions and limitations.

## Dispatch results (electrolysis repo, DE-LU day-ahead 2025-10-30 → 2026-10-30)

At **1.5 × electrolyser + 24 h H2/O2 storage**, perfect-foresight LP (O3) cuts electricity
cost by about **23 %** vs follow-demand across the three electrolyser configs; rolling
day-ahead (O4) recovers 93–98 % of that. At 1.0 × capacity the saving is &lt; 1 % — storage
alone is not enough; oversizing is the lever (oxy_full O3: 266 → 179 EUR/MWh_heat from
1× to 2×). Mean DA price 110.8 EUR/MWh; O3 volume-weighted purchase ~85 EUR/MWh_el.

| Config | O1 | O3 | O4 | O3 VWAP |
|---|---|---|---|---|
| oxy_none_elec | 98.4 | 75.4 | 77.0 | 85.0 |
| oxy_partial | 210.1 | 162.3 | 165.8 | 85.7 |
| oxy_full | 268.1 | 206.1 | 210.5 | 85.3 |

All figures EUR/MWh_heat except VWAP (EUR/MWh_el). Details in the
[dispatch README](https://github.com/DataWithSyed/biomass-heat-electrolysis-dispatch).


## LCOH results (LCOH repo, 10 MW / 1000 degC, EUR 2025)

Natural gas in the same furnace costs **122.7 EUR/MWh_heat** (Eurostat DE I4 2026-S1
44.1 EUR/MWh_GCV excl. taxes, plus EUA 76 EUR/t). CAPEX is scaled from GoBiGas cost data, which
makes it a conservative, first-of-a-kind basis. The electrolyser chains are sized at their
LCOH-optimal point on rolling day-ahead dispatch (2.5×, 24 h).

| Chain | LCOH EUR/MWh_heat | Break-even CO2 EUR/t | Integrated site* |
|---|---|---|---|
| Steam gasification (DFB) | **268** | **453** | 207 / 295 EUR/t |
| Oxyfuel, O2 from ASU | 282 | 490 | 221 / 332 |
| Oxyfuel, electrolyser O2, H2 blended | 329 | 610 | 275 / 470 |
| Air gasification | 330 | 612 | 261 / 436 |
| Oxyfuel + partial methanation | 555 | 1197 | 463 / 958 |
| Oxyfuel + full methanation | 575 | 1249 | 491 / 1029 |

\*Auxiliary/project costs and staff halved (assumption). At 10 MW no chain beats gas in any
of 10,000 Monte Carlo draws (CO2 50–200 EUR/t). Electrolytic H2 for methanation roughly
doubles the cost at 2025-26 German power prices. Scale is the main lever: at 100 MW of heat
DFB reaches 144 EUR/MWh (break-even 131 EUR/t), or 129 EUR/MWh (93 EUR/t) on an integrated
site. Details in the [LCOH README](https://github.com/DataWithSyed/biomass-heat-lcoh).

## Scenario results (scenarios repo, 10 MW, EUR 2025 per MWh heat)

Best feasible chain per process scenario, central cost case (natural gas at the same furnace
temperature with the same air preheat; CO2 76 EUR/t):

| Scenario | Best feasible chain | LCOH no preheat / recuperated | Natural gas | Break-even CO2 EUR/t |
|---|---|---|---|---|
| P1 300 degC, continuous | steam DFB | 193 / 186 | 73 / 68 | 595 / 625 |
| P2 800 degC, two shifts | steam DFB | 427 / 378 | 102 / 79 | 1,089 / 1,279 |
| P3 1000 degC, continuous | steam DFB | 268 / 219 | 123 / 85 | 453 / 578 |
| P4 1300 degC, retrofit-free | oxy + full methanation (only one) | 777 / 501 | 180 / 102 | 1,134 / 1,317 |

Recuperation lowers every chain's cost but helps gas more in relative terms. Utilisation
matters more than temperature. The sourced ASU cost (15 MEUR for 1.84 t/h) is about 3× the
step-4 placeholder and raises the ASU oxyfuel chain from 282 to 297 EUR/MWh. Details in the
[scenarios README](https://github.com/DataWithSyed/biomass-heat-scenarios).

## Dashboard (step 6)

The [dashboard](https://github.com/DataWithSyed/biomass-heat-dashboard) puts steps 2–5 behind
one screen. The user states a process requirement and gets the feasible chains, their LCOH
breakdown and the CO2 price at which each one would beat gas. A temperature sweep (continuous
duty, central costs) adds two findings:

| Process T | Best chain, retrofit allowed | LCOH / gas | Break-even CO2 | Retrofit-free (only oxy + full methanation) | Break-even CO2 |
|---:|---|---:|---:|---:|---:|
| 300 degC | steam DFB | 193 / 73 | 595 | 391 | 1,457 |
| 800 degC | steam DFB | 237 / 102 | 498 | 500 | 1,316 |
| 1000 degC | steam DFB | 268 / 123 | 453 | 575 | 1,249 |
| 1300 degC | steam DFB | 351 / 180 | 379 | 777 | 1,134 |

* Whether the burner may be changed matters more than any price input. Without a retrofit, the
  cheapest LCOH roughly doubles at every temperature.
* With a retrofit, break-even CO2 falls steadily with process temperature (cold air). With
  recuperative preheat the fall is much flatter (625 → 539 EUR/t).

## Repository layout

```
docs/methods.md      literature and methods overview (verifiable references only)
docs/scenarios.md    technical and economic scenario definitions
report/              final write-up (step 7)
```

## Licence

MIT, see [LICENSE](LICENSE). Text and figures may be reused with attribution.
