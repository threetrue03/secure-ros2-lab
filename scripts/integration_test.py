"""Bounded integration evidence from actual motor logs, no mocked DDS results."""
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ['camera', 'perception', 'navigation', 'motor', 'attacker']


def compose(mode, *arguments, check=True):
    return subprocess.run(['docker', 'compose', '-f', f'compose.{mode}.yaml',
                           '--profile', 'attack', *arguments], cwd=ROOT,
                          check=check, capture_output=True, text=True, timeout=120)


def verify(mode):
    compose(mode, 'up', '-d', *SERVICES)
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        logs = compose(mode, 'logs', '--no-color', 'motor').stdout
        attacker = compose(mode, 'logs', '--no-color', 'attacker').stdout
        if 'kind=LEGITIMATE_PATTERN' in logs and 'lab status received:' in logs and \
                'attempting unauthorized /cmd_vel publication' in attacker:
            if mode == 'insecure' and 'kind=ATTACKER_PATTERN' in logs:
                break
            if mode == 'secure':
                # Observe a full additional interval after the attack attempt.
                time.sleep(10)
                break
        time.sleep(1)
    motor = compose(mode, 'logs', '--no-color', 'motor').stdout
    all_logs = compose(mode, 'logs', '--no-color').stdout
    (ROOT / 'artifacts').mkdir(exist_ok=True)
    (ROOT / 'artifacts' / f'{mode}-integration.txt').write_text(all_logs, encoding='utf-8')
    if 'kind=LEGITIMATE_PATTERN' not in motor or 'lab status received:' not in motor:
        raise AssertionError(f'{mode}: missing legitimate commands or attacker heartbeat')
    attacker = compose(mode, 'logs', '--no-color', 'attacker').stdout
    if 'attempting unauthorized /cmd_vel publication' not in attacker:
        raise AssertionError(f'{mode}: attacker never attempted publication')
    # Require live services, rather than treating a crashed attacker as enforcement.
    running = set(compose(mode, 'ps', '--status', 'running', '--services').stdout.split())
    if set(SERVICES) - running:
        raise AssertionError(f'{mode}: services stopped: {set(SERVICES) - running}')
    reached = 'kind=ATTACKER_PATTERN' in motor
    if reached != (mode == 'insecure'):
        raise AssertionError(f'{mode}: unexpected attacker command delivery={reached}')
    print(f'{mode}: legitimate command and heartbeat received; attacker command received={reached}')


def main():
    # A clean log window is necessary for comparing delivery in each mode.
    try:
        for mode in ('insecure', 'secure'):
            compose(mode, 'down', '--remove-orphans')
        if not (ROOT / 'security/runtime/.ready').is_file():
            subprocess.run(['make', 'secure-setup'], cwd=ROOT, check=True, timeout=120)
        for mode in ('insecure', 'secure'):
            try:
                verify(mode)
            finally:
                compose(mode, 'down', '--remove-orphans', check=False)
    finally:
        for mode in ('insecure', 'secure'):
            compose(mode, 'down', '--remove-orphans', check=False)


if __name__ == '__main__':
    main()
