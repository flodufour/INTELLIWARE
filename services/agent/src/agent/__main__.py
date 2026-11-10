"""Placeholder entry point until the agent block is implemented."""

import signal
import sys
import time

signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
print("agent: placeholder running", flush=True)
while True:
    time.sleep(3600)
