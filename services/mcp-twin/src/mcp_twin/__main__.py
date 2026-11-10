"""Placeholder entry point until the mcp-twin block is implemented."""

import signal
import sys
import time

signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
print("mcp-twin: placeholder running", flush=True)
while True:
    time.sleep(3600)
