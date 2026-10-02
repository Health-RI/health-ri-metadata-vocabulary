"""Publication safeguards: numeric ordering, invalid input, immutable snapshots."""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_vocabulary import build


class PublicationTests(unittest.TestCase):
    def test_reviewed_new_release_promotes_latest_without_publishing_archives(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repository'
            shutil.copytree(build.ROOT, root, ignore=shutil.ignore_patterns('__pycache__', 'site'))
            current = build.releases()[-1]
            old_version = build.version_of(current)
            major, minor, _ = map(int, old_version.split('.'))
            new_version = f'{major}.{minor + 1}.0'
            original = root / current.relative_to(build.ROOT)
            archived_html = original.with_suffix('.html').read_bytes()
            new = original.with_name(f'{build.STEM}-v{new_version}.ttl')
            text = original.read_text().replace(old_version, new_version)
            text = re.sub(r'    owl:priorVersion [^;]+;\n', '', text)
            text = text.replace('    owl:versionInfo',
                                f'    owl:priorVersion <{build.BASE}/v{old_version}> ;\n    owl:versionInfo')
            new.write_text(text)
            with patch.object(build, 'ROOT', root), \
                    patch.object(build, 'SHAPES', root / 'validation/health-ri-metadata-shapes.ttl'), \
                    patch.object(build, 'EXAMPLES', root / 'examples'):
                # A new source cannot silently relabel supporting artifacts.
                old_latest = (root / 'vocabulary/latest' / build.NAME).read_bytes()
                with self.assertRaisesRegex(ValueError, 'review compatibility'):
                    build.build()
                self.assertEqual((root / 'vocabulary/latest' / build.NAME).read_bytes(), old_latest)
                for support in [*build.EXAMPLES.glob('*.ttl'), build.SHAPES]:
                    support.write_text(support.read_text().replace(
                        f'{build.BASE}/v{old_version}>', f'{build.BASE}/v{new_version}>'))
                build.build()
            latest = root / 'vocabulary/latest'
            self.assertEqual((latest / build.NAME).read_bytes(), new.read_bytes())
            self.assertEqual((latest / 'index.html').read_bytes(), new.with_suffix('.html').read_bytes())
            self.assertEqual(original.with_suffix('.html').read_bytes(), archived_html)
            self.assertEqual({p.name for p in latest.iterdir()},
                             {build.NAME, 'index.html'})

    def test_numeric_version_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for version in ('0.9.0', '0.10.0', '0.2.0'):
                directory = root / 'vocabulary/versioned'
                directory.mkdir(parents=True, exist_ok=True)
                (directory / f'{build.STEM}-v{version}.ttl').touch()
            with patch.object(build, 'ROOT', root):
                self.assertEqual([build.version_of(p) for p in build.releases()],
                                 ['0.2.0', '0.9.0', '0.10.0'])

    def test_version_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = Path(tmp) / f'{build.STEM}-v0.2.0.ttl'
            shutil.copyfile(build.ROOT / f'vocabulary/versioned/{build.STEM}-v0.1.0.ttl', release)
            with self.assertRaisesRegex(ValueError, 'incorrect'):
                build.validate_release(release)

    def test_existing_release_cannot_change_or_disappear(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / 'vocabulary/versioned/health-ri-metadata-vocabulary-v0.1.0.ttl'
            file.parent.mkdir(parents=True)
            file.write_text('# original\n')
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root,
                                               stderr=subprocess.DEVNULL, text=True).strip()
            git('init')
            git('add', '.')
            git('-c', 'user.name=Validation', '-c', 'user.email=validation@example.org',
                'commit', '-m', 'Temporary test fixture')
            base = git('rev-parse', 'HEAD')
            with patch.object(build, 'ROOT', root):
                build.check_immutable(base)
                file.write_text('# changed\n')
                with self.assertRaisesRegex(ValueError, 'Immutable'):
                    build.check_immutable(base)
                file.unlink()
                with self.assertRaisesRegex(ValueError, 'Immutable'):
                    build.check_immutable(base)
