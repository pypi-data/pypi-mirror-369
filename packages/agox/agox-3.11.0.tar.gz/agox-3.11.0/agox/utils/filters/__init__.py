"""
This module contains the filters that can be used to filter candidate (or ase.Atoms) objects.
This is useful for filtering out candidates that are not interesting, e.g. if the energy is too high.
"""

from .ABC_filter import FilterBaseClass, SumFilter
from .all import AllFilter
from .energy import EnergyFilter
from .kmeans_energy import KMeansEnergyFilter
from .none import NoneFilter
from .random import RandomFilter
from .sparse_filter import SparsifierFilter
from .voronoi import VoronoiFilter

__all__ = [
    "FilterBaseClass",
    "AllFilter",
    "NoneFilter",
    "EnergyFilter",
    "SumFilter",
    "KMeansEnergyFilter",
    "SparsifierFilter",
    "RandomFilter",
    "VoronoiFilter",
]
