# RapidLLM

RapidLLM is a Python framework for building predictable, reliable multi-tool LLM agents. It emphasizes **multi-tool orchestration** over single-call monolithic prompts, making your agents more modular, testable, and efficient.

## Features
- Simple multi-tool agent architecture.
- Clear separation of concerns between tools.
- Predictable step-by-step execution.
- Easy to extend with your own tools.

## Installation
```bash
pip install rapidllm

## Quick Example

Below is a very minimal example of using RapidLLM to create an agent that lists files:

from rapidllm.agent import run_agent
from rapidllm.tools import list_files_tool

# Define available tools
TOOLS = [list_files_tool]

if __name__ == "__main__":
    run_agent(
        system_prompt="List all files in the src directory.",
        tools=TOOLS,
        model="gpt-4"
    )
