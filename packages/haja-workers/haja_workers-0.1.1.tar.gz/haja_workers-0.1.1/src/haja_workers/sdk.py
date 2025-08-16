from __future__ import annotations

import asyncio
from typing import Any

from haja_workers.communication.grpc_communicator import CommunicatorConfig, GrpcCommunicator
from haja_workers.handlers.activate import activate
from haja_workers.rpc.rpc import RpcClient
from haja_workers.config import Config, load_config
from haja_workers.dispatcher.dispatcher import Dispatcher
from haja_workers.state.global_state import GlobalState
from haja_workers.grpccache.grpccache import Client as GrpcCacheClient
from haja_workers.grpcstore.grpcstore import Client as GrpcStoreClient
from haja_workers.state.event_state import EventState
from haja_workers.handlers.inbound_workflow_handler import handle_list_functions, _handle_server_name


class Server:
    """Haja Workers server for running workflow functions.
    
    The Server class is the main entry point for creating and running workflow
    functions. It handles communication with the Haja workflow system, manages
    function registration, and provides access to storage and caching capabilities.
    
    Args:
        config: Configuration for the server. If None, loads configuration
            from environment variables and .env files using load_config().
    
    Example:
        Basic usage with default configuration:
        >>> server = Server()
        >>> # Register functions and start
        
        With custom configuration:
        >>> config = Config(
        ...     server_name="my-worker",
        ...     grpc_server_address="workflow.server.com:50052"
        ... )
        >>> server = Server(config)
    """
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or load_config()
        self._communicator = GrpcCommunicator(
            CommunicatorConfig(
                address=self.config.grpc_server_address,
                server_name=self.config.server_name,
                server_api_token=self.config.server_api_token
            )
        )
        self._dispatcher = Dispatcher()
        self._gs = GlobalState(
            server_name=self.config.server_name,
            workflow_comm=self._communicator,
            dispatcher=self._dispatcher,
        )
        self._gs.rpc_client = RpcClient.new_with_communicator(self._communicator)
        # Initialize cache and store clients
        self._gs.grpc_cache = GrpcCacheClient(self._communicator, server_name=self._gs.server_name)
        self._gs.grpc_store = GrpcStoreClient(self._communicator, server_name=self._gs.server_name)
        self._functions: list[Any] = []

    def register_function(self, function_impl: Any) -> None:
        """Register a workflow function with this server.
        
        Functions must be created using Function[InputType, OutputType] and
        have a handler attached via .with_handler().
        
        Args:
            function_impl: A function implementation created with Function class
                and configured with .with_handler().
                
        Example:
            >>> def my_function():
            ...     fn = Function[MyInput, MyOutput](
            ...         name="my_function",
            ...         version="1.0.0",
            ...         description="My function"
            ...     )
            ...     async def handler(inputs, event, gs):
            ...         return MyOutput(...)
            ...     return fn.with_handler(handler)
            >>> 
            >>> server = Server()
            >>> server.register_function(my_function())
        """
        self._functions.append(function_impl)

    async def _register_server(self) -> None:
        """Register the server with the workflow server"""
        # Create an empty event state for server registration
        event_state = EventState(
            server=self._gs.server_name,
            function="",
            version="",
            node="",
            workflow="",
            run="",
            function_server=self._gs.server_name,
            correlation_id="startup",
        )
        
        # Send server name and function list
        await handle_list_functions(self._gs, event_state)
        print(f"Server '{self._gs.server_name}' registered with workflow server")

    async def _send_startup_broadcast(self) -> None:
        """Send the function list on startup"""
        startup_event_state = EventState(
            server=self._gs.server_name,
            function="startup",
            version="1.0",
            node="startup",
            workflow="startup",
            run="startup",
            function_server=self._gs.server_name,
            correlation_id="startup",
        )
        await handle_list_functions(self._gs, startup_event_state)
        print("Startup function list broadcast sent")

    async def start(self) -> None:
        """Start the workflow server and begin processing requests.
        
        This method:
        1. Establishes connection to the workflow server
        2. Registers all functions with the server
        3. Injects global state (for storage/cache access) into functions
        4. Registers this server instance with the workflow system
        5. Begins listening for workflow events
        6. Runs indefinitely until interrupted
        
        The server will block indefinitely, processing workflow events as they
        arrive. Use Ctrl+C or send a SIGINT to stop the server.
        
        Raises:
            ConnectionError: If unable to connect to the workflow server
            ValueError: If any registered functions are invalid
            
        Example:
            >>> server = Server()
            >>> server.register_function(my_function())
            >>> await server.start()  # Runs forever
        """
        await self._communicator.start()
        for f in self._functions:
            # Inject global state into functions that support it (for access to grpc_store/cache/etc.)
            if hasattr(f, "set_global_state") and callable(getattr(f, "set_global_state")):
                f.set_global_state(self._gs)
            definition = f.get_function_definition()
            # server attribution injection left to list functions call
            key = f"{self._gs.server_name}:{definition['name']}:{definition['version']}"
            self._gs.functions[key] = f
        
        # Register server with workflow server
        await self._register_server()
        
        # Send startup broadcast
        await self._send_startup_broadcast()
        
        await activate(self._gs)
        # Block forever
        await asyncio.Event().wait()
