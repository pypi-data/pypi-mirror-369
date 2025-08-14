import json
import logging
from litellm import completion
from .tools import all_tools, get_tool, generate_tool_specs
from .utils import extract_function_call, normalize_arguments, assistant_func_call_entry

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, model: str, system_prompt: str, initial_user_message: str = None):
        self.model = model
        self.system_prompt = system_prompt
        self.initial_user_message = initial_user_message
        self.tools = generate_tool_specs(all_tools())
        self.messages = [{"role": "system", "content": system_prompt}]
        if initial_user_message:
            self.messages.append({"role": "user", "content": initial_user_message})
    
    def run(self, max_steps: int = 20, log_ouput = True):
        steps = 0
        while steps < max_steps:
            steps += 1
            logger.info("Agent step %d", steps)
            response = completion(
                model=self.model,
                messages=self.messages,
                functions=self.tools,
                function_call="auto"
                )
            message = response["choices"][0]["message"]
            func_name, func_args_raw = extract_function_call(message)

            if not func_name:
                logger.error("No function_call in message. Stopping. Assistant content: %s", getattr(message, "content", None))
                break

            try:
                func_args = normalize_arguments(func_args_raw)
            except Exception as e:
                logger.exception("Failed to parse function arguments: %s", e)
                break
            
            logger.info("Executing tool %s with args %s", func_name, func_args)
            tool_fn = get_tool(func_name)
            if tool_fn is None:
                logger.error("Tool not found: %s", func_name)
                break

            try:
                result = tool_fn(**func_args)
                if log_ouput:
                    print(result)
                else:
                    continue
            except Exception as e:
                # Report the error back to LLM and stop
                err = {"error": str(e)}
                self.messages.append(assistant_func_call_entry(func_name, func_args_raw))
                self.messages.append({"role": "function", "name": func_name, "content": json.dumps(err)})
                logger.exception("Tool raised an exception")
                break

            # Append assistant function call and the tool result (as a function message)
            self.messages.append(assistant_func_call_entry(func_name, func_args_raw))
            self.messages.append({"role": "function", "name": func_name, "content": json.dumps(result)})

            if func_name == "terminate":
                logger.info("Agent requested termination.")
                break
        
        logger.info("Agent run finished after %d steps", steps)
        return