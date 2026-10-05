"""Export only participant material; never expose CA keys to robot services."""
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

FILES = ('key.pem', 'cert.pem', 'identity_ca.cert.pem', 'permissions_ca.cert.pem',
         'governance.p7s', 'permissions.p7s')
PERMISSIONS = {
    'robot/camera': ({'rt/camera/frame_meta'}, set()),
    'robot/perception': ({'rt/perception/target'}, {'rt/camera/frame_meta'}),
    'robot/navigation': ({'rt/cmd_vel'}, {'rt/perception/target'}),
    'robot/motor': (set(), {'rt/cmd_vel', 'rt/lab/attacker/status'}),
    'lab/attacker': ({'rt/lab/attacker/status', 'rt/parameter_events'}, set()),
}


def validate_permissions(permission, enclave):
    if permission.findtext('.//grant/default') != 'DENY':
        raise RuntimeError(f'Default permission is not DENY for {enclave}')
    if permission.findtext('.//grant/subject_name') != f'CN=/{enclave}':
        raise RuntimeError(f'Unexpected permission identity for {enclave}')
    domains = permission.findall('.//domains/id')
    if not domains or any(domain.text != '42' for domain in domains):
        raise RuntimeError(f'Unexpected permission domain for {enclave}')
    for direction, expected in zip(('publish', 'subscribe'), PERMISSIONS[enclave]):
        actual = {topic.text for topic in permission.findall(f'.//allow_rule/{direction}/topics/topic')}
        if actual != expected | {'ros_discovery_info'}:
            raise RuntimeError(f'Unexpected {direction} permissions for {enclave}: {actual}')
    if enclave == 'lab/attacker':
        denied = {topic.text for topic in permission.findall('.//deny_rule/publish/topics/topic')}
        if 'rt/cmd_vel' not in denied:
            raise RuntimeError('Missing explicit attacker command denial')


def export(root, output):
    governance = ET.parse(root / 'enclaves/governance.xml')
    rules = governance.findall('.//domain_rule')
    if not rules:
        raise RuntimeError('No DDS governance domain rules found')
    for rule in rules:
        if rule.findtext('domains/id') != '42':
            raise RuntimeError('Governance must govern lab domain 42')
        for tag in ('allow_unauthenticated_participants',):
            if rule.findtext(tag) != 'false':
                raise RuntimeError(f'Unsafe governance: {tag}')
        if rule.findtext('enable_join_access_control') != 'true':
            raise RuntimeError('Join access control is disabled')
        topics = rule.findall('.//topic_rule')
        if not topics:
            raise RuntimeError('No DDS topic governance rules found')
        for topic in topics:
            for tag in ('enable_read_access_control', 'enable_write_access_control'):
                if topic.findtext(tag) != 'true':
                    raise RuntimeError(f'Unsafe topic governance: {tag}')
            if topic.findtext('data_protection_kind') not in ('ENCRYPT', 'ENCRYPT_WITH_ORIGIN_AUTHENTICATION'):
                raise RuntimeError('DDS payload encryption is not enabled')
    for enclave in PERMISSIONS:
        source = root / 'enclaves' / enclave
        permission = ET.parse(source / 'permissions.xml')
        validate_permissions(permission, enclave)
        destination = output / enclave.split('/')[-1] / 'enclaves' / enclave
        destination.mkdir(parents=True, mode=0o700)
        for name in FILES:
            # Dereference SROS2 symlinks so mounts contain their own public CA
            # certs and signed governance, without needing the signing store.
            shutil.copyfile(source / name, destination / name)
            (destination / name).chmod(0o600)


if __name__ == '__main__':
    export(Path(sys.argv[1]), Path(sys.argv[2]))
