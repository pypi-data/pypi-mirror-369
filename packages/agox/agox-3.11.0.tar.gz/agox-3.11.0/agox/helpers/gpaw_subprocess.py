import os
from pathlib import Path

from ase.calculators.calculator import Calculator, all_changes, all_properties


class SubprocessGPAW(Calculator):
    """
    GPAW calculator that uses a subprocess to run the calculation.

    Parameters
    -------------
    ncores (int): The number of cores to use.
        If None, the number of cores is determined by the number of cores available.

    **kwargs:
        Additional keyword arguments to pass to the GPAW for calculation settings.
        Eg.
            kwargs = {
                'mode': {'name': 'pw', 'ecut': cutoff},
                'xc': 'PBE',
        Is a planewave PBE calculation.
        The same dict can be passed directly to the normal GPAW calculator, to exactly
        reproduce the calculation settings.
    """

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self, ncores=None, log_directory="gpaw_logs/", **kwargs):
        super().__init__()
        self.kwargs = kwargs

        if ncores is None:
            ncores = len(os.sched_getaffinity(0))
        self.ncores = ncores
        self.count = 0

        self.log_directory = Path(log_directory)
        if not self.log_directory.exists():
            self.log_directory.mkdir(parents=True)

    def calculate(self, atoms=None, properties=all_properties, system_changes=all_changes):
        from ase.calculators.subprocesscalculator import gpaw_process  # Because of ASE versions.

        super().calculate(atoms, properties, system_changes)

        # Update the log file name.
        kwargs = self.kwargs.copy()
        if kwargs.get("txt", "-") != "-":
            name = Path(kwargs["txt"]).stem + f"_{self.count}.txt"
            kwargs["txt"] = str(self.log_directory / name)

        # Run the calculation.
        with gpaw_process(ncores=self.ncores, **kwargs) as gpaw:
            gpaw._run_calculation(self.atoms.copy(), properties, system_changes)
            results = gpaw.protocol.recv()

        self.results.update(results)
        self.count += 1
