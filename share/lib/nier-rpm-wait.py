#!/usr/bin/env python3
"""Wait briefly for RPM's POSIX write lock without changing its lock file."""
import fcntl
import time
from pathlib import Path


def wait_for_rpm(path=Path('/usr/lib/sysimage/rpm/.rpm.lock'), seconds=60):
    try:
        source = path.open('rb')
    except FileNotFoundError:
        return True
    with source:
        for attempt in range(seconds + 1):
            try:
                fcntl.lockf(source, fcntl.LOCK_SH | fcntl.LOCK_NB)
                fcntl.lockf(source, fcntl.LOCK_UN)
                return True
            except BlockingIOError:
                if attempt == 0:
                    print('Waiting for the RPM transaction before running Nier migrations...')
                if attempt < seconds:
                    time.sleep(1)
    return False


if __name__ == '__main__':
    if not wait_for_rpm():
        raise SystemExit('RPM is busy; retry Nier migrations after the package transaction completes.')
