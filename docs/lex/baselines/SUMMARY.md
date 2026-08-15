# Baseline summary

Status: **commands defined, numbers pending first reference run**.

See [../baselines.md](../baselines.md) for the measurement contract and
`lex/scripts/baseline-bench.sh` to produce CSV artifacts.

## Latest accepted results

| Date | HW id | Model | Quant | Backend | PP tok/s | TG tok/s | PPL | Commit | Notes |
|------|-------|-------|-------|---------|----------|----------|-----|--------|-------|
| _TBD_ | cpu-ref | gemma-3-1b-it | Q4_K_M | cpu | — | — | — | — | Fill after first run |

## How to update

1. Build with `cmake --preset lex-cpu && cmake --build --preset lex-cpu -j`
2. Run `./lex/scripts/baseline-bench.sh --model /path/to/model.gguf --out docs/lex/baselines`
3. Paste headline numbers into the table above
4. Commit CSV + this summary in the same PR
