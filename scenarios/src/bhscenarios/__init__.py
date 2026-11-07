"""Industrial scenario screening for biomass process-heat chains.

The runnable code lives in this umbrella repository under ``scenarios/``.
The roadmap name ``biomass-heat-scenarios`` is the package name only.
There is no separate repository.
"""
from .screen import run_screening

__version__ = "0.1.0"

__all__ = ["run_screening", "__version__"]
