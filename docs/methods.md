# Methods and literature overview

This note gives the method choices and the literature behind them. It only lists
references with a resolvable DOI or a well-known textbook. Where a claim is my own modelling
choice, it says so. Short summaries describe what each source is used for here. They are
not abstracts.

## 1. Industrial high-temperature process heat

Industrial heat demand is commonly broken down by branch and temperature level. A large
share of it is above 400-500 degC, in steel, non-metallic minerals (cement, lime, glass,
ceramics) and chemicals, and is mostly supplied by fossil fuels. Naegler et al. (2015)
quantify the European industrial heat demand by branch and temperature level. Madeddu et al.
(2020) estimate how much of it could be electrified directly, which frames the part where
a renewable *gas* is the more practical route.

*Used for:* choice of process-temperature levels in the scenarios (docs/scenarios.md).

## 2. Biomass gasification technologies

* **Air-blown** (fixed or fluidised bed): simplest and cheapest. The product gas is diluted by
  ~45-55 vol-% N2, giving a low heating value (roughly 4-7 MJ/Nm3).
* **Oxygen/steam ("oxyfuel")**: no N2 dilution, medium heating value, needs an O2 source
  (air separation unit or electrolysis).
* **Allothermal steam (dual fluidised bed, DFB)**: char is burnt in a separate combustor that
  heats the bed material. This gives an N2-free, H2-rich gas without pure O2. The GoBiGas
  plant in Gothenburg is the best-documented commercial-scale bio-SNG example (Thunman et
  al. 2019).

Overviews: Molino et al. (2016); Basu (2018); Higman & van der Burgt (2008).

## 3. Gasification modelling

Puig-Arnavat et al. (2010) review the model families: thermodynamic equilibrium
(stoichiometric or Gibbs minimisation), kinetic, CFD and artificial neural networks.
Equilibrium models are transparent and need few parameters. They over-predict H2 and
under-predict CH4, tar and char, so they are usually corrected, for example with
restricted equilibrium or fixed CH4/char yields. Zainal et al. (2001) is a widely used
stoichiometric equilibrium formulation based on water-gas shift and methane formation.

*Choice here:* quasi-equilibrium gasifier with elemental balances, water-gas shift at the
outlet temperature, a fixed (calibrated) CH4 yield, carbon conversion < 1, and the oxidant
flow solved from the energy balance (biomass formation enthalpy from the HHV). Biomass HHV
comes from the unified correlation of Channiwala & Parikh (2002).

## 4. Gas cleaning and conditioning

Tar, particulates, alkali, sulphur and nitrogen species have to be removed before
methanation catalysts and most burners. Woolcock & Brown (2013) review hot and cold
cleaning technologies. *Choice here:* cleaning is treated as complete, with an energy
penalty (cooling, condensation, pressure drop and blower).

## 5. Methanation (bio-SNG)

Catalytic methanation (CO + 3H2 -> CH4 + H2O, CO2 + 4H2 -> CH4 + 2H2O) is strongly
exothermic and limited by equilibrium at high temperature, so it uses staged fixed-bed
reactors with intercooling or fluidised beds. Kopyscinski et al. (2010) review SNG from
coal and dry biomass from 1950 to 2009. Rönsch et al. (2016) review methanation from
fundamentals to current projects.

*Choice here:* external H2 is added to reach a share of the stoichiometric module
M = (H2 - CO2)/(CO + CO2) = 3 (partial 50 %, full 100 %), followed by chemical equilibrium of
CO methanation and water-gas shift at the last stage's conditions.

## 6. Electrolysis, power-to-gas and storage

Water electrolysis (alkaline, PEM, solid oxide) produces H2 and stoichiometric O2
(~7.9 kg O2 per kg H2). Buttler & Spliethoff (2018) review efficiency, flexibility and
part-load. Schmidt et al. (2017) give expert-elicited future cost and performance. Götz
et al. (2016) review power-to-gas chains including methanation. Two points matter for this
project. First, electrolysis O2 can replace an air separation unit for oxyfuel
gasification. Second, flexible electrolysers with H2/O2 storage can shift electricity
demand to low-price hours. The dispatch repo will quantify that trade-off.

## 7. Agent-based modelling of energy systems

Agent-based modelling represents a system as autonomous agents with their own state and
rules that interact through messages (Macal & North 2010). In Python, Mesa is the
reference framework (Masad & Kazil 2015; Kazil et al. 2020). Ringkjøb et al. (2018) review
energy-system modelling tools more broadly.

*Choice here:* a lightweight agent framework without a Mesa dependency. Process units, the
market and the operating strategy are agents. A plant scheduler steps them in a fixed order
each hour and passes stream and price messages. This keeps the model easy to install as a
dependency of later repos and transparent to test.

## 8. Economic assessment

The levelised cost of heat follows the standard levelised-cost approach of discounted
lifetime costs over discounted lifetime useful energy (Short et al. 1995):

LCOH = (sum_t (CAPEX_t + OPEX_t + fuel_t + electricity_t + CO2_t - revenues_t) / (1+r)^t) /
       (sum_t Q_heat,t / (1+r)^t)

The comparison case is natural gas in the same burner, including EU ETS allowance costs on
fossil CO2. Biogenic CO2 is treated as zero-rated, with a sensitivity case. Sensitivity
analysis will use one-at-a-time (tornado) and Monte Carlo sampling. All cost inputs will be
cited in `biomass-heat-lcoh`.

## 9. Data sources (planned)

* German/Luxembourg day-ahead prices: Energy-Charts (Fraunhofer ISE) API and SMARD
  (Bundesnetzagentur). Licence terms will be checked and cited in the dispatch repo.
* EU ETS allowance prices: public sources to be identified and cited in the LCOH repo.
* Thermodynamic data: GRI-Mech 3.0 NASA polynomials (via Cantera's `gri30.yaml`).

## References

* Basu, P. (2018). *Biomass Gasification, Pyrolysis and Torrefaction: Practical Design and Theory*, 3rd ed. Academic Press.
* Buttler, A., Spliethoff, H. (2018). Current status of water electrolysis for energy storage, grid balancing and sector coupling via power-to-gas and power-to-liquids: A review. *Renewable and Sustainable Energy Reviews* 82, 2440-2454. https://doi.org/10.1016/j.rser.2017.09.003
* Channiwala, S.A., Parikh, P.P. (2002). A unified correlation for estimating HHV of solid, liquid and gaseous fuels. *Fuel* 81(8), 1051-1063. https://doi.org/10.1016/S0016-2361(01)00131-4
* Götz, M., Lefebvre, J., Mörs, F., et al. (2016). Renewable Power-to-Gas: A technological and economic review. *Renewable Energy* 85, 1371-1390. https://doi.org/10.1016/j.renene.2015.07.066
* Higman, C., van der Burgt, M. (2008). *Gasification*, 2nd ed. Gulf Professional Publishing.
* Kazil, J., Masad, D., Crooks, A. (2020). Utilizing Python for Agent-Based Modeling: The Mesa Framework. In *Social, Cultural, and Behavioral Modeling* (SBP-BRiMS 2020), LNCS, 308-317. https://doi.org/10.1007/978-3-030-61255-9_30
* Kopyscinski, J., Schildhauer, T.J., Biollaz, S.M.A. (2010). Production of synthetic natural gas (SNG) from coal and dry biomass - A technology review from 1950 to 2009. *Fuel* 89(8), 1763-1783. https://doi.org/10.1016/j.fuel.2010.01.027
* Macal, C.M., North, M.J. (2010). Tutorial on agent-based modelling and simulation. *Journal of Simulation* 4(3), 151-162. https://doi.org/10.1057/jos.2010.3
* Madeddu, S., Ueckerdt, F., Pehl, M., et al. (2020). The CO2 reduction potential for the European industry via direct electrification of heat supply (power-to-heat). *Environmental Research Letters* 15(12), 124004. https://doi.org/10.1088/1748-9326/abbd02
* Masad, D., Kazil, J. (2015). Mesa: An Agent-Based Modeling Framework. *Proceedings of the 14th Python in Science Conference*, 51-58. https://doi.org/10.25080/Majora-7b98e3ed-009
* Molino, A., Chianese, S., Musmarra, D. (2016). Biomass gasification technology: The state of the art overview. *Journal of Energy Chemistry* 25(1), 10-25. https://doi.org/10.1016/j.jechem.2015.11.005
* Naegler, T., Simon, S., Klein, M., Gils, H.C. (2015). Quantification of the European industrial heat demand by branch and temperature level. *International Journal of Energy Research* 39(15), 2019-2030. https://doi.org/10.1002/er.3436
* Puig-Arnavat, M., Bruno, J.C., Coronas, A. (2010). Review and analysis of biomass gasification models. *Renewable and Sustainable Energy Reviews* 14(9), 2841-2851. https://doi.org/10.1016/j.rser.2010.07.030
* Ringkjøb, H.-K., Haugan, P.M., Solbrekke, I.M. (2018). A review of modelling tools for energy and electricity systems with large shares of variable renewables. *Renewable and Sustainable Energy Reviews* 96, 440-459. https://doi.org/10.1016/j.rser.2018.08.002
* Rönsch, S., Schneider, J., Matthischke, S., et al. (2016). Review on methanation - From fundamentals to current projects. *Fuel* 166, 276-296. https://doi.org/10.1016/j.fuel.2015.10.111
* Schmidt, O., Gambhir, A., Staffell, I., et al. (2017). Future cost and performance of water electrolysis: An expert elicitation study. *International Journal of Hydrogen Energy* 42(52), 30470-30492. https://doi.org/10.1016/j.ijhydene.2017.10.045
* Short, W., Packey, D.J., Holt, T. (1995). *A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies*. NREL/TP-462-5173. https://doi.org/10.2172/35391
* Thunman, H., Gustavsson, C., Larsson, A., et al. (2019). Economic assessment of advanced biofuel production via gasification using cost data from the GoBiGas plant. *Energy Science & Engineering* 7(1), 217-229. https://doi.org/10.1002/ese3.271
* Woolcock, P.J., Brown, R.C. (2013). A review of cleaning technologies for biomass-derived syngas. *Biomass and Bioenergy* 52, 54-84. https://doi.org/10.1016/j.biombioe.2013.02.036
* Zainal, Z.A., Ali, R., Lean, C.H., Seetharamu, K.N. (2001). Prediction of performance of a downdraft gasifier using equilibrium modeling for different biomass materials. *Energy Conversion and Management* 42(12), 1499-1515. https://doi.org/10.1016/S0196-8904(00)00078-9
