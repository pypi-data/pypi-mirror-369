# Haja Workers SDK

Python SDK for building workers that integrate with the Haja workflow system.

## Installation

```bash
pip install haja_workers
```

## Quick Start

```python
import asyncio
from haja_workers import Server, SimpleFunction

async def main():
    server = Server()
    
    # Define a simple function
    echo = SimpleFunction[dict, dict](
        name="echo", 
        version="1.0.0", 
        description="Echoes input"
    ).with_handler(lambda inputs: inputs)
    
    # Register and start
    server.register_function(echo)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Create input functions
- Store chat history
- Handle workflow events
- Communicate with the Haja workflow system

## Examples

See the `examples/` directory for more detailed usage examples.
