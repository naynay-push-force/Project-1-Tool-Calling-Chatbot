# CLI Assistant

---

## Overview

A command-line assistant (CLI) chatbot that routes user messages to local tools 
(calculator, file ops, weather) via OpenAI function calling.

---

## Prerequisite

- Python 3.9
- `uv` (`pip install uv`)

---

## How to run it

The following is for windows:

1. Install dependencies from lockfile

```powershell
uv sync
```

2. Set environment by copying env template

```powershell
Copy-Item .env.example.txt .env
```

3. Edit `.env` and set your API key

4. Direct the interpreter to the CLI script entry point

```powershell
uv run cli-assistant
```

---

## Available commands

- `/help` — show available commands
- `/tools` — list tools and their descriptions 
- `/quit` — exit
- `/tool <name> <json_args>` — run a tool directly, 
  i.e., `/tool calculate {"expression":"2+2"}`

---

## Repository Structure

```
src/
    cli_assistant/
                  tools/
                    base.py
                    calculator.py
                    file_ops.py
                    registry.py
                    weather.py
                  ui/
                    formatter.py
                  __init__.py
                  cli.py
                  config.py
                  llm.py
.env.example.txt
```

---

## How to add a tool

1. Add a python module into `src/cli_assistant/tools`

2. Define a class for the tool in question as inheriting from the 
   abstract class `BaseTool`

3. Attribute it with its inherited properties such as name, description
   and paramerters as per `src/cli_assistant/tools/base.py`.

4. Define an execute function 

5. Register it in `_register_tools()` in `cli.py`:
   `registry.register(YourTool())`

