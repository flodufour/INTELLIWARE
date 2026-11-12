# robot-command

Command format between the robot MCP server (`services/mcp-robot`, main machine) and the robot controller (`services/robot`, robot machine). Issue #16.

The robot MCP server sends one task at a time. The controller runs it, checks the result with vision, and reports a status. Human confirmation and twin updates happen before and after, in the MCP server; the controller never talks to the twin.

## Transport

HTTP with JSON bodies. The two services run on different machines, so ROS 2 stays inside the robot block.

- Base URL: `ROBOT_URL` environment variable of the MCP server, default `http://localhost:8100`.
- Tasks are asynchronous: the MCP server creates a task, then polls its status (every 0.5 s is enough).

| Method | Path | Body | Response |
|--------|------|------|----------|
| `POST` | `/tasks` | Command | `202` Task status (`queued`), `409` if a task is already running, `422` if the command is invalid |
| `GET` | `/tasks/{task_id}` | | `200` Task status, `404` if unknown |
| `POST` | `/stop` | | `200` Task status of the stopped task, or `{}` if idle. Stops the arm at once and frees the robot (see [Stop](#stop)) |
| `GET` | `/health` | | `200` `{"state": "idle" \| "busy" \| "error", "task_id": "..." \| null}` |

## Command

```json
{
  "task_id": "3f2b8c1e-9a4d-4e7b-8f0a-2c6d1e5b7a90",
  "action": "retrieve",
  "part": "propeller",
  "slot": "B2",
  "instruction": "pick the propeller from slot B2"
}
```

| Field | Type | Rule |
|-------|------|------|
| `task_id` | string | Unique id chosen by the MCP server (a UUID), reused in the twin trace. Sending the same `task_id` again returns the existing task |
| `action` | string | `store`, `retrieve` or `home` |
| `part` | string | Part type name in English, lowercase, as in the twin (e.g. `propeller`). Omitted for `home` |
| `slot` | string | Slot id as in the twin: level letter and position, e.g. `A1`, `B2` (`^[A-Z][1-9]$`). Omitted for `home` |
| `instruction` | string | Rendered from the template below, exactly |

### Instructions

The VLA is trained on these sentences and nothing else, so they are fixed. The agent maps any French or English request to an action, a part and a slot; the MCP server renders the English sentence.

| Action | Template | Start | End |
|--------|----------|-------|-----|
| `store` | `store the {part} in slot {slot}` | Part on the tray | Part in the slot, arm at home |
| `retrieve` | `pick the {part} from slot {slot}` | Part in the slot | Part on the tray, arm at home |
| `home` | `go home` | Any | Arm at home pose, gripper open |

The controller rejects with `422` a command whose `instruction` does not match its fields.

## Task status

```json
{
  "task_id": "3f2b8c1e-9a4d-4e7b-8f0a-2c6d1e5b7a90",
  "status": "failed",
  "attempts": 3,
  "failure": "grasp_failed",
  "part_location": "slot",
  "message": "part dropped back into slot B2 three times",
  "started_at": "2026-11-12T14:03:05Z",
  "finished_at": "2026-11-12T14:03:52Z"
}
```

| Field | Type | Rule |
|-------|------|------|
| `task_id` | string | From the command |
| `status` | string | `queued`, `running`, `succeeded`, `failed`, `stopped` |
| `attempts` | integer | Grasp attempts so far, `0` before the first |
| `failure` | string or null | Set only when `status` is `failed`, see below |
| `part_location` | string or null | Where vision last saw the part: `slot`, `tray`, `gripper`, `unknown`. Reported from vision on every final status, including `stopped`. Null for `home` |
| `message` | string | Short English text for logs and the technician |
| `started_at`, `finished_at` | string or null | ISO 8601 UTC |

`succeeded`, `failed` and `stopped` are final. The MCP server updates the twin from `part_location`: on success the part is where the task said; otherwise the twin is corrected and the next scan confirms.

### Failures

| `failure` | When | Retried by the controller |
|-----------|------|---------------------------|
| `part_missing` | No part in the source (slot for `retrieve`, tray for `store`) | No |
| `target_occupied` | Destination not free (slot for `store`, tray for `retrieve`) | No |
| `grasp_failed` | Part dropped or not grasped after the last attempt | Yes, up to 3 attempts in total |
| `timeout` | Task longer than 120 s | No |
| `robot_error` | Driver, CAN or vision error | No |

Every failure ends with the arm stopped in a safe pose. A missing part is always reported, never retried silently.

## Stop

`POST /stop` is a software stop only: it depends on the network and the software. **A physical emergency stop on the arm remains mandatory, whatever the software state.** Safety rules: Antoine, sprint 2.

After a stop the robot is free at once (`/health` returns `idle`). The part may be in the gripper: `part_location` says where vision sees it (`gripper` or `unknown`), and the twin is corrected from it.

## Mock

[mock.py](mock.py) is a mock controller with no dependencies, for working on the MCP server without the robot. Each task takes 3 s and succeeds, except:

- slot `Z9`: `part_missing`
- part `broken`: `grasp_failed` after 3 attempts

```sh
python contracts/robot-command/mock.py            # listens on :8100
curl -X POST localhost:8100/tasks -d '{"task_id": "t1", "action": "retrieve", "part": "propeller", "slot": "B2", "instruction": "pick the propeller from slot B2"}'
curl localhost:8100/tasks/t1
```
