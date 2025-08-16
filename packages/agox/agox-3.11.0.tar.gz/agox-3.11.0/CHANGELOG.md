# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.11.0] - 2025-08-15

* Moved build system to CI for making it easier to manage releases.
* Added Grand Canonical modules.

## [3.10.2] - 2025-06-24

* Fixed issue with package discovery breaking non-editable installs.

## [3.10.1] - 2025-06-24 

* Yanked this release.
* Failure

## [3.10.0]

### Added

* `CalculatorModel` and `CompositionModel` both intended for use with universal potentials.
* Added replica exchange modules: a sampler, a collector and an acquisitor. 
* Added replica exchange documentation with two scripts: one short test script and one real DFT script.

### Fixed

* Fixed LCB-penalty acquisition function after changes in 3.9.0
* Added `check_callback` to allow calculations to be discarded according to user defined criteria. 

## [3.9.0] - 2024-10-23

### Changed

* Analysis code refactored into several modules and classes, rather than monolithic `batch_analysis`
* Analysis code has almost full test coverage now.
* Updated CLI tools to use `click` rather than `ArgumentParser` some changes to flags.
* Python version requirement increased to `3.10` or higher. Tests will run on `3.10` for merge requests to `dev` or `stable` and weekly tests will run `3.10`, `3.11`, `3.12`. Motivated by newest Scipy and Numpy 
version not support `3.8` or `3.9`.
* Numpy version locked to `<2` at least until `GPAW` releases a version that allows `>2`.
* Added ruff rules to `pyproject.toml`
* Refactoring of Observer code into several modules and some clean up of the logic, should be more approachable now. 
* Removal of 'Tracker' as it was an entirely unused feature. 
* Rewritten and simplified `Writer` using `rich` for easy construction of more elaborate output layouts. 
* Refactoring of `Confinement`-class - is now not inherited from but created by classes that use it. Simplifies inheritance patterns and 
makes the `Confinement`-class more versatile.
* Installation problem fixed with changes to `pyproject.toml`. 

## [3.8.0] - 2024-8-26

### Added

* Added surface centering postprocessor
* Added adsorption site-aware Voronoi graph descriptor
* Added LCB-penalty acquisition function
* Added Ray-based Parallel Tempering implementation and renamed old implementation to Concurrent Tempering.

## [3.7.0] - 2024-8-2

### Added

* Improved Ray stability by trying to avoid asking for too many resources at once and refactored a bit more.
* Added additional plotting utility to more easily create plots with custom color schemes.
* Fixed issue with BoxConstraint lacking methods used by ASE's VASP calculator.
* Added parity plot functionality and some simple metrics.
* Revamped some tests and added examples with different calculators to documentation.
* Added Ensemble LGPR model.

## [3.6.0] - 2024-4-2

### Added

* Added symmetry generators.
* Changed the internal workings of generators & samplers. Better support for generators that have multiple parents.
* Removed use of custom docker image for testing, added testing pipelines for other python versions.
* Scheduling functionality for the SparseGPR to control how often sparsification is done during a search.
* Printing of git commit sha with the version with the AGOX logo at the start of a run.
* Sparse GPR no longer trains projected process uncertainty by default, as it can be very slow.
* Sparse GPR saves fewer attributes with model.save, resulting in much smaller files.
* Plots produced by generators now indicate atoms that are fixed.
* Block generators added that place blocks of atoms (rattle and random
  implemented)
* MD generator added.

### Changed

* Changelog using Keep a Changelog guidelines.

### Fixed

* Fixed bug in visual ordering of atoms plotted with `plot_atoms` when the `repeat` option is used.

## [3.5.3] - 2023-12-19

### Added

* Added wrap keyword in BoxConstraint to control if atoms are wrapped
  inside periodic confinement directions. Default is false to conform
  with BFGS.

## [3.5.2] - 2023-11-16

### Added

* Added SafeBFGS which fixes an issue where relaxations take an indefinite amount of time due the Hessian becoming singular and the optimization step containing nans.

## [3.5.1] - 2023-11-15

### Fixed

* Fixes issue where jobs using Ray often crash at the very beginning of the run.

## [3.5.0] - 2023-11-07

### Changed

* Small updates to Ray, but installing Ray with more dependencies easist option is to do `pip install ray[default]`.

## [3.4.0] - 2023-10-26

### Added

* Added a postprocessor to filter disjoint candidates.

## [3.3.0] - 2023-10-17

### Added

* Added coverage report to gitlab CI.

## [3.2.5] - 2023-10-17

### Added

* Added a method to make it easier handle transfer and regular data with the sparse GPR.

## [3.2.4] - 2023-10-16

### Changed

* Minor documentation fixes.

## [3.2.3] - 2023-10-09

### Fixed

* Bug fixes for sparsifiers and added a test for sparsifiers.

## [3.2.2] - 2023-09-22

### Fixed

* Bug fixes related to Cython release of 3+

## [3.2.1] - 2023-09-14

### Changed

* Pin Cython to 0.29.36

## [3.2.0] - 2023-09-08

### Added

* Added possibility to train sparse GPRs on energies and forces.

## [3.1.2] - 2023-09-08

### Fixed

* Fixed bug where the DescriptorBaseClass takes kwargs and therefore wouldnt throw an error for unused keyword arguments leading to unintended behaviour.

## [3.1.1] - 2023-08-07

### Fixed

* Bugfix for `_make_local_sigma` method

## [3.1.0] - 2023-07-18

### Added

* Updated documentation about Ray and about using filters to analyze structures, both are in bonus topics.
* Added FeatureDistanceFilter and a test for it.

## [3.0.0] - 2023-07-10

### Changed

* Rewritten GPR and SparseGPR models able to handle both global and local descriptors
* GPR kernels inheriting from Scikit-learn, but with added functionality
* Descriptor initialization has changed to better fit into standard AGOX use.

### Added

* Parallel hyperparameter optimization using Ray.
* Filters and sparsifiers to use with GPR models
* Ability to add validation data to models.
* New and improved save/load format for models
* Analytical forces
* Uncertainty quantification with projected process for Sparse GPR
* Analytical uncertainty forces
* Marginal likelihood for Sparse GPR
* Monte Carlo hyperparameter optimization for Sparse GPR

## [2.3.0] - 2023-05-02

### Changed

* Gitlab CI now enabled.
* Plotting code cleaned up.
* Replaced the logger with a more general tracker module.

### Fixed

* GPAW_IO bug fixes.
* Bug fixes for parallel collector with updatable generators.

### Added

* Complemenetary Energy Generator added.
* Cache for e.g. descriptors added.

### Removed

* Removed 'test_scripts' directory which was not supposed to be used anymore.

[Unreleased]: https://gitlab.com/agox/agox/-/compare/v3.9.0...dev
[3.9.0]: https://gitlab.com/agox/agox/-/compare/v3.8.0...v3.9.0
[3.8.0]: https://gitlab.com/agox/agox/-/compare/v3.7.0...v3.8.0
[3.7.0]: https://gitlab.com/agox/agox/-/compare/v3.6.0...v3.7.0
[3.6.0]: https://gitlab.com/agox/agox/-/compare/v3.5.2...v3.6.0
[3.5.2]: https://gitlab.com/agox/agox/-/compare/v3.5.1...v3.5.2
[3.5.1]: https://gitlab.com/agox/agox/-/compare/v3.5.0...v3.5.1
[3.5.0]: https://gitlab.com/agox/agox/-/compare/v3.4.0...v3.5.0
[3.4.0]: https://gitlab.com/agox/agox/-/compare/v3.3.0...v3.4.0
[3.3.0]: https://gitlab.com/agox/agox/-/compare/v3.2.5...v3.3.0
[3.2.5]: https://gitlab.com/agox/agox/-/compare/v3.2.4...v3.2.5
[3.2.4]: https://gitlab.com/agox/agox/-/compare/v3.2.3...v3.2.4
[3.2.3]: https://gitlab.com/agox/agox/-/compare/v3.2.2...v3.2.3
[3.2.2]: https://gitlab.com/agox/agox/-/compare/v3.2.1...v3.2.2
[3.2.1]: https://gitlab.com/agox/agox/-/compare/v3.2.0...v3.2.1
[3.2.0]: https://gitlab.com/agox/agox/-/compare/v3.1.2...v3.2.0
[3.1.2]: https://gitlab.com/agox/agox/-/compare/v3.1.1...v3.1.2
[3.1.1]: https://gitlab.com/agox/agox/-/compare/v3.1.0...v3.1.1
[3.1.0]: https://gitlab.com/agox/agox/-/compare/v3.0.0...v3.1.0
[3.0.0]: https://gitlab.com/agox/agox/-/compare/v2.3.0...v3.0.0
[2.3.0]: https://gitlab.com/agox/agox/-/compare/v2.2.1...v2.3.0
