# Lex roadmap

Source plan: issue
[#1 — Implementation Plan: Improving lex-llama.cpp](https://github.com/cogpy/lex-llama.cpp/issues/1).

This file tracks **execution status** for milestones. Prefer vertical slices
with tests over broad rewrites.

## Milestones

### M0 — Fork operable (current)

- [x] Lex product docs (`docs/lex/`)
- [x] Support matrix + baseline command contract
- [x] Upstream sync runbook
- [x] Minimal CI on `main` (CPU build/tests + server tests)
- [x] Lex CMake presets + safe/router preset library
- [x] Router failure/stress tests expansion
- [x] Priority tool-call template golden expansion (fast path)
- [ ] First numerical bench/PPL rows committed (needs model artifacts on a runner)
- [ ] GitHub labels/epics created from [issue-taxonomy.md](issue-taxonomy.md)

### M1 — Server reliability

- [ ] Router lifecycle productionization beyond tests (timeouts, memory pressure)
- [ ] Tool-calling metrics on fixed suite
- [ ] Speculative: metrics + shared draft decision
- [ ] WebUI smoke e2e chat + model switch
- [ ] Security defaults profile wired into docs/scripts (presets landed in M0)

### M2 — Runtime solidification

- [ ] Arch interface extraction (incremental)
- [ ] Memory save/restore + SWA metadata
- [ ] Graph reuse `can_reuse` coverage
- [ ] Backend sampling ship-or-hide decision

### M3 — Perf & backend floor

- [ ] FA/MoE/vision op gaps on Tier-1
- [ ] Published quant ladder with numbers
- [ ] Nightly perf gates

### M4 — DX & packaging

- [ ] Containers + richer preset library
- [ ] Conversion modularization start
- [ ] Versioned API/REST changelog process

### M5 — Selective upstreaming / long-tail

- [ ] Upstream-bound patches cherry-picked cleanly
- [ ] Tier-2 backends on demand
- [ ] Advanced multimodal device-path embeddings

## P0 backlog (from plan §12)

| # | Item | Status |
|---|------|--------|
| 1 | Define Lex support matrix + baseline benches | Matrix + commands done; numbers pending |
| 2 | Wire minimal CI (CPU build/tests + server tests) | `lex-ci.yml` |
| 3 | Router load/unload stress + failure UX tests | Expanded `test_router.py` |
| 4 | Tool-call golden tests for priority templates | Expanded fast golden set |
| 5 | Document upstream merge process | `upstream-sync.md` |

## Execution principles

1. Vertical slices, not horizontal rewrites
2. One subsystem per change set
3. Measure before claiming wins
4. CPU correctness first
5. Isolate Lex product code when possible
6. Every bug becomes a regression test
7. Respect server scope (`tools/server/README-dev.md`)
