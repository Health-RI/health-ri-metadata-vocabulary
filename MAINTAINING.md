# Maintaining the vocabulary

## Sources and release contract

`vocabulary/versioned/X.Y.Z/` is the authoritative source for each complete release.
It contains `health-ri-metadata-vocabulary.ttl`, `health-ri-metadata-shapes.ttl`, and
`example.ttl`. All terms in the vocabulary belong to the same release; term IRIs
are stable and unversioned. Shapes and examples accompany that release.

Release source files and published `docs/versioned/X.Y.Z/index.html` snapshots are
immutable. Never edit or delete a published snapshot, even to correct a typo.
Create a new complete release. The workflow compares against its base commit and
fails if existing snapshots have changed. This is a CI safeguard, not a substitute
for repository branch protection or access control.

`vocabulary/latest/`, `docs/latest/`, and `CITATION.cff` are generated/current files.
The Pages `site/` directory is disposable output. Do not edit generated files by hand.
There is no second authoritative source tree that can drift from release sources.

## Semantic Versioning

The public interface comprises term IRIs, their documented meaning, RDF/OWL axioms,
and accompanying validation constraints. The vocabulary follows
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

- At `1.0.0` and above: incompatible changes require a major version; compatible
  additions require a minor version; compatible corrections require a patch.
- During `0.y.z` development, stability is not promised. Use a new minor version
  for breaking semantic or validation changes and a patch for compatible corrections.
- Do not silently change the meaning of a published term; explain compatibility
  implications in the changelog and assess whether a different term is necessary.
- Repository-only tooling changes do not require a vocabulary release unless they
  alter the published vocabulary or its release contract.

The publication pipeline accepts numeric `X.Y.Z` releases (including `0.1.0`).
SemVer prerelease/build suffixes are not published by this pipeline. Draft work
stays on branches until ready for a numbered release.

## Add a release

1. Copy the previous complete release directory to a new `X.Y.Z` directory.
2. Edit the new vocabulary. Update `owl:versionInfo`, `dcat:version`,
   `owl:versionIRI`, `dcterms:modified`, the version-specific documentation link,
   and the bibliographic citation. Preserve the vocabulary's original issued date.
   Set `owl:priorVersion` to the preceding version IRI. Update shapes/example as needed.
3. Add a dated vocabulary-level entry to `CHANGELOG.md` using Keep a Changelog
   categories. Include any breaking semantics or validation effects explicitly.
4. Run the README validation commands and review both RDF and generated HTML.
5. Commit the new release and changelog to `main` (or merge a reviewed branch).

Adding the complete release directory is sufficient to trigger generation and
publication; no hard-coded current-version configuration needs changing. The
highest version is selected numerically, not by modification date or string order.
All historical snapshots remain available. The workflow commits generated
latest/HTML/citation files using `GITHUB_TOKEN`, which does not recursively trigger
another push workflow. The same run uploads the site for Pages deployment.

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

The official site will be `https://health-ri.github.io/health-ri-metadata-vocabulary/`.
The w3id redirects are maintained separately; their adoption is not performed by
this repository. Until they are installed, use the repository files directly.

## Dependencies and review

`requirements.txt` pins the full tested Python environment, including transitive
dependencies. Use Python 3.12. Action dependencies are pinned to commit SHAs with
release labels in comments. Upgrade deliberately, run all checks, and inspect
newly generated documentation before accepting upgrades. Past HTML snapshots are
preserved when the generator changes.

Tests cover release metadata, IRI-only values, explicit Concept typing,
subject typing, optionality, and multiple values. Review the clinical meaning and
external identifiers separately; syntax validation cannot establish those facts.
