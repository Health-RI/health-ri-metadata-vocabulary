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
