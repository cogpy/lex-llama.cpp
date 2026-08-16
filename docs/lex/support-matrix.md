# Lex support matrix

This is the **Tier-1 allowlist** Lex CI and release smoke tests optimize for.
Everything outside this matrix may work (inherited from upstream) but is not a
Lex release blocker.

Last updated: 2026-08-15

## Platforms (host OS)

| Platform | Status | Notes |
|----------|--------|-------|
| Linux x86_64 | Tier-1 | Primary CI (`lex-ci.yml`) |
| macOS Apple Silicon | Tier-1 | Metal builds validated upstream; Lex CI may be opt-in |
| Windows x86_64 | Tier-2 | Track upstream MSVC/LLVM workflows |
| Linux aarch64 | Tier-2 | Useful for edge; not PR-blocking yet |

## Backends

| Backend | Tier | Lex commitment |
|---------|------|----------------|
| CPU (x86-64 / ARM) | 1 | Always-green build + unit tests |
| CUDA | 1 | Perf/quality target; GPU runners optional |
| Metal | 1 | Apple Silicon first-class |
| Vulkan | 1 | Cross-vendor GPU path |
| HIP / SYCL / MUSA / OpenCL / WebGPU / CANN / Hexagon / OpenVINO / zDNN / ZenDNN | 2 | Timeboxed; docs must stay honest |

## Products / binaries

| Binary | Tier | Notes |
|--------|------|-------|
| `llama-server` | 1 | OAI + Anthropic compat, tools, WebUI, router |
| `llama-cli` | 1 | Interactive / batch CLI |
| `llama-bench` | 1 | PP/TG baselines |
| `llama-perplexity` | 1 | Quality baselines |
| `llama-quantize` / `llama-imatrix` | 1 | Quant ladder tooling |
| `llama-mtmd-*` | 2 | Multimodal CLI helpers |
| Other `tools/*` | 2 | As needed |

## Model allowlist (CI / baselines)

Small fixtures preferred for PR CI. Larger models are nightly/manual.

| Role | Model (HF GGUF) | Why |
|------|-----------------|-----|
| Tiny text (CI) | `ggml-org/models` stories / tinyllama fixtures used by server tests | Fast server pytest |
| Small instruct | `ggml-org/gemma-3-1b-it-GGUF` | First-run path |
| Small instruct (alt) | `ggml-org/tinygemma3-GGUF:Q8_0` | Router tests |
| MoE smoke | stories MoE fixture (`ServerPreset.stories15m_moe`) | MoE path coverage |
| Multimodal smoke | `ggml-org/tinygemma3-GGUF` + mmproj as used by vision tests | MTMD path |
| Tool-call templates | Jinja under `models/templates/` (see below) | Parser golden suite |

### Priority chat/tool template families

Golden tool-call coverage targets these families (template files in
`models/templates/`):

1. Llama 3.x (`meta-llama-Llama-3.1/3.2/3.3-*-Instruct`)
2. Hermes tool-use (`NousResearch-Hermes-2/3-*-tool_use`)
3. Qwen2.5 / Qwen3 (`Qwen-Qwen2.5-*`, `Qwen3-Coder`)
4. Mistral (`mistralai-Mistral-Nemo-Instruct-2407`)
5. DeepSeek reasoning distill (`deepseek-ai-DeepSeek-R1-Distill-*`)
6. Command-R tool use (`CohereForAI-c4ai-command-r*-tool_use`)
7. Functionary (`meetkai-functionary-medium-v3.*`) — slow/opt-in
8. Firefunction (`fireworks-ai-llama-3-firefunction-v2`) — slow/opt-in

## Quant ladder (recommended)

Curated defaults for Lex docs and presets (not exclusive):

| Use case | Quant | Notes |
|----------|-------|-------|
| Highest quality local | `Q8_0` / `Q6_K` | Reference quality |
| Default balanced | `Q5_K_M` / `Q4_K_M` | Primary recommend |
| Memory-tight | `Q4_K_S` / `IQ4_XS` | Validate PPL before shipping |
| Native MXFP4 models | vendor MXFP4 | When model ships native format |

Publish PPL + bench numbers in [baselines.md](baselines.md) before calling a
quant “Lex recommended” for a given family.

## Server feature flags

| Feature | Default (Lex safe profile) | Notes |
|---------|----------------------------|-------|
| Bind address | `127.0.0.1` | Localhost only |
| API key | required in safe profile | Optional upstream |
| Tools / MCP | off | Enable only in trusted envs |
| Router mode | opt-in | Powerful; document threat model |
| Backend sampling | off | Experimental |
| WebUI | on | Static assets remain public |

## Non-goals (matrix)

- Parity across every niche backend on every PR
- Multi-tenant SaaS hardening inside the server process
- Server-side multi-step agent loops (out of server scope)
