# Health-RI Metadata Vocabulary

Health-RI-specific RDF terms for describing health datasets at metadata and catalogue
level. This vocabulary complements reused standards; it is not a complete metadata
schema, a disease terminology, or the broader Semantic Interoperability Initiative.

| Item | Value |
| --- | --- |
| Preferred prefix | `hri` |
| Namespace | `https://w3id.org/health-ri/metadata-vocabulary#` |
| Vocabulary IRI | `https://w3id.org/health-ri/metadata-vocabulary` |
| Versioning | Whole-vocabulary Semantic Versioning, initially `0.1.0` |
| License | [CC BY 4.0](LICENSE) |
| Official repository | [Health-RI/health-ri-metadata-vocabulary](https://github.com/Health-RI/health-ri-metadata-vocabulary) |
| Official documentation | [GitHub Pages](https://health-ri.github.io/health-ri-metadata-vocabulary/) |

The official publication and w3id links become live after the implementation is
merged into the official repository, Pages is enabled, and the separate w3id
configuration is accepted. A fork is a staging location, not a canonical namespace.

## Access

- [Latest Turtle vocabulary](vocabulary/latest/health-ri-metadata-vocabulary.ttl)
- [Versioned Turtle and archived HTML](vocabulary/versioned/)
- [Latest PyLODE HTML](vocabulary/latest/index.html)
- [SHACL validation](validation/health-ri-metadata-shapes.ttl)
- [Turtle usage example](examples/health-condition-of-interest.ttl)
- [Changelog](CHANGELOG.md), [citation metadata](CITATION.cff), and [maintenance](MAINTAINING.md)

## Health condition of interest

`hri:healthConditionOfInterest` relates a dataset to an identified concept representing
a disease, disorder, or clinical condition that the dataset as a whole concerns at
metadata or catalogue level.

It is an `owl:ObjectProperty` with `rdfs:domain dcat:Dataset` and
`rdfs:range skos:Concept`. These axioms entail typing; they are not data-validation
constraints. The separate SHACL shape requires a Dataset subject and IRI-valued
Concept objects. No minimum or maximum count is imposed (`0..*`). No new clinical
class or closed terminology list is introduced.

```turtle
@prefix hri: <https://w3id.org/health-ri/metadata-vocabulary#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<https://example.org/dataset/1> a dcat:Dataset ;
    hri:healthConditionOfInterest <http://snomed.info/id/22298006> .
<http://snomed.info/id/22298006> a skos:Concept .
```

This describes dataset-level aboutness. It does not assert diagnoses for individual
patients, records, samples, or observations, or enumerate all diagnoses in the data.
SNOMED CT, ICD-10, ICD-11, and other appropriate clinical concept systems may supply
values where an IRI identifies the intended concept. No particular identifier
pattern is mandated. The example is not a complete HealthDCAT-AP record.

The Concept typing is the Health-RI metadata convention; it does not claim that
external terminology publishers natively use SKOS. Where an external IRI is also an
OWL class, its use here is as a concept individual (OWL 2 punning when applicable),
not as an assertion that the dataset has an instance of that disease class.
SHACL cannot determine clinical appropriateness merely from an IRI and Concept type;
that remains a semantic review responsibility.

The term replaces the previously proposed SIO `SIO_000332` solution for requirement
R-U-04. No equivalence, subproperty, or SKOS mapping is asserted. Historical
replacement alone does not establish a formal semantic relationship, and SIO's
additional entailments have not been adopted here.

## Local validation and documentation

Use Python 3.12 in a virtual environment:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python -m unittest discover -s scripts/tests -v
python scripts/build.py
cffconvert --validate
python -m http.server --directory vocabulary/latest 8000
```

The build reads `vocabulary/versioned/health-ri-metadata-vocabulary-vX.Y.Z.ttl`,
selects the highest numeric `X.Y.Z` version, and copies it to
`vocabulary/latest/health-ri-metadata-vocabulary.ttl`. PyLODE creates the matching
versioned `.html` snapshot and copies it to `vocabulary/latest/index.html`.
Pages publishes the latest directory directly: the site URL opens the current
specification, and archived HTML remains in GitHub rather than on Pages.
No separate tracked `docs` directory or generated `site` copy is needed.
On Windows, activate with
`.venv\Scripts\Activate.ps1` in PowerShell.

To validate metadata data independently, load the SHACL file with the data graph,
without importing the vocabulary's domain/range axioms or enabling inference.
Supply the Concept types in that graph (or an explicitly provided terminology graph).
Otherwise inference may supply missing types before validation. The example and
tests use explicit typing and no inference.

## Attribution and provenance

Cite the specific whole-vocabulary version using [CITATION.cff](CITATION.cff).
The authors are [Ana Konrad](https://orcid.org/0009-0002-3089-9558),
[Hannah Neikes](https://orcid.org/0000-0001-8306-0380),
[Niek van Ulzen](https://orcid.org/0000-0003-0771-3516), and
[Pedro Paulo F. Barcelos](https://orcid.org/0000-0003-2736-7817).
Health-RI is the publisher. Authors are recorded as both creators and contributors;
this does not imply an additional set of contributors.

The release infrastructure is informed by the
[Health-RI Mapping Vocabulary](https://github.com/Health-RI/semantic-interoperability/tree/main/vocabulary)
and its latest/versioned and PyLODE patterns. The scripts here are a separate,
smaller implementation. Metadata design uses OWL, Dublin Core, DCAT, VANN, FOAF,
SKOS, MOD, and Schema.org. `owl:imports` references the SKOS ontology because the
property uses `skos:Concept` and SKOS annotations. It does not import the Semantic
Interoperability Initiative's semiotics ontology. The local validation checks do
not fetch imports or infer types before checking the example.
All original repository content is licensed under CC BY 4.0. External terminology
references and third-party dependencies retain their own licensing conditions.

The SHACL file is a small, separate application-validation artifact: OWL/RDFS range
axioms cannot enforce IRI-only values, while `sh:nodeKind sh:IRI` rejects blank nodes
and literals. It is not a second vocabulary or a replacement for the full Health-RI
Metadata Schema. The example is an executable illustration and validation fixture.
Neither file needs to be copied or added when releasing a new vocabulary version.
