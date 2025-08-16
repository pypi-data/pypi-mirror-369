# Usage:
# configs = discover_configs(Path("agents"))
# load_order = topo_sort(configs)
import json, importlib, sys
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict
from pydantic import BaseModel, PrivateAttr, create_model
from one_prompt_agents.mcp_agent import MCPAgent

import logging
logger = logging.getLogger(__name__) 

class AgentConfig(BaseModel):
    """Represents the configuration for an agent, loaded from a config.json file.

    Attributes:
        name (str): The unique name of the agent.
        prompt_file (str): The filename of the prompt instructions within the agent's folder.
        return_type (str): The name of the Pydantic class defining the agent's output structure.
                           This class is expected to be in a `return_type.py` file in the agent's folder.
        inputs_description (str): A description of the inputs the agent expects.
        tools (List[str]): A list of names of other agents or static MCP servers this agent can use.
        model (str | None): The language model to be used by the agent (e.g., "gpt-4-1106-preview").
                            Defaults to None, which may result in a default model being used later.
        strategy_name (str): The name of the chat strategy to use for this agent. Defaults to "default".
        _path (Path): Private attribute storing the relative path to the agent's configuration folder.
                      This is set during discovery.
        tools_config (Dict[str, Any] | None): Additional configuration for the tools used by the agent.
    """
    name: str
    prompt_file: str
    return_type: str | None = None
    inputs_description: str
    tools: List[str]
    _path: Path = PrivateAttr()
    model: str | None = None
    strategy_name: str = "default"
    tools_config: Dict[str, Any] | None = None

def discover_configs(agents_dir: Path) -> Dict[str, AgentConfig]:
    """Discovers agent configurations from subdirectories of `agents_dir`.

    Each agent is expected to have its own folder containing a `config.json` file.
    This function reads these JSON files, validates them against `AgentConfig`,
    and stores the agent's folder path.

    Args:
        agents_dir (Path): The directory containing agent configuration folders.

    Returns:
        Dict[str, AgentConfig]: A dictionary mapping agent names to their configurations.
    """
    configs = {}
    for folder in agents_dir.iterdir():
        cfg_path = folder / "config.json"
        if cfg_path.exists():
            data = json.loads(cfg_path.read_text())
            if "strategy_name" not in data:
                data["strategy_name"] = "default"
            configs[data["name"]] = AgentConfig(**data)
            configs[data["name"]]._path = folder.name
    return configs

def topo_sort(configs: Dict[str, AgentConfig]) -> List[str]:
    """Performs a topological sort on agent configurations based on their tool dependencies.

    This ensures that agents are loaded in an order where their dependencies (other agents
    they use as tools) are loaded first.

    Args:
        configs (Dict[str, AgentConfig]): A dictionary of agent configurations.

    Returns:
        List[str]: A list of agent names in the order they should be loaded.

    Raises:
        ValueError: If a cyclic dependency between agents is detected.
    """
    graph = defaultdict(list)
    wildcard_agents = []
    for name, cfg in configs.items():
        if "*" in cfg.tools:
            wildcard_agents.append(name)
            continue
        for dep in cfg.tools:
            if dep in configs:
                graph[dep].append(name)
    visited, temp, order = set(), set(), []
    def dfs(node):
        if node in temp:
            raise ValueError(f"Cyclic dependency at {node}")
        if node not in visited:
            temp.add(node)
            for nei in graph[node]:
                dfs(nei)
            temp.remove(node); visited.add(node); order.append(node)
    for node in configs:
        if node not in wildcard_agents:
            dfs(node)
    order.reverse()  # reverse to get the correct order
    logger.info(f"Load order (pre-wildcard): {order}")
    # Add wildcard agents at the end
    order += wildcard_agents
    logger.info(f"Final load order (wildcard last): {order}")
    return order  # dependencies first, wildcard agents last

def import_module_from_path(path: Path):
    """Dynamically imports a Python module from a given file path.

    This is used to load the `return_type.py` file for each agent, which defines
    the Pydantic model for the agent's output.

    Args:
        path (Path): The path to the Python file to import.

    Returns:
        module: The imported module object.
    """
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module        # supports intra-module imports
    spec.loader.exec_module(module)        # run the code
    return module

def load_agents(configs, load_order, static_servers, job_queue):
    """Loads and initializes all agents based on their configurations and load order.

    For each agent, this function:
    1. Locates its configuration and folder.
    2. Dynamically imports its `return_type.py` to get the output Pydantic model.
    3. Resolves its tool dependencies, linking to already loaded agents or static MCP servers.
    4. Initializes an `MCPAgent` instance for it.

    Args:
        configs (Dict[str, AgentConfig]): Dictionary of all agent configurations.
        load_order (List[str]): List of agent names in the correct loading order.
        static_servers (Dict[str, Any]): Dictionary of pre-initialized static MCP servers
                                         that agents can use as tools.
        job_queue (asyncio.Queue): The job queue to be used by the loaded `MCPAgent` instances.

    Returns:
        Dict[str, MCPAgent]: A dictionary mapping agent names to their loaded `MCPAgent` instances.
    """
    loaded = {}
    for name in load_order:
        cfg = configs[name]
        folder = Path("agents_config") / cfg._path

        # --------------------------------------------------------------
        # Determine the ReturnType model.
        # It is optional – if either the config omits `return_type` or the
        # `return_type.py` file is missing/empty, we fall back to a minimal
        # pydantic model which strategies can augment later.
        # --------------------------------------------------------------
        default_return_model_name = f"{cfg.name}Return"
        ReturnType: type[BaseModel]

        if cfg.return_type is not None:
            return_type_file = folder / "return_type.py"
            if return_type_file.exists():
                try:
                    mod = import_module_from_path(return_type_file)
                    ReturnType = getattr(mod, cfg.return_type)
                except (AttributeError, FileNotFoundError, ImportError, SyntaxError) as e:
                    logger.warning(
                        f"Agent '{cfg.name}': Could not import return type '{cfg.return_type}' "
                        f"from {return_type_file}. Falling back to empty model. Error: {e}"
                    )
                    ReturnType = create_model(default_return_model_name, __base__=BaseModel)  # type: ignore[arg-type]
            else:
                logger.info(
                    f"Agent '{cfg.name}': return_type.py not found. Using default empty return model."
                )
                ReturnType = create_model(default_return_model_name, __base__=BaseModel)  # type: ignore[arg-type]
        else:
            # Completely optional.
            ReturnType = create_model(default_return_model_name, __base__=BaseModel)  # type: ignore[arg-type]

        # wildcard support for tools
        if "*" in cfg.tools:
            # All other agent names except self, plus all static server names
            all_tools = [n for n in configs if n != name] + list(static_servers.keys())
            cfg.tools = all_tools

        # resolve tool list: either static or other agents
        tools = []
        for t in cfg.tools:
            if t in static_servers:
                tools.append(static_servers[t])
            else:
                tools.append(loaded[t])

        mcp_agent = MCPAgent(
            name           = cfg.name,
            prompt_file    = str(folder / cfg.prompt_file),
            return_type     = ReturnType,
            inputs_description   = cfg.inputs_description,
            mcp_servers    = tools,
            job_queue  = job_queue,
            model= cfg.model if cfg.model is not None else "o4-mini", 
            strategy_name = cfg.strategy_name if hasattr(cfg, 'strategy_name') else "default",
            tools_config = cfg.tools_config if hasattr(cfg, 'tools_config') else None
        )
        loaded[name] = mcp_agent
    return loaded
