def cluster_confinement():
    import numpy as np
    from ase import Atoms

    from agox.environments import Environment

    template = Atoms("", cell=np.eye(3) * 12)
    confinement_cell = np.eye(3) * 6
    confinement_corner = np.array([3, 3, 3])
    environment = Environment(
        template=template,
        symbols="Au8Ni8",
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
    )
    environment.plot("plots/cluster_confinement.png")


def surface_film_confinement():
    import numpy as np
    from ase.build import fcc100

    from agox.environments import Environment

    # Define a template surface using ASE functions.
    template = fcc100("Au", size=(4, 4, 2), vacuum=5.0)
    template.pbc = [True, True, False]
    template.positions[:, 2] -= template.positions[:, 2].min()

    # Confinement cell matches the template cell in x & y but is smaller in z.
    confinement_cell = template.cell.copy()
    confinement_cell[2, 2] = 4.0

    # Confinement corner is at the origin of the template cell, except in z where
    # it is shifted up.
    z0 = template.positions[:, 2].max()
    confinement_corner = np.array([0, 0, z0])  # Confinement corner is at cell origin

    environment = Environment(
        template=template,
        symbols="Ni8",
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
        box_constraint_pbc=[True, True, False],  # Confinement is not periodic in z
    )

    environment.plot("plots/surface_film_confinement.png")


def surface_cluster_confinement():
    import numpy as np
    from ase.build import fcc100

    from agox.environments import Environment

    # Define a template surface using ASE functions.
    template = fcc100("Au", size=(4, 4, 2), vacuum=5.0)
    template.pbc = [True, True, False]
    template.positions[:, 2] -= template.positions[:, 2].min()

    # Confinemnet cell is a 6x6x6 cube
    confinement_cell = np.eye(3) * 6

    # Confinement cell is centered in the template cell
    z0 = template.positions[:, 2].max()
    x0 = template.cell[0, 0] / 2 - confinement_cell[0, 0] / 2
    y0 = template.cell[1, 1] / 2 - confinement_cell[1, 1] / 2
    confinement_corner = np.array([x0, y0, z0])  # Confinement corner is at cell origin

    environment = Environment(
        template=template,
        symbols="Ni8",
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
        box_constraint_pbc=[True, True, False],  # Confinement is not periodic in z
    )

    environment.plot("plots/surface_cluster_confinement.png")


def two_d_environment():
    import numpy as np
    from ase import Atoms

    from agox.environments import Environment

    template = Atoms("", cell=np.eye(3) * 12)
    confinement_cell = np.eye(3) * 6
    confinement_cell[2, 2] = 0  # Zero height of confinement cell for the third dimension.
    confinement_corner = np.array([3, 3, 6])
    environment = Environment(
        template=template,
        symbols="Au4Ni4",
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
    )

    environment.plot("plots/two_d_environment.png")


def surface_toplayer_unconstrained():
    import numpy as np
    from ase.build import fcc100
    from ase.constraints import FixAtoms

    from agox.environments import Environment

    # Define a template surface using ASE functions.
    template = fcc100("Au", size=(4, 4, 2), vacuum=5.0)
    template.pbc = [True, True, False]
    template.positions[:, 2] -= template.positions[:, 2].min()

    # Confinement cell matches the template cell in x & y but is smaller in z.
    confinement_cell = template.cell.copy()
    confinement_cell[2, 2] = 4.0

    # Confinement corner is at the origin of the template cell, except in z where
    # it is shifted up.
    z0 = template.positions[:, 2].max()
    confinement_corner = np.array([0, 0, z0])  # Confinement corner is at cell origin

    # Fix bottom layers:
    constraint = FixAtoms(mask=[atom.position[2] < 2.0 for atom in template])

    environment = Environment(
        template=template,
        symbols="Ni8",
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
        box_constraint_pbc=[True, True, False],  # Confinement is not periodic in z
        fix_template=False,
        constraints=[constraint],
    )

    environment.plot("plots/surface_toplayer_unc.png")


if __name__ == "__main__":
    cluster_confinement()
    surface_film_confinement()
    surface_cluster_confinement()
    two_d_environment()
    surface_toplayer_unconstrained()
