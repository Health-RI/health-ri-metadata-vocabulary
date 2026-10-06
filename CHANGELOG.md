# Changelog

All notable changes to the complete Health-RI Metadata Vocabulary are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and vocabulary releases follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Terms do not have independent release versions.

## [0.5.0] - 2026-10-06

### Changed
- Extend `hri:healthConditionOfInterest` usage guidance and SHACL identifier validation to support ORPHAcode concepts using canonical ORDO IRIs (`http://www.orpha.net/ORDO/Orphanet_<code>`) alongside SNOMED CT and ICD-10.
- Expand the health-condition usage example to include separate SNOMED CT, ICD-10, and ORPHAcode statements; update supporting release references and generated publication artifacts.

## [0.4.3] - 2026-10-05

### Changed
- Replace `rdfs:comment` with `dcterms:description` on `hri:healthConditionOfInterest` and `hri:anatomicalLocationCovered`, preserving their description text and all other property annotations and axioms.
- Update release metadata, supporting release references, and generated publication artifacts. Existing versioned snapshots, example data, and SHACL constraints remain unchanged.

## [0.4.2] - 2026-10-05

### Changed
- Automatically render the vocabulary's existing logo as an image before the title instead of an ordinary Metadata entry in newly generated PyLODE documentation.
- Wrap property Example content, including long IRIs and unbroken strings, within its container using scoped styling.
- Render each property's source `skos:definition` in a Definition field after Is Defined By and before Description; omit the field when no definition is supplied.
- Publish a new documentation snapshot and update release metadata and supporting references. Term definitions, RDF/OWL axioms, SHACL constraints, and example data are unchanged; existing release snapshots remain immutable.

## [0.4.1] - 2026-10-03

### Changed
- Declare the versioned vocabulary Turtle file the sole normative specification for each release, with precedence over supporting resources.
- Explicitly identify SHACL shapes, examples, and generated HTML documentation as non-normative; clarify that shape checks are implementation guidance and do not introduce or override vocabulary requirements.
- Distinguish the normative vocabulary interface from compatibility tracking for the supporting validator. Clarify property annotations about use of the shapes.
- Update supporting release references and generated publication files. Vocabulary axioms, SHACL constraints, and example data are unchanged.

## [0.4.0] - 2026-10-02

### Changed
- Update vocabulary abstract, description, keywords, citation, and property annotations; add creator email IRIs and remove the two property history notes from the current release.
- Restrict health-condition usage to SNOMED CT or ICD-10 concepts and update the existing SHACL shape with the agreed identifier-pattern alternatives. This is a breaking validation change: previously accepted identifiers from other terminologies now fail. Pattern matching does not verify existence, activity status, or clinical suitability.
- Update supporting artifact references, current documentation, and generated publication/citation files to 0.4.0. Preserve archived releases and the anatomical range and hierarchy validation.

## [0.3.0] - 2026-10-02

### Changed

- Require SNOMED CT anatomical IRIs and a supplied subclass path to Anatomical structure (91723000), including the root itself, in the anatomical SHACL shape. The OWL Full range restriction remains in place.
- Attribute examples solely to Pedro Paulo F. Barcelos and the shapes to all four vocabulary creators, with ORCID identifiers and names.
- Remove duplicate vocabulary contributor assertions; use `/spec` and `/git` PIDs in vocabulary homepage/repository metadata and refine discovery keywords.
- Remove the local declaration of SNOMED 91723000 as an OWL class, retaining the external IRI in the range axiom. Clean supporting-file prefixes and comments.
- Update release documentation, generated HTML, and citation metadata.

### Added

- A validation command accepting a separate trusted SNOMED named-class hierarchy, excluding submitted subclass assertions and avoiding vocabulary inference.
- Regression tests for hierarchy membership, evidence isolation, and attribution.
- Build-time consistency checks against the highest numbered vocabulary release: latest Turtle/HTML, citation metadata, and explicitly maintained example/SHACL release references. Supporting references are never silently rewritten.
- Regression checks for missing/stale references and inconsistent generated outputs.

### Compatibility

- Stricter anatomical validation rejects values accepted by the structural-only 0.2.1/0.2.2 checks. The development minor version signals this change. Historical release snapshots and the health-condition semantics are unchanged.

## [0.2.2] - 2026-10-02

### Added

- Vocabulary-level `vann:example` links to both usage examples and `sh:suggestedShapesGraph` linking to the existing `/shacl` resource.
- Self-describing metadata in both examples and the validation file, including their purpose, publisher, license, format, language, modification date, and accompanying vocabulary release. The discovery relationships are repeated in each relevant supporting file.
- Documentation of discovery semantics and supporting-artifact metadata.

### Compatibility

- Metadata-only patch: property definitions, OWL axioms, example data, and SHACL constraints are unchanged. Previous release snapshots remain immutable.

## [0.2.1] - 2026-10-01

### Changed

- Replaced the anatomical property's `skos:Concept` range with an OWL Full `owl:hasValue` restriction on `rdfs:subClassOf`, targeting SNOMED CT 91723000.
- Removed anatomical Concept typing, namespace, and hierarchy-membership SHACL checks; retained Dataset-subject and IRI-object checks. The range axiom entails subclass membership and does not validate authoritative SNOMED membership.
- Updated the anatomical example, documentation, release checks, inference tests, generated latest representations, and citation metadata.
- **Compatibility:** this changes formal semantics and validation expectations. Version 0.2.1 was explicitly requested despite that semantic change; it is not a claim of patch-level compatibility. The health-condition term and all previous release snapshots remain unchanged.

## [0.2.0] - 2026-10-01

### Added

- `hri:anatomicalLocationCovered` for R-U-03 dataset-level anatomical coverage. Domain is `dcat:Dataset`; RDF range is `skos:Concept`, with a controlled value range of SNOMED CT Anatomical structure (91723000) or descendants (`<< 91723000`).
- Separate SHACL checks for concept IRIs and the supplied SNOMED subclass hierarchy, with optional, repeatable use; a standalone lung-coverage example and tests.

### Changed

- Superseded the earlier R-U-03 EUCAIM modelling proposal with the Health-RI term, without asserting a formal mapping to EUCAIM.
- Updated current documentation, citation metadata, and latest representations. Archived 0.1.0 files and health-condition semantics remain unchanged.
- Validate every usage example and test promotion from the current release.
- Restructured the initial 0.1.0 implementation at the maintainers' request: flat versioned TTL/HTML files and latest-only Pages publication.
- Moved tests and pinned dependencies under `scripts/`; moved validation and the usage example to separate supporting directories.
- Completed initial vocabulary metadata and attributed the four authors with verified ORCID identifiers. This is a correction of the initial implementation, not a change to the health-condition property's semantics.

## [0.1.0] - 2026-09-30

### Added

- Initial development release of the Health-RI Metadata Vocabulary.
- `hri:healthConditionOfInterest` for dataset-level clinical aboutness, with domain `dcat:Dataset` and range `skos:Concept`.
- Separate SHACL validation requiring IRI values, with optional, repeatable use.
- Vocabulary metadata, a Turtle usage example, and CC BY 4.0 licensing.
- Versioned sources, generated latest representations, PyLODE documentation, and automated validation and GitHub Pages publication infrastructure.

[0.5.0]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.5.0.ttl
[0.4.3]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.4.3.ttl
[0.4.2]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.4.2.ttl
[0.1.0]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.1.0.ttl

[0.2.0]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.2.0.ttl

[0.2.1]: https://github.com/Health-RI/health-ri-metadata-vocabulary/blob/main/vocabulary/versioned/health-ri-metadata-vocabulary-v0.2.1.ttl
