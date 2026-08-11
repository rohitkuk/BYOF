"""
Multi-provider LLM dispatch for BYOF item scoring.

Configure via env vars:
  BYOF_LLM_PROVIDER = anthropic | openai | ollama | openrouter | opencode  (default: anthropic)
  BYOF_LLM_MODEL    = override model (optional)

Provider-specific keys:
  ANTHROPIC_API_KEY    — required for anthropic
  OPENAI_API_KEY       — required for openai
  OPENROUTER_API_KEY   — required for openrouter
  OPENCODE_ZEN_API_KEY — required for opencode (get at opencode.ai/auth)
  (ollama needs no key; runs at http://localhost:11434)

Free options:
  openrouter  → BYOF_LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free
  opencode    → BYOF_LLM_MODEL=deepseek-v4-flash-free  (check opencode.ai/docs/zen for current free model IDs)
"""
import json
import os

from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("BYOF_LLM_PROVIDER", "anthropic").lower()
_MODEL_OVERRIDE = os.getenv("BYOF_LLM_MODEL", "")

_DEFAULTS = {
    "anthropic": "claude-haiku-4-5-20251001",
    "openai": "gpt-4o-mini",
    "ollama": "llama3.2",
    "openrouter": "meta-llama/llama-3.1-8b-instruct:free",
    "opencode": "deepseek-v4-flash-free",
}

# Comma-separated fallback models tried in order if primary fails
# e.g. BYOF_LLM_FALLBACK_MODELS=big-pickle,minimax-m3,deepseek-v4-flash
_FALLBACK_MODELS = [
    m.strip()
    for m in os.getenv("BYOF_LLM_FALLBACK_MODELS", "").split(",")
    if m.strip()
]

_anthropic_client = None
_openai_client = None


def _model() -> str:
    return _MODEL_OVERRIDE or _DEFAULTS.get(PROVIDER, "claude-haiku-4-5-20251001")


def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


def _get_openai():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        if PROVIDER == "openai":
            _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        elif PROVIDER == "ollama":
            _openai_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        elif PROVIDER == "openrouter":
            _openai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
            )
        elif PROVIDER == "opencode":
            _openai_client = OpenAI(
                base_url="https://opencode.ai/zen/v1",
                api_key=os.getenv("OPENCODE_ZEN_API_KEY", ""),
            )
    return _openai_client


def _call_anthropic(
    prompt: str, tool_name: str, tool_description: str, schema: dict
) -> tuple[dict | None, dict]:
    tool = {"name": tool_name, "description": tool_description, "input_schema": schema}
    response = _get_anthropic().messages.create(
        model=_model(),
        max_tokens=512,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool_name},
        messages=[{"role": "user", "content": prompt}],
    )
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return dict(block.input), usage
    return None, usage


def _openai_usage(response) -> dict:
    u = getattr(response, "usage", None)
    return {
        "input_tokens": getattr(u, "prompt_tokens", 0) or 0,
        "output_tokens": getattr(u, "completion_tokens", 0) or 0,
    }


def _try_openai_model(
    model: str, prompt: str, tool_name: str, tool_description: str, schema: dict
) -> tuple[dict | None, dict]:
    """Try one model: tool_choice first, JSON mode fallback on 400."""
    client = _get_openai()
    tool = {
        "type": "function",
        "function": {"name": tool_name, "description": tool_description, "parameters": schema},
    }

    # Attempt 1: tool_choice=auto
    try:
        response = client.chat.completions.create(
            model=model, max_tokens=512, tools=[tool], tool_choice="auto",
            messages=[{"role": "user", "content": prompt}],
        )
        usage = _openai_usage(response)
        msg = response.choices[0].message if response.choices else None
        if msg and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.function.name == tool_name:
                    return json.loads(tc.function.arguments), usage
    except Exception as e:
        status = getattr(e, "status_code", None)
        if status != 400:
            raise  # non-400 errors bubble up to model-fallback loop

    # Attempt 2: JSON mode (handles thinking models that reject tool_choice)
    json_prompt = (
        prompt
        + f"\n\nRespond with valid JSON only matching this schema: {json.dumps(schema)}"
    )
    response = client.chat.completions.create(
        model=model, max_tokens=512,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": json_prompt}],
    )
    usage = _openai_usage(response)
    content = response.choices[0].message.content if response.choices else None
    if content:
        return json.loads(content), usage
    return None, usage


def _call_openai_compat(
    prompt: str, tool_name: str, tool_description: str, schema: dict
) -> tuple[dict | None, dict]:
    """Try primary model, then each fallback model in order."""
    models = [_model()] + _FALLBACK_MODELS
    last_exc = None
    for model in models:
        try:
            result, usage = _try_openai_model(model, prompt, tool_name, tool_description, schema)
            if result is not None:
                return result, usage
        except Exception as e:
            last_exc = e
            continue
    return None, {}


def call_structured(
    prompt: str, tool_name: str, tool_description: str, schema: dict
) -> tuple[dict | None, dict]:
    """Call configured LLM with a structured output tool.
    Returns (result_dict, usage). Returns (None, {}) on any failure."""
    try:
        if PROVIDER == "anthropic":
            return _call_anthropic(prompt, tool_name, tool_description, schema)
        if PROVIDER in ("openai", "ollama", "openrouter", "opencode"):
            return _call_openai_compat(prompt, tool_name, tool_description, schema)
        return None, {}
    except Exception:
        return None, {}
