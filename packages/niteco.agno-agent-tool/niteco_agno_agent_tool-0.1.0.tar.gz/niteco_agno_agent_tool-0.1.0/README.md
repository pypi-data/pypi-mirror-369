# Niteco Agno Agent Tool Service

A service that manages and executes agno agents with OPAL SDK integration.

## Features

- **Agent Registry**: Register and manage multiple agno agents
- **Tool Integration**: Seamless integration with OPAL Tools SDK
- **FastAPI Backend**: RESTful API for agent interactions
- **Async Support**: Full async/await support for agent operations
- **Health Monitoring**: Built-in health checks and metrics

## Installation

```bash
pip install niteco.agno-agent-tool
```

## Quick Start

```python
from fastapi import FastAPI
from agno.agent import Agent
from niteco.agno_agent_tool import create_agno_agent_service

# Create FastAPI app
app = FastAPI()

# Create the service
service = create_agno_agent_service(app)

# Register an agent
agent = Agent(agent_id="my_agent", name="My Agent")
service.register_agent(agent, "I help with general tasks")

# Start the service
@app.on_event("startup")
async def startup():
    await service.startup()

@app.on_event("shutdown") 
async def shutdown():
    await service.shutdown()
```

## API Usage

Once your service is running, you can interact with registered agents:

```bash
# Run an agent
curl -X POST "http://localhost:8000/agents/my_agent/run" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, agent!"}'
```

## Core Components

### AgnoAgentToolService

The main service class that extends OPAL's ToolsService:

- Manages agent registry
- Provides FastAPI endpoints
- Handles agent execution
- Monitors service health

### AgentToolRegistry

Registry for managing agent instances:

- Register/unregister agents
- Track running tasks
- Manage agent metadata

### AgentRunRequest

Pydantic model for agent execution requests:

```python
class AgentRunRequest(BaseModel):
    message: str
```

## Requirements

- Python >= 3.8
- fastapi >= 0.95.0
- agno >= 1.7.0
- optimizely-opal.opal-tools-sdk >= 0.1.0
- pydantic >= 2.0.0
- uvicorn >= 0.20.0

## Development

Install with development dependencies:

```bash
pip install niteco.agno-agent-tool[dev]
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.