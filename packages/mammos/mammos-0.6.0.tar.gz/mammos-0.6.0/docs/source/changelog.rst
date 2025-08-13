=========
Changelog
=========

The format follows `Keep a Changelog <https://keepachangelog.com/>`__. Versions
follow `semantic versioning <https://semver.org/>`__, the metapackage version is
updated according to the largest bump of any of the dependent packages.

0.6.0 -- 2025-08-13
===================

Added
-----

``mammos-entity``
  - CSV files written with :py:mod:`mammos_entity.io` can now optionally contain
    a description. (`PR52
    <https://github.com/MaMMoS-project/mammos-entity/pull/52>`__)
  - Support for YAML as additional file format in :py:mod:`mammos_entity.io`.
    (`PR59 <https://github.com/MaMMoS-project/mammos-entity/pull/59>`__, `PR69
    <https://github.com/MaMMoS-project/mammos-entity/pull/69>`__, `PR70
    <https://github.com/MaMMoS-project/mammos-entity/pull/70>`__)
  - Two new functions :py:func:`mammos_entity.io.entities_to_file` and
    :py:func:`mammos_entity.io.entities_from_file` to write and read entity
    files. The file type is inferred from the file extension. (`PR57
    <https://github.com/MaMMoS-project/mammos-entity/pull/57>`__)
  - A function :py:func:`mammos_entity.concat_flat` to concatenate compatible
    entities, quantities and array-likes into a single entity. (`PR56
    <https://github.com/MaMMoS-project/mammos-entity/pull/56>`__)
``mammos-mumag``
  - Add function :py:func:`mammos_mumag.hysteresis.read_result` to read the result of a hysteresis loop from a folder (without running the hysteresis calculation again). (`PR48 <https://github.com/MaMMoS-project/mammos-mumag/pull/48>`__)
  - Implement :py:class:`mammos_mumag.mesh.Mesh` class that can read and display information of local meshes, meshes on Zenodo and meshes given by the user. (`PR53 <https://github.com/MaMMoS-project/mammos-mumag/pull/53>`__)
  - (`PR42 <https://github.com/MaMMoS-project/mammos-mumag/pull/42>`__)

Changed
-------

``mammos-analysis``
  - The Kuz'min formula to evaluate micromagnetic properties can now accept
    Curie Temperature Tc and spontaneous magnetisation at zero temperature Ms_0
    as optional inputs. If given, they are not optimised by fitting the
    magnetisation curve. (`PR12
    <https://github.com/MaMMoS-project/mammos-analysis/pull/12>`__)
  - The initial guess for the optimization of the Curie Temperature in Kuz'min
    formula is set to a much lower temperature (depending on the data). (`PR18
    <https://github.com/MaMMoS-project/mammos-analysis/pull/18>`__)
``mammos-entity``
  - When reading files with :py:mod:`mammos_entity.io` IRIs are now checked in
    addition to ontology labels and file reading fails if there is a mismatch
    between IRI and ontology label. (`PR68
    <https://github.com/MaMMoS-project/mammos-entity/pull/68>`__)
``mammos-mumag``
  - Changed the output of the hysteresis loop in compliance with :py:mod:`mammos_entity.io` v2. (`PR54 <https://github.com/MaMMoS-project/mammos-mumag/pull/54>`__)
  - (`PR46 <https://github.com/MaMMoS-project/mammos-mumag/pull/46>`__)

Deprecated
----------

``mammos-entity``
  - The functions ``mammos.entity.io.entities_to_csv`` and
    ``mammos_entity.io.entities_from_csv`` have been deprecated. Use
    :py:func:`mammos_entity.io.entities_to_file` and
    :py:func:`mammos_entity.io.entities_from_file` instead. (`PR58
    <https://github.com/MaMMoS-project/mammos-entity/pull/58>`__)

Fixed
-----

``mammos-entity``
  - On Windows, CSV files written with mammos-entity had blank lines between all
    data lines. (`PR66
    <https://github.com/MaMMoS-project/mammos-entity/pull/66>`__)
  - Writing CSV files with entities of different shapes 0 and 1, where elements
    with shape 0 were broadcasted is no longer supported as it is not round-trip
    safe. (`PR67 <https://github.com/MaMMoS-project/mammos-entity/pull/67>`__)
``mammos-dft``
  - Update attribute name of uniaxial anisotropy constant to `Ku_0` from `K1_0`
    for the returned `MicromagneticProperties` object during a database lookup.
    ([#19](https://github.com/MaMMoS-project/mammos-dft/pull/19))
``mammos-mumag``
  - Fixed the default values of the :py:class:`~mammos_mumag.materials.MaterialDomain` class (`PR41
    <https://github.com/MaMMoS-project/mammos-mumag/pull/41>`__)

0.5.0 -- 2025-07-11
===================

Added
-----

``mammos-entity``
  - A new submodule :py:mod:`mammos_entity.io` that provides two functions to
    write and read CSV files with additional ontology metadata. For more details
    refer to the new :doc:`io documentation </examples/mammos-entity/io>`.
    (`PR29 <https://github.com/MaMMoS-project/mammos-entity/pull/29>`__, `PR46
    <https://github.com/MaMMoS-project/mammos-entity/pull/46>`__, `PR47
    <https://github.com/MaMMoS-project/mammos-entity/pull/47>`__ )

Fixed
-----

``mammos-entity``
  - Fix bug when defining unitless entities. (`PR37
    <https://github.com/MaMMoS-project/mammos-entity/pull/37>`__ and `PR45
    <https://github.com/MaMMoS-project/mammos-entity/pull/45>`__)

0.4.0 -- 2025-06-27
===================

Changed
-------

``mammos-entity``
  - The ``Entity`` class is no longer a subclass of ``mammos_units.Quantity``.
    As a consequence it does no longer support mathematical operations. Use the
    attribute ``.quantity`` (or the short-hand ``.q``) to access the underlying
    quantity and to perform (mathematical) operations. (`PR28
    <https://github.com/MaMMoS-project/mammos-entity/pull/28>`__)
  - The package now comes with a bundled ontology consisting of `EMMO
    <https://github.com/emmo-repo/EMMO>`__ (version 1.0.0-rc3) and `Magnetic
    Material <https://github.com/MaMMoS-project/MagneticMaterialsOntology>`__
    (version 0.0.3). Internet access is no longer required. (`PR33
    <https://github.com/MaMMoS-project/mammos-entity/pull/33>`__)
``mammos``
  - Use Fe16N2 instead of Nd2Fe14B in hard magnet workflow. (`PR17
    <https://github.com/MaMMoS-project/mammos/pull/17>`__)

0.3.0 -- 2025-06-11
===================

Added
-----

``mammos-entity``
  - New predefined entity ``mammos_entity.J``
  - New predefined entity ``mammos_entity.Js``
``mammos-mumag``
  - Optional argument ``plotter`` in ``plot_configuration`` to add a vector plot
    of a magnetization configuration to a :py:class:`pyvista.Plotter` provided
    by the caller.

Changed
-------

``mammos-entity``
  - Return a ``mammos_units.UnitConversionError`` (inherited from
    ``astropy.units``) when trying initialize an entity with incompatible units.

0.2.0 -- 2025-06-06
===================

Added
-----

``mammos``
  - Command-line script ``mammos-fetch-examples`` to download all example
    notebooks.
``mammos-entity``
  - Entity objects have ``ontology_label_with_iri`` attribute.

Changed
-------

``mammos-entity``
  - When trying to initialize an entity with a wrong unit the error message does
    now show the required unit defined in the ontology.

Fixed
-----

``mammos-entity``
  - ``Entity.to`` did not return a new entity in the requested units and instead
    used the default entity units.
  - ``Entity.axis_label``: unit inside parentheses instead of brackets.

0.1.0 -- 2025-06-05
===================

Added
-----

``mammos`` -- 0.1.0
  - Workflows for hard magnets and sensor shape optimization.
  - Ensures compatible software components are installed.
``mammos-analysis`` -- 0.1.0
  - Calculation of macroscopic properties (Mr, Hc, BHmax) from a hysteresis
    loop.
  - Fitting of the linear segment of a hysteresis loop.
  - Calculation of temperature-dependent micromagnetic properties from atomistic
    spin dynamics simulations using Kuz’min equations.
``mammos-dft`` -- 0.3.0
  - Database lookup functionality for a selection of pre-computed materials.
``mammos-entity`` -- 0.5.0
  - Provides entities: quantities with links to the MaMMoS ontology (based on
    EMMO) by combining ``mammos-units`` and `EMMOntoPy
    <https://github.com/emmo-repo/EMMOntoPy>`__.
  - Helper functions to simplify creation of commonly required magnetic entities.
``mammos-mumag`` -- 0.6.0
  - Finite-element hysteresis loop calculations.
  - Requires a separate installation of `esys-escript
    <https://github.com/LutzGross/esys-escript.github.io/>`__.
``mammos-spindynamics`` -- 0.2.0
  - Database lookup functionality for a selection of pre-computed materials.
``mammos-units`` -- 0.3.1
  - Extension of astropy.units that allows working with quantities (units with
    values) containing additional units relevant for magnetism.
