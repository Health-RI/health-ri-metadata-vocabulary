# Maintaining the vocabulary

## Sources and release contract

The sole normative specification for each release is its versioned vocabulary Turtle file:
`vocabulary/versioned/health-ri-metadata-vocabulary-vX.Y.Z.ttl`.
The version is part of the filename, not a directory name. All terms belong to the
same vocabulary version and retain their stable, unversioned term IRIs.

PyLODE generates an adjacent `health-ri-metadata-vocabulary-vX.Y.Z.html` snapshot.
The highest numbered release is copied to `vocabulary/latest/health-ri-metadata-vocabulary.ttl`
and its documentation to `vocabulary/latest/index.html`. These latest files and
`CITATION.cff` are generated; do not edit them by hand.

Published versioned Turtle and HTML snapshots are immutable. Add a new version
rather than editing or deleting an existing snapshot. CI checks existing snapshots
against its base commit; branch protection remains a separate repository setting.
The explicitly requested restructuring and metadata correction of the initial
0.1.0 implementation is a one-time migration from commit `e9bc4ca`; the build script
limits that exception to the old paths at that exact commit.

Generated HTML documentation is non-normative and is derived from the vocabulary.
The SHACL file in `validation/` and examples in `examples/` are also non-normative
supporting artifacts, not additional release inputs. They provide IRI checks, health-condition Concept typing and SNOMED CT/WHO ICD-10 identifier patterns, anatomical hierarchy checks,
and runnable usage examples. New releases require reviewed matching references in these support files; no versioned copies of these support files are required.

## Semantic Versioning

The normative vocabulary interface comprises term IRIs, their documented meaning,
and RDF/OWL axioms in the versioned Turtle file. The accompanying SHACL constraints
are non-normative implementation guidance. Changes to their validation behaviour
are still tracked for compatibility and release versioning; this does not make
them vocabulary requirements. In case of discrepancy, the versioned vocabulary
Turtle file takes precedence. The vocabulary follows
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

- At `1.0.0` and above: incompatible changes require a major version; compatible
  additions require a minor version; compatible corrections require a patch.
- During `0.y.z` development, stability is not promised. Use a new minor version
  for term additions or breaking semantic or validation changes, and a patch for compatible corrections.
- Do not silently change the meaning of a published term; explain compatibility
  implications in the changelog and assess whether a different term is necessary.
- Repository-only tooling changes do not require a vocabulary release unless they
  alter the published vocabulary or its release contract.

The publication pipeline accepts numeric `X.Y.Z` releases (including `0.1.0`).
SemVer prerelease/build suffixes are not published by this pipeline. Draft work
stays on branches until ready for a numbered release.

## Add a release

1. Copy the previous vocabulary TTL to
   `vocabulary/versioned/health-ri-metadata-vocabulary-vX.Y.Z.ttl`.
2. Edit the new vocabulary. Update `owl:versionInfo`, `dcat:version`,
   `owl:versionIRI`, `dcterms:modified`, the version-specific documentation link,
   and the bibliographic citation. Preserve the vocabulary's original issued date.
   Set `owl:priorVersion` to the preceding version IRI. Update the separate
   shapes/examples when validation or usage guidance changes. For every release,
   review their compatibility and explicitly update their document-level
   `dcterms:references` to the new release IRI, even if their data/constraints
   remain unchanged. The build rejects missing, stale, or conflicting references.
3. Add a dated vocabulary-level entry to `CHANGELOG.md` using Keep a Changelog
   categories. Include any breaking semantics or validation effects explicitly.
4. Run the README validation commands and review both RDF and generated HTML.
5. Commit the new release and changelog to `main` (or merge a reviewed branch).

Adding a new versioned TTL triggers the publication workflow; reviewed supporting
release references must also match before generation and publication can pass; no hard-coded current-version configuration needs changing. The
highest version is selected numerically, not by modification date or string order.
All historical snapshots remain stored in GitHub; only the latest documentation
is deployed to Pages. The workflow commits generated
latest/HTML/citation files using `GITHUB_TOKEN`, which does not recursively trigger
another push workflow. The same run uploads `vocabulary/latest/` directly as the Pages artifact. No
separate `docs/` or `site/` copy is maintained.

## Automation and Pages

Pull requests validate/build only. Pushes to `main` and manual workflow runs on
`main` also commit generated outputs to that same repository. Deployment uses the
official GitHub Pages artifact and deployment actions. The built site is retained
as an artifact even if deployment is blocked because Pages has not been enabled.

To activate publication in the repository that should host the site:

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
2. Run **Actions → Validate and publish vocabulary → Run workflow** on `main`.

If GitHub displays “Workflows aren't being run on this fork”, enable workflows
there first. Canonical RDF metadata and w3id targets always identify Health-RI;
workflow credentials and deployment target come from the current repository.
No workflow writes to an upstream repository. The workflow requests contents-write
only for generated-file updates, and pages-write/id-token-write only for deployment.

The official site will be `https://health-ri.github.io/health-ri-metadata-vocabulary/`,
opening the latest PyLODE specification directly. Archived HTML is stored in
`vocabulary/versioned/` and may be inspected or downloaded through GitHub, but is
not deployed as historical Pages URLs.
The w3id redirects are maintained separately; their adoption is not performed by
this repository. Until they are installed, use the repository files directly.

## Dependencies and review

`scripts/requirements.txt` pins the full tested Python environment, including transitive
dependencies. Use Python 3.12. Action dependencies are pinned to commit SHAs with
release labels in comments. Upgrade deliberately, run all checks, and inspect
newly generated documentation before accepting upgrades. Past HTML snapshots are
preserved when the generator changes.

Tests cover release metadata, IRI-only values, explicit Concept typing,
subject typing, optionality, multiple values, and anatomical subclass entailment. Review the clinical meaning and
external identifiers separately; syntax validation cannot establish those facts.

For `hri:anatomicalLocationCovered`, version 0.2.1 uses an OWL Full range restriction
on `rdfs:subClassOf` with `owl:hasValue` set to SNOMED CT `91723000`.
Do not interpret the resulting subclass entailment as authoritative terminology
validation. Since 0.3.0, anatomical SHACL also checks SNOMED IRI syntax and a
subclass path to that root. Use `scripts/validate.py` with an independently trusted
SNOMED hierarchy; see the README for input format, provenance, and limitations.
The inference regression test exercises the relevant RDF/OWL rules; it is not a
complete OWL Full consistency checker. OWL 2 DL tools cannot be assumed to support
this metamodeling pattern.

The 0.2.1 number is an explicitly requested exception to the development versioning
guideline above: the release changes formal range semantics and removes anatomical
Concept typing and hierarchy-validation requirements. Retain the archived 0.2.0
files unchanged.

The existing w3id proposal uses version-pattern redirects and already covers
`v0.4.1`; this release does not require new redirect rules.


## Supporting Turtle metadata

Keep the document headers in `examples/` and `validation/` current when editing
those files: update `dcterms:modified` and the accompanying release reference as
appropriate. Do not invent original publication dates or individual authorship.
For a new example, add its `vann:example` link to the next vocabulary release and
repeat the same triple in the example file. Keep the shapes association as
`sh:suggestedShapesGraph` to the existing `/shacl` IRI. These metadata links do not
change validation targets or constraints. Supporting artifacts remain unversioned;
never retrofit discovery links into immutable historical vocabulary snapshots.


The 0.3.0 release tightens anatomical validation and therefore uses a new minor
version under the development versioning policy. Preserve the earlier release
snapshots. Regression checks cover root/direct/transitive paths, unknown values,
non-SNOMED IRIs, cycles, and exclusion of submitted subclass assertions.

Use the four vocabulary creators for the SHACL file and Pedro Paulo F. Barcelos
alone for the examples, identified by ORCID and name. Do not duplicate creators
as contributors unless recording a distinct contribution is needed. Keep comments
focused on usage and avoid release-specific wording for unchanged range axioms.
