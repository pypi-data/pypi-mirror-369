# Niteco Agno Agent Tool

A service that manages and executes agno agents with OPAL SDK integration. This repository contains both the core package and example agent implementations, including an eCommerce Analytics Agent that provides industry KPI benchmarks.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Niteco.Opal-Agno-agent-tool
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
├── cr_statistic_agent/          # eCommerce Analytics Agent
│   ├── agent.py                 # Main agent implementation
│   ├── agent_prompt.py          # Agent prompts and configurations
│   ├── csv_output/              # Sample data files
│   └── json_to_csv_parser.py    # Data processing utilities
├── niteco/                      # Public package source
│   └── agno_agent_tool/         # Agent tool service package
└── requirements.txt             # Development dependencies
```

## Running the eCommerce Analytics Agent

```bash
cd cr_statistic_agent
python agent.py
```

The agent service will be available at `http://localhost:8001`

## Core Architecture

### AgnoAgentToolService
The main service (`niteco/agno_agent_tool/agno_agent_tool_service.py`) extends OPAL ToolsService to:
- Manage agno agent lifecycle and registration
- Provide FastAPI endpoints for agent interaction
- Integrate with OPAL SDK for tool registration
- Handle async agent execution with proper error handling

### eCommerce Analytics Agent
The example agent (`cr_statistic_agent/agent.py`) provides:
- eCommerce KPI analysis using DuckDB
- Industry benchmarks from Dynamic Yield dataset (200M+ users, 400+ brands)
- 7 KPI tables: conversion_rate, add_to_cart_rate, cart_abandonment_rate, average_order_value, units_per_transaction, average_transactions_per_user, device_usage
- Automatic CSV to database conversion for analytics

## Key Dependencies

- **agno** - Agent framework providing the base Agent class and tools
- **OPAL SDK** (`optimizely-opal.opal-tools-sdk`) - Tools service integration
- **FastAPI** - Web framework for REST API endpoints  
- **DuckDB** - In-memory analytical database for CSV data processing
- **Groq** - LLM provider integration
- **python-dotenv** - Environment variable management

## Package Development

### Building the Package
The public package is located in `/niteco` and can be built using:

```bash
# Build the package
python setup.py sdist bdist_wheel

# Install package in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

### Testing and Quality
```bash
# Run tests (if pytest is installed)
pytest

# Code formatting (if available)
black .
isort .

# Type checking (if mypy is installed)
mypy niteco/
```

### Public Package Installation
For end-users, install the published package:

```bash
pip install niteco.agno-agent-tool
```

## Contributing

1. Make changes in the development environment
2. Test your changes with the example agents
3. Update the public package in `/niteco` if needed
4. Submit a pull request

## License

MIT License