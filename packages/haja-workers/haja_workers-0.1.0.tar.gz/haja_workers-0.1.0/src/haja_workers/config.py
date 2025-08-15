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
