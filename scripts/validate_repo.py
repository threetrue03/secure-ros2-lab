"""Host validation with standard Python; image mode validates copied build inputs."""
import argparse
import ast
from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
IMAGE = '--image' in sys.argv


class RepositoryTests(unittest.TestCase):
    def test_package_manifests_and_python_syntax(self):
        for name in ('secure_robot', 'lab_attacker'):
            manifest = ET.parse(ROOT / 'ros2_ws/src' / name / 'package.xml')
            self.assertEqual(manifest.findtext('name'), name)
        for path in ROOT.rglob('*.py'):
            if '.git' not in path.parts:
                ast.parse(path.read_text(encoding='utf-8'), filename=str(path))

    def test_policy_is_least_privilege(self):
        policy = ET.parse(ROOT / 'security/policies/lab.policy.xml')
        expected = {
            '/robot/camera': {'camera/frame_meta'},
            '/robot/perception': {'perception/target'},
            '/robot/navigation': {'cmd_vel'},
            '/robot/motor': set(),
            '/lab/attacker': {'lab/attacker/status', 'parameter_events'},
        }
        enclaves = policy.findall('.//enclave')
        self.assertEqual({e.attrib['path'] for e in enclaves}, set(expected))
        for enclave in enclaves:
            allowed = {t.text for t in enclave.findall('.//topics[@publish="ALLOW"]/topic')}
            self.assertEqual(allowed, expected[enclave.attrib['path']])
            for topic in enclave.findall('.//topic'):
                self.assertNotIn('*', topic.text)
        attacker = next(e for e in enclaves if e.attrib['path'] == '/lab/attacker')
        self.assertEqual(attacker.findtext('.//topics[@publish="DENY"]/topic'), 'cmd_vel')

    def test_attacker_commands_and_scope(self):
        sys.path.insert(0, str(ROOT / 'ros2_ws/src/lab_attacker'))
        from types import SimpleNamespace
        from lab_attacker.commands import populate_command, validate_scope
        command = SimpleNamespace(linear=SimpleNamespace(x=0), angular=SimpleNamespace(z=0))
        populate_command(command)
        self.assertEqual((command.linear.x, command.angular.z), (0.8, 1.0))
        for environment in ({}, {'LAB_SCOPE': 'secure-ros2-lab-isolated', 'ROS_DOMAIN_ID': '0'}):
            with self.assertRaises(RuntimeError):
                validate_scope(environment)
        validate_scope({'LAB_SCOPE': 'secure-ros2-lab-isolated', 'ROS_DOMAIN_ID': '42'})

    def test_explicit_governance_enforces_security(self):
        governance = ET.parse(ROOT / 'security/policies/governance.xml')
        rule = governance.find('.//domain_rule')
        self.assertEqual(rule.findtext('domains/id'), '42')
        self.assertEqual(rule.findtext('allow_unauthenticated_participants'), 'false')
        self.assertEqual(rule.findtext('enable_join_access_control'), 'true')
        topic = rule.find('.//topic_rule')
        self.assertEqual(topic.findtext('topic_expression'), '*')
        for name in ('enable_read_access_control', 'enable_write_access_control'):
            self.assertEqual(topic.findtext(name), 'true')
        self.assertEqual(topic.findtext('data_protection_kind'), 'ENCRYPT')

    @unittest.skipIf(IMAGE, 'Git and Compose source files excluded from image inputs')
    def test_required_files_and_secret_ignores(self):
        required = ['Dockerfile', 'Makefile', 'README.md', 'LICENSE', '.env.example',
                    'compose.insecure.yaml', 'compose.secure.yaml', '.github/workflows/ci.yml',
                    'docs/architecture.md', 'docs/threat-model.md', 'docs/container-security.md',
                    'docs/wireshark-analysis.md', 'docs/evidence/README.md']
        for name in required:
            self.assertTrue((ROOT / name).is_file(), name)
        secrets = ['.env', 'security/runtime/keystore/private/ca.key.pem',
                   'security/runtime/mounts/attacker/enclaves/lab/attacker/key.pem',
                   'security/demo/private.key', 'artifacts/sbom.cdx.json']
        for name in secrets:
            result = subprocess.run(['git', 'check-ignore', '--quiet', name], cwd=ROOT)
            self.assertEqual(result.returncode, 0, name)
        tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
        for name in tracked:
            self.assertFalse(name == '.env' or name.startswith('security/runtime/') or
                             name.endswith(('.key', '.pem')), name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', action='store_true')
    parser.parse_args()
    unittest.main(argv=[sys.argv[0]], verbosity=2)
