#!/usr/bin/env bash
# Run Lex baseline bench (and optional perplexity) and write artifacts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$ROOT/build-lex-cpu}"
OUT_DIR="${OUT_DIR:-$ROOT/docs/lex/baselines}"
MODEL=""
WIKITEXT=""
THREADS="${THREADS:-$(nproc 2>/dev/null || sysctl -n hw.logicalcpu)}"
NGL="${NGL:-0}"
PROMPT_TOKENS="${PROMPT_TOKENS:-512}"
GEN_TOKENS="${GEN_TOKENS:-128}"
HW_ID="${HW_ID:-dev-local}"
RUN_PPL=0

usage() {
    cat <<EOF
Usage: $(basename "$0") --model PATH [options]

Options:
  --model PATH          GGUF model path (required)
  --out DIR             Artifact directory (default: docs/lex/baselines)
  --build-dir DIR       Build directory (default: build-lex-cpu)
  --threads N           CPU threads (default: nproc)
  --ngl N               GPU layers (default: 0)
  --prompt-tokens N     llama-bench -p (default: 512)
  --gen-tokens N        llama-bench -n (default: 128)
  --wikitext PATH       If set (or --ppl), run llama-perplexity on this file
  --ppl                 Require --wikitext and run perplexity
  --hw-id ID            Hardware label (default: dev-local)
  -h, --help            Show help
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model) MODEL="$2"; shift 2 ;;
        --out) OUT_DIR="$2"; shift 2 ;;
        --build-dir) BUILD_DIR="$2"; shift 2 ;;
        --threads) THREADS="$2"; shift 2 ;;
        --ngl) NGL="$2"; shift 2 ;;
        --prompt-tokens) PROMPT_TOKENS="$2"; shift 2 ;;
        --gen-tokens) GEN_TOKENS="$2"; shift 2 ;;
        --wikitext) WIKITEXT="$2"; RUN_PPL=1; shift 2 ;;
        --ppl) RUN_PPL=1; shift ;;
        --hw-id) HW_ID="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
done

if [[ -z "$MODEL" ]]; then
    echo "--model is required" >&2
    usage >&2
    exit 2
fi
if [[ ! -f "$MODEL" ]]; then
    echo "Model not found: $MODEL" >&2
    exit 1
fi

BENCH_BIN="$BUILD_DIR/bin/llama-bench"
PPL_BIN="$BUILD_DIR/bin/llama-perplexity"
if [[ ! -x "$BENCH_BIN" ]]; then
    echo "Missing $BENCH_BIN — build with: cmake --preset lex-cpu && cmake --build --preset lex-cpu -j --target llama-bench" >&2
    exit 1
fi

mkdir -p "$OUT_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
COMMIT="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
MODEL_BASE="$(basename "$MODEL" .gguf)"
CSV_PATH="$OUT_DIR/bench-${HW_ID}-${MODEL_BASE}-${STAMP}.csv"
LOG_PATH="$OUT_DIR/bench-${HW_ID}-${MODEL_BASE}-${STAMP}.log"

{
    echo "lex baseline"
    echo "date_utc=$STAMP"
    echo "commit=$COMMIT"
    echo "hw_id=$HW_ID"
    echo "model=$MODEL"
    echo "threads=$THREADS"
    echo "ngl=$NGL"
    echo "prompt_tokens=$PROMPT_TOKENS"
    echo "gen_tokens=$GEN_TOKENS"
    echo "bench_bin=$BENCH_BIN"
} | tee "$LOG_PATH"

echo "Running llama-bench → $CSV_PATH"
"$BENCH_BIN" \
    -m "$MODEL" \
    -p "$PROMPT_TOKENS" \
    -n "$GEN_TOKENS" \
    -t "$THREADS" \
    -ngl "$NGL" \
    -o csv | tee -a "$LOG_PATH" | tee "$CSV_PATH"

if [[ "$RUN_PPL" -eq 1 ]]; then
    if [[ -z "$WIKITEXT" || ! -f "$WIKITEXT" ]]; then
        echo "--ppl requires an existing --wikitext PATH" >&2
        exit 1
    fi
    if [[ ! -x "$PPL_BIN" ]]; then
        echo "Missing $PPL_BIN — build target llama-perplexity" >&2
        exit 1
    fi
    PPL_LOG="$OUT_DIR/ppl-${HW_ID}-${MODEL_BASE}-${STAMP}.log"
    echo "Running llama-perplexity → $PPL_LOG"
    "$PPL_BIN" \
        -m "$MODEL" \
        -f "$WIKITEXT" \
        -t "$THREADS" \
        -ngl "$NGL" | tee -a "$LOG_PATH" | tee "$PPL_LOG"
fi

echo "Done. Update docs/lex/baselines/SUMMARY.md with headline numbers."
