# Git Conventions

## Branches

- `main`: always stable. **No direct commits.**
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
5. Open a Pull Request to `main`.
6. At least **one approved review** before merging.
7. Merge with **squash and merge**, then delete the branch.

## Pull Requests

- Title uses the commit format (`feat: ...`).
- Description: what changes, why, and how to test.
- Keep PRs small and focused: one PR = one task.
- Rebase on `main` if the branch is behind: `git pull --rebase origin main`

## Never commit

- Secrets: passwords, API keys, `.env` files
- Generated files: `node_modules/`, `__pycache__/`, `dist/`, `build/`
- Personal IDE or OS files: `.vscode/`, `.idea/`, `.DS_Store`

List them in `.gitignore`.
