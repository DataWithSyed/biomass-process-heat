"""Screening constants.

Cited limits are copied from the named public document. Everything else is an
author screening assumption and is not a measured plant value, a regulatory
limit, or a burner certificate.
"""
from __future__ import annotations

# --- cited: EASEE-gas CBP 2005-001/02 (approved 6 Nov 2008), section 3 and 4 ---
# Gross (superior) Wobbe index. Combustion reference temperature 25 degC.
# Volume reference 0 degC and 1.01325 bar(a). Energy unit kWh.
# The CBP writes the lower end as [13.60] and recommends 13.76 as the
# implementation start because of sparse data below that. The screening band
# uses the stated recommended range 13.60-15.81 kWh/m3, not a legal limit.
EASEE_WOBBE_KWH_MIN = 13.60
EASEE_WOBBE_KWH_MAX = 15.81
KWH_TO_MJ = 3.6  # exact SI
WOBBE_MIN_MJ_NM3 = EASEE_WOBBE_KWH_MIN * KWH_TO_MJ  # 48.96
WOBBE_MAX_MJ_NM3 = EASEE_WOBBE_KWH_MAX * KWH_TO_MJ  # 56.916
# Relative density, same CBP, dimensionless (m3/m3 in the CBP table).
DENSITY_MIN = 0.555
DENSITY_MAX = 0.700

# --- screening assumptions (not in the CBP) -------------------------------------------------------
# S5. The CBP says its Wobbe band is for insignificant hydrogen and gives no
# number. 1 vol-% dry is the cut used here for "not negligible".
H2_NOT_NEGLIGIBLE_VOL = 1.0
# S6. A second flag at 10 vol-% dry. Public appliance discussions use figures
# of this order. It is not applied as a certificate and it is not read out of
# the CBP.
H2_ELEVATED_VOL = 10.0
# S7. T_ad - T_process below this is flagged "tight margin" and still ranked.
# At or below 0 K the case is thermally infeasible (no driving force).
TIGHT_MARGIN_K = 200.0

# S2 / S3. Full-load hours.
# 8000 h is Thunman's value, already the LCOH model's central FLH (L-A3).
CONTINUOUS_FLH_H = 8000.0
# P1 in the umbrella scenario sheet says "continuous 8760 h". That is a
# no-outage calendar year, kept as its own case so it is not mixed into the
# temperature comparison.
P1_CALENDAR_FLH_H = 8760.0
# Two shifts, 16 h x 5 days x 52 weeks. No public holidays. Screening assumption.
TWO_SHIFT_HOURS_PER_DAY = 16
TWO_SHIFT_DAYS_PER_WEEK = 5
TWO_SHIFT_WEEKS = 52
TWO_SHIFT_FLH_H = float(TWO_SHIFT_HOURS_PER_DAY * TWO_SHIFT_DAYS_PER_WEEK * TWO_SHIFT_WEEKS)

HEAT_MW = 10.0
TEMPERATURES_C = (300, 800, 1000, 1300)
REFERENCE_T_C = 1000.0

# Published electrolyser sizing at the reference temperature (LCOH v0.1).
# Not re-optimised here. See reference_dispatch.py.
ELECTROLYSER_CONFIGS = ("oxy_none_elec", "oxy_partial", "oxy_full")
CHAIN_ORDER = (
    "steam_dfb",
    "oxy_none",
    "oxy_none_elec",
    "air",
    "oxy_partial",
    "oxy_full",
)
