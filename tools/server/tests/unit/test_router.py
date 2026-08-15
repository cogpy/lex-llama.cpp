import pytest
from utils import *

server: ServerProcess

@pytest.fixture(autouse=True)
def create_server():
    global server
    server = ServerPreset.router()


def test_router_props():
    global server
    server.models_max = 2
    server.no_models_autoload = True
    server.start()
    res = server.make_request("GET", "/props")
    assert res.status_code == 200
    assert res.body["role"] == "router"
    assert res.body["max_instances"] == 2
    assert res.body["models_autoload"] is False
    assert res.body["build_info"].startswith("b")


@pytest.mark.parametrize(
    "model,success",
    [
        ("ggml-org/tinygemma3-GGUF:Q8_0", True),
        ("non-existent/model", False),
    ]
)
def test_router_chat_completion_stream(model: str, success: bool):
    global server
    server.start()
    content = ""
    ex: ServerError | None = None
    try:
        res = server.make_stream_request("POST", "/chat/completions", data={
            "model": model,
            "max_tokens": 16,
            "messages": [
                {"role": "user", "content": "hello"},
            ],
            "stream": True,
        })
        for data in res:
            if data["choices"]:
                choice = data["choices"][0]
                if choice["finish_reason"] in ["stop", "length"]:
                    assert "content" not in choice["delta"]
                else:
                    assert choice["finish_reason"] is None
                    content += choice["delta"]["content"] or ''
    except ServerError as e:
        ex = e

    if success:
        assert ex is None
        assert len(content) > 0
    else:
        assert ex is not None
        assert content == ""


def _get_model_status(model_id: str) -> str:
    res = server.make_request("GET", "/models")
    assert res.status_code == 200
    for item in res.body.get("data", []):
        if item.get("id") == model_id or item.get("model") == model_id:
            return item["status"]["value"]
    raise AssertionError(f"Model {model_id} not found in /models response")


def _wait_for_model_status(model_id: str, desired: set[str], timeout: int = 60) -> str:
    deadline = time.time() + timeout
    last_status = None
    while time.time() < deadline:
        last_status = _get_model_status(model_id)
        if last_status in desired:
            return last_status
        time.sleep(1)
    raise AssertionError(
        f"Timed out waiting for {model_id} to reach {desired}, last status: {last_status}"
    )


def _load_model_and_wait(
    model_id: str, timeout: int = 60, headers: dict | None = None
) -> None:
    load_res = server.make_request(
        "POST", "/models/load", data={"model": model_id}, headers=headers
    )
    assert load_res.status_code == 200
    assert isinstance(load_res.body, dict)
    assert load_res.body.get("success") is True
    _wait_for_model_status(model_id, {"loaded"}, timeout=timeout)


def test_router_unload_model():
    global server
    server.start()
    model_id = "ggml-org/tinygemma3-GGUF:Q8_0"

    _load_model_and_wait(model_id)

    unload_res = server.make_request("POST", "/models/unload", data={"model": model_id})
    assert unload_res.status_code == 200
    assert unload_res.body.get("success") is True
    _wait_for_model_status(model_id, {"unloaded"})


def test_router_models_max_evicts_lru():
    global server
    server.models_max = 2
    server.start()

    candidate_models = [
        "ggml-org/tinygemma3-GGUF:Q8_0",
        "ggml-org/test-model-stories260K:F32",
        "ggml-org/test-model-stories260K-infill:F32",
    ]

    # Load only the first 2 models to fill the cache
    first, second, third = candidate_models[:3]

    _load_model_and_wait(first, timeout=120)
    _load_model_and_wait(second, timeout=120)

    # Verify both models are loaded
    assert _get_model_status(first) == "loaded"
    assert _get_model_status(second) == "loaded"

    # Load the third model - this should trigger LRU eviction of the first model
    _load_model_and_wait(third, timeout=120)

    # Verify eviction: third is loaded, first was evicted
    assert _get_model_status(third) == "loaded"
    assert _get_model_status(first) == "unloaded"


def test_router_no_models_autoload():
    global server
    server.no_models_autoload = True
    server.start()
    model_id = "ggml-org/tinygemma3-GGUF:Q8_0"

    res = server.make_request(
        "POST",
        "/v1/chat/completions",
        data={
            "model": model_id,
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 4,
        },
    )
    assert res.status_code == 400
    assert "error" in res.body

    _load_model_and_wait(model_id)

    success_res = server.make_request(
        "POST",
        "/v1/chat/completions",
        data={
            "model": model_id,
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 4,
        },
    )
    assert success_res.status_code == 200
    assert "error" not in success_res.body


def test_router_api_key_required():
    global server
    server.api_key = "sk-router-secret"
    server.start()

    model_id = "ggml-org/tinygemma3-GGUF:Q8_0"
    auth_headers = {"Authorization": f"Bearer {server.api_key}"}

    res = server.make_request(
        "POST",
        "/v1/chat/completions",
        data={
            "model": model_id,
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 4,
        },
    )
    assert res.status_code == 401
    assert res.body.get("error", {}).get("type") == "authentication_error"

    _load_model_and_wait(model_id, headers=auth_headers)

    authed = server.make_request(
        "POST",
        "/v1/chat/completions",
        headers=auth_headers,
        data={
            "model": model_id,
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 4,
        },
    )
    assert authed.status_code == 200
    assert "error" not in authed.body


def test_router_load_model_not_found():
    global server
    server.no_models_autoload = True
    server.start()

    res = server.make_request(
        "POST", "/models/load", data={"model": "non-existent/model"}
    )
    assert res.status_code == 404
    assert "error" in res.body
    err = res.body["error"]
    assert "not found" in err.get("message", "").lower()


def test_router_unload_model_not_found():
    global server
    server.start()

    res = server.make_request(
        "POST", "/models/unload", data={"model": "non-existent/model"}
    )
    assert res.status_code in (400, 404)
    assert "error" in res.body
    err = res.body["error"]
    assert "not found" in err.get("message", "").lower()


def test_router_unload_model_not_running():
    global server
    server.no_models_autoload = True
    server.start()
    model_id = "ggml-org/tinygemma3-GGUF:Q8_0"

    # Ensure the model is known but not running.
    assert _get_model_status(model_id) != "loaded"

    res = server.make_request("POST", "/models/unload", data={"model": model_id})
    assert res.status_code == 400
    assert "error" in res.body
    assert "not running" in res.body["error"].get("message", "").lower()


def test_router_load_already_running():
    global server
    server.start()
    model_id = "ggml-org/tinygemma3-GGUF:Q8_0"

    _load_model_and_wait(model_id)

    res = server.make_request("POST", "/models/load", data={"model": model_id})
    assert res.status_code == 400
    assert "error" in res.body
    assert "already running" in res.body["error"].get("message", "").lower()


def test_router_concurrent_load_unload_stress():
    """Lex P0: concurrent admin load/unload should not crash the router."""
    global server
    server.models_max = 2
    server.no_models_autoload = True
    server.start()

    models = [
        "ggml-org/tinygemma3-GGUF:Q8_0",
        "ggml-org/test-model-stories260K:F32",
    ]

    def load_one(model_id: str):
        return server.make_request("POST", "/models/load", data={"model": model_id})

    def unload_one(model_id: str):
        return server.make_request("POST", "/models/unload", data={"model": model_id})

    # Parallel load both models
    load_results = parallel_function_calls([
        (load_one, (models[0],)),
        (load_one, (models[1],)),
    ])
    assert all(res is not None for res in load_results)
    for res in load_results:
        assert res.status_code == 200, res.body
        assert res.body.get("success") is True

    for model_id in models:
        _wait_for_model_status(model_id, {"loaded"}, timeout=120)

    # Parallel unload
    unload_results = parallel_function_calls([
        (unload_one, (models[0],)),
        (unload_one, (models[1],)),
    ])
    assert all(res is not None for res in unload_results)
    for res in unload_results:
        assert res.status_code == 200, res.body
        assert res.body.get("success") is True

    for model_id in models:
        _wait_for_model_status(model_id, {"unloaded"}, timeout=120)

    # Router should still answer props after stress
    props = server.make_request("GET", "/props")
    assert props.status_code == 200
    assert props.body.get("role") == "router"


def test_router_chat_model_not_found_error_shape():
    global server
    server.start()

    res = server.make_request(
        "POST",
        "/v1/chat/completions",
        data={
            "model": "non-existent/model",
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 4,
        },
    )
    assert res.status_code in (400, 404)
    assert "error" in res.body
    err = res.body["error"]
    assert isinstance(err, dict)
    assert err.get("message")
    # Keep a stable machine-readable type for clients when present
    if "type" in err:
        assert isinstance(err["type"], str)
