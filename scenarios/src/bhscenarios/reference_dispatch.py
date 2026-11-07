"""Pinned 1000 degC dispatch snapshot from the public LCOH study.

Source: https://github.com/DataWithSyed/biomass-heat-lcoh
commit b4d68537751ef8ca6cb618679497e1c71a44d13e

* ``PUBLISHED_O4`` rows are the LCOH-optimal points in ``results/sizing_grid_O4.csv``
  (strategy ``O4_rolling_day_ahead``, capacity factor 2.5, storage 24 h).
* ``PUBLISHED_MEAN_DA_EUR_MWH`` is ``mean_da_price_eur_mwh`` in ``results/run_meta.json``.
* ``PUBLISHED_LCOH_EUR_MWH`` is the central-scenario total in ``results/lcoh_results.csv``.

These figures are outputs of that study at 10 MW and 1000 degC with a continuous
duty. They are not re-measured here. This package does not re-solve the
day-ahead LP. See economics.py for how they are scaled, and for where that
scaling stops being valid.
"""
from __future__ import annotations

PUBLISHED_COMMIT = "b4d68537751ef8ca6cb618679497e1c71a44d13e"
PUBLISHED_MEAN_DA_EUR_MWH = 110.82610775025681

PUBLISHED_O4 = {
    "oxy_partial": {
        "strategy": "O4_rolling_day_ahead",
        "capacity_factor": 2.5,
        "storage_h": 24.0,
        "electrolyser_mw": 45.708473754446466,
        "h2_storage_kg": 7977.731434815026,
        "o2_storage_kg": 28860.873290936517,
        "electricity_eur_per_mwh_heat": 127.98090867097366,
        "electricity_mwh_per_mwh_heat": 1.8943893428797247,
        "electrolyser_flh_frac": 0.39968040178061875,
        "o2_vent_kg_per_mwh_heat": 143.27737053527807,
    },
    "oxy_full": {
        "strategy": "O4_rolling_day_ahead",
        "capacity_factor": 2.5,
        "storage_h": 24.0,
        "electrolyser_mw": 59.38357800822959,
        "h2_storage_kg": 10364.516643742842,
        "o2_storage_kg": 18747.74828038571,
        "electricity_eur_per_mwh_heat": 161.41011736996867,
        "electricity_mwh_per_mwh_heat": 2.417299881757927,
        "electrolyser_flh_frac": 0.3996804017806187,
        "o2_vent_kg_per_mwh_heat": 264.28559598277076,
    },
    "oxy_none_elec": {
        "strategy": "O4_rolling_day_ahead",
        "capacity_factor": 2.5,
        "storage_h": 24.0,
        "electrolyser_mw": 22.05617932389717,
        "h2_storage_kg": 3849.5766905158284,
        "o2_storage_kg": 30552.10502190744,
        "electricity_eur_per_mwh_heat": 58.80602480714786,
        "electricity_mwh_per_mwh_heat": 0.8875016143892489,
        "electrolyser_flh_frac": 0.3996804017806186,
        "o2_vent_kg_per_mwh_heat": 0.07265177353685703,
    },
}

# Central case, EUR/MWh of process heat, 10 MW / 1000 degC / 8000 h.
PUBLISHED_LCOH_EUR_MWH = {
    "steam_dfb": 268.2436919597052,
    "oxy_none": 282.324244715427,
    "oxy_none_elec": 328.77680405544896,
    "air": 329.7940871788776,
    "oxy_partial": 555.3566365695083,
    "oxy_full": 575.3207939063768,
    "natural_gas": 122.74438178668782,
}
