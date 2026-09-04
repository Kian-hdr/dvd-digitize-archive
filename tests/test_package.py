import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


monitor = module('monitor')
installer = module('install')


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='dvd test spaces ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'sample file').write_bytes(b'x' * 1200)

    def run_monitor(self, *args, env=None):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/monitor.py'),
                               str(self.root), '--once', *args], capture_output=True,
                              text=True, env=env, timeout=15)

    def test_decimal_units(self):
        self.assertEqual(monitor.human_bytes(1200), '1.20 KB')
        self.assertEqual(monitor.human_bytes(1000000000), '1.00 GB')

    def test_measure_spaces(self):
        self.assertEqual(monitor.measure(self.root), (1200, 1))

    def test_measure_does_not_follow_symlinks(self):
        (self.root / 'linked-file').symlink_to(self.root / 'sample file')
        (self.root / 'linked-directory').symlink_to(self.root, target_is_directory=True)
        self.assertEqual(monitor.measure(self.root), (1200, 1))

    def test_unknown_progress(self):
        result = self.run_monitor()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('no reliable denominator', result.stdout)
        self.assertNotIn('\033', result.stdout)
        self.assertNotIn('100%', result.stdout)

    def test_observation_leaves_existing_process_running(self):
        sleeper = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
        try:
            self.assertEqual(self.run_monitor().returncode, 0)
            self.assertIsNone(sleeper.poll())
        finally:
            sleeper.terminate()  # only this test-created disposable process
            sleeper.wait(timeout=5)

    def test_zero_interval_rejected(self):
        self.assertNotEqual(self.run_monitor('--interval', '0').returncode, 0)

    def test_invalid_environment_interval_rejected(self):
        env = dict(os.environ, DVD_MONITOR_INTERVAL='garbage')
        result = self.run_monitor(env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('Traceback', result.stderr)

    def test_sibling_path_rejected(self):
        self.assertNotEqual(self.run_monitor('--watch', str(self.root) + '-other').returncode, 0)

    def test_parent_traversal_rejected(self):
        self.assertNotEqual(self.run_monitor('--watch', str(self.root / '..')).returncode, 0)

    def test_external_log_rejected(self):
        self.assertNotEqual(self.run_monitor('--log', str(self.root.parent / 'outside.log')).returncode, 0)

    def test_symlink_escape_rejected(self):
        (self.root / 'escape').symlink_to(self.root.parent, target_is_directory=True)
        self.assertNotEqual(self.run_monitor('--watch', str(self.root / 'escape')).returncode, 0)

    def test_total_requires_explicit_watch(self):
        self.assertNotEqual(self.run_monitor('--expected-bytes', '1200').returncode, 0)

    def test_fixed_monitor_denominator(self):
        result = self.run_monitor('--watch', str(self.root), '--expected-bytes', '1200')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('100.0%', result.stdout)
        self.assertIn('not completion', result.stdout)

    def test_negative_size_rejected(self):
        self.assertNotEqual(self.run_monitor('--expected-bytes', '-1').returncode, 0)

    def test_missing_workspace_rejected(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/monitor.py'),
                                 str(self.root / 'missing'), '--once'], capture_output=True, timeout=15)
        self.assertNotEqual(result.returncode, 0)

    def test_bounded_error_log(self):
        log = self.root / 'read.log'
        log.write_text('read error\n' + 'okay\n' * 20000 + 'I/O error\n')
        self.assertIn('1 recognized lines', monitor.error_summary(log))

    @unittest.skipUnless(shutil.which('zsh'), 'optional zsh is unavailable')
    def test_original_entrypoints(self):
        env = dict(os.environ, DVD_MONITOR_ONCE='1')
        for name, args in [('live_project_monitor.zsh', []),
                           ('live_rip_monitor.zsh', [str(self.root), '1200'])]:
            result = subprocess.run(['zsh', str(ROOT / 'scripts' / name), str(self.root), *args],
                                    capture_output=True, text=True, timeout=15, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('DVD archive project monitor', result.stdout)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='dvd install test ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.dest = self.root / 'skill copy'

    def test_install_complete(self):
        installer.install(ROOT, self.dest)
        for name in installer.FILES + installer.DIRS:
            self.assertTrue((self.dest / name).exists(), name)
        self.assertFalse((self.dest / '.git').exists())
        result = subprocess.run([sys.executable, str(self.dest / 'scripts/monitor.py'),
                                 str(self.root), '--once'], capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0)

    def test_existing_unchanged(self):
        self.dest.mkdir()
        sentinel = self.dest / 'SKILL.md'
        sentinel.write_text('existing custom skill')
        with self.assertRaises(ValueError):
            installer.install(ROOT, self.dest)
        self.assertEqual(sentinel.read_text(), 'existing custom skill')
        self.assertEqual(list(self.dest.iterdir()), [sentinel])

    def test_existing_symlink_refused(self):
        self.dest.symlink_to(self.root / 'missing')
        with self.assertRaises(ValueError):
            installer.install(ROOT, self.dest)
        self.assertTrue(self.dest.is_symlink())

    def test_dry_run_no_mutation(self):
        installer.install(ROOT, self.dest, dry_run=True)
        self.assertFalse(self.dest.exists())

    def test_source_descendant_refused(self):
        with self.assertRaises(ValueError):
            installer.install(ROOT, ROOT / 'test-new-install', dry_run=True)

    def test_incomplete_source_refused(self):
        with self.assertRaises(ValueError):
            installer.install(self.root, self.dest, dry_run=True)

    def test_source_symlink_refused(self):
        fake = self.root / 'source'
        fake.mkdir()
        (fake / 'SKILL.md').symlink_to(ROOT / 'SKILL.md')
        with self.assertRaises(ValueError):
            installer.install(fake, self.dest, dry_run=True)


class PackageTests(unittest.TestCase):
    def test_prompt_matches_readme(self):
        prompt = (ROOT / 'SETUP_PROMPT.md').read_text().split('```text\n', 1)[1].split('\n```', 1)[0]
        self.assertIn('```text\n' + prompt + '\n```', (ROOT / 'README.md').read_text())
        self.assertIn('https://github.com/Kian-hdr/dvd-digitize-archive', prompt)

    def test_markdown_links_resolve(self):
        for path in ROOT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent / target.split('#')[0]).exists(), f'{path}: {target}')

    def test_original_inventory_preserved(self):
        names = ['SKILL.md', 'agents/openai.yaml', 'scripts/live_project_monitor.zsh',
                 'scripts/live_rip_monitor.zsh']
        names += ['references/' + name + '.md' for name in
                  ('workspace-standard', 'live-progress-monitor', 'parallel-orchestration',
                   'processing-and-verification', 'selectable-subtitles')]
        for name in names:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_empty_manifest_is_honest(self):
        manifest = json.loads((ROOT / 'templates/manifest.json').read_text())
        self.assertEqual(manifest['discs'], [])
        self.assertEqual(manifest['titles'], [])
        self.assertIsNone(manifest['updated_at'])

    def test_no_private_paths_or_key_material(self):
        patterns = [r'/Users/[^/\s]+/', r'/home/[^/\s]+/', r'-----BEGIN .*PRIVATE KEY-----',
                    r'gh[pousr]_[A-Za-z0-9]{30,}', r'AKIA[A-Z0-9]{16}']
        for directory in ('references', 'agents', 'templates'):
            for path in (ROOT / directory).rglob('*'):
                if path.is_file():
                    for pattern in patterns:
                        self.assertIsNone(re.search(pattern, path.read_text()), str(path))

    def test_smoke_existing_destination_preserved(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            self.skipTest('FFmpeg unavailable')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sentinel = root / 'keep.txt'
            sentinel.write_text('keep')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/smoke_test.py'),
                                     '--workspace', temporary], capture_output=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(root.iterdir()), [sentinel])
            self.assertEqual(sentinel.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
