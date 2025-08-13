# Changelog

All notable changes to regpy will be documented in this file, starting from version 0.3.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Moreover, starting with version 0.3 we adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- For future follow structure

## [Unreleased]

### Added: New features or components

### Changed: Changes in existing functionality

### Deprecated: Features soon to be removed

### Removed: Features removed in this version

### Fixed: Bugs that were fixed
-->
## [0.4.2]

### Added

- added citation doi from zenodo including citation file CITATION.cff

## Changed

- amended a problem when combining more than two stop rules

## [0.4.1]

### Changed

- fixed some minor errors in documentation
- some issues in the testing were fixed
- Examples have been moved to a extra submodule

## [0.4.0]

### Added

- github workflows for publication on PyPi and Dockerhub
- added `LICENSE`
- added `INSTALLATION.md`, `USAGE.md` and `CHANGELOG.md`
- using `sphinx` to create the documentation
  - added more detailed instructions on the usage of `regpy`
- added `rclone.conf` for automatic upload to webserver
- convexity and Lipschitz constant to functionals
- general proximal parameters can be processed in proximal of functionals by `**proximal_par`
- added `QuadraticNonneg` functional for quadratic norm with non negativity constraint and `QuadraticPositiveSemidef` for matrices with respect to the Hilbert-Schmidt norm
- new `regpy.operators.ngsolve.SecondOrderEllipticCoefficientPDE` class to define second order elliptic parameter identification problems using `ngsolve`
  - with example in `ngsolve` for diffusion problem
- new linear solvers:
  - alternating minimization algorithm (AMA), `AMA` in `linear.ADMM`
  - forward backward splitting for general functionals, `ForwardBackwardSplitting` in `linear.proximal_gradient`
  - FISTA method for general functionals, `FISTA` in `linear.proximal_gradient`
  - `Tikhonov` can work with as well `TikhonovRegularizationSetting`
- utility functions to numerically test functionals for moreaus identity, subgradient, young equality
- utility functions for test for operators
- `vecsps.negsolve.NgsSpace` works now with general composed finite element systems
- `requirements.txt` include now explicitly the version dependence
- added more tests

### Changed

- `Dockerfile` now creates a image including a working jupyter server
- `README.md` includes now more specific installation instructions
- the gitlab ci now separates the creation of the documentation and the publication to the server and divides the test in core and examples
- examples are now pushed to a own git on [github](https://github.com/regpy/regpy-examples.git) and imported as a git submodule
- `pyproject.toml`
  - using dynamic extraction from git tag for version numbering
  - dependencies now allow for `numpy` versions `2.x`
  - dependency of `ngsolve` option now checks the `mkl` version because of issues with `2025.0.x`
  - removed examples as module
- renamed functionals on direct sum from `FunctionalProductSpace` to `FunctionalOnDirectSum`
- localized the import in `solvers` module
- moves `DualityGapStopping` from `solvers` to `stoprules`
- changed `vecsps.curves` to simplify.

### Deprecated <!-- Features soon to be removed -->

### Removed

- `makedoc` using `pdoc3` to generate the documentation was removed and changed to `sphinx`
- removed `irgnm_l1_fid`

### Fixed

- evaluation of base transform `BasisTransform` for two dimensional spaces

## [0.3.1] -

### Changed

- changed from the `setup.py` installation style to `pyproject.toml`

### Fixed

- fixing that accuracy of parallelogram identity of the tensor product hilbert space is usually of 1e-9 bugging the tests

## [0.3.0] - 2024-05-26

This version can be viewed as a initial version for future releases. It majorly changed functionality and is not backward compatible to the first release of version 0.1.

### Added

- **Additions to the `regpy.operators` module**
  - added product spaces as `regpy.vecsps.Prod` for tensor product spaces implemented the respective Hilbert space configuration as `regpy.hilbert.TensorProd`
    - for easy use you can simply use an abstract space on the product vector space
    - added module `regpy.operators.bases_transform` that offer operators to transform between product spaces
  - added convolution operators in module `regpy.operators.convolution`
  - added module for parallel computation of operators `regpy.operators.parallel_operators`
- **Additions to the `regpy.functionals` and `regpy.vecsps`**
  - abstract functionals similar to abstract Hilbert Spaces
    - provide the method `regpy.functionals.as_functional` that maps a Functional, HilberSpace or callable to a functional on an explicit vector space `regpy.vecsps.VectorSpace`.
  - new functionals
    - `IntegralFunctionalBase` for functionals defined via $v\mapsto \int_\Omega f(v(x),w(x))\mathrm{d}x $
    - derivatives of the `IntegralFunctionalBase` such as: `LppPower`, `L1MeasureSpace`, `KullbackLeibler`, `RelativeEntropy`, `Huber`, `QuadraticIntv`
    - for constraint optimization we have `QuadraticBilateralConstraints`
- **Additions to `regpy.solvers`**
  - new `RegSolver` that is a derivate class from the original `regpy.solvers.Solver` using a `RegularizationSetting`
    - offers method `runWithDP` as a convenience to run a solver with the discrepancy principle
  - new `RegularizationSetting` (replacing the old `HilbertSpacesetting`)
  - `TikhonovRegularizationSetting` as derivate of `RegularizationSetting` including a regularization parameter
    - offers a dual setting
- **Additions to the `ngsolve` interface**
  - the `ngsolve` interface has its own submoduls in each relevant path introducing
    - Introducing new `regpy.functionals.ngsolve` and revising the `regpy.vecsps.nsovle` (originally `regpy.discrs.nsolve`), `regpy.operators.ngsolve` and `regpy.hilbert.ngsolve`
- **Adding test using `pytest`**
  - added general unit tests and test on the examples
- **Added a Dockerfile**

### Changed

- **Changes to `regpy.solvers`**
  - Solvers were split into two submodules `regpy.solvers.linear` and `regpy.solvers.nonlinear` dividing for each use case
    - each solver type has its own submodule in the respective module
  - the class `HilbertSpaceSetting` from `regpy.solvers` was renamed to `RegularizationSetting`
    - the setting now can handle functionals as penalty and data fidelity
    - the setting remains backward compatible and allows `HilbertSpaces` and their abstract versions as input for penalty and data fidelity
    - the setting was extended to supply methods to check adjoint and derivate as well as to compute the operator norm
- **Changes examples and documentation**
  - the examples were striped by some outdated examples and asserted for functionality
  - as a new rule we assume that every examples should include a python notebooks (Every notebook should be stripped of its output before saving it.)
  - operators which for specific examples were moved to the specific example, for example `regpy.operators.mediumscattering` is no longer a module of regpy but only part of the corresponding example in `/examples/mediumscattering`
  - Documentation for core modules was extended and reviewed.

### Removed

- removed `nfft` submodule `regpy.operators.nfft`.
- removed some solvers that did not properly work or were never used

