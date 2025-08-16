import numpy as np
from ase.atom import Atom
from ase.atoms import Atoms
from ase.build import fcc111
from numpy.typing import NDArray

from agox.candidates.standard import StandardCandidate
from agox.postprocessors.surface_centering import SurfaceCenteringPostprocess


def test_surface_centering():
    rng = np.random.default_rng(1234)

    size = (5, 5, 1)
    template: Atoms = fcc111("Cu", size)
    unit_cell: NDArray = template.info["adsorbate_info"]["cell"]

    p = SurfaceCenteringPostprocess(template_size=size)

    for _ in range(10):
        # generate a random position within the minimal unit cell
        uc_position = rng.random(2)
        xy_position = uc_position @ unit_cell

        # add an atom at this position
        atom = Atom("Zn", position=[xy_position[0], xy_position[1], 2.0])
        candidate = StandardCandidate.from_atoms(template=template, atoms=template + atom)

        # center the atom
        centered = p.postprocess(candidate)

        # get the xy offset applied to the atom
        dx = (centered[-1].position - atom.position)[:2]

        # get the offset in terms of minimal unit cell units
        duc = np.linalg.solve(unit_cell.T, dx)

        # check whether this offset is integral
        assert np.all(np.isclose(duc, np.round(duc)))
