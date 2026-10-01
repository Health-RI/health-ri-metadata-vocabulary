"""Validate complete releases, generate latest files and a portable Pages site."""
from __future__ import annotations

import argparse
import datetime
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
STEM = 'health-ri-metadata-vocabulary'
NAME = STEM + '.ttl'
SHAPES = ROOT / 'validation/health-ri-metadata-shapes.ttl'
EXAMPLES = ROOT / 'examples'
SEMVER = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def version_of(path):
    match = re.fullmatch(STEM + r'-v(' + SEMVER.pattern + r')\.ttl', path.name)
    require(match is not None, f'Invalid release filename: {path.name}; use {STEM}-vX.Y.Z.ttl')
    return match.group(1)


def releases():
    directory = ROOT / 'vocabulary/versioned'
    require(not any(p.is_dir() for p in directory.iterdir()),
            'Versioned releases must be flat files, not version subdirectories')
    entries = list(directory.glob('*.ttl'))
    require(bool(entries), 'No versioned vocabulary files found')
    return sorted(entries, key=lambda p: tuple(map(int, version_of(p).split('.'))))


def validate_release(file, previous=None):
    version = version_of(file)
    g = Graph().parse(file)
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
    if tuple(map(int, version.split('.'))) >= (0, 2, 0):
        term = HRI.anatomicalLocationCovered
        require((term, RDF.type, OWL.ObjectProperty) in g, 'Expected anatomical object property')
        require(g.value(term, RDFS.domain) == DCAT.Dataset, 'Expected anatomical Dataset domain')
        require(g.value(term, RDFS.range) == SKOS.Concept, 'Expected anatomical Concept range')
        require((term, RDF.type, OWL.FunctionalProperty) not in g, 'Anatomical property must be repeatable')
    return g


def validate_example():
    shapes = Graph().parse(SHAPES)
    examples = sorted(EXAMPLES.glob('*.ttl'))
    require(bool(examples), 'No usage examples found')
    for file in examples:
        example = Graph().parse(file)
        conforms, _, report = validate(example, shacl_graph=shapes, inference='none', meta_shacl=True)
        require(conforms, f'{file.name} fails SHACL\n{report}')


def check_immutable(base):
    """Reject edits/deletions of release sources or already published HTML."""
    if not base or set(base) == {'0'}:
        return
    paths = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', base, '--',
         'vocabulary/versioned', 'docs/versioned'], cwd=ROOT, text=True).splitlines()
    for path in paths:
        old = subprocess.check_output(['git', 'show', f'{base}:{path}'], cwd=ROOT)
        # Explicitly requested migration of the initial implementation on 2026-09-30.
        # The exception applies only to the known legacy paths at this exact base commit.
        if base == 'e9bc4cac163d7be67709caaecd98a94d74c34051' and (
                path.startswith('vocabulary/versioned/0.1.0/') or
                path == 'docs/versioned/0.1.0/index.html'):
            continue
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
    for file in versions:
        validate_release(file, previous)
        previous = version_of(file)
    validate_example()
    current = versions[-1]
    version = version_of(current)
    latest = ROOT / 'vocabulary/latest'
    latest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(current, latest / NAME)
    # A versioned HTML snapshot is generated once alongside its Turtle source.
    for file in versions:
        output = file.with_suffix('.html')
        if not output.exists():
            temporary = output.with_suffix('.tmp.html')
            try:
                subprocess.run(['pylode', str(file), '-p', 'ontpub',
                                '-c', 'true', '-o', str(temporary)], check=True)
                require(f'{BASE}/v{version_of(file)}' in temporary.read_text(),
                        f'PyLODE output lacks the version IRI: {file.name}')
                temporary.replace(output)
            finally:
                temporary.unlink(missing_ok=True)
        require(f'{BASE}/v{version_of(file)}' in output.read_text(),
                f'Documentation version mismatch: {output.name}')
    shutil.copyfile(current.with_suffix('.html'), latest / 'index.html')
    # The latest directory itself is the Pages artifact; archives stay in GitHub.
    (latest / '.nojekyll').touch()
    citation = yaml.safe_load((ROOT / 'CITATION.cff').read_text())
    graph = Graph().parse(current)
    citation['version'] = version
    citation['date-released'] = str(graph.value(URIRef(BASE), DCTERMS.modified))
    citation['url'] = f'{BASE}/v{version}'
    (ROOT / 'CITATION.cff').write_text(yaml.safe_dump(citation, sort_keys=False, allow_unicode=True))
    check_links(latest)
    require((latest / NAME).read_bytes() == current.read_bytes(), 'Latest Turtle mismatch')
    require((latest / 'index.html').read_bytes() == current.with_suffix('.html').read_bytes(),
            'Latest HTML mismatch')
    print(f'Validated {len(versions)} release(s); latest={version}; Pages ready in vocabulary/latest/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='Base Git commit for release immutability checks')
    args = parser.parse_args()
    try:
        build(args.base)
    except Exception as exc:
        raise SystemExit(f'Publication failed: {exc}') from exc
