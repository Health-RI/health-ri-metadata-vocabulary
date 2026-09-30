import importlib.util
import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import BNode, Graph, Literal, RDF, URIRef
from rdflib.namespace import DCAT, SKOS

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class VocabularyTests(unittest.TestCase):
    def setUp(self):
        self.release = build.releases()[-1]
        self.shape = Graph().parse(self.release / 'health-ri-metadata-shapes.ttl')
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
            previous = release.name

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
