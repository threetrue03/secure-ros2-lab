"""Validate and sign explicit access-control governance with the local CA."""
from pathlib import Path
import shutil
import subprocess
import sys

from lxml import etree
from sros2.policy import get_transport_schema


def configure(root, policy):
    schema = etree.XMLSchema(etree.parse(str(get_transport_schema('dds', 'governance.xsd'))))
    schema.assertValid(etree.parse(str(policy)))
    unsigned = root / 'enclaves/governance.xml'
    signed = root / 'enclaves/governance.p7s'
    shutil.copyfile(policy, unsigned)
    subprocess.run([
        'openssl', 'smime', '-sign', '-text', '-in', str(unsigned),
        '-signer', str(root / 'public/permissions_ca.cert.pem'),
        '-inkey', str(root / 'private/permissions_ca.key.pem'),
        '-out', str(signed), '-md', 'sha256',
    ], check=True)
    # Verify the generated S/MIME signature without printing credentials.
    subprocess.run([
        'openssl', 'smime', '-verify', '-in', str(signed),
        '-CAfile', str(root / 'public/permissions_ca.cert.pem'),
        '-out', '/dev/null',
    ], check=True)


if __name__ == '__main__':
    configure(Path(sys.argv[1]), Path(sys.argv[2]))
