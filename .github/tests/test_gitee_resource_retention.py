"""Run the actual workflow cleanup shell against a local Gitee API substitute."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


WORKFLOW = Path(__file__).parents[1] / 'workflows/sync-gitee-recent-release.yml'
STEP = 'Retain only the synced Gitee resource release'

FAKE_CURL = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse

path = Path(os.environ['FAKE_GITEE_STATE'])
state = json.loads(path.read_text())
args = sys.argv[1:]
url = urlparse(args[-1])
method = args[args.index('-X') + 1] if '-X' in args else 'GET'
state['requests'].append([method, url.path, url.query])
result = None
failed = False
if method == 'DELETE':
    release_id = int(url.path.rsplit('/', 1)[1])
    if state.get('delete_failure'):
        failed = True
    elif not state.get('ignore_delete'):
        state['releases'] = [r for r in state['releases'] if r['id'] != release_id]
else:
    query = parse_qs(url.query)
    page = int(query.get('page', ['1'])[0])
    size = int(query.get('per_page', ['100'])[0])
    if state.get('list_failure') == page:
        failed = True
    elif state.get('malformed'):
        result = {'message': 'invalid response'}
    else:
        result = state['releases'][(page - 1) * size:page * size]
path.write_text(json.dumps(state))
if failed:
    sys.exit(22)
if result is not None:
    print(json.dumps(result))
'''


def step_shell(name):
    source = WORKFLOW.read_text()
    step = source.split(f'      - name: {name}\n', 1)[1]
    return textwrap.dedent(step.split('        run: |\n', 1)[1].split('\n      - name:', 1)[0])


def cleanup_shell():
    return step_shell(STEP)


@unittest.skipUnless(subprocess.check_output(['bash', '-c', 'echo ${BASH_VERSINFO[0]}'],
                                           text=True).strip() != '3', 'Requires runner Bash 4+')
class AssetDownloadTests(unittest.TestCase):
    def run_download(self, names):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_gh = root / 'gh'
            fake_gh.write_text('''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
target = Path(sys.argv[sys.argv.index('--dir') + 1])
for name in json.loads(os.environ['FAKE_ASSET_NAMES']):
    (target / name).write_bytes(b'resource-package')
''')
            fake_gh.chmod(0o755)
            env_file = root / 'env'
            output_file = root / 'output'
            env = dict(os.environ, PATH=f'{root}{os.pathsep}{os.environ["PATH"]}',
                       RUNNER_TEMP=str(root), GITHUB_ENV=str(env_file),
                       GITHUB_OUTPUT=str(output_file), GITHUB_REPOSITORY='test/resources',
                       AVDB_CSV_RELEASE_TAG='2026-10-28-08-00-24',
                       FAKE_ASSET_NAMES=json.dumps(names))
            result = subprocess.run(['bash', '-c', step_shell('Download and validate GitHub 30D assets')],
                                    env=env, capture_output=True, text=True)
            return result, env_file.read_text() if env_file.exists() else ''

    def names(self, sites=('sehuatang', 'X1080X', 'LTX', 'FTAV')):
        return [f'30D_{site}_2026-10-28-08-00-24.zip' for site in sites]

    def test_all_four_sites_including_ftav_are_exported_for_upload(self):
        names = self.names()
        result, env = self.run_download(names)
        self.assertEqual(result.returncode, 0, result.stderr)
        exported = dict(line.split('=', 1) for line in env.splitlines())
        self.assertEqual([exported[f'AVDB_CSV_NAME_{i}'] for i in range(1, 5)], sorted(names))
        self.assertRegex(exported['AVDB_CSV_NAMES_FINGERPRINT'], r'^[a-f0-9]{64}$')

    def test_missing_site_is_rejected(self):
        result, env = self.run_download(self.names(('sehuatang', 'X1080X', 'LTX')))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Expected exactly four 30D zip assets, found 3', result.stderr)
        self.assertEqual(env, '')

    def test_unexpected_site_is_rejected(self):
        result, env = self.run_download(self.names(('sehuatang', 'X1080X', 'LTX', 'unknown')))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unexpected 30D asset name', result.stderr)
        self.assertEqual(env, '')

    def test_duplicate_site_is_rejected(self):
        names = self.names(('sehuatang', 'X1080X', 'LTX'))
        names.append('30D_LTX_2026-10-28-08-00-25.zip')
        result, env = self.run_download(names)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Duplicate 30D asset for website', result.stderr)
        self.assertEqual(env, '')


class ResourceReleaseRetentionTests(unittest.TestCase):
    def run_cleanup(self, releases, **options):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_curl = root / 'curl'
            fake_curl.write_text(FAKE_CURL)
            fake_curl.chmod(0o755)
            state_path = root / 'state.json'
            state_path.write_text(json.dumps(dict(releases=releases, requests=[], **options)))
            env = dict(os.environ, PATH=f'{root}{os.pathsep}{os.environ["PATH"]}',
                       RUNNER_TEMP=str(root), FAKE_GITEE_STATE=str(state_path),
                       GITEE_TOKEN='test-token', AVDB_GITEE_BASE_URL='https://gitee.test',
                       AVDB_GITEE_OWNER='avdb', AVDB_GITEE_REPO='resources',
                       AVDB_GITEE_RELEASE_ID='7', AVDB_CSV_RELEASE_TAG='current')
            result = subprocess.run(['bash', '-c', cleanup_shell()], env=env,
                                    capture_output=True, text=True)
            return result, json.loads(state_path.read_text())

    def test_collects_all_pages_before_deleting_and_keeps_verified_id(self):
        # Current is deliberately on page two; response order is irrelevant.
        releases = [dict(id=i, tag_name=f'old-{i}') for i in range(10, 111)]
        releases.append(dict(id=7, tag_name='current'))
        result, state = self.run_cleanup(releases)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(state['releases'], [dict(id=7, tag_name='current')])
        self.assertEqual([r[0] for r in state['requests'][:3]], ['GET', 'GET', 'DELETE'])
        self.assertEqual(len([r for r in state['requests'] if r[0] == 'DELETE']), 101)

    def test_already_single_release_is_idempotent(self):
        result, state = self.run_cleanup([dict(id=7, tag_name='current')])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(r[0] == 'GET' for r in state['requests']))

    def test_refuses_cleanup_when_current_missing_or_tag_mismatched(self):
        for releases in ([], [dict(id=8, tag_name='old')], [dict(id=7, tag_name='wrong')]):
            with self.subTest(releases=releases):
                result, state = self.run_cleanup(releases)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(all(r[0] == 'GET' for r in state['requests']))

    def test_list_failure_or_malformed_response_does_not_delete(self):
        releases = [dict(id=7, tag_name='current')]
        for options in (dict(list_failure=1), dict(malformed=True)):
            with self.subTest(options=options):
                result, state = self.run_cleanup(releases, **options)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(all(r[0] == 'GET' for r in state['requests']))

    def test_later_page_failure_does_not_delete(self):
        releases = [dict(id=i, tag_name=f'old-{i}') for i in range(10, 110)]
        result, state = self.run_cleanup(releases, list_failure=2)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(all(r[0] == 'GET' for r in state['requests']))

    def test_delete_failure_or_incomplete_cleanup_fails_workflow(self):
        releases = [dict(id=7, tag_name='current'), dict(id=8, tag_name='old')]
        for options in (dict(delete_failure=True), dict(ignore_delete=True)):
            with self.subTest(options=options):
                result, state = self.run_cleanup(releases, **options)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(dict(id=7, tag_name='current'), state['releases'])

    def test_cleanup_runs_after_asset_verification_with_default_success_condition(self):
        source = WORKFLOW.read_text()
        self.assertLess(source.index('- name: Verify Gitee release contains only 30D assets'),
                        source.index(f'- name: {STEP}'))
        step = source.split(f'      - name: {STEP}\n', 1)[1].split('\n      - name:', 1)[0]
        self.assertNotIn('if:', step)


if __name__ == '__main__':
    unittest.main()
