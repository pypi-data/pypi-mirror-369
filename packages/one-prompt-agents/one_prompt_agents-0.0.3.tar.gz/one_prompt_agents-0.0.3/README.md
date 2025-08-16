# One-Prompt Agents

One-Prompt Agents is a lightweight framework for creating and running AI agents with remarkable simplicity. The core idea is that an AI agent can be defined with just two key components:

1.  A **prompt file**: Contains the natural language instructions for the agent.
2.  A **JSON configuration file**: Defines the agent's behavior, tools, and output structure.

This approach makes it easy to quickly prototype, test, and deploy AI agents for various tasks.

## Core Concept: Simplicity in Agent Definition

The framework's strength lies in its straightforward approach to defining agents. Each agent is self-contained within its own directory and primarily consists of a prompt and a configuration file.

### Directory Structure

All agents reside within a main directory named `agents_config`. This directory should be located in the root of your project, from where you'll run the main application.

Each agent has its own subdirectory within `agents_config`:

```
your-project-root/
├── agents_config/
│   ├── AgentName1/
│   │   ├── config.json
│   │   ├── prompt.txt
│   │   └── return_type.py (optional)
│   └── AgentName2/
│       ├── config.json
│       ├── another_prompt.md
│       └── return_type.py (optional)
└── src/
    └── one_prompt_agents/
        └── main.py
```

### Key Components

Inside each agent's directory (e.g., `AgentName1`), you'll find:

1.  **`config.json`**: This is the heart of the agent's definition.
    *   `name` (string): The unique name of the agent. This name is used to identify and call the agent.
    *   `prompt_file` (string): The filename of the text file containing the agent's core prompt (e.g., "prompt.txt", "instructions.md").
    *   `return_type` (string, _optional_): The name of a Pydantic model class defined in `return_type.py`. If this field is omitted **or** the `return_type.py` file is absent/empty, the framework will create a minimal model automatically and the selected prompt-strategy will augment it with any fields it needs.
    *   `inputs_description` (string): A human-readable description of what inputs the agent expects. This helps in understanding how to interact with the agent.
    *   `tools` (list of strings): A list of other agents or pre-defined MCP (Multi-Capability Agent Protocol) server names that this agent can utilize as tools. If the agent doesn't use any tools, this can be an empty list `[]`.
    *   `model` (string, optional): Specifies the underlying language model to be used (e.g., "o4-mini", "gpt-4"). If omitted, a default model (currently "o4-mini") is used.

2.  **Prompt File** (e.g., `prompt.txt`, `another_prompt.md`):
    *   This is a plain text or markdown file containing the natural language instructions, persona, and context for the AI agent. The content of this file will guide the agent's behavior and responses.

3.  **`return_type.py`** (optional):
    *   If present, this Python file defines a Pydantic model corresponding to the `return_type` string (if provided) in `config.json`.
    *   Providing your own model lets you enforce additional structure in the agent's output. When the file is missing the framework falls back to an empty model, which strategies will extend as necessary at runtime.

    Example `return_type.py`:
    ```python
    from pydantic import BaseModel, Field
    from typing import List

    class AnalysisResult(BaseModel):
        summary: str = Field(description="A brief summary of the analysis.")
        keywords: List[str] = Field(description="A list of extracted keywords.")
        confidence: float = Field(description="A confidence score for the analysis.")
    ```
    In this example, the `config.json` for this agent would have `"return_type": "AnalysisResult"`.

## System Requirements

*   **Python**: Version 3.8 or higher.
*   **pip**: Python package installer (usually comes with Python).
*   **git**: For cloning the repository.

### API Keys

This application interacts with OpenAI services and requires an `OPENAI_API_KEY` environment variable to be set.
Please ensure you have this environment variable configured with your valid OpenAI API key before running the application.
For example:
```bash
export OPENAI_API_KEY='your_openai_api_key_here'
```
The application will not function correctly without this key.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/one-prompt-agents.git # Replace with the actual repository URL
    cd one-prompt-agents
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Creating Your First Agent: An "EchoAgent" Example

Let's illustrate how simple it is to create an agent. We'll make an "EchoAgent" that simply returns the prompt it receives.

1.  **Create the agent's directory structure:**

    First, ensure you have the main `agents_config` directory in your project root. Then, create a directory for your new agent:

    ```
    your-project-root/
    ├── agents_config/
    │   └── EchoAgent/           # Create this directory
    │       ├── config.json      # We'll create this file
    │       ├── prompt.txt       # We'll create this file
    │       └── return_type.py   # We'll create this file
    └── ... (other project files)
    ```

2.  **Create the `config.json` file:**

    Create `agents_config/EchoAgent/config.json` with the following content:

    ```json
    {
        "name": "EchoAgent",
        "prompt_file": "prompt.txt",
        "return_type": "EchoResponse",
        "inputs_description": "Any text prompt that the agent will echo back in the 'content' field.",
        "tools": [],
        "model": "o4-mini"
    }
    ```

3.  **Create the `prompt.txt` file:**

    Create `agents_config/EchoAgent/prompt.txt` with the following content:

    ```text
    You are an Echo Agent. Your sole purpose is to return the exact text provided to you by the user.
    The user's text will be provided as input. You must return this text in the 'content' field of your response.
    Do not add any extra information, explanations, or greetings. Just echo the input into the 'content' field.
    ```

4.  **Create the `return_type.py` file:**

    Create `agents_config/EchoAgent/return_type.py` with the following content:

    ```python
    from pydantic import BaseModel, Field

    class EchoResponse(BaseModel):
        content: str = Field(description="The exact text that was provided in the prompt.")
    ```

And that's it! You've defined a simple agent. The framework will load this agent based on these files. The `EchoResponse` model ensures that the output will be a JSON object with a `content` field.

## Running Agents

Once you have defined your agents in the `agents_config` directory (located at the root of your project), you can run them using the commands configured in `pyproject.toml`. Ensure your project's virtual environment is activated to use these commands.

### 1. Interactive REPL Mode

This mode allows you to chat with a specific agent directly in your console. The agent's textual response is typically expected to be found in a `content` field of its structured JSON output.

*   **Start REPL:**
    ```bash
    run_agent <agent_name>
    ```
    Example:
    ```bash
    run_agent EchoAgent
    ```
    You'll be prompted for input, and the agent will respond. If the agent's `return_type.py` defines a `content` field, that's what will be displayed as the primary response.

### 2. Autonomous Console Mode

This mode runs an agent with a single prompt directly from the command line and typically prints its full structured output (or a summary, depending on agent design).

*   **Run agent:**
    ```bash
    run_agent <agent_name> "<your_prompt_here>"
    ```
    Example:
    ```bash
    run_agent EchoAgent "Hello from the console!"
    ```

### 3. HTTP Server Mode

This mode starts a FastAPI server, allowing you to interact with your agents via HTTP requests.

*   **Start the server:**
    ```bash
    run_server
    ```
    By default, the server runs on `http://127.0.0.1:9000`. You might see logging options like `run_server --log -v` if you need more detailed output or file logging, similar to the previous `python -m src.one_prompt_agents.main --log -v`.

*   **Triggering an agent:**
    Send a `POST` request to the `/{agent_name}/run` endpoint. The body of the request should be a JSON object containing the prompt.
    For example, to run our `EchoAgent`:
    ```bash
    curl -X POST http://127.0.0.1:9000/EchoAgent/run              -H "Content-Type: application/json"              -d '{"prompt": "Hello, world!"}'
    ```
    The agent will process the request asynchronously. The immediate response will be:
    ```json
    {"status": "started", "agent": "EchoAgent"}
    ```
    The actual output of the agent (the echoed text in this case) will be processed in the background.

*   **Helper Script (`http_start.py`):**
    The project includes a helper script `http_start.py` that ensures the server is running (starting it if necessary) and then triggers an agent. This script still uses `python -m ...` as it's a standalone utility.
    ```bash
    python -m src.one_prompt_agents.http_start <agent_name> "<your_prompt_here>"
    ```
    Example:
    ```bash
    python -m src.one_prompt_agents.http_start EchoAgent "This is a test prompt."
    ```

**Important:** Remember that the `agents_config` directory, containing all your agent definitions, must be present in the directory from which you execute these commands.

## Advanced Strategy: The "Make a Plan" Approach

For more complex tasks that require multiple steps or objectives, agents can be designed to first create a plan and then execute it. This strategy enhances the agent's autonomy and allows for better progress tracking, especially in autonomous scenarios.

### Core Idea

Instead of directly trying to solve the entire task with a single response, the agent's initial goal is to outline a series of steps (a plan) to achieve the overall objective.

1.  **Define a Plan-Oriented `return_type`**:
    The agent's `return_type.py` would define Pydantic models representing the plan and its individual tasks. Each task could have attributes like a description and a completion status (e.g., "pending", "completed").

    Example `return_type.py` for a planning agent:
    ```python
    from pydantic import BaseModel, Field
    from typing import List

    class Task(BaseModel):
        task_id: int = Field(description="Unique identifier for the task.")
        description: str = Field(description="What needs to be done for this task.")
        status: str = Field(default="pending", description="Status of the task, e.g., 'pending', 'completed'.")

    class PlanResponse(BaseModel):
        plan_summary: str = Field(description="A brief summary of the overall plan.")
        tasks: List[Task] = Field(description="A list of tasks to be executed.")
        next_task_id: int | None = Field(default=None, description="The ID of the next task to be executed.")
    ```
    The agent's `config.json` would then specify `"return_type": "PlanResponse"`.

2.  **Prompt for Planning**:
    The agent's prompt file (e.g., `prompt.txt`) would instruct it to analyze the user's request, break it down into manageable steps, and return this plan using the defined `PlanResponse` structure.

3.  **Interaction Flow**:
    *   **User**: Provides an initial complex prompt (e.g., "Research topic X and write a summary").
    *   **Agent (First Interaction)**: Returns a `PlanResponse` JSON object detailing the steps (e.g., Task 1: Search for sources, Task 2: Read and analyze sources, Task 3: Draft summary, Task 4: Review and finalize summary). Initially, all tasks are "pending".
    *   **User/Orchestrator**: Reviews the plan. Then, in subsequent turns, instructs the agent to execute the plan, often step-by-step (e.g., "Proceed with the next step", "Execute task 2").
    *   **Agent (Subsequent Interactions)**: Executes the indicated task. It might return an updated `PlanResponse` showing the completed task and potentially the output of that specific task, or a simpler status update. It might also update the `next_task_id`.

### Benefits

*   **Handles Complex Goals**: Breaks down large tasks into smaller, manageable parts.
*   **Transparency & Control**: Users can see the agent's plan before execution and guide the process.
*   **Progress Tracking**: Easy to see which steps have been completed and what's next.
*   **Flexibility**: Allows for iterative execution and potential plan adjustments if needed.

This "make a plan" strategy is particularly effective for autonomous agents designed to perform multi-stage operations. For interactive agents, the core idea of returning a structured response (like the `content` field in the EchoAgent) remains the primary mode of simple interaction, but more complex interactive agents could also adopt planning for guided task completion.

## Logging

The `main.py` script provides options to control logging:

*   `--log`: If this flag is present, logs will be redirected to a file (e.g., `mcp.log`).
*   `-v` or `--verbose`: Enables verbose output by setting the logging level to DEBUG. This is useful for troubleshooting and understanding the agent's internal operations.

Example of running the server with verbose logging to a file:
```bash
python -m src.one_prompt_agents.main --log -v
```

## Advanced: Agent Tools and Dependencies

Agents can be designed to use other agents or pre-defined MCP (Multi-Capability Agent Protocol) servers as "tools." This allows you to build more complex systems where agents can delegate specific tasks to specialized tools or other agents.

This is configured in an agent's `config.json` file using the `tools` field:

```json
{
    "name": "MyMainAgent",
    "prompt_file": "main_prompt.txt",
    "return_type": "MainResponse",
    "inputs_description": "Input for the main agent.",
    "tools": ["AnotherAgentName", "SomeMCPTool"], // Names of other agents or MCP servers
    "model": "o4-mini"
}
```

In this example, `MyMainAgent` would have access to `AnotherAgentName` (which must also be defined in the `agents_config` directory) and `SomeMCPTool` (which should be a pre-configured MCP server known to the system). The prompt for `MyMainAgent` would then instruct it on how and when to use these tools.

The framework handles the resolution and communication with these declared tools.

## Extending with Custom MCP Servers

Beyond using other agents as tools, the framework supports the integration of custom MCP (Multi-Capability Agent Protocol) servers. This allows you to connect specialized, independently running services or capabilities that adhere to the MCP standard. The `mcp_servers_loader.py` module is responsible for discovering and loading these custom MCP servers.

### How it Works

1.  **Directory for MCP Servers**:
    *   Create a directory in your project, conventionally named `mcp_servers/` (this is configurable via `SEARCH_DIR` in `mcp_servers_loader.py`). This directory will house your custom MCP server definitions.

2.  **MCP Server Definition Files**:
    *   Inside the `mcp_servers/` directory, create Python files for each of your custom MCP servers.
    *   These files must have a specific suffix, by default `_mcp_server.py` (configurable via `MODULE_SUFFIX` in `mcp_servers_loader.py`). For example, `my_custom_tool_mcp_server.py`.

3.  **Defining MCP Server Instances**:
    *   Within each such Python file, define one or more module-level instances of `MCPServerSse` or `MCPServerStdio` (from `agents.mcp`). These are the classes that represent your MCP server's client-side interface.
    *   Each instance must have a unique `name` attribute. This name is how agents will refer to this MCP server in their `tools` list in `config.json`.

    Example `mcp_servers/apify_example_mcp_server.py`:
    ```python
    import os
    import sys
    from pathlib import Path
    from agents.mcp import MCPServerStdio, MCPServerSse
    from types import MethodType

    # --- NEW: Apify SSE server ---
    APIFY_TOKEN = os.getenv("APIFY_TOKEN")
    if not APIFY_TOKEN:
        sys.exit("❌  export APIFY_TOKEN first")

    apify_server = MCPServerSse(
        params={
            "url": f"https://actors-mcp-server.apify.actor/sse?enableAddingActors=true", #
            "headers": {
                "Authorization": f"Bearer {APIFY_TOKEN}",
                # Apify also accepts this custom header, either is fine:
                # "x-apify-token": APIFY_TOKEN,
            },
            "timeout": 180,
            "sse_read_timeout": 300,
        },
        client_session_timeout_seconds=60,
        cache_tools_list=True,
        name="apify-mcp-server",
    )

    ```

4.  **Automatic Discovery and Loading**:
    *   When the main application starts (via `cli.py`), the `collect_servers()` function from `mcp_servers_loader.py` is invoked.
    *   It scans the `SEARCH_DIR` (e.g., `mcp_servers/`) for files ending with `MODULE_SUFFIX` (e.g., `_mcp_server.py`).
    *   It dynamically imports these modules.
    *   It collects all top-level instances of `MCPServerSse` or `MCPServerStdio` found in these modules. These are made available to agents that list them in their `tools`.
    *   If a module defines a callable `main()` function at the top level, it is executed. Any `asyncio.Task` returned by `main()` will be collected and managed by the main application loop, allowing your MCP server to run its own asynchronous operations if needed (e.g., starting the actual server-side component that the `MCPServerSse` instance connects to).

### Key Expectations and Features

*   **Naming**: The `name` attribute of your `MCPServerSse` or `MCPServerStdio` instance is crucial. It's the identifier used in an agent's `config.json` `tools` array.
*   **Configuration (`params`)**: The `params` dictionary passed to the `MCPServerSse` or `MCPServerStdio` constructor should contain all necessary information for the client to connect to and interact with your actual MCP server (e.g., URL, timeouts).
*   **Server-Side Logic (Optional `main()` hook)**:
    *   The `MCPServerSse`/`MCPServerStdio` instances you define are *clients* that enable agents to talk to your MCP-compliant service.
    *   If the actual service (the server part of your MCP tool) needs to be started or managed by the One-Prompt Agents framework itself, you can implement this logic within the optional `main()` function in your `*_mcp_server.py` file.
    *   For example, `main()` could start a local FastAPI/Uvicorn server that implements the MCP tool's functionality, and the `MCPServerSse` instance would point to this local server's URL.
*   **Agent Integration**: Once an MCP server is loaded, any agent can list its `name` in its `tools` array (in its `config.json`). The framework will then inject this pre-configured `MCPServerSse` or `MCPServerStdio` instance into the agent, allowing the agent's prompt to delegate tasks to it.

This mechanism provides a flexible way to extend the capabilities of your agents by integrating with external or custom-built MCP-compliant tools and services.
