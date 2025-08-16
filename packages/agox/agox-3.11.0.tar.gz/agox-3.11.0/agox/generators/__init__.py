"""
Generators are are responsible for generating new configurations.
Typically there are two types of generators:

* Those that can generate a candidate by modifying one or more configurations.
* Those that can generate a candidate without any input configurations.

The first catagory of generators require a Sampler to sample the configurations
that it uses as a basis for generating a new candidate. The second category of
generators do not require a sampler.

The generators have to generate a candidate that follows the rules set by the
environment, that is

* The correct stoichoimetry
* Inside the confinement box.
"""
# ruff: noqa: I001, E402

from typing import TypeAlias
from agox.generators.ABC_generator import GeneratorBaseClass
Generator: TypeAlias = GeneratorBaseClass

from agox.generators.ce_generator import ComplementaryEnergyGenerator
from agox.generators.cog import CenterOfGeometryGenerator
from agox.generators.MD import MDgenerator
from agox.generators.permutation import PermutationGenerator
from agox.generators.random import RandomGenerator
from agox.generators.rattle import RattleGenerator
from agox.generators.replace import ReplaceGenerator
from agox.generators.reuse import ReuseGenerator
from agox.generators.sampling import SamplingGenerator
from agox.generators.steepest_descent import SteepestDescentGenerator
from agox.generators.symmetry import SymmetryGenerator
from agox.generators.symmetry_permutation import SymmetryPermutationGenerator
from agox.generators.symmetry_rattle import SymmetryRattleGenerator
from agox.generators.add_remove import AddRemoveGenerator

__all__ = ["GeneratorBaseClass", 
           "RandomGenerator", 
           "RattleGenerator", 
           "ReplaceGenerator",
           "ReuseGenerator", 
           "PermutationGenerator",
           "SteepestDescentGenerator", 
           "CenterOfGeometryGenerator", 
           "SamplingGenerator", 
           "ComplementaryEnergyGenerator", 
           "SymmetryGenerator", 
           "SymmetryRattleGenerator", 
           "SymmetryPermutationGenerator", 
           "MDGenerator",
           "AddRemoveGenerator"]

