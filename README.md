# Health-RI Metadata Vocabulary

Health-RI-specific RDF terms for describing health datasets at metadata and catalogue
level. This vocabulary complements reused standards; it is not a complete metadata
schema, a disease terminology, or the broader Semantic Interoperability Initiative.

| Item | Value |
| --- | --- |
| Preferred prefix | `hri` |
| Namespace | `https://w3id.org/health-ri/metadata-vocabulary#` |
| Vocabulary IRI | `https://w3id.org/health-ri/metadata-vocabulary` |
| Versioning | Whole-vocabulary Semantic Versioning, current release `0.4.1` |
| License | [CC BY 4.0](LICENSE) |
| Official repository | [Health-RI/health-ri-metadata-vocabulary](https://github.com/Health-RI/health-ri-metadata-vocabulary) |
| Official documentation | [GitHub Pages](https://health-ri.github.io/health-ri-metadata-vocabulary/) |

The official publication and w3id links become live after the implementation is
merged into the official repository, Pages is enabled, and the separate w3id
configuration is accepted. A fork is a staging location, not a canonical namespace.

## Normative status

For each release, the versioned vocabulary Turtle file is the sole normative specification of the Health-RI Metadata Vocabulary. The accompanying examples, SHACL shapes, and generated HTML documentation are non-normative supporting resources. They illustrate usage and provide suggested validation checks; they do not introduce or override vocabulary requirements. In case of discrepancy, the versioned vocabulary Turtle file takes precedence.

The `vocabulary/latest/` Turtle file is a copy of the latest versioned vocabulary.
Applying the supporting SHACL shapes is optional unless a separate application
profile requires them. Validation reports describe conformance to those shapes;
they are not a complete assessment of conformity to the vocabulary.

## Access

- [Latest Turtle vocabulary](vocabulary/latest/health-ri-metadata-vocabulary.ttl)
- [Versioned Turtle and archived HTML](vocabulary/versioned/)
- [Latest PyLODE HTML](vocabulary/latest/index.html)
- [SHACL validation](validation/health-ri-metadata-shapes.ttl)
- [Health-condition example](examples/health-condition-of-interest.ttl)
- [Anatomical-coverage example](examples/anatomical-location-covered.ttl)
- [Changelog](CHANGELOG.md), [citation metadata](CITATION.cff), and [maintenance](MAINTAINING.md)

## Health condition of interest

`hri:healthConditionOfInterest` relates a dataset to an identified concept representing
a disease, disorder, or clinical condition that the dataset as a whole concerns at
metadata or catalogue level.

It is an `owl:ObjectProperty` with `rdfs:domain dcat:Dataset` and
`rdfs:range skos:Concept`. These axioms entail typing; they are not data-validation
constraints. When used, the separate non-normative SHACL shape requires a Dataset subject and IRI-valued
Concept objects with SNOMED CT or WHO ICD-10 identifier patterns. No minimum or
maximum count is imposed (`0..*`). No new clinical class is introduced.

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
Values must identify suitable SNOMED CT or ICD-10 concepts. Since `0.4.0`, SHACL
checks the SNOMED CT or WHO ICD-10 identifier format, with an optional release year
for ICD-10. This lightweight check does not verify existence, activity status, or
clinical suitability; invented identifiers matching the patterns also pass. The example is not a complete HealthDCAT-AP record.

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

## Anatomical location covered

Introduced in `0.2.0` and revised in `0.2.1`, `hri:anatomicalLocationCovered`
relates a dataset to an anatomical class describing its aggregate anatomical coverage.
Use is optional and repeatable (`0..*`). It does not pair a body site with a
particular modality, data category, sample, or record within a mixed dataset.

Since version `0.2.1`, the vocabulary uses this **OWL Full / RDF-Based Semantics** range:

```turtle
@prefix hri: <https://w3id.org/health-ri/metadata-vocabulary#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sct: <http://snomed.info/id/> .

hri:anatomicalLocationCovered a owl:ObjectProperty ;
    rdfs:domain dcat:Dataset ;
    rdfs:range [
        a owl:Restriction ;
        owl:onProperty rdfs:subClassOf ;
        owl:hasValue sct:91723000
    ] .

```

Every linked value is thereby a subclass of **91723000 |Anatomical structure
(body structure)|**. Subclass transitivity and reflexivity include indirect subclasses
and the root itself. The restriction operates on `rdfs:subClassOf`, so this pattern
is **outside OWL 2 DL**. See the [OWL 2 RDF-Based Semantics](https://www.w3.org/TR/owl2-rdf-based-semantics/)
and [SNOMED anatomical-structure model](https://docs.snomed.org/snomed-ct-specifications/snomed-ct-editorial-guide/readme/authoring/domain-specific-modeling/body-structure/body-structure-attributes-summary).

Use SNOMED anatomical class IRIs for the intended terminology binding. The
[example](examples/anatomical-location-covered.ttl) links directly to
`http://snomed.info/id/39607008` (Lung structure), typed as `owl:Class`.
It includes the subsumption assertion for readability; the range axiom also entails
that assertion. It does not assert immediate parenthood or type the value as an
individual anatomical structure. **No `skos:Concept` typing is required.**

This is a semantic assertion, not terminology validation: an inappropriate value
also acquires the subclass relationship. The axiom does not restrict identifier
namespaces, verify active status, or establish that SNOMED itself asserts the
relationship. Checking authoritative membership requires a separate terminology
lookup or validation process. From `0.3.0`, the accompanying non-normative SHACL shape requires
Dataset subjects, SNOMED CT IRIs, and a zero-or-more-step `rdfs:subClassOf` path
to Anatomical structure. This accepts the root, direct subclasses, and indirect
subclasses. Missing hierarchy evidence causes validation to fail for non-root
values. The original OWL Full range restriction is retained.

The explicit `sct:91723000 a owl:Class` declaration is no longer repeated in the
vocabulary; the external term is referenced in the restriction without locally
redeclaring it. This does not remove the class semantics entailed by use of
`rdfs:subClassOf`.

The term supersedes the R-U-03 `eucaim:hasBodySite` / `eucaim:BP1000024` proposal
without asserting a formal mapping. The `0.2.1` change replaces the earlier
`skos:Concept` range and SHACL hierarchy checks. It changes formal semantics and
validation expectations; the patch number was explicitly selected by the
maintainers and should not be interpreted as a compatibility guarantee.
The `0.2.1` release left the health-condition property unchanged; `0.4.0` narrows
its documented terminology binding and adds identifier-pattern validation.

## Local validation and documentation

Use Python 3.12 in a virtual environment:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/build.py
python -m unittest discover -s scripts/tests -v
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

For anatomical validation against terminology evidence, run:

```sh
python scripts/validate.py metadata.ttl --snomed-hierarchy trusted-snomed-hierarchy.ttl
```

The hierarchy input must be a trusted RDF export from the SNOMED CT edition and
release selected by the validator operator. It must contain named-class
`rdfs:subClassOf` edges sufficient to reach `http://snomed.info/id/91723000`.
A complete relevant hierarchy or a complete subset covering the submitted values
is suitable. An RF2 distribution or an OWL axiom export is not directly equivalent
to this input: prepare the named-class hierarchy first. Record the edition,
release date, and export provenance with the validation results.

The command removes submitted `rdfs:subClassOf` statements and copies subclass
edges only from that separate trusted input. It performs no vocabulary imports or
OWL/RDFS inference. Thus a subclass assertion supplied by the metadata author,
or produced from the vocabulary's range axiom, cannot itself make a value pass.
The operator is responsible for the trustworthiness of the hierarchy file; the
command cannot authenticate its source or detect invented facts in that file.
This checks hierarchy membership, not concept activity status or clinical
appropriateness. The root itself is permitted without a subclass edge.

Supply the original metadata, before inference. Health-condition values still
require `skos:Concept` typing in the metadata; anatomical values do not.
The command returns exit code 0 for conformance, 1 for violations, and 2 for
input or execution errors.

The build's example check uses the illustrative subclass assertion inside the
anatomical example as an offline fixture. It checks that the example and shapes
work together; it is not independent SNOMED verification. A generic SHACL engine
can use the shapes directly, but only checks the graph it is given: use the
separate-input command above when submitted hierarchy claims must not be trusted.

## Attribution and provenance

Cite the specific whole-vocabulary version using [CITATION.cff](CITATION.cff).
The authors are [Ana Konrad](https://orcid.org/0009-0002-3089-9558),
[Hannah Neikes](https://orcid.org/0000-0001-8306-0380),
[Niek van Ulzen](https://orcid.org/0000-0003-0771-3516), and
[Pedro Paulo F. Barcelos](https://orcid.org/0000-0003-2736-7817).
Health-RI is the publisher. The four authors are creators of the vocabulary and
the SHACL file. Pedro Paulo F. Barcelos is the sole creator of both usage examples.
Each creator is identified by ORCID and name. Duplicate contributor assertions
were removed from the current vocabulary; past releases retain their metadata.

The release infrastructure is informed by the
[Health-RI Mapping Vocabulary](https://github.com/Health-RI/semantic-interoperability/tree/main/vocabulary)
and its latest/versioned and PyLODE patterns. The scripts here are a separate,
smaller implementation. Metadata design uses OWL, Dublin Core, DCAT, VANN, FOAF,
SKOS, MOD, and Schema.org. `owl:imports` references the SKOS ontology because the
health-condition property uses `skos:Concept` and both properties use SKOS annotations. It does not import the Semantic
Interoperability Initiative's semiotics ontology. The local validation checks do
not fetch imports or infer types before checking the examples.
All original repository content is licensed under CC BY 4.0. External terminology
references and third-party dependencies retain their own licensing conditions.

The SHACL file is a small, separate application-validation artifact: OWL/RDFS range
axioms cannot enforce IRI-only values, while `sh:nodeKind sh:IRI` rejects blank nodes
and literals. It is not a second vocabulary or a replacement for the full Health-RI
Metadata Schema. The examples are executable illustrations and validation fixtures.
These supporting artifacts are updated when usage or validation changes; they do
not need per-version copies.


## Discovering examples and validation shapes

From version `0.2.2`, the vocabulary links to its two usage examples with
[`vann:example`](https://vocab.org/vann/#example), and to the suggested shapes
with [`sh:suggestedShapesGraph`](https://www.w3.org/ns/shacl#suggestedShapesGraph).
Each supporting Turtle file repeats the same vocabulary-to-artifact statement;
this is the same relationship in another document, not an inverse property.

- Vocabulary IRI: `https://w3id.org/health-ri/metadata-vocabulary` (no trailing slash).
- Example IRIs: `https://w3id.org/health-ri/metadata-vocabulary/example/health-condition-of-interest`
  and `https://w3id.org/health-ri/metadata-vocabulary/example/anatomical-location-covered`.
- Shapes IRI: `https://w3id.org/health-ri/metadata-vocabulary/shacl` (the existing redirect).

Examples describe themselves as `foaf:Document` and explicitly state their
non-normative, incomplete-record status. The shapes graph is identified as
`owl:Ontology`, consistent with the declared range of `sh:suggestedShapesGraph`;
this does not make it normative or create another set of domain terms.

Supporting files include a title, description, identifier, publisher, license,
language, Turtle format, modification date, primary topic, repository link, and
reference to the vocabulary version they accompany. Their metadata describes the
supporting artifact, not the fictional dataset illustrated inside it. Original
creation dates are not inferred. Creator attribution follows the explicit
assignments described above.

`sh:suggestedShapesGraph` is defined in the W3C SHACL vocabulary as an extension;
it was not documented in the body of the 2017 Recommendation. It is a discovery
hint, not a guarantee that validators automatically fetch or apply the shapes.
Our validation commands continue to supply the shapes explicitly. No
`owl:imports` dependency is added for these links.

Example and shapes IRIs refer to mutable supporting files; `dcterms:references`
records the vocabulary release they currently accompany. Historical vocabulary
snapshots remain unchanged. The proposed w3id rules support these addresses;
until those rules are deployed, open the repository files directly.


The example IRI identifies an RDF document, so `foaf:Document` is appropriate.
Its `foaf:primaryTopic` identifies the vocabulary property demonstrated by that
document, not the fictional dataset inside it. The shapes graph uses
`owl:Ontology` as graph-level metadata, matching the declared range of
`sh:suggestedShapesGraph`; it is not an assertion that the constraints are OWL
axioms or that the file defines a second domain ontology.

The vocabulary's `foaf:homepage` and `schema:codeRepository` use the `/spec` and
`/git` PIDs. Health-RI's organizational homepage remains `https://www.health-ri.nl/`:
`https://w3id.org/health-ri` already identifies the publisher organization in this
RDF. Using it as its own `foaf:homepage` would also type that same resource as a
FOAF Document, which FOAF declares disjoint with Organization. A document PID and
an organization PID should identify distinct resources.


## Release consistency checks

The publication build uses the highest numerically numbered versioned Turtle file
as its source of truth. After generation it verifies the latest Turtle, latest
HTML's explicit version fields, and `CITATION.cff` version, release date, and URL.

Before generating outputs, the build requires every example's document-level
`dcterms:references` and the shapes graph's corresponding reference to identify
that same vocabulary release. Missing, outdated, or conflicting vocabulary release
references stop publication with a compatibility-review message. These references
are not automatically rewritten: review the examples and shapes, then update
their references explicitly. They identify the release the files accompany, not
independent versions of the supporting files. The normal example SHACL checks
also run; they do not replace the compatibility review.
