"""Credential export tests use synthetic files; no real key is generated."""
import importlib.util
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import unittest
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('export_credentials', ROOT / 'security/scripts/export_credentials.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


@contextmanager
def fixture_directory():
    # These files are deliberately synthetic, not secrets. Standard mkdir
    # avoids owner-only Windows temp ACLs unsupported by some sandboxes.
    path = ROOT / 'artifacts' / f'test-credentials-{uuid.uuid4().hex}'
    path.mkdir()
    try:
        yield path
    finally:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT / 'artifacts'):
            raise RuntimeError('Fixture cleanup escaped artifacts')
        shutil.rmtree(path)


class ExportTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'artifacts').mkdir(exist_ok=True)

    def fixture(self, root, protection='ENCRYPT'):
        enclaves = root / 'enclaves'
        enclaves.mkdir()
        (enclaves / 'governance.xml').write_text(f'''<dds><domain_access_rules><domain_rule>
        <domains><id>42</id></domains>
        <allow_unauthenticated_participants>false</allow_unauthenticated_participants>
        <enable_join_access_control>true</enable_join_access_control><topic_access_rules><topic_rule>
        <enable_read_access_control>true</enable_read_access_control>
        <enable_write_access_control>true</enable_write_access_control>
        <data_protection_kind>{protection}</data_protection_kind>
        </topic_rule></topic_access_rules></domain_rule></domain_access_rules></dds>''')
        for enclave in ('robot/camera', 'robot/perception', 'robot/navigation', 'robot/motor', 'lab/attacker'):
            path = enclaves / enclave
            path.mkdir(parents=True)
            dds = ET.Element('dds')
            grant = ET.SubElement(ET.SubElement(dds, 'permissions'), 'grant')
            ET.SubElement(grant, 'subject_name').text = f'CN=/{enclave}'
            allowed = ET.SubElement(grant, 'allow_rule')
            ET.SubElement(ET.SubElement(allowed, 'domains'), 'id').text = '42'
            for direction, names in zip(('publish', 'subscribe'), exporter.PERMISSIONS[enclave]):
                topics = ET.SubElement(ET.SubElement(allowed, direction), 'topics')
                for name in names | {'ros_discovery_info'}:
                    ET.SubElement(topics, 'topic').text = name
            if enclave == 'lab/attacker':
                denied = ET.SubElement(grant, 'deny_rule')
                ET.SubElement(ET.SubElement(denied, 'domains'), 'id').text = '42'
                ET.SubElement(ET.SubElement(ET.SubElement(denied, 'publish'), 'topics'), 'topic').text = 'rt/cmd_vel'
            ET.SubElement(grant, 'default').text = 'DENY'
            ET.ElementTree(dds).write(path / 'permissions.xml')
            for name in exporter.FILES:
                (path / name).write_text('SYNTHETIC TEST FIXTURE, NOT A CREDENTIAL')

    @unittest.skipIf(os.name == 'nt', 'Owner-only POSIX credential export requires Linux')
    def test_exports_only_own_participant_files(self):
        with fixture_directory() as directory:
            base = Path(directory)
            self.fixture(base)
            exporter.export(base, base / 'mounts')
            for service in ('camera', 'perception', 'navigation', 'motor', 'attacker'):
                files = list((base / 'mounts' / service).rglob('*'))
                self.assertEqual({p.name for p in files if p.is_file()}, set(exporter.FILES))
                self.assertFalse(any('private' in p.parts for p in files))

    def test_rejects_unencrypted_governance(self):
        with fixture_directory() as directory:
            base = Path(directory)
            self.fixture(base, 'NONE')
            with self.assertRaisesRegex(RuntimeError, 'encryption'):
                exporter.export(base, base / 'mounts')

    def test_compiled_permissions_are_exact_and_reject_command_grant(self):
        with fixture_directory() as directory:
            self.fixture(directory)
            for enclave in exporter.PERMISSIONS:
                permission = ET.parse(directory / 'enclaves' / enclave / 'permissions.xml')
                exporter.validate_permissions(permission, enclave)
            attacker = ET.parse(directory / 'enclaves/lab/attacker/permissions.xml')
            ET.SubElement(attacker.find('.//allow_rule/publish/topics'), 'topic').text = 'rt/cmd_vel'
            with self.assertRaisesRegex(RuntimeError, 'publish permissions'):
                exporter.validate_permissions(attacker, 'lab/attacker')


if __name__ == '__main__':
    unittest.main()
