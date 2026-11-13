"""Exercise the robot-command mock over HTTP, without an arm or a GPU."""

import importlib.util
import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest


@pytest.fixture
def controller():
    path = Path(__file__).resolve().parents[2] / "contracts/robot-command/mock.py"
    spec = importlib.util.spec_from_file_location("robot_command_mock", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.TASK_SECONDS = 0.5
    server = module.ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    def request(method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            base_url + path, data=data, method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            response = urllib.request.urlopen(req, timeout=3)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    try:
        yield request
    finally:
        try:
            request("POST", "/stop")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def command(task_id="test-task", action="retrieve", part="propeller", slot="A1"):
    template = "store the {part} in slot {slot}" if action == "store" else "pick the {part} from slot {slot}"
    return {
        "task_id": task_id, "action": action, "part": part, "slot": slot,
        "instruction": template.format(part=part, slot=slot),
    }


def wait_for_task(controller, task_id, statuses=("succeeded", "failed", "stopped")):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        status, task = controller("GET", f"/tasks/{task_id}")
        assert status == 200
        if task["status"] in statuses:
            return task
        time.sleep(0.01)
    pytest.fail(f"Task {task_id} did not reach {statuses}")


@pytest.mark.parametrize(("action", "location"), [("store", "slot"), ("retrieve", "tray")])
def test_completed_move_reports_location(controller, action, location):
    assert controller("POST", "/tasks", command(action=action))[0] == 202
    task = wait_for_task(controller, "test-task")
    assert task["status"] == "succeeded"
    assert task["part_location"] == location
    assert task["failure"] is None
    assert task["started_at"] and task["finished_at"]
    assert controller("GET", "/health")[1] == {"state": "idle", "task_id": None}


@pytest.mark.parametrize("change", [{"instruction": "move somewhere"}, {"slot": "a1"}])
def test_invalid_command_does_not_start_a_move(controller, change):
    assert controller("POST", "/tasks", command() | change)[0] == 422
    assert controller("GET", "/health")[1]["state"] == "idle"


def test_duplicate_task_is_idempotent_and_another_task_is_rejected(controller):
    cmd = command()
    assert controller("POST", "/tasks", cmd)[0] == 202
    assert controller("POST", "/tasks", cmd)[0] == 202
    assert controller("POST", "/tasks", command(task_id="another-task"))[0] == 409
    assert wait_for_task(controller, "test-task")["status"] == "succeeded"
    assert controller("GET", "/tasks/another-task")[0] == 404


@pytest.mark.parametrize(
    ("part", "slot", "failure", "location", "attempts"),
    [("propeller", "Z9", "part_missing", "unknown", 0),
     ("broken", "A1", "grasp_failed", "slot", 3)],
)
def test_failure_reports_reason_and_part_location(controller, part, slot, failure, location, attempts):
    assert controller("POST", "/tasks", command(part=part, slot=slot))[0] == 202
    task = wait_for_task(controller, "test-task")
    assert task["status"] == "failed"
    assert (task["failure"], task["part_location"], task["attempts"]) == (failure, location, attempts)


def test_stop_frees_robot_and_cannot_be_overwritten_by_completion(controller):
    assert controller("POST", "/tasks", command())[0] == 202
    wait_for_task(controller, "test-task", statuses=("running",))
    status, stopped = controller("POST", "/stop")
    assert status == 200
    assert stopped["status"] == "stopped"
    assert stopped["part_location"] == "unknown"
    assert controller("GET", "/health")[1] == {"state": "idle", "task_id": None}

    home = {"task_id": "home-after-stop", "action": "home", "instruction": "go home"}
    assert controller("POST", "/tasks", home)[0] == 202
    assert wait_for_task(controller, "home-after-stop")["status"] == "succeeded"
    assert controller("GET", "/tasks/test-task")[1]["status"] == "stopped"
