import numpy as np


def atomic_numerical_derivative(func, atoms, delta=1e-3):
    N_atoms = len(atoms)

    f_output_shape = func(atoms).shape
    F = np.zeros((N_atoms, 3, *f_output_shape))

    stencil = [-2, -1, 0, 1, 2]

    for a in range(N_atoms):
        for d in range(3):
            f = {}
            for s in stencil:
                atoms_tmp = atoms.copy()
                atoms_tmp.positions[a, d] += delta * s
                f[s] = func(atoms_tmp)

            F[a, d] = (1 * f[-2] - 8 * f[-1] + 0 * f[0] + 8 * f[1] - 1 * f[2]) / (12 * delta)

    return -F
