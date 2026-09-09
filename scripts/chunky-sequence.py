#!/usr/bin/env python3
"""Chain Chunky pregeneration tasks: poll the server log for the previous
task's finish marker, then start the next task via RCON. Lets you run
overnight pregeneration campaigns unattended.

Edit TASKS below: (finish_marker, [rcon commands to fire next]).

Known pitfall (MC 26.2 + Chunky): stopping/restarting the server puts a
running task into paused state and it will NOT resume by itself —
recover with `chunky continue` (`chunky start` replies "already started").
"""
import os
import subprocess
import sys
import time

LOG = "/opt/mcserver/server/logs/latest.log"
MAX_WAIT_HOURS = 2
RCON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mc-rcon.py")

FINISH_MARKER = "Task finished for minecraft:the_nether"
NEXT = [
    "chunky world minecraft:overworld",
    "chunky radius 5000",
    "chunky start",
]


def rcon(cmd):
    r = subprocess.run(
        ["python3", RCON, cmd],
        capture_output=True, text=True, timeout=30,
    )
    return (r.stdout + r.stderr).strip()


deadline = time.time() + MAX_WAIT_HOURS * 3600
while time.time() < deadline:
    try:
        with open(LOG, errors="replace") as f:
            log = f.read()
    except OSError:
        log = ""
    if FINISH_MARKER in log:
        break
    time.sleep(60)
else:
    print("TIMEOUT waiting for previous chunky task")
    sys.exit(1)

print("previous task done -> starting next", flush=True)
for cmd in NEXT:
    print(rcon(cmd), flush=True)
print("NEXT TASK STARTED", flush=True)
