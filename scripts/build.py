"""Validate complete releases, generate latest files and a portable Pages site."""
from __future__ import annotations

import argparse
import datetime
import html
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from bs4 import BeautifulSoup
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCAT, DCTERMS, OWL, SKOS, XSD

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://w3id.org/health-ri/metadata-vocabulary'
HRI = Namespace(BASE + '#')
VANN = Namespace('http://purl.org/vocab/vann/')
SCHEMA = Namespace('https://schema.org/')
REPO = 'https://github.com/Health-RI/health-ri-metadata-vocabulary'
LICENSE = URIRef('https://creativecommons.org/licenses/by/4.0/')
NAME = 'health-ri-metadata-vocabulary.ttl'
FILES = (NAME, 'health-ri-metadata-shapes.ttl', 'example.ttl')
SEMVER = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def releases():
    entries = list((ROOT / 'vocabulary/versioned').iterdir())
    require(bool(entries), 'No versioned releases found')
    for entry in entries:
        require(entry.is_dir() and SEMVER.fullmatch(entry.name),
                f'Invalid release directory: {entry.name}; use X.Y.Z')
    return sorted(entries, key=lambda p: tuple(map(int, p.name.split('.'))))


def validate_release(directory, previous=None):
    version = directory.name
    for name in FILES:
        require((directory / name).is_file(), f'{version}: missing {name}')
    g = Graph().parse(directory / NAME)
    ontology = URIRef(BASE)
    require(set(g.subjects(RDF.type, OWL.Ontology)) == {ontology},
            f'{version}: expected one ontology with the canonical IRI')
    expected = {
        OWL.versionIRI: URIRef(f'{BASE}/v{version}'),
        OWL.versionInfo: Literal(version), URIRef(str(DCAT) + 'version'): Literal(version),
        VANN.preferredNamespacePrefix: Literal('hri'),
        VANN.preferredNamespaceUri: Literal(BASE + '#', datatype=XSD.anyURI),
        DCTERMS.license: LICENSE, SCHEMA.codeRepository: URIRef(REPO),
    }
    for predicate, value in expected.items():
        require(set(g.objects(ontology, predicate)) == {value},
                f'{version}: incorrect {predicate}')
    for predicate in (DCTERMS.title, DCTERMS.description, DCTERMS.creator,
                      DCTERMS.publisher, DCTERMS.issued, DCTERMS.modified):
        require(bool(list(g.objects(ontology, predicate))), f'Missing {predicate}')
    for predicate in (DCTERMS.issued, DCTERMS.modified):
        value = g.value(ontology, predicate)
        require(value.datatype == XSD.date, f'{predicate}: expected xsd:date')
        datetime.date.fromisoformat(str(value))
    if previous:
        require(g.value(ontology, OWL.priorVersion) == URIRef(f'{BASE}/v{previous}'),
                f'{version}: owl:priorVersion must identify {previous}')
    else:
        require(not list(g.objects(ontology, OWL.priorVersion)), 'Initial release has no prior version')
    local_subjects = {s for s in g.subjects() if str(s).startswith(BASE + '#')}
    if version == '0.1.0':
        require(local_subjects == {HRI.healthConditionOfInterest},
                '0.1.0 must contain exactly one Health-RI domain term')
    for term in local_subjects:
        for predicate in (RDFS.label, SKOS.definition, RDFS.isDefinedBy):
            require(bool(list(g.objects(term, predicate))), f'{term}: missing {predicate}')
        require(not list(g.objects(term, OWL.versionInfo)), 'No independent term versioning')
    term = HRI.healthConditionOfInterest
    require((term, RDF.type, OWL.ObjectProperty) in g, 'Expected an object property')
    require(g.value(term, RDFS.domain) == DCAT.Dataset, 'Expected Dataset domain')
    require(g.value(term, RDFS.range) == SKOS.Concept, 'Expected Concept range')
    require((term, RDF.type, OWL.FunctionalProperty) not in g, 'Property must be repeatable')
    shapes = Graph().parse(directory / FILES[1])
    example = Graph().parse(directory / FILES[2])
    conforms, _, report = validate(example, shacl_graph=shapes, inference='none', meta_shacl=True)
    require(conforms, f'{version}: example fails SHACL\n{report}')
    return g


def check_immutable(base):
    """Reject edits/deletions of release sources or already published HTML."""
    if not base or set(base) == {'0'}:
        return
    paths = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', base, '--',
         'vocabulary/versioned', 'docs/versioned'], cwd=ROOT, text=True).splitlines()
    for path in paths:
        old = subprocess.check_output(['git', 'show', f'{base}:{path}'], cwd=ROOT)
        file = ROOT / path
        require(file.is_file() and file.read_bytes() == old,
                f'Immutable release file changed or removed: {path}; add a new version')


def check_links(directory):
    for page in directory.rglob('*.html'):
        soup = BeautifulSoup(page.read_text(), 'html.parser')
        for element in soup.select('[href], [src]'):
            value = element.get('href', element.get('src', ''))
            url = urlsplit(value)
            if url.scheme or url.netloc or not value:
                continue
            target = (page.parent / unquote(url.path)).resolve() if url.path else page
            if target.is_dir():
                target = target / 'index.html'
            require(target.is_file(), f'{page}: broken local link {value}')
            if url.fragment and target.suffix == '.html':
                target_soup = soup if target == page else BeautifulSoup(target.read_text(), 'html.parser')
                require(target_soup.find(id=unquote(url.fragment)) is not None,
                        f'{page}: missing fragment {value}')


def build(base=None):
    check_immutable(base)
    versions = releases()
    previous = None
    for directory in versions:
        validate_release(directory, previous)
        previous = directory.name
    current = versions[-1]
    latest = ROOT / 'vocabulary/latest'
    latest.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copyfile(current / name, latest / name)
    # Generate a snapshot once; never silently regenerate past documentation.
    for directory in versions:
        output = ROOT / 'docs/versioned' / directory.name / 'index.html'
        if not output.exists():
            output.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['pylode', str(directory / NAME), '-p', 'ontpub',
                            '-c', 'true', '-o', str(output)], check=True)
        require('health condition of interest' in output.read_text().lower(),
                f'Incomplete PyLODE output: {output}')
    latest_doc = ROOT / 'docs/latest/index.html'
    latest_doc.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'docs/versioned' / current.name / 'index.html', latest_doc)
    # Citation metadata follows the selected vocabulary release automatically.
    citation = yaml.safe_load((ROOT / 'CITATION.cff').read_text())
    graph = Graph().parse(current / NAME)
    citation['version'] = current.name
    citation['date-released'] = str(graph.value(URIRef(BASE), DCTERMS.modified))
    citation['url'] = f'{BASE}/v{current.name}'
    (ROOT / 'CITATION.cff').write_text(yaml.safe_dump(citation, sort_keys=False, allow_unicode=True))
    site = ROOT / 'site'
    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(ROOT / 'docs', site)
    shutil.copytree(ROOT / 'vocabulary', site / 'vocabulary')
    for name in ('LICENSE', 'CHANGELOG.md', 'CITATION.cff', 'README.md', 'MAINTAINING.md'):
        shutil.copyfile(ROOT / name, site / name)
    items = ''.join(f'<li><a href="versioned/{p.name}/index.html">Version {p.name}</a> '
                    f'(<a href="vocabulary/versioned/{p.name}/{NAME}">Turtle</a>)</li>'
                    for p in reversed(versions))
    (site / 'index.html').write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Health-RI Metadata Vocabulary</title></head><body>
<main><h1>Health-RI Metadata Vocabulary</h1>
<p>Current vocabulary version: {html.escape(current.name)}. Prefix: <code>hri</code>.</p>
<p>Namespace: <code>{BASE}#</code>. Development releases (0.x) are subject to change.</p>
<p><a href="latest/index.html">Current PyLODE specification</a> ·
<a href="vocabulary/latest/{NAME}">Current Turtle vocabulary</a> ·
<a href="vocabulary/latest/health-ri-metadata-shapes.ttl">SHACL</a> ·
<a href="vocabulary/latest/example.ttl">Example</a></p>
<h2>Complete vocabulary releases</h2><ul>{items}</ul>
<p><a href="{REPO}">Official repository</a> · <a href="CHANGELOG.md">Changelog</a> ·
<a href="CITATION.cff">Citation</a> · <a href="LICENSE">CC BY 4.0 license</a></p>
</main></body></html>''')
    (site / '.nojekyll').touch()
    check_links(site)
    for name in FILES:
        require((latest / name).read_bytes() == (current / name).read_bytes(), 'Latest mismatch')
    print(f'Validated {len(versions)} release(s); latest={current.name}; Pages site ready in site/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='Base Git commit for release immutability checks')
    args = parser.parse_args()
    try:
        build(args.base)
    except Exception as exc:
        raise SystemExit(f'Publication failed: {exc}') from exc
