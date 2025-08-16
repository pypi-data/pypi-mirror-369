# ---------------------------------------------------------------------------------------------------
# File: mcp_agent.py
# ---------------------------------------------------------------------------------------------------
import asyncio
from fastmcp import FastMCP
from agents.mcp import MCPServerStdio, MCPServerSse
from agents import Agent, Runner, trace, enable_verbose_stdout_logging, RunHooks, WebSearchTool, FileSearchTool
from typing import Any, List
from one_prompt_agents.utils import uvicorn_log_level
from one_prompt_agents.job_manager import submit_job, get_job
from pydantic import BaseModel
from one_prompt_agents.strategies import get_chat_strategy  # local import to avoid cycles

import logging
logger = logging.getLogger(__name__) 

next_port = 8000

class InteractiveReply(BaseModel):
    assistant_reply: str

class MCPAgent(MCPServerSse):
    """Represents an agent that is also an MCP SSE (Server-Sent Events) server.

    This class encapsulates an `Agent` and exposes it as a tool through a `FastMCP`
    server. It allows other agents or systems to interact with this agent via SSE.
    It manages a job queue for processing requests and can interact with other MCP servers.

    Each MCPAgent instance holds two underlying `agents.Agent` instances:
    1.  `agent`: The primary agent used for autonomous runs, configured with the specific
        `return_type` defined in its configuration.
    2.  `interactive_agent`: A secondary agent created specifically for interactive REPL
        sessions. This agent always uses a fixed `InteractiveReply` Pydantic model
        (with an `assistant_reply: str` field), ensuring a consistent output format
        for direct user chats.

    Attributes:
        url (str): The SSE URL where this MCPAgent is listening.
        job_queue (asyncio.Queue): The queue used to submit jobs to this agent.
        mcp_servers (List[Any]): A list of other MCP servers this agent can interact with.
        prompt_file (str): Path to the file containing the agent's instructions.
        return_type (Any): The expected Pydantic model or type for the main agent's output.
        inputs_description (str): A description of the inputs this agent expects.
        strategy_name (str): The name of the chat strategy for jobs processed by this agent.
        agent (Agent): The underlying `agents.Agent` instance for autonomous operation.
        interactive_agent (Agent): The agent instance for interactive REPL sessions.
        mcp (FastMCP): The `FastMCP` server instance that exposes this agent as tools.
        mcp_task (asyncio.Task): The asyncio task running the `FastMCP` server.
    """
    def __init__(
        self,
        name: str,
        prompt_file: str,
        return_type: Any,
        inputs_description: str,
        mcp_servers: List[Any],
        job_queue: asyncio.Queue,
        model: str,
        strategy_name: str = "default",
        tools_config: dict = None,
    ):
        """Initializes the MCPAgent.

        Args:
            name (str): The name of the agent.
            prompt_file (str): Path to the file containing the agent's instructions.
            return_type (Any): The Pydantic model or type for the agent's output.
            inputs_description (str): A description of the inputs this agent expects.
            mcp_servers (List[Any]): List of other MCP servers for the agent to use.
            job_queue (asyncio.Queue): The job queue for submitting tasks to this agent's chat worker.
            model (str): The model name (e.g., "gpt-4-1106-preview") for the underlying agent.
            strategy_name (str, optional): The chat strategy to use. Defaults to "default".
            tools_config (dict, optional): Configuration for tools to be used by the agent.
                                           Keys are tool names (str), values are parameter dicts or None.
                                           Defaults to None (no tools).
        """
        global next_port
        next_port += 1
        self.url = f"http://127.0.0.1:{next_port}/sse"
        super().__init__(
            params={
                'url': self.url,
                'timeout': 8,
                'sse_read_timeout': 100
            },
            cache_tools_list=True,
            client_session_timeout_seconds=120,
            name=name,
        )
        self.job_queue = job_queue
        self.mcp_servers = mcp_servers
        self.prompt_file = prompt_file
        # Make sure the return_type satisfies the requirements of the chosen prompt strategy
        strategy_cls = get_chat_strategy(strategy_name)
        augmented_return_type = strategy_cls.ensure_return_type(return_type)
        self.return_type = augmented_return_type
        self.inputs_description = inputs_description
        self.strategy_name = strategy_name

        with open(prompt_file, 'r', encoding='utf-8') as f:
            instructions = f.read()

        agent_tools = []
        if tools_config:
            logger.info(f"Configuring tools for agent {name} based on tools_config: {tools_config}")
            tool_mapping = {
                "WebSearchTool": WebSearchTool,
                "FileSearchTool": FileSearchTool,
                # Add other supported tools here
            }

            for tool_name, params in tools_config.items():
                logger.info(f"Attempting to add tool: {tool_name} with params: {params}")
                if tool_name in tool_mapping:
                    ToolClass = tool_mapping[tool_name]
                    try:
                        if params and isinstance(params, dict):
                            agent_tools.append(ToolClass(**params))
                            logger.info(f"Successfully added tool '{tool_name}' with provided parameters.")
                        else: # params is None or not a dict (e.g. empty list, though dict is expected)
                            agent_tools.append(ToolClass())
                            logger.info(f"Successfully added tool '{tool_name}' with default parameters.")
                    except Exception as e:
                        logger.error(f"Error instantiating tool {tool_name} with params {params}: {e}")
                else:
                    logger.warning(f"Tool '{tool_name}' in tools_config is not recognized or supported.")

        self.agent = Agent(
            name=name,
            instructions=instructions,
            model=model,
            output_type=augmented_return_type,
            mcp_servers=mcp_servers,
            tools=agent_tools,
        )

        # Add interactive_agent with fixed return_type
        self.interactive_agent = Agent(
            name=f"{name}_interactive",
            instructions=instructions,
            model=model,
            output_type=InteractiveReply,
            mcp_servers=mcp_servers,
            tools=agent_tools,
        )

        # FastMCP server to expose this agent as a tool
        self.mcp = FastMCP(
            name=f"{name}_mcp",
            version='0.2.0',
            description=f"This MCP allows to call the {name} agent.",
        )
        self.mcp.add_tool(
            name=f"start_agent_{name}",
            description=f"Starts the {name} agent async. No wait for it's response.",
            fn=lambda inputs: self._start(inputs)
        )
        self.mcp.add_tool(
            name=f"_start_and_wait_{name}",
            description=f"Starts a new job for the agent {name} and waits until it\'s finished.",
            fn=self._start_and_wait
        )
        self.mcp.add_tool(
            name=f"get_agent_info_{name}",
            description=f"This method returns further information about the agent {self.agent.name}. This agent description: {self.inputs_description}",
            fn=self._get_agent_info
        )


        # Start FastMCP SSE for other agents to call
        loop = asyncio.get_event_loop()
        self.mcp_task = loop.create_task(
            self.mcp.run_sse_async(
                host='127.0.0.1',
                port=next_port,
                log_level=uvicorn_log_level(),
            )
        )

    async def _start(self, inputs) -> str:
        """Handles a simple start request for the agent.

        Submits a job to the agent's queue and returns a job ID.
        This is exposed as an MCP tool: `start_agent_{name}`.

        Args:
            inputs: The input prompt or data for the agent.

        Returns:
            str: A message indicating the job has started, along with the job ID.
        """
        # Submit a job for this agent, no dependencies
        job_id = await submit_job(self.job_queue, self.agent, str(inputs), self.strategy_name)
        return f'Agent is running. Job started: {job_id}'


    async def _start_and_wait(self, agent_inputs: str, your_job_id: str) -> str:
        """Starts a job for this agent and makes the calling agent's job wait for its completion.

        This method is exposed as an MCP tool: `_start_and_wait_{name}`.
        It submits a job for the current MCPAgent. Then, it modifies the job specified
        by `your_job_id` (the calling agent's job) to depend on the newly created job.
        The calling agent's job status is set to 'in_queue' and it's put back on the
        job queue to wait.

        Args:
            agent_inputs (str): The input/prompt for the job of this MCPAgent.
            your_job_id (str): The job ID of the agent that is calling this tool and needs to wait.

        Returns:
            str: A message indicating the job has started and the calling agent should wait.
                 Returns an error message if `your_job_id` is not found.
        """
        # Submit a job for this agent, no dependencies
        job_id = await submit_job(self.job_queue, self.agent, agent_inputs, self.strategy_name)

        waiter = get_job(your_job_id)

        if not waiter:
            return f"Job {your_job_id} not found. You must provide your own job id to wait for another job."
        else:# change the waiter job status to in_queue 
            waiter.status = 'in_queue'
            # add the job id to the waiter's depends_on
            waiter.depends_on.append(job_id)
            # add the job id to the waiter's chat_history
            waiter.chat_history += f"Job {job_id} has been started.\n"
            # put the waiter back in the job queue
            await self.job_queue.put(waiter)

        return f"Job {job_id} has been started. To wait for it\'s completion return your plan."

    def _get_agent_info(self) -> dict:
        """Returns information about the agent.

        This is exposed as an MCP tool: `get_agent_info`.

        Returns:
            dict: A dictionary containing the agent's name, prompt, model, and prompt strategy.
        """
        return {
            'AgentName': self.agent.name,
            'Prompt': self.agent.instructions,
            'Model': self.agent.model,
            'PromptStrategy': self.strategy_name
        }

    async def end_and_cleanup(self):
        """Shuts down the MCPAgent's FastMCP server and cleans up SSE client resources.

        This method should be called during application shutdown to ensure graceful
        termination of background tasks and network connections.
        """
        if self.mcp_task:
            self.mcp_task.cancel()
            await asyncio.gather(self.mcp_task, return_exceptions=True)
        # cleanup SSE client
        await asyncio.gather(self.cleanup())

async def start_agent(mcp_agent: MCPAgent, inputs, strategy_name=None):
    """Submits a job to the specified MCPAgent's job queue.

    This is a utility function to trigger an agent run. It should be called
    from an async context.

    Args:
        mcp_agent (MCPAgent): The MCPAgent instance to run.
        inputs: The input prompt or data for the agent.
        strategy_name (str, optional): The name of the chat strategy to use.
            If None, uses the `mcp_agent.strategy_name` or defaults to "default".
    """
    # Submit a job for this agent, no dependencies
    await submit_job(mcp_agent.job_queue, mcp_agent.agent, str(inputs), strategy_name or getattr(mcp_agent, 'strategy_name', 'default'))
