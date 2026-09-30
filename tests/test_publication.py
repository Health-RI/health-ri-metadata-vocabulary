"""Publication safeguards: numeric ordering, invalid input, immutable snapshots."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_vocabulary import build


class PublicationTests(unittest.TestCase):
    def test_numeric_version_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for version in ('0.9.0', '0.10.0', '0.2.0'):
                (root / 'vocabulary/versioned' / version).mkdir(parents=True)
            with patch.object(build, 'ROOT', root):
                self.assertEqual([p.name for p in build.releases()],
                                 ['0.2.0', '0.9.0', '0.10.0'])

    def test_version_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = Path(tmp) / '0.2.0'
            shutil.copytree(build.ROOT / 'vocabulary/versioned/0.1.0', release)
            with self.assertRaisesRegex(ValueError, 'incorrect'):
                build.validate_release(release)

    def test_existing_release_cannot_change_or_disappear(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / 'vocabulary/versioned/0.1.0/example.ttl'
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
