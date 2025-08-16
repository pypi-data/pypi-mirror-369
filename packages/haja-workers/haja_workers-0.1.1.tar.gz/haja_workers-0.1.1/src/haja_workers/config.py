from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv, find_dotenv


logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration for Haja Workers server.
    
    This class holds all configuration parameters needed to connect and operate
    a Haja Workers server instance.
    
    Attributes:
        server_name: Unique identifier for this worker instance. Used to register
            with the workflow server and distinguish this worker from others.
        grpc_server_address: Network address of the Haja workflow server in 
            format 'host:port' (e.g., 'localhost:50051' or 'server.com:50052').
        server_api_token: Authentication token for connecting to the workflow
            server. Leave empty if authentication is not required.
        cache_ttl_seconds: Default time-to-live in seconds for cached function
            results. Functions can override this value individually.
            
    Example:
        >>> config = Config(
        ...     server_name="my-worker",
        ...     grpc_server_address="workflow.server.com:50052",
        ...     server_api_token="your-token-here",
        ...     cache_ttl_seconds=600
        ... )
    """
    server_name: str = "python-execution-server"
    grpc_server_address: str = "localhost:50051"
    server_api_token: str = ""
    cache_ttl_seconds: int = 300


def _load_dotenv_best_effort() -> None:
    """Load .env using multiple discovery strategies without overriding existing env vars."""
    # 1) Prefer VS Code injected env (via envFile) and OS env; do not override
    # 2) Try to find .env from current working directory upward
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path, override=False)
        logger.info("Loaded .env from %s", dotenv_path)
        return

    # 3) Try repository root and package root fallbacks
    sdk_dir = Path(__file__).resolve().parent
    repo_root = sdk_dir.parent.parent
    package_root = sdk_dir.parent
    candidates = [repo_root / ".env", package_root / ".env"]
    for candidate in candidates:
        if candidate.exists():
            load_dotenv(dotenv_path=str(candidate), override=False)
            logger.info("Loaded .env from %s", candidate)
            return

    # 4) Final fallback: load default locations without path (usually no-op)
    load_dotenv(override=False)
    logger.info("No .env file found; using environment defaults")


def load_config() -> Config:
    """Load configuration from environment variables and .env files.
    
    Searches for .env files in multiple locations and loads configuration
    from environment variables. Does not override existing environment variables.
    
    The search order for .env files is:
    1. Current working directory and parent directories
    2. Repository root directory
    3. Package root directory
    
    Environment Variables:
        SERVER_NAME: Unique identifier for this worker (default: "python-execution-server")
        GRPC_SERVER_ADDRESS: Workflow server address (default: "localhost:9090")
        SERVER_API_TOKEN: Authentication token (default: "")
        CACHE_TTL_SECONDS: Default cache TTL in seconds (default: "300")
    
    Returns:
        Config: A fully configured Config instance with values from environment
            variables or defaults.
            
    Example:
        >>> # With .env file containing SERVER_NAME=my-worker
        >>> config = load_config()
        >>> print(config.server_name)
        'my-worker'
    """
    _load_dotenv_best_effort()
    config = Config(
        server_name=os.getenv("SERVER_NAME", "python-execution-server"),
        grpc_server_address=os.getenv("GRPC_SERVER_ADDRESS", "localhost:9090"),
        server_api_token=os.getenv("SERVER_API_TOKEN", ""),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
    )
    logger.info(
        "Config loaded: server_name=%s grpc_server_address=%s cache_ttl_seconds=%s",
        config.server_name,
        config.grpc_server_address,
        config.cache_ttl_seconds,
    )
    return config
