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
        for iri in ('https://example.org/condition/a', 'https://example.org/condition/b'):
            value = URIRef(iri)
            self.graph.add((self.dataset, self.term, value))
            self.graph.add((value, RDF.type, SKOS.Concept))
        self.assertTrue(self.conforms())

    def test_literal_rejected(self):
        self.graph.add((self.dataset, self.term, Literal('condition')))
        self.assertFalse(self.conforms())

    def test_blank_concept_rejected(self):
        value = BNode()
        self.graph.add((self.dataset, self.term, value))
        self.graph.add((value, RDF.type, SKOS.Concept))
        self.assertFalse(self.conforms())

    def test_untyped_iri_rejected(self):
        self.graph.add((self.dataset, self.term, URIRef('https://example.org/condition')))
        self.assertFalse(self.conforms())

    def test_untyped_subject_rejected(self):
        self.graph.remove((self.dataset, RDF.type, DCAT.Dataset))
        value = URIRef('https://example.org/condition')
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

    def test_root_and_multiple_values(self):
        self.add_value(self.root)
        self.add_value(self.lung)
        self.graph.add((self.lung, RDFS.subClassOf, self.root))
        self.assertTrue(self.conforms())

    def test_transitive_descendant(self):
        # Synthetic path only: these test identifiers are not terminology assertions.
        leaf = URIRef('http://snomed.info/id/999999001')
        middle = URIRef('http://snomed.info/id/999999002')
        self.add_value(leaf)
        self.graph.add((leaf, RDFS.subClassOf, middle))
        self.graph.add((middle, RDFS.subClassOf, self.root))
        self.assertTrue(self.conforms())

    def test_missing_hierarchy_evidence_rejected(self):
        self.add_value(self.lung)
        self.assertFalse(self.conforms())

    def test_body_structure_and_disease_rejected(self):
        for code in ('123037004', '22298006'):
            with self.subTest(code=code):
                value = URIRef('http://snomed.info/id/' + code)
                self.add_value(value)
                self.assertFalse(self.conforms())
                self.graph.remove((self.dataset, self.term, value))

    def test_wrong_namespace_rejected_even_with_path(self):
        value = URIRef('https://example.org/anatomy')
        self.add_value(value)
        self.graph.add((value, RDFS.subClassOf, self.root))
        self.assertFalse(self.conforms())

    def test_anatomical_instance_is_not_subclass_evidence(self):
        self.add_value(self.lung)
        self.graph.add((self.lung, RDF.type, self.root))
        self.assertFalse(self.conforms())

    def test_untyped_concept_and_dataset_rejected(self):
        self.graph.add((self.dataset, self.term, self.root))
        self.assertFalse(self.conforms())
        self.graph.add((self.root, RDF.type, SKOS.Concept))
        self.graph.remove((self.dataset, RDF.type, DCAT.Dataset))
        self.assertFalse(self.conforms())

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
