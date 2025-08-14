import json
from typing import Any, Tuple

def extract_function_call(message) -> Tuple[str, Any]:
    """Handle both dict-stle and objec-style messages returned by LLM clinet.
    
    Returns (func_name, func_args_raw) where func_args_raw is usually a JSON string or a dict-like object.
    """

    # Dict-like (OpenAI-style)
    if isinstance(message, dict):
        fc = message.get("function_call")
        if not fc:
            return None, None
        if isinstance(fc, dict):
            return fc.get("name"), fc.get("arguments")
        return getattr(fc, "name", None), getattr(fc, "arguments", None)
    
    # Object-style (LiteLLM wrappers)
    fc = getattr(message, "function_call", None)
    if fc is None:
        return None, None
    return getattr(fc, "name", None), getattr(fc, "arguments", None)

def normalize_arguments(func_args_raw: Any) -> dict:
    """Return a Python dict parsed fromt the raw arguments.
    
    - If string -> parse JSON
    - If None -> {}
    - If dict/object -> return as-is
    """
    if func_args_raw is None:
        return {}
    if isinstance(func_args_raw, str):
        s = func_args_raw.strip()
        if not s:
            return {}
        return json.loads(s)
    return func_args_raw

def assistant_func_call_entry(func_name: str, func_args_raw: Any, assistant_content: str = None) -> dict:
    """Normalize assistant function-call into a serializable dict message for messages list."""
    if isinstance(func_args_raw, str):
        args_json = func_args_raw
    else:
        args_json = json.dumps(func_args_raw or {})
    return {"role": "assistant", "content": assistant_content or None, "function_call": {"name": func_name, "arguments": args_json}}