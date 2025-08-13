# CBT Query MCP Server

A simple Model Context Protocol (MCP) server for querying TensorRT test coverage and case mapping data.

## Features

- Query all test cases and files
- Get coverage mapping by case name
- Query cases by files and/or functions
- Simple HTTP client with proper error handling
- Minimal logging and clean code structure

## Installation

### Prerequisites

- Python 3.10 or later
- pip package manager

### Option 1: Using Installation Scripts

#### Windows
```batch
# Run the Windows installation script
install.bat
```

#### Unix/Linux/macOS
```bash
# Run the Unix installation script
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

#### Windows
```batch
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install the package
pip install -e .
```

#### Unix/Linux/macOS
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package
pip install -e .
```

### Option 3: Using uv (if available)
```bash
# Initialize with uv
uv init
cd cbt-query

# Create virtual environment and activate it
uv venv
source .venv/bin/activate  # Unix
# or
.venv\Scripts\activate.bat  # Windows

# Install dependencies
uv add "mcp[cli]" httpx requests
```

## Usage

### Running the Server

After installation, you can run the server in several ways:

#### Method 1: Using the installed command
```bash
# Activate virtual environment first
source venv/bin/activate  # Unix
# or
venv\Scripts\activate.bat  # Windows

# Run the server
cbt-query
```

#### Method 2: Using Python module
```bash
python -m cbt_query
```

#### Method 3: Direct execution
```bash
python main.py
```

### Configuration for Cursor

Add the following configuration to your `~/.cursor/mcp.json` file:

#### Windows
export CBT_SERVER_URL="http://dlswqa-nas:12345/"
```json
{
    "mcpServers": {
        "cbt_query": {
            "command": "python",
            "args": [
                "-m", "cbt_query"
            ],
            "cwd": "C:\\path\\to\\your\\cbt-query\\installation"
        }
    }
}
```

#### Unix/Linux/macOS
```json
{
    "mcpServers": {
        "cbt_query": {
            "command": "python3",
            "args": [
                "-m", "cbt_query"
            ],
            "cwd": "/path/to/your/cbt-query/installation"
        }
    }
}
```

#### Alternative configuration using uv
```json
{
    "mcpServers": {
        "cbt_query": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/your/cbt-query",
                "run",
                "python",
                "-m", "cbt_query"
            ]
        }
    }
}
```

## Available Tools

The MCP server provides the following tools:

- `query_all_cases`: Get all test cases from the server
- `query_all_files`: Get all files from the server  
- `query_by_case`: Get coverage mapping by case name
- `query`: Query cases by files and/or functions

## API Examples

```python
# Get all cases
await query_all_cases()

# Get all files
await query_all_files()

# Get coverage by case
await query_by_case("test_case_name")

# Query by file
await query(file_name="example.cpp")

# Query by function
await query(funcs="example_function")

# Query by file and function
await query(file_name="example.cpp", funcs="example_function")
```

## Development

uv init new_project
cd new_project

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx requests pip


# cursor setup 

```
# ~/.cursor/mcp.json
{
  "mcpServers": {
    "trt_query": {
      "command": "python",
      "args": [
        "-m",
        "cbt_query"
      ],
      "env": {
        "CBT_SERVER_URL": "http://dlswqa-nas:12345/"
      }
    }
  }
}
```



## Environment Setup

Make sure to set the `CBT_SERVER_URL` environment variable:

```bash
export CBT_SERVER_URL="http://your-server:12345"
```

### Debug Mode

To enable debug mode with detailed logging, set the `CBT_DEBUG` environment variable:

```bash
export CBT_DEBUG=1
# or
export CBT_DEBUG=true
```

## Troubleshooting

### Common Issues

1. **CBT_SERVER_URL not set**: Make sure the environment variable is set
2. **Import errors**: Verify all dependencies are installed in the active environment
3. **Connection errors**: Check that the CBT server is running and accessible

### Logging

The server logs to stderr with INFO level by default.
