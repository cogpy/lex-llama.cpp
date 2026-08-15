# Lex (lex-llama.cpp)

`cogpy/lex-llama.cpp` is a product-oriented fork of
[ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp).

Lex tracks upstream closely and adds a thin product layer: curated support
matrix, safer operator defaults, packaging/presets, and fork CI that stays green
on GitHub-hosted runners.

## Who this is for

- Operators who want a reliable local OpenAI-compatible server (`llama-server`)
  with WebUI, tool calling, and optional multi-model router mode
- Developers integrating libllama / server HTTP APIs into apps
- Contributors improving inference quality on Tier-1 backends without forking
  the entire backend matrix on day one

## How Lex differs from upstream

| Area | Upstream llama.cpp | Lex |
|------|--------------------|-----|
| Mission | Broad research + every backend | Product fork with curated matrix |
| Default branch CI | Large multi-backend surface (`master`) | Minimal always-green CI on `main` |
| Docs | Upstream project docs | Plus `docs/lex/*` product docs |
| Presets | Generic INI presets | Lex safe/router preset library under `lex/presets/` |
| Divergence | N/A | Prefer Lex-only paths (`lex/`, `docs/lex/`) |

Deep runtime changes still live in shared trees (`src/`, `ggml/`, `tools/server/`)
when necessary, but product defaults and operator docs stay isolated to reduce
merge pain.

## Tier-1 products

- `llama-server` (+ WebUI, router mode)
- `llama-cli`
- `llama-quantize` / `llama-imatrix` / `llama-bench` / `llama-perplexity`

## Quick links

- [Support matrix](support-matrix.md)
- [Upstream sync runbook](upstream-sync.md)
- [Quality baselines](baselines.md)
- [Roadmap & backlog](roadmap.md)
- [Issue taxonomy](issue-taxonomy.md)
- [Safe server defaults](../../lex/presets/README.md)

## First-run path (CPU)

```sh
cmake --preset lex-cpu
cmake --build --preset lex-cpu -j
./build-lex-cpu/bin/llama-server \
  -hf ggml-org/gemma-3-1b-it-GGUF \
  --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080` for the WebUI.

For hardened local defaults, see `lex/presets/README.md`.

## Strategy

Lex follows **Strategy B with selective A contributions** (see issue #1):

1. Keep a regularly synced core with upstream llama.cpp
2. Land Lex product surface in predictable paths
3. Upstream high-signal runtime fixes when they are generally useful
