import importlib.util
import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import BNode, Graph, Literal, RDF, URIRef
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


if __name__ == '__main__':
    unittest.main()
