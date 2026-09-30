# Maintaining the vocabulary

## Sources and release contract

Authoritative releases are flat files:
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

The SHACL file in `validation/` and example in `examples/` are supporting artifacts,
not additional release inputs. They provide the IRI-only data check and a runnable
usage example. Adding one new versioned vocabulary Turtle file is sufficient for
the publication pipeline; no versioned copies of these support files are required.

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

1. Copy the previous vocabulary TTL to
   `vocabulary/versioned/health-ri-metadata-vocabulary-vX.Y.Z.ttl`.
2. Edit the new vocabulary. Update `owl:versionInfo`, `dcat:version`,
   `owl:versionIRI`, `dcterms:modified`, the version-specific documentation link,
   and the bibliographic citation. Preserve the vocabulary's original issued date.
   Set `owl:priorVersion` to the preceding version IRI. Update the separate
   shape/example only if the accompanying validation or usage guidance changes.
3. Add a dated vocabulary-level entry to `CHANGELOG.md` using Keep a Changelog
   categories. Include any breaking semantics or validation effects explicitly.
4. Run the README validation commands and review both RDF and generated HTML.
5. Commit the new release and changelog to `main` (or merge a reviewed branch).

Adding the new versioned TTL file is sufficient to trigger generation and
publication; no hard-coded current-version configuration needs changing. The
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
subject typing, optionality, and multiple values. Review the clinical meaning and
external identifiers separately; syntax validation cannot establish those facts.
