# Quality baselines

Lex tracks **prompt processing (PP)** and **token generation (TG)** separately,
plus perplexity (PPL) on fixed prompts/models from the
[support matrix](support-matrix.md).

Numbers below start as a **command contract**. Fill measured values after the
first baseline run on reference hardware and commit CSV/JSON artifacts under
`docs/lex/baselines/`.

## Golden commands

Build (CPU reference):

```sh
cmake --preset lex-cpu
cmake --build --preset lex-cpu -j --target llama-bench llama-perplexity llama-server llama-cli
```

Or use the helper:

```sh
./lex/scripts/baseline-bench.sh --help
./lex/scripts/baseline-bench.sh --model /path/to/model.gguf --out docs/lex/baselines
```

### Bench (PP / TG)

```sh
./build-lex-cpu/bin/llama-bench \
  -m "$MODEL" \
  -p 512 -n 128 \
  -t "$(nproc)" \
  -ngl 0 \
  -o csv
```

Record at least:

| Field | Meaning |
|-------|---------|
| `pp512` | Prompt processing tok/s @ 512 prompt |
| `tg128` | Generation tok/s @ 128 tokens |
| `n_threads` | CPU threads |
| `n_gpu_layers` | Offload depth (`0` = CPU-only) |
| `backend` | cpu / cuda / metal / vulkan |
| `model` | GGUF name + quant |
| `commit` | git SHA |

### Perplexity

```sh
./build-lex-cpu/bin/llama-perplexity \
  -m "$MODEL" \
  -f "$WIKITEXT" \
  -t "$(nproc)" \
  -ngl 0
```

Use a fixed evaluation file (e.g. wikitext-2 raw) and record PPL + runtime.

### Server latency (optional smoke)

```sh
./build-lex-cpu/bin/llama-server -m "$MODEL" --host 127.0.0.1 --port 8080 &
# warm-up + measure p50/p95 for short completion requests
```

Router concurrency should use `-np` / multi-slot configurations when measuring
multi-user realism.

## Reference hardware labels

Tag every result row with a hardware id:

| ID | Description |
|----|-------------|
| `cpu-ref` | GitHub `ubuntu-latest` or equivalent CI CPU |
| `dev-local` | Contributor workstation (specify CPU/GPU in notes) |
| `gpu-cuda-ref` | Named NVIDIA GPU + driver |
| `gpu-metal-ref` | Named Apple Silicon |

## Results store

| Path | Contents |
|------|----------|
| `docs/lex/baselines/README.md` | How to read artifacts |
| `docs/lex/baselines/*.csv` | `llama-bench` CSV outputs |
| `docs/lex/baselines/SUMMARY.md` | Human-readable latest numbers |

Do not commit huge model files. Artifacts are numbers + command lines only.

## Regression policy (initial)

| Metric | PR CI | Nightly |
|--------|-------|---------|
| Build + ctest | required | required |
| Server pytest (`not slow`) | required | required |
| Bench/PPL vs baseline | manual / optional | fail if TG or PP regresses > 10% on `cpu-ref` without note |
| Full backend-ops | optional | Tier-1 when runners exist |

## First baseline checklist

- [ ] Record CPU bench for `gemma-3-1b-it` Q4_K_M (or matrix default)
- [ ] Record PPL on fixed wikitext sample
- [ ] Record server short-completion latency smoke
- [ ] Link hardware notes in `SUMMARY.md`
