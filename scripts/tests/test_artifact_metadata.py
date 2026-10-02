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

    def test_requested_attribution_and_persistent_links(self):
        vocabulary = URIRef(build.BASE)
        graph = Graph().parse(build.releases()[-1])
        creators = {URIRef('https://orcid.org/' + value) for value in (
            '0009-0002-3089-9558', '0000-0001-8306-0380',
            '0000-0003-0771-3516', '0000-0003-2736-7817')}
        self.assertEqual(set(graph.objects(vocabulary, DCTERMS.creator)), creators)
        self.assertFalse(list(graph.objects(vocabulary, DCTERMS.contributor)))
        self.assertEqual(graph.value(vocabulary, FOAF.homepage), URIRef(build.BASE + '/spec'))
        self.assertEqual(graph.value(vocabulary, build.SCHEMA.codeRepository), URIRef(build.BASE + '/git'))
        self.assertNotIn((URIRef('http://snomed.info/id/91723000'), RDF.type, OWL.Class), graph)
        shapes = Graph().parse(build.SHAPES)
        self.assertEqual(set(shapes.objects(URIRef(build.BASE + '/shacl'), DCTERMS.creator)), creators)
        for creator in creators:
            self.assertTrue(shapes.value(creator, FOAF.name))
        for path in build.EXAMPLES.glob('*.ttl'):
            example = Graph().parse(path)
            resource = URIRef(build.BASE + '/example/' + path.stem)
            pedro = URIRef('https://orcid.org/0000-0003-2736-7817')
            self.assertEqual(set(example.objects(resource, DCTERMS.creator)), {pedro})
            self.assertEqual(str(example.value(pedro, FOAF.name)), 'Pedro Paulo F. Barcelos')
