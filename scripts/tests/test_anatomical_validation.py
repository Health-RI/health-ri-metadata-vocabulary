"""Exercise range validation and the separation of submitted and trusted evidence."""
import importlib.util
import unittest
from rdflib import Graph, RDF, RDFS, URIRef
from rdflib.namespace import DCAT
from test_vocabulary import build

spec = importlib.util.spec_from_file_location('validate_metadata', build.ROOT / 'scripts/validate.py')
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


class TrustedHierarchyTests(unittest.TestCase):
    def setUp(self):
        self.data = Graph()
        self.hierarchy = Graph()
        self.dataset = URIRef('https://example.org/dataset')
        self.root = URIRef('http://snomed.info/id/91723000')
        self.lung = URIRef('http://snomed.info/id/39607008')
        self.data.add((self.dataset, RDF.type, DCAT.Dataset))

    def conforms(self, value):
        self.data.set((self.dataset, build.HRI.anatomicalLocationCovered, value))
        return validation.validate_metadata(self.data, self.hierarchy)[0]

    def test_root_and_direct_subclass(self):
        self.assertTrue(self.conforms(self.root))
        self.hierarchy.add((self.lung, RDFS.subClassOf, self.root))
        self.assertTrue(self.conforms(self.lung))

    def test_transitive_path(self):
        # Synthetic hierarchy edges test traversal, not clinical terminology facts.
        middle = URIRef('http://snomed.info/id/123456789')
        self.hierarchy.add((self.lung, RDFS.subClassOf, middle))
        self.hierarchy.add((middle, RDFS.subClassOf, self.root))
        self.assertTrue(self.conforms(self.lung))

    def test_missing_hierarchy_and_unknown_snomed_value_fail(self):
        self.assertFalse(self.conforms(self.lung))
        self.assertFalse(self.conforms(URIRef('http://snomed.info/id/999999999')))

    def test_submitted_or_inferred_subclass_does_not_supply_evidence(self):
        self.data.add((self.lung, RDFS.subClassOf, self.root))
        self.assertFalse(self.conforms(self.lung))

    def test_non_snomed_iri_rejected_even_with_path(self):
        other = URIRef('https://example.org/anatomy')
        self.hierarchy.add((other, RDFS.subClassOf, self.root))
        self.assertFalse(self.conforms(other))

    def test_unrelated_hierarchy_and_cycles_fail(self):
        other = URIRef('http://snomed.info/id/123456789')
        self.hierarchy.add((self.lung, RDFS.subClassOf, other))
        self.hierarchy.add((other, RDFS.subClassOf, self.lung))
        self.assertFalse(self.conforms(self.lung))
