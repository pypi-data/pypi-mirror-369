import inspect
from typing import Callable, Dict, List

_TOOL_REGISTRY: Dict[str, Callable] = {}

def tool(name: str = None):
    """Decorator to register a function as a tool.
    
    Usage:
        @tool()
        def list_files():
            ...
    """
    def decorator(fn: Callable):
        key = name or fn.__name__
        _TOOL_REGISTRY[key] = fn
        return fn
    return decorator

def get_tool(name: str):
    return _TOOL_REGISTRY.get(name)

def all_tools() -> List[Callable]:
    return list(_TOOL_REGISTRY.values())

def generate_tool_specs(functions: List[Callable]):
    """Create function-calling specs (JSON schema) from Python functions.
    
    Simple rules:
    - Uses docstring for description
    - Uses type hints for param types (string/number/boolean fallback)
    - Treats all parameters as top-level properties
    """
    specs = []
    for fn in functions:
        sig = inspect.signature(fn)
        props = {}
        required = []
        for name, param in sig.parameters.items():
            ann = param.annotation
            typ = "string"
            if ann in (int, float):
                typ = "number"
            elif ann == bool:
                typ = "boolean"
            props[name] = {"type": typ}
            if param.default is inspect.Parameter.empty:
                required.append(name)
        
        specs.append({
            "name": fn.__name__,
            "description": inspect.getdoc(fn) or "",
            "parameters": {"type": "object", "properties": props, "required": required},
        })
    return specs