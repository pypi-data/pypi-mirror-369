"""
While generators generate candidates, postprocessors are used to apply common
postprocessing steps to all generated candidates. For example, the centering postprocessor
will center all candidates in the cell.

The most common postprocessors is the relax postprocessor, which performs a local
optimization on all candidates. Parallel implementations of this postprocessor are
also available and are recommended for searches that generated multiple candidates
pr. iteration.
"""
# ruff: noqa: I001, E402
from typing import TypeAlias

from .ABC_postprocess import PostprocessBaseClass
Postprocess: TypeAlias = PostprocessBaseClass

from .centering import CenteringPostProcess
from .disjoint_filtering import DisjointFilteringPostprocess
from .minimum_dist import MinimumDistPostProcess
from .ray_relax import ParallelRelaxPostprocess
from .relax import RelaxPostprocess
from .surface_centering import SurfaceCenteringPostprocess
from .wrap import WrapperPostprocess

__all__ = [
    "PostprocessBaseClass",
    "Postprocess",
    "CenteringPostProcess",
    "DisjointFilteringPostprocess",
    "MinimumDistPostProcess",
    "ParallelRelaxPostprocess",
    "RelaxPostprocess",
    "SurfaceCenteringPostprocess",
    "WrapperPostprocess",
]
