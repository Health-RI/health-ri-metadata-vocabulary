"""Reject stale or missing release metadata without rewriting supporting files."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rdflib import DCTERMS, Graph, Literal, URIRef
import yaml
from test_vocabulary import build


class VersionConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        shutil.copytree(build.ROOT, self.root, ignore=shutil.ignore_patterns('__pycache__'))
        for attr, value in [('ROOT', self.root),
                            ('EXAMPLES', self.root / 'examples'),
                            ('SHAPES', self.root / 'validation/health-ri-metadata-shapes.ttl')]:
            mock = patch.object(build, attr, value)
            mock.start()
            self.addCleanup(mock.stop)
        self.current = build.releases()[-1]
        self.version = build.version_of(self.current)

    def test_current_artifacts_match(self):
        build.check_publication_consistency(self.current)

    def test_support_references_missing_stale_conflicting_or_literal(self):
        files = [(p, URIRef(build.BASE + '/example/' + p.stem))
                 for p in build.EXAMPLES.glob('*.ttl')]
        files.append((build.SHAPES, URIRef(build.BASE + '/shacl')))
        for file, subject in files:
            original = file.read_bytes()
            for mode in ('missing', 'stale', 'conflicting', 'literal'):
                with self.subTest(file=file.name, mode=mode):
                    graph = Graph().parse(data=original, format='turtle')
                    if mode != 'conflicting':
                        graph.remove((subject, DCTERMS.references, None))
                    if mode in ('stale', 'conflicting'):
                        graph.add((subject, DCTERMS.references, URIRef(build.BASE + '/v0.0.0')))
                    if mode == 'literal':
                        graph.add((subject, DCTERMS.references, Literal(build.BASE + '/v' + self.version)))
                    graph.serialize(file, format='turtle')
                    before = file.read_bytes()
                    with self.assertRaisesRegex(ValueError, 'review compatibility'):
                        build.check_support_versions(self.current)
                    self.assertEqual(file.read_bytes(), before)
                    file.write_bytes(original)

    def test_stale_latest_turtle_rejected(self):
        file = self.root / 'vocabulary/latest' / build.NAME
        file.write_text(file.read_text().replace(self.version, '0.0.0'))
        with self.assertRaisesRegex(ValueError, 'Latest Turtle mismatch'):
            build.check_publication_consistency(self.current)

    def test_stale_latest_html_rejected(self):
        file = self.root / 'vocabulary/latest/index.html'
        file.write_text(file.read_text().replace(self.version, '0.0.0'))
        with self.assertRaisesRegex(ValueError, 'Latest HTML mismatch'):
            build.check_publication_consistency(self.current)

    def test_matching_copies_with_wrong_documentation_version_rejected(self):
        # An incidental current-version link must not conceal a stale version field.
        html = self.current.with_suffix('.html').read_text()
        html = html.replace(f'<dd><p>{self.version}</p></dd>', '<dd><p>0.0.0</p></dd>')
        for file in (self.current.with_suffix('.html'), self.root / 'vocabulary/latest/index.html'):
            file.write_text(html)
        with self.assertRaisesRegex(ValueError, 'documentation .*versionInfo'):
            build.check_publication_consistency(self.current)

    def test_citation_fields_must_match(self):
        file = self.root / 'CITATION.cff'
        original = file.read_text()
        for key in ('version', 'date-released', 'url'):
            with self.subTest(field=key):
                citation = yaml.safe_load(original)
                citation[key] = 'incorrect'
                file.write_text(yaml.safe_dump(citation))
                with self.assertRaisesRegex(ValueError, 'CITATION.cff: ' + key):
                    build.check_publication_consistency(self.current)
                file.write_text(original)

    def test_build_refreshes_stale_generated_outputs_without_rewriting_support(self):
        support = {p: p.read_bytes() for p in [*build.EXAMPLES.glob('*.ttl'), build.SHAPES]}
        latest = self.root / 'vocabulary/latest'
        for file in (latest / build.NAME, latest / 'index.html', self.root / 'CITATION.cff'):
            file.write_text(file.read_text().replace(self.version, '0.0.0'))
        with self.assertRaisesRegex(ValueError, 'Latest Turtle mismatch'):
            build.check_publication_consistency(self.current)
        build.build()
        build.check_publication_consistency(self.current)
        for file, content in support.items():
            self.assertEqual(file.read_bytes(), content)
