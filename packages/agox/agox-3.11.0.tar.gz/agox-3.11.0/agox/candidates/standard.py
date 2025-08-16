from ase.calculators.singlepoint import SinglePointCalculator as SPC

from agox.candidates.ABC_candidate import CandidateBaseClass


class StandardCandidate(CandidateBaseClass):
    """
    Standard candidate class.
    """

    @classmethod
    def from_atoms(cls, template, atoms):
        candidate = cls(
            template=template, positions=atoms.positions, numbers=atoms.numbers, cell=atoms.cell, pbc=atoms.pbc
        )
        if hasattr(atoms, "calc"):
            if atoms.calc is not None:
                if "energy" in atoms.calc.results:
                    if "forces" in atoms.calc.results:
                        candidate.calc = SPC(
                            candidate,
                            energy=atoms.get_potential_energy(apply_constraint=False),
                            forces=atoms.get_forces(apply_constraint=False),
                        )
                    else:
                        candidate.calc = SPC(candidate, energy=atoms.get_potential_energy(apply_constraint=False))
        return candidate
