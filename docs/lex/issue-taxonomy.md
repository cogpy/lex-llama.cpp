# Issue taxonomy

Create these labels on the GitHub repo (Settings → Labels or `gh label create`)
before large-scale feature work. They match plan §3.4.

## Area labels

| Label | Color suggestion | Use for |
|-------|------------------|---------|
| `area:ggml-backend` | `#5319E7` | Backend ops/kernels |
| `area:memory` | `#1D76DB` | KV / SWA / hybrid / recurrent memory |
| `area:server` | `#B60205` | `llama-server`, router, HTTP |
| `area:chat` | `#D93F0B` | Templates, tool calling, parsers |
| `area:packaging` | `#0E8A16` | CMake, containers, presets, install |
| `area:models` | `#FBCA04` | Conversion, arch enablement |
| `area:security` | `#BFDADC` | Auth, bind defaults, MCP/tools safety |
| `area:perf` | `#C5DEF5` | Bench, sched, kernels perf |
| `area:lex` | `#006B75` | Fork docs/product-only work |

## Type labels

| Label | Use for |
|-------|---------|
| `type:bug` | Incorrect behavior |
| `type:debt` | TODOs / structure cleanup |
| `type:feature` | New user-facing capability |
| `type:upstream-sync` | Merge/conflict follow-ups |
| `type:docs` | Documentation only |

## Tier labels

| Label | Meaning |
|-------|---------|
| `tier:1` | Blocks Lex quality bar / matrix |
| `tier:2` | Important but not release-blocking |
| `tier:3` | Nice-to-have / long-tail |

## Suggested epics (milestones)

Open tracking issues titled:

1. `Epic M0: Fork operable`
2. `Epic M1: Server reliability`
3. `Epic M2: Runtime solidification`
4. `Epic M3: Perf & backend floor`
5. `Epic M4: DX & packaging`
6. `Epic M5: Upstreaming & long-tail`

Link child issues with the labels above.

## Example `gh` bootstrap

```sh
gh label create "area:server" --color B60205 --description "llama-server / router / HTTP" || true
gh label create "area:lex" --color 006B75 --description "Lex product layer" || true
gh label create "type:upstream-sync" --color 0052CC --description "Upstream merge work" || true
gh label create "tier:1" --color E11D48 --description "Tier-1 support matrix" || true
# ...repeat for the full tables
```
