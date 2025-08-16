import numpy as np
from ase.calculators.singlepoint import SinglePointCalculator

from agox.candidates import Candidate
from agox.helpers.confinement import Confinement
from agox.postprocessors.ABC_postprocess import PostprocessBaseClass


class CenteringPostProcess(PostprocessBaseClass):
    """
    Centers a candidate object to the middle of the cell.

    Should not be used for periodic systems.
    """

    name = "CenteringPostProcess"

    def __init__(self, confinement: Confinement | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.confinement = confinement

    def postprocess(self, candidate: Candidate) -> Candidate:
        """
        Centers a candidate object to the middle of the cell.

        Parameters
        ----------
        candidate : Candidate
            Candidate object to be centered.

        Returns
        -------
        candidate : Candidate
            Centered candidate object.

        """
        center_candidate = candidate.copy()
        if candidate.pbc.any():
            self.writer("CenteringPostProcess used on a periodic system, won't have any effect. Consider removing from script.")
            return candidate

        results = None
        if hasattr(candidate, "calc"):
            if hasattr(candidate.calc, "results"): 
                results = candidate.calc.results
                    
        com = candidate.get_center_of_mass()
        cell_middle = np.sum(candidate.get_cell(), 0) / 2
        center_candidate.positions = candidate.positions - com + cell_middle

        if self.confinement is not None:
            if not self.confinement.check_confinement(center_candidate.positions).all():
                self.writer.debug('Confinement violated after centering.')
                return candidate
        
        if results is not None: 
            center_candidate.calc = SinglePointCalculator(center_candidate, **results)
        return center_candidate
