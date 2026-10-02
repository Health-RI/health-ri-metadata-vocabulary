# Changelog

All notable changes to the complete Health-RI Metadata Vocabulary are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and vocabulary releases follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Terms do not have independent release versions.

## [Unreleased]

### Changed

- Restructured the initial 0.1.0 implementation at the maintainers' request:
  flat versioned TTL/HTML files and latest-only Pages publication.
- Moved tests and pinned dependencies under `scripts/`; moved validation and
  the usage example to separate supporting directories.
- Completed initial vocabulary metadata and attributed the four authors with
  verified ORCID identifiers. This is a correction of the initial implementation,
  not a change to the health-condition property's semantics.

## [0.2.2] - 2026-10-02

### Added

- Vocabulary-level `vann:example` links to both usage examples and
  `sh:suggestedShapesGraph` linking to the existing `/shacl` resource.
- Self-describing metadata in both examples and the validation file, including
  their purpose, publisher, license, format, language, modification date, and
  accompanying vocabulary release. The discovery relationships are repeated
  in each relevant supporting file.
- Documentation of discovery semantics and supporting-artifact metadata.

### Compatibility

- Metadata-only patch: property definitions, OWL axioms, example data, and SHACL
  constraints are unchanged. Previous release snapshots remain immutable.

## [0.2.1] - 2026-10-01

### Changed

- Replaced the anatomical property's `skos:Concept` range with an OWL Full
  `owl:hasValue` restriction on `rdfs:subClassOf`, targeting SNOMED CT 91723000.
- Removed anatomical Concept typing, namespace, and hierarchy-membership SHACL
  checks; retained Dataset-subject and IRI-object checks. The range axiom entails
  subclass membership and does not validate authoritative SNOMED membership.
- Updated the anatomical example, documentation, release checks, inference tests,
  generated latest representations, and citation metadata.
- **Compatibility:** this changes formal semantics and validation expectations.
  Version 0.2.1 was explicitly requested despite that semantic change; it is not
  a claim of patch-level compatibility. The health-condition term and all previous
  release snapshots remain unchanged.

## [0.2.0] - 2026-10-01

### Added

- `hri:anatomicalLocationCovered` for R-U-03 dataset-level anatomical coverage.
  Domain is `dcat:Dataset`; RDF range is `skos:Concept`, with a controlled value
  range of SNOMED CT Anatomical structure (91723000) or descendants (`<< 91723000`).
- Separate SHACL checks for concept IRIs and the supplied SNOMED subclass hierarchy,
  with optional, repeatable use; a standalone lung-coverage example and tests.

### Changed

- Superseded the earlier R-U-03 EUCAIM modelling proposal with the Health-RI term,
  without asserting a formal mapping to EUCAIM.
- Updated current documentation, citation metadata, and latest representations.
  Archived 0.1.0 files and health-condition semantics remain unchanged.
- Validate every usage example and test promotion from the current release.

## [0.1.0] - 2026-09-30

### Added

- Initial development release of the Health-RI Metadata Vocabulary.
- `hri:healthConditionOfInterest` for dataset-level clinical aboutness, with
  domain `dcat:Dataset` and range `skos:Concept`.
- Separate SHACL validation requiring IRI values, with optional, repeatable use.
- Vocabulary metadata, a Turtle usage example, and CC BY 4.0 licensing.
- Versioned sources, generated latest representations, PyLODE documentation,
  and automated validation and GitHub Pages publication infrastructure.

[Unreleased]: https://github.com/Health-RI/health-ri-metadata-vocabulary/commits/main
[0.1.0]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.1.0.ttl

[0.2.0]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.2.0.ttl

[0.2.1]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.2.1.ttl
