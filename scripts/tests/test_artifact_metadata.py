"""Discovery links describe supporting files without changing their data role."""
import unittest
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS, FOAF, OWL, SH, XSD
from test_vocabulary import build

VANN = Namespace('http://purl.org/vocab/vann/')


class ArtifactMetadataTests(unittest.TestCase):
    def test_supporting_documents_and_discovery_links(self):
        vocabulary = URIRef(build.BASE)
        graph = Graph().parse(build.releases()[-1])
        entries = [(path, URIRef(build.BASE + '/example/' + path.stem),
                    VANN.example, FOAF.Document) for path in build.EXAMPLES.glob('*.ttl')]
        entries.append((build.SHAPES, URIRef(build.BASE + '/shacl'),
                        SH.suggestedShapesGraph, OWL.Ontology))
        for path, resource, relationship, kind in entries:
            with self.subTest(file=path.name):
                support = Graph().parse(path)
                self.assertIn((vocabulary, relationship, resource), graph)
                self.assertIn((vocabulary, relationship, resource), support)
                self.assertIn((resource, RDF.type, kind), support)
                for predicate in (DCTERMS.title, DCTERMS.description, DCTERMS.identifier,
                                  DCTERMS.publisher, DCTERMS.license, DCTERMS.language,
                                  DCTERMS.modified, DCTERMS.references, FOAF.primaryTopic):
                    self.assertTrue(list(support.objects(resource, predicate)), predicate)
                self.assertEqual(support.value(resource, DCTERMS.format), Literal('text/turtle'))
                self.assertEqual(support.value(resource, DCTERMS.modified).datatype, XSD.date)
                self.assertNotIn((resource, OWL.imports, vocabulary), support)
                if kind == FOAF.Document:
                    self.assertNotIn((resource, RDF.type, build.DCAT.Dataset), support)
                    self.assertIn('Non-normative', str(support.value(resource, DCTERMS.description)))
