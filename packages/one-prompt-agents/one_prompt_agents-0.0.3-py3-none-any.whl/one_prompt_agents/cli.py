"""
This is the main command-line interface (CLI) entry point for the one-prompt-agents framework.

It uses `argparse` to handle command-line arguments for various operations like selecting
an agent, providing a prompt, configuring logging, and choosing run modes (REPL, autonomous,
or HTTP server).

This module orchestrates the entire application lifecycle:
- Initializes logging.
- Starts the main MCP server and discovers other MCP servers.
- Discovers and loads agent configurations.
- Sets up the asyncio event loop and signal handlers.
- Manages the job queue and chat workers.
- Loads all agents and makes them available to other modules (API, MCP setup).
- Handles different run modes based on CLI arguments.
- Ensures graceful shutdown of all components.
"""
import argparse
import asyncio
import os
import sys
import signal
import uvicorn
import logging
from pathlib import Path

from one_prompt_agents.agents_loader import discover_configs, topo_sort, load_agents
from one_prompt_agents.core_chat import chat_worker, user_chat
from one_prompt_agents.job_manager import submit_job, JOBS # Ensure JOBS is imported
from one_prompt_agents.mcp_servers_loader import collect_servers
from one_prompt_agents.logging_setup import setup_logging
from one_prompt_agents.http_start import ensure_server, trigger
from one_prompt_agents.utils import uvicorn_log_level

# Import the new modules
from one_prompt_agents.api import app as fastapi_app, set_agents_for_api
from one_prompt_agents.mcp_setup import mcp as main_mcp, start_mcp_server, set_agents_for_mcp_setup, set_job_queue_for_mcp_setup

logger = logging.getLogger(__name__)

# Global agents dictionary, to be populated by load_agents
# and then passed to api.py and mcp_setup.py
AGENTS_REGISTRY = {}

def run_server_cli():
    """Parses command-line arguments for agent_name and prompt, then triggers ensure_server and trigger.
    This is intended to be a CLI entry point for starting a specific agent task via HTTP,
    likely by ensuring the main FastAPI server is up and then POSTing to it.
    """
    parser = argparse.ArgumentParser(description="Run an agent task by ensuring the server is running and triggering it.")
    parser.add_argument("agent_name", help="Agent to target")
    parser.add_argument("prompt", help="Input prompt for the agent")
    args = parser.parse_args()
    
    # The original ensure_server and trigger from http_start.py are used here.
    # ensure_server might try to start the main FastAPI server if not running.
    if ensure_server(args.agent_name, args.prompt): # ensure_server needs agent_name and prompt for its own logic if any
        trigger(args.agent_name, args.prompt)
    else:
        logger.error("Failed to ensure server is running. Cannot trigger agent.")

def main_cli():
    """The main command-line interface entry point for the application.

    Orchestrates application setup, agent loading, and run mode execution based on CLI args.
    """
    global AGENTS_REGISTRY
    NUM_WORKERS = 4  # Define the number of workers

    parser = argparse.ArgumentParser(description="One-Prompt Agents Framework CLI")
    parser.add_argument("agent_name", nargs="?", help="Agent to target for REPL or autonomous run")
    parser.add_argument("prompt", nargs="?", help="Input prompt for autonomous mode. If provided with agent_name, runs autonomously.")
    parser.add_argument("--log", action="store_true", dest="log_to_file", help="Redirect logs to a file.")
    parser.add_argument("-v", "--verbose", action="store_const", const=logging.DEBUG, dest="log_level", help="Enable verbose output (sets logging level to DEBUG).")
    
    # Potentially add a sub-command for run_server_cli if desired
    # parser.add_subparsers(...) 

    args = parser.parse_args()

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: The OPENAI_API_KEY environment variable is not set. Please set it before running the application.", file=sys.stderr)
        sys.exit(1)
    if not args.log_level:
        print('Logging disabled')
        logging.disable(logging.CRITICAL)
    else:
        print('Enabling logging')
        # Pass args.log_level to setup_logging if it should also control console level, 
        # or rely on its default DEBUG for file and basicConfig for console.
        setup_logging(log_to_file=args.log_to_file, level=args.log_level or logging.INFO)

    logger.info("Starting main MCP server...")
    main_mcp_task = start_mcp_server() # From mcp_setup.py

    logger.info("Collecting external MCP servers...")
    mcp_servers, mcp_tasks = collect_servers() # From mcp_servers_loader.py
    mcp_tasks.append(main_mcp_task)
    logger.info(f"External MCP Servers collected: {list(mcp_servers.keys())}")

    logger.info("Discovering and ordering agent configurations...")
    configs = discover_configs(Path("agents_config"))
    load_order = topo_sort(configs)

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, loop.stop)

    job_queue = asyncio.Queue()
    worker_tasks = [loop.create_task(chat_worker(job_queue)) for _ in range(NUM_WORKERS)]
    logger.info(f"Started {NUM_WORKERS} chat workers.")

    # Pass the job queue to the mcp_setup module so it can add queue-dependent tools
    set_job_queue_for_mcp_setup(job_queue)

    server_task = None # Initialize server_task
    server_instance = None # Initialize server_instance
    should_start_server = False # Flag to control server startup

    try:
        logger.info("Loading agents...")
        AGENTS_REGISTRY = load_agents(configs, load_order, mcp_servers, job_queue)
        logger.info(f"Loaded agents: {list(AGENTS_REGISTRY.keys())}")

        set_agents_for_api(AGENTS_REGISTRY)
        set_agents_for_mcp_setup(AGENTS_REGISTRY)
        logger.info("Agent registries in api.py and mcp_setup.py have been updated.")

        if args.agent_name and not args.prompt: # REPL mode
            logger.info(f"Starting interactive REPL for agent: {args.agent_name}")
            target_mcp_agent = AGENTS_REGISTRY.get(args.agent_name)
            if not target_mcp_agent:
                logger.error(f"Agent {args.agent_name} not found for REPL mode.")
                raise ValueError(f"Agent {args.agent_name} not found.")
            loop.run_until_complete(user_chat(target_mcp_agent))
            logger.info("Interactive REPL terminated by user.")
            # In REPL mode, we typically don't start the server afterwards.
            should_start_server = False

        elif args.agent_name and args.prompt: # Autonomous mode
            logger.info(f"Starting autonomous console run for agent: {args.agent_name} with prompt: '{args.prompt[:50]}...'")
            target_mcp_agent = AGENTS_REGISTRY.get(args.agent_name)
            if not target_mcp_agent:
                logger.error(f"Agent {args.agent_name} not found for autonomous mode.")
                raise ValueError(f"Agent {args.agent_name} not found.")

            async def run_job_and_wait():
                job_id = await submit_job(job_queue, target_mcp_agent.agent, args.prompt, target_mcp_agent.strategy_name)
                logger.info(f"Submitted job {job_id} for agent {args.agent_name}")
                
                # Keep track of initially submitted jobs if needed, though checking all JOBS is more robust.
                # initial_job_ids = {job_id} # If you only want to track this specific job and its children.
                                            # For now, we'll wait for ALL jobs in the system.

                while True:
                    await asyncio.sleep(1) # Check every second
                    
                    all_jobs_processed = True
                    if not job_queue.empty(): # If queue has items, not all processed by workers yet
                        all_jobs_processed = False
                    else:
                        # If queue is empty, check JOBS dictionary for any non-terminal states
                        if not JOBS: # If JOBS itself is empty and queue is empty.
                            logger.info("JOBS dictionary is empty and job_queue is empty. All jobs considered processed.")
                            all_jobs_processed = True
                        else:
                            active_jobs_found = False
                            for j_id, job_data in JOBS.items():
                                # Terminal states
                                terminal_states = ['done', 'failed', 'cancelled', 'error']
                                if job_data.status not in terminal_states:
                                    logger.debug(f"Job {j_id} is still active with status: {job_data.status}. Waiting...")
                                    active_jobs_found = True
                                    break 
                            if active_jobs_found:
                                all_jobs_processed = False
                            else:
                                # All jobs in JOBS are in a terminal state, and queue is empty
                                all_jobs_processed = True
                    
                    if all_jobs_processed:
                        logger.info(f"All jobs, including {job_id} and its dependencies (based on JOBS dict and job_queue), appear to be completed.")
                        break
                
                # Optional: A final job_queue.join() with a timeout could be a safeguard.
                # This ensures any tasks put on the queue *just* as the above loop was exiting are processed.
                # However, the JOBS check should be the primary condition.
                try:
                    await asyncio.wait_for(job_queue.join(), timeout=5.0)
                    logger.info("job_queue.join() completed successfully after JOBS check.")
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for job_queue.join() after main job completion check. This might be okay if JOBS indicated all done.")

                logger.info(f"Job {job_id} and all other jobs in the system (based on JOBS dict and queue observation) are completed.")
            
            loop.run_until_complete(run_job_and_wait())
            logger.info("Autonomous console run completed.")
            # After autonomous run, proceed to start the server.
            should_start_server = True

        else: # Default to server mode if no specific mode selected
            logger.info("No specific agent/prompt provided. Defaulting to HTTP server mode.")
            should_start_server = True

        if should_start_server:
            logger.info("Starting HTTP server...")
            config = uvicorn.Config(fastapi_app, host="127.0.0.1", port=9000, loop="asyncio", log_level=uvicorn_log_level())
            server_instance = uvicorn.Server(config) # Assign to server_instance
            server_task = loop.create_task(server_instance.serve()) # Use server_instance
            logger.info("HTTP server started. Running event loop forever.")
            try:
                # Only run forever if the server is meant to be the primary mode or after an autonomous run.
                # If loop.stop() was called by run_job_and_wait or REPL, this might exit quickly.
                # We need to ensure it runs if the server is up.
                if not loop.is_closed() and not loop.is_running(): # If loop was stopped e.g. by run_job_and_wait
                     loop.run_forever() # Restart it for the server
                elif not loop.is_closed(): # If it's already running (e.g. first time server start)
                    pass # It will be handled by the existing run_forever or specific run_until_complete
                # If the loop is already running because of other tasks, loop.run_forever() might not be needed
                # if the server_task keeps it alive.
                # For explicit server mode, loop.run_forever() is typical.
                # Let's ensure loop.run_forever() is called if server is up and no other mode stopped the loop.
                if server_task and not server_task.done():
                    loop.run_forever()

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received. Shutting down server.")
            # The finally block will handle server shutdown
            
    except ValueError as err:
        logger.error(f"ValueError during main execution: {err}", exc_info=True)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logger.info("Initiating graceful shutdown...")

        async def shutdown_async():
            """Gathers and runs all async cleanup tasks concurrently."""
            logger.info("--- Starting Async Shutdown Sequence ---")

            # 1. Shutdown Uvicorn HTTP server if it was started
            if server_task and server_instance and server_instance.started:
                logger.info("Shutting down main Uvicorn HTTP server...")
                try:
                    await server_instance.shutdown()
                    logger.info("Main Uvicorn HTTP server shut down.")
                except Exception as e:
                    logger.error(f"Error shutting down Uvicorn: {e}", exc_info=True)
            elif server_task and not server_task.done():
                server_task.cancel()

            # 2. Gather all agent and external server cleanup coroutines
            cleanup_coroutines = []
            logger.info(f"Gathering cleanup tasks for agents: {list(AGENTS_REGISTRY.keys())}")
            for agent in AGENTS_REGISTRY.values():
                if hasattr(agent, 'end_and_cleanup'):
                    cleanup_coroutines.append(agent.end_and_cleanup())
            
            logger.info(f"Gathering cleanup tasks for external MCP servers: {list(mcp_servers.keys())}")
            for srv in mcp_servers.values():
                if hasattr(srv, 'cleanup'):
                    cleanup_coroutines.append(srv.cleanup())
            
            # Run all cleanup coroutines concurrently
            if cleanup_coroutines:
                logger.info(f"Executing {len(cleanup_coroutines)} cleanup coroutines...")
                results = await asyncio.gather(*cleanup_coroutines, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        logger.error(f"Error during async cleanup: {res}", exc_info=res)
                logger.info("Agent and server cleanup coroutines finished.")

            # 3. Cancel all remaining top-level tasks (workers, main MCP, etc.)
            tasks_to_cancel = mcp_tasks + worker_tasks
            logger.info(f"Cancelling {len(tasks_to_cancel)} background tasks...")
            for task in tasks_to_cancel:
                if not task.done():
                    task.cancel()
            
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
            logger.info("Background tasks cancelled.")

            # 4. Shutdown default executor for threads
            logger.info("Shutting down default executor...")
            await loop.shutdown_default_executor()
            logger.info("Default executor shut down.")
            logger.info("--- Async Shutdown Sequence Complete ---")

        if not loop.is_closed():
            logger.info("Running final shutdown sequence.")
            loop.run_until_complete(shutdown_async())
            
            # Add a small delay to allow cancelled tasks to finish their cleanup
            # before the event loop is closed. This prevents "Event loop is closed" errors.
            logger.info("Draining event loop before final close...")
            loop.run_until_complete(asyncio.sleep(0.1))

            loop.close()
            logger.info("Event loop closed.")
        else:
            logger.info("Event loop was already closed.")
        
        logging.shutdown()
        print("Application shutdown complete.")

if __name__ == "__main__":
    # This allows running: python -m one_prompt_agents.cli <args>
    # Or if this file is made executable and put on PATH: cli <args>
    main_cli() 