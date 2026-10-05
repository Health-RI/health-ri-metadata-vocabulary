"""Render source-driven property fields without changing vocabulary semantics."""
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup
from pylode.profiles.ontpub import OntPub
from rdflib import Graph
from rdflib.namespace import FOAF, RDFS, SKOS

from test_vocabulary import build


class DocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = '''
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ex: <https://example.org/future#> .
<https://example.org/future> a owl:Ontology ;
    dct:title "Future vocabulary" ;
    foaf:logo <https://example.org/logo.png> .
ex:futureProperty a owl:ObjectProperty ;
    rdfs:label "future property" ;
    rdfs:isDefinedBy <https://example.org/future> ;
    skos:definition "A source-driven definition."@en ;
    rdfs:comment "Independent description." ;
    skos:scopeNote "Independent scope." ;
    skos:example "Long example with https://example.org/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" .
ex:withoutDefinition a owl:DatatypeProperty ;
    rdfs:label "without definition" ;
    rdfs:isDefinedBy <https://example.org/future> ;
    rdfs:comment "Description is not a definition." .
ex:withoutDefinedBy a owl:ObjectProperty ;
    rdfs:label "without defined by" ;
    skos:definition "Definition without an Is Defined By row." ;
    rdfs:comment "Description remains present." .
ex:multilingual a owl:AnnotationProperty ;
    rdfs:label "multilingual" ;
    rdfs:isDefinedBy <https://example.org/future> ;
    skos:definition "<not-markup> & a definition."@en, "Een definitie."@nl .
'''
        cls.raw_html = OntPub(Graph().parse(data=cls.source, format='turtle')).make_html()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source_file = Path(self.tmp.name) / 'future.ttl'
        self.html = Path(self.tmp.name) / 'future.html'
        self.source_file.write_text(self.source)
        self.html.write_text(self.raw_html)
        build.customize_documentation(self.html, self.source_file)
        self.soup = BeautifulSoup(self.html.read_text(), 'html.parser')

    def table(self, name):
        for entity in self.soup.select('.property.entity'):
            table = entity.find('table')
            if table.select_one('tr td code').get_text(strip=True) == 'https://example.org/future#' + name:
                return table
        self.fail('Property documentation not found: ' + name)

    def test_logo_uses_source_and_precedes_title_without_metadata_url(self):
        metadata = self.soup.select_one('#metadata')
        image = metadata.find('img')
        self.assertEqual(image['src'], 'https://example.org/logo.png')
        self.assertEqual(image['alt'], 'Health-RI Logo')
        self.assertIs(metadata.find('h1').find_previous('img'), image)
        self.assertFalse(metadata.select(f'dt a[href="{FOAF.logo}"]'))
        self.assertNotIn('https://example.org/logo.png', metadata.get_text())
        self.assertEqual(self.source_file.read_text(), self.source)

    def test_definition_matches_rdf_and_follows_defined_by_before_description(self):
        table = self.table('futureProperty')
        labels = [row.th.get_text(strip=True) for row in table.find_all('tr')]
        self.assertEqual(labels[:6], ['IRI', 'Is Defined By', 'Definition',
                                     'Description', 'Scope Note', 'Example'])
        definition = table.find('a', href=str(SKOS.definition)).find_parent('tr').td
        self.assertEqual(definition.get_text(strip=True), 'A source-driven definition.')
        self.assertEqual(definition.p['lang'], 'en')
        self.assertIn('Independent description.', table.get_text())
        self.assertEqual(len(table.find_all('a', href=str(SKOS.definition))), 1)

    def test_missing_definition_is_not_fabricated(self):
        table = self.table('withoutDefinition')
        self.assertIsNone(table.find('a', href=str(SKOS.definition)))
        self.assertIn('Description is not a definition.', table.get_text())

    def test_missing_defined_by_places_definition_after_iri(self):
        table = self.table('withoutDefinedBy')
        self.assertIsNone(table.find('a', href=str(RDFS.isDefinedBy)))
        self.assertEqual([row.th.get_text(strip=True) for row in table.find_all('tr')][:3],
                         ['IRI', 'Definition', 'Description'])

    def test_all_language_values_are_preserved_and_html_is_escaped(self):
        definition = self.table('multilingual').find('a', href=str(SKOS.definition)).find_parent('tr').td
        self.assertEqual({p['lang']: p.get_text() for p in definition.find_all('p')},
                         {'en': '<not-markup> & a definition.', 'nl': 'Een definitie.'})
        self.assertIsNone(definition.find('not-markup'))

    def test_wrapping_is_scoped_to_example_content(self):
        table = self.table('futureProperty')
        examples = table.select('td.hri-example')
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0].find_parent('tr').th.get_text(strip=True), 'Example')
        self.assertIn('https://example.org/' + 'a' * 160, examples[0].get_text())
        style = self.soup.find('style', id='hri-documentation-style').string
        self.assertIn('.property.entity .hri-example pre', style)
        self.assertIn('white-space: pre-wrap', style)
        self.assertIn('overflow-wrap: anywhere', style)
        self.assertFalse(self.table('withoutDefinition').select('.hri-example'))

