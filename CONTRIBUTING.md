# Git Conventions

## Branches

- `main`: always stable. **No direct commits**, except by the repository admin.
- One branch per task, created from `main`:

| Prefix      | Use                       | Example               |
|-------------|---------------------------|-----------------------|
| `feature/`  | New feature               | `feature/login-page`  |
| `fix/`      | Bug fix                   | `fix/null-user-crash` |
| `docs/`     | Documentation             | `docs/setup-guide`    |
| `refactor/` | Restructuring, no new behavior | `refactor/api-client` |
| `chore/`    | Config, dependencies, tooling | `chore/update-deps` |

Lowercase, words separated by hyphens, short and explicit.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <short imperative description>

[optional body: why, not how]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`.

Examples:

```
feat: add user login form
fix: handle empty response from API
docs: add installation steps to README
```

Rules:
- Description of 72 characters max, no trailing period.
- Imperative mood: "add", not "added" or "adds".
- One commit = one logical change. No "fix stuff" or "wip".

## Workflow

1. Update `main`: `git checkout main && git pull`
2. Create a branch: `git checkout -b feature/my-task`
3. Commit often, in small clean commits.
4. Push: `git push -u origin feature/my-task`
5. Open a Pull Request to `main`, with `Closes #N` in the description.
6. At least **one approved review from a code owner** (`.github/CODEOWNERS`). The repository admin can merge without it.
7. Merge with **squash and merge** (the only method enabled). The branch is deleted automatically.

## Pull Requests

- Title uses the commit format (`feat: ...`).
- Description: what changes, why, and how to test.
- Link the issue with `Closes #N`: on merge, the issue closes and the board moves it to Done.
- Keep PRs small and focused: one PR = one task.
- Rebase on `main` if the branch is behind: `git pull --rebase origin main`

## Never commit

- Secrets: passwords, API keys, `.env` files
- Generated files: `node_modules/`, `__pycache__/`, `dist/`, `build/`
- Personal IDE or OS files: `.vscode/`, `.idea/`, `.DS_Store`

List them in `.gitignore`.

## Third-party files

The repository is under the MIT license. Files we did not write (datasets, manuals, CAD) keep their original license: store them in their own folder with their source and LICENSE file.

## Checks

Use Python 3.12, the same version as the service containers:

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest
docker compose config --quiet
docker compose -f docker-compose.robot.yml config --quiet
```

CI runs these checks on every PR and push to `main`, and installs all service
packages from their `pyproject.toml` files. Tests live in `tests/` or in each
service's `tests/` folder. The initial suite exercises the robot-command mock
over HTTP: valid moves, invalid commands, duplicate requests, failures and stops.
It needs neither robot hardware nor a GPU. The standalone MCP mocks keep their
dependencies in their script headers and are run with `uv run` (see `contracts/mcp`).

`lint-and-test` is a required check: a PR cannot be merged while it fails.
