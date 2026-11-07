"""Figures for the screening. Flue-exit temperature and process temperature are labelled separately."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .assumptions import CHAIN_ORDER
from .technical import available_heat_curve

COLORS = {
    "steam_dfb": "#2E7D32",
    "oxy_none": "#EF6C00",
    "oxy_none_elec": "#6A1B9A",
    "air": "#1565C0",
    "oxy_partial": "#C62828",
    "oxy_full": "#00838F",
    "natural_gas": "#212121",
}
SHORT = {
    "steam_dfb": "Steam DFB",
    "oxy_none": "Oxyfuel, ASU",
    "oxy_none_elec": "Oxyfuel, electrolyser O2",
    "air": "Air gasification",
    "oxy_partial": "Partial methanation",
    "oxy_full": "Full methanation",
    "natural_gas": "Natural gas",
}


def plot_screening(df: pd.DataFrame, path: Path) -> Path:
    """Two panels: recomputed LCOH against process temperature, and available heat against flue exit."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8), constrained_layout=True)

    ax = axes[0]
    sub = df[(df["load_id"] == "continuous")].copy()
    for config in CHAIN_ORDER:
        g = sub[sub["config"] == config].sort_values("t_process_c")
        ax.plot(g["t_process_c"], g["lcoh"], marker="o", color=COLORS[config], label=SHORT[config])
    ng = sub[sub["config"] == "natural_gas"].sort_values("t_process_c")
    ax.plot(ng["t_process_c"], ng["lcoh"], marker="s", color=COLORS["natural_gas"],
            linestyle="--", label=SHORT["natural_gas"])
    ax.set_xlabel("Process temperature (°C)")
    ax.set_ylabel("LCOH (EUR/MWh heat)")
    ax.set_title("Recomputed at each temperature\n8000 h, flue exit = process temperature")
    ax.set_xticks([300, 800, 1000, 1300])
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    curve = pd.DataFrame(available_heat_curve())
    for config in (*CHAIN_ORDER, "natural_gas"):
        g = curve[curve["config"] == config].dropna(subset=["available_heat_frac"])
        style = "--" if config == "natural_gas" else "-"
        ax.plot(g["t_flue_c"], g["available_heat_frac"], color=COLORS[config],
                linestyle=style, label=SHORT[config])
    ax.set_xlabel("Flue-gas exit temperature (°C)")
    ax.set_ylabel("Available heat / fuel LHV")
    ax.set_title("Burner balance at the flue exit\nnot a rescale of the 1000 °C point")
    ax.set_xlim(200, 1500)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, -0.08))
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return path
