# Upstream sync runbook

Lex regularly merges from [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp).
Goal: keep conflict cost low and avoid forking `ggml/` unless necessary.

## Remotes

```sh
# once per clone
git remote add upstream https://github.com/ggml-org/llama.cpp.git || true
git fetch upstream
git fetch origin
```

Default Lex branch: `main`  
Upstream default branch: `master`

## Cadence

- **Weekly** (preferred): merge `upstream/master` into `main`
- **Emergency**: cherry-pick critical security/correctness fixes anytime
- Record sync notes in the PR body (conflict hotspots + follow-ups)

## Merge procedure

```sh
git checkout main
git pull origin main
git fetch upstream
git checkout -b sync/upstream-$(date +%Y%m%d)
git merge upstream/master
# resolve conflicts
cmake --preset lex-cpu && cmake --build --preset lex-cpu -j
ctest --test-dir build-lex-cpu -L main --output-on-failure --timeout 900
# optional: server tests if tools/server touched
git push -u origin HEAD
# open PR into main
```

### Conflict ownership (by path)

| Path | Owner focus |
|------|-------------|
| `lex/`, `docs/lex/`, `.github/workflows/lex-*.yml` | Lex product — rarely touch upstream |
| `tools/server/**` | Server maintainers; high churn upstream |
| `src/**`, `include/**` | Runtime; prefer small Lex deltas |
| `ggml/**` | Avoid Lex-only edits; upstream-first |
| `common/**` | Shared CLI/params; merge carefully |
| `models/templates/**` | Usually take upstream unless Lex golden needs pin |
| `convert_hf_to_gguf.py`, `gguf-py/**` | Conversion; test after merge |

## Isolation rules

Prefer Lex-only changes under:

- `lex/` — presets, helper scripts, product CLI wrappers
- `docs/lex/` — fork docs
- `.github/workflows/lex-*.yml` — fork CI

Avoid drive-by formatting or renames in upstream files; they multiply conflicts.

## After merge checklist

- [ ] `lex-ci` workflow green on the sync PR
- [ ] Skim upstream release notes / breaking API changes (`include/llama.h`, server REST)
- [ ] Update [support-matrix.md](support-matrix.md) if backends/products changed
- [ ] Refresh baseline commands if bench flags changed ([baselines.md](baselines.md))
- [ ] File follow-up issues for deferred conflicts (label `type:upstream-sync`)

## Upstream contribution

When a Lex fix is generally useful:

1. Extract a minimal patch against upstream `master`
2. Follow upstream `CONTRIBUTING.md` / `AGENTS.md` (human-owned, small PRs)
3. Do **not** open fully AI-generated PRs upstream
4. After upstream merge, drop the Lex duplicate on next sync

## Abort / rollback

If a sync is too hot:

```sh
git merge --abort   # if still in progress
# or revert the merge commit on main after review
```

Ship a smaller cherry-pick set instead of a full merge when time-boxed.
