# Lex presets

INI presets for operator-friendly defaults. See upstream
[docs/preset.md](../../docs/preset.md) for syntax.

## Files

| File | Purpose |
|------|---------|
| `safe-local.ini` | Hardened single-process mental model (document flags; use with CLI) |
| `router-models.ini` | Example `--models-preset` for router mode with CI-sized models |

## Safe local server

Local bind + API key + tools off are **server process flags**, not always
expressible as per-model preset keys. Recommended invocation:

```sh
export LLAMA_API_KEY="change-me"

./build-lex-cpu/bin/llama-server \
  -m /path/to/model.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  --api-key "$LLAMA_API_KEY" \
  -c 8192 \
  -t "$(nproc)" \
  -ngl 0
```

Do **not** enable MCP / built-in tools unless the environment is fully trusted.
See `SECURITY.md` and `docs/lex/support-matrix.md`.

## Router example

```sh
./build-lex-cpu/bin/llama-server \
  --models-preset lex/presets/router-models.ini \
  --models-max 2 \
  --host 127.0.0.1 \
  --port 8080 \
  --api-key "$LLAMA_API_KEY"
```

Adjust HF repo tags and context sizes for your hardware before production use.
