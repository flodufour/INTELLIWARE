"""Mock robot controller implementing the robot-command contract (README.md).

Standard library only. Run: python mock.py [port]
"""

import json
import re
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TEMPLATES = {
    "store": "store the {part} in slot {slot}",
    "retrieve": "pick the {part} from slot {slot}",
    "home": "go home",
}
SLOT = re.compile(r"^[A-Z][1-9]$")
TASK_SECONDS = 3
MAX_ATTEMPTS = 3

tasks: dict[str, dict] = {}
current: str | None = None
lock = threading.Lock()


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate(cmd: dict) -> str | None:
    """Return an error message, or None if the command is valid."""
    action = cmd.get("action")
    if not isinstance(cmd.get("task_id"), str) or not cmd["task_id"]:
        return "task_id is required"
    if action not in TEMPLATES:
        return f"action must be one of {sorted(TEMPLATES)}"
    if action != "home":
        if not isinstance(cmd.get("part"), str) or not cmd["part"].islower():
            return "part must be a lowercase name"
        if not isinstance(cmd.get("slot"), str) or not SLOT.match(cmd["slot"]):
            return "slot must match ^[A-Z][1-9]$"
    expected = TEMPLATES[action].format(part=cmd.get("part"), slot=cmd.get("slot"))
    if cmd.get("instruction") != expected:
        return f"instruction must be '{expected}'"
    return None


def finish(task: dict, status: str, **fields) -> None:
    task.update(status=status, finished_at=now(), **fields)


def run(cmd: dict) -> None:
    global current
    task = tasks[cmd["task_id"]]
    action = cmd["action"]
    source = "tray" if action == "store" else "slot"
    target = "slot" if action == "store" else "tray"
    task.update(status="running", started_at=now())

    if cmd.get("slot") == "Z9":
        finish(task, "failed", failure="part_missing", part_location="unknown",
               message=f"no part in {source}")
    else:
        attempts = MAX_ATTEMPTS if cmd.get("part") == "broken" else 1
        for attempt in range(1, attempts + 1):
            task["attempts"] = attempt
            time.sleep(TASK_SECONDS / attempts)
            if task["status"] == "stopped":
                break
        if task["status"] == "stopped":
            pass
        elif cmd.get("part") == "broken":
            finish(task, "failed", failure="grasp_failed", part_location=source,
                   message=f"part dropped {MAX_ATTEMPTS} times")
        else:
            finish(task, "succeeded", part_location=None if action == "home" else target,
                   message="done")
    with lock:
        current = None


class Handler(BaseHTTPRequestHandler):
    def reply(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.reply(200, {"state": "busy" if current else "idle", "task_id": current})
        elif self.path.startswith("/tasks/") and self.path[7:] in tasks:
            self.reply(200, tasks[self.path[7:]])
        else:
            self.reply(404, {"error": "not found"})

    def do_POST(self) -> None:
        global current
        if self.path == "/stop":
            with lock:
                task = tasks.get(current) if current else None
                if task:
                    finish(task, "stopped", message="stopped on request")
            self.reply(200, task or {})
            return
        if self.path != "/tasks":
            self.reply(404, {"error": "not found"})
            return
        try:
            cmd = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except (ValueError, TypeError):
            self.reply(422, {"error": "body must be JSON"})
            return
        if not isinstance(cmd, dict) or (error := validate(cmd)):
            self.reply(422, {"error": error or "body must be an object"})
            return
        with lock:
            if cmd["task_id"] in tasks:
                self.reply(202, tasks[cmd["task_id"]])
                return
            if current:
                self.reply(409, {"error": f"task {current} is running"})
                return
            current = cmd["task_id"]
            tasks[current] = {
                "task_id": current, "status": "queued", "attempts": 0, "failure": None,
                "part_location": None if cmd["action"] == "home" else
                ("tray" if cmd["action"] == "store" else "slot"),
                "message": "", "started_at": None, "finished_at": None,
            }
            self.reply(202, tasks[current])
        threading.Thread(target=run, args=(cmd,), daemon=True).start()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8100
    print(f"mock robot controller on :{port}", flush=True)
    ThreadingHTTPServer(("", port), Handler).serve_forever()
