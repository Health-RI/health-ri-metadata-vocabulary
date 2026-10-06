import importlib.util
import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import BNode, Graph, Literal, RDF, RDFS, URIRef
from rdflib.namespace import DCAT, SKOS, DCTERMS, OWL

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class VocabularyTests(unittest.TestCase):
    def setUp(self):
        self.release = build.releases()[-1]
        self.shape = Graph().parse(build.SHAPES)
        self.graph = Graph()
        self.dataset = URIRef('https://example.org/dataset')
        self.graph.add((self.dataset, RDF.type, DCAT.Dataset))
        self.term = build.HRI.healthConditionOfInterest

    def conforms(self):
        return validate(self.graph, shacl_graph=self.shape, inference='none')[0]

    def test_release_metadata(self):
        previous = None
        for release in build.releases():
            build.validate_release(release, previous)
            previous = build.version_of(release)

    def test_initial_authors_and_requested_metadata(self):
        graph = Graph().parse(ROOT / f'vocabulary/versioned/{build.STEM}-v0.1.0.ttl')
        vocabulary = URIRef(build.BASE)
        authors = {URIRef('https://orcid.org/' + identifier) for identifier in (
            '0009-0002-3089-9558', '0000-0001-8306-0380',
            '0000-0003-0771-3516', '0000-0003-2736-7817')}
        self.assertEqual(set(graph.objects(vocabulary, DCTERMS.creator)), authors)
        self.assertEqual(set(graph.objects(vocabulary, DCTERMS.contributor)), authors)
        for predicate in (DCTERMS.abstract, DCTERMS.identifier, DCAT.landingPage,
                          URIRef('http://xmlns.com/foaf/0.1/logo'),
                          URIRef('https://w3id.org/mod#repository'), OWL.imports):
            self.assertTrue(list(graph.objects(vocabulary, predicate)))

    def test_optional(self):
        self.assertTrue(self.conforms())

    def test_multiple_values(self):
        for iri in ('http://snomed.info/id/22298006',
                    'http://id.who.int/icd/release/10/2019/I21',
                    'http://www.orpha.net/ORDO/Orphanet_558'):
            value = URIRef(iri)
            self.graph.add((self.dataset, self.term, value))
            self.graph.add((value, RDF.type, SKOS.Concept))
        self.assertTrue(self.conforms())

    def test_condition_identifier_patterns(self):
        cases = {
            'http://snomed.info/id/22298006': True,
            'http://id.who.int/icd/release/10/I21': True,
            'http://id.who.int/icd/release/10/2019/I21.0': True,
            'http://id.who.int/icd/release/10/2019/I20-I25': True,
            'http://id.who.int/icd/release/10/2019/IX': True,
            'http://www.orpha.net/ORDO/Orphanet_558': True,
            # Format-only validation intentionally accepts invented identifiers.
            'http://snomed.info/id/999999999999999999': True,
            'http://www.orpha.net/ORDO/Orphanet_999999999': True,
            'https://example.org/condition': False,
            'http://snomed.info/id/not-a-number': False,
            'http://snomed.info/id/22298006/extra': False,
            'http://id.who.int/icd/entity/123': False,
            'http://id.who.int/icd/release/11/2026-01/mms/123': False,
            'http://id.who.int/icd/release/10/': False,
            'http://id.who.int/icd/release/10/2019/I21/extra': False,
            'https://www.orpha.net/ORDO/Orphanet_558': False,
            'http://www.orpha.net/ORDO/558': False,
            'http://www.orpha.net/ORDO/Orphanet_not-a-number': False,
        }
        for iri, expected in cases.items():
            with self.subTest(iri=iri):
                value = URIRef(iri)
                self.graph.add((self.dataset, self.term, value))
                self.graph.add((value, RDF.type, SKOS.Concept))
                self.assertEqual(self.conforms(), expected)
                self.graph.remove((self.dataset, self.term, value))

    def test_health_condition_example_covers_supported_terminologies(self):
        example = Graph().parse(build.EXAMPLES / 'health-condition-of-interest.ttl')
        values = set(example.objects(None, self.term))
        self.assertEqual(values, {
            URIRef('http://snomed.info/id/22298006'),
            URIRef('http://id.who.int/icd/release/10/2019/I21'),
            URIRef('http://www.orpha.net/ORDO/Orphanet_558'),
        })

    def test_literal_rejected(self):
        self.graph.add((self.dataset, self.term, Literal('condition')))
        self.assertFalse(self.conforms())

    def test_blank_concept_rejected(self):
        value = BNode()
        self.graph.add((self.dataset, self.term, value))
        self.graph.add((value, RDF.type, SKOS.Concept))
        self.assertFalse(self.conforms())

    def test_untyped_iri_rejected(self):
        self.graph.add((self.dataset, self.term, URIRef('http://snomed.info/id/22298006')))
        self.assertFalse(self.conforms())

    def test_untyped_subject_rejected(self):
        self.graph.remove((self.dataset, RDF.type, DCAT.Dataset))
        value = URIRef('http://snomed.info/id/22298006')
        self.graph.add((self.dataset, self.term, value))
        self.graph.add((value, RDF.type, SKOS.Concept))
        self.assertFalse(self.conforms())



class AnatomicalTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.shapes = Graph().parse(build.SHAPES)
        self.dataset = URIRef('https://example.org/dataset/anatomy')
        self.term = build.HRI.anatomicalLocationCovered
        self.root = URIRef('http://snomed.info/id/91723000')
        self.lung = URIRef('http://snomed.info/id/39607008')
        self.graph.add((self.dataset, RDF.type, DCAT.Dataset))

    def add_value(self, value):
        self.graph.add((self.dataset, self.term, value))
        self.graph.add((value, RDF.type, SKOS.Concept))

    def conforms(self):
        return validate(self.graph, shacl_graph=self.shapes, inference='none')[0]

    def test_latest_has_no_formal_anatomical_range(self):
        graph = Graph().parse(build.releases()[-1])
        self.assertFalse(list(graph.objects(self.term, RDFS.range)))

    def test_unverified_class_rejected(self):
        value = URIRef('https://example.org/unverified-class')
        self.graph.add((self.dataset, self.term, value))
        self.assertFalse(self.conforms())

    def test_untyped_dataset_rejected(self):
        self.graph.add((self.dataset, self.term, self.lung))
        self.graph.remove((self.dataset, RDF.type, DCAT.Dataset))
        self.assertFalse(self.conforms())

    def test_property_use_does_not_entail_anatomical_subclass(self):
        from owlrl import DeductiveClosure, RDFS_OWLRL_Semantics
        graph = Graph().parse(build.releases()[-1])
        values = (self.lung, URIRef('https://example.org/unverified-class'))
        for value in values:
            graph.add((self.dataset, self.term, value))
        DeductiveClosure(RDFS_OWLRL_Semantics).expand(graph)
        for value in values:
            self.assertNotIn((value, RDFS.subClassOf, self.root), graph)

    def test_literal_and_blank_values_rejected(self):
        for value in (Literal('91723000'), BNode()):
            with self.subTest(value=value):
                self.graph.add((self.dataset, self.term, value))
                self.assertFalse(self.conforms())
                self.graph.remove((self.dataset, self.term, value))

    def test_previous_term_unchanged_and_two_terms_in_02(self):
        old = Graph().parse(ROOT / f'vocabulary/versioned/{build.STEM}-v0.1.0.ttl')
        new = Graph().parse(ROOT / f'vocabulary/versioned/{build.STEM}-v0.2.0.ttl')
        term = build.HRI.healthConditionOfInterest
        self.assertEqual(set(old.predicate_objects(term)), set(new.predicate_objects(term)))
        self.assertEqual({s for s in new.subjects() if str(s).startswith(build.BASE + '#')},
                         {term, self.term})


if __name__ == '__main__':
    unittest.main()
