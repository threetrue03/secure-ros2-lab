"""Configuration contract checks; Docker config remains the runtime authority."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class ComposeTests(unittest.TestCase):
    def test_network_hardening_and_service_credentials(self):
        for mode in ('insecure', 'secure'):
            document = yaml.safe_load((ROOT / f'compose.{mode}.yaml').read_text())
            self.assertTrue(document['networks']['lab']['internal'])
            self.assertEqual(document['networks']['lab']['driver'], 'bridge')
            for name in ('camera', 'perception', 'navigation', 'motor', 'attacker'):
                service = document['services'][name]
                self.assertTrue(service['read_only'])
                self.assertEqual(service['cap_drop'], ['ALL'])
                self.assertNotIn('ports', service)
                self.assertNotIn('network_mode', service)
                self.assertEqual(service['environment']['ROS_DOMAIN_ID'], '42')
                self.assertEqual(service['environment']['ROS_SECURITY_ENABLE'], str(mode == 'secure').lower())
                if mode == 'secure':
                    self.assertEqual(service['environment']['ROS_SECURITY_STRATEGY'], 'Enforce')
                    mount, = service['volumes']
                    self.assertTrue(mount['read_only'])
                    self.assertFalse(mount['bind']['create_host_path'])
                    self.assertEqual(mount['source'], f'./security/runtime/mounts/{name}')
            self.assertEqual(document['services']['attacker']['profiles'], ['attack'])


if __name__ == '__main__':
    unittest.main()
