# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Switch is a Python CLI tool for managing multiple Anthropic Claude API configurations. It allows users to easily switch between different environments (development, testing, production) with support for both auth_token and api_key authentication methods.

## Core Architecture

### Main Components

- **CLI Interface** (`claude_switch/cli.py`): Click-based command line interface with interactive features using questionary
- **Configuration Manager** (`claude_switch/config.py`): Handles JSON config file management, credential storage, and shell integration
- **Core Logic** (`claude_switch/core.py`): Business logic for configuration operations and environment management

### Key Features

- Multi-configuration management with secure credential storage
- Interactive configuration selection with arrow key navigation
- Shell integration for automatic environment variable loading
- Support for both API keys and auth tokens with custom naming
- Cross-shell compatibility (bash, zsh, fish)

## Development Commands  

### Installation and Setup

```bash
# Install in development mode using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .

# Activate virtual environment if using .venv
source .venv/bin/activate
```

### Testing Commands

```bash
# Run the CLI tool directly
python -m claude_switch.cli

# Test installed commands
cs --help
claude-switch --help

# Verify installation
cs --version
```

### Package Management

```bash
# Build package for distribution
python -m build

# Install from local build
pip install dist/claude_switch-1.0.0-py3-none-any.whl
```

## Configuration Structure

The tool uses `~/.claude-switch/config.json` for configuration storage with this structure:

```json
{
  "version": "2.0",
  "active": "config_name",
  "configs": {
    "config_name": {
      "base_url": "https://api.anthropic.com",
      "api_keys": ["key1", "key2|custom_name"],
      "auth_tokens": ["token1", "token2|custom_name"], 
      "note": "Description",
      "active_key": 0,
      "active_auth": -1
    }
  }
}
```

## Key Implementation Details

### Interactive Features

- Uses `questionary` for arrow key navigation in configuration selection
- Supports ESC key cancellation with confirmation prompts
- Visual indicators (✅) for active configurations and credentials

### Shell Integration

- Generates dynamic shell wrapper scripts in `~/.claude-switch/`
- Creates `cs-wrapper.sh` for command aliases and environment loading
- Automatic environment variable export via `env.sh`

### Credential Management

- Supports credential naming with pipe separator (`credential|name`)
- Automatic credential masking for display (`key[:4]...key[-4:]`)
- Per-configuration active credential tracking

### Error Handling

- Graceful handling of missing configurations
- JSON repair for corrupted config files
- File permission management (0o600 for config files)

## Development Notes

### Dependencies

- `click>=8.0.0`: CLI framework
- `questionary>=2.0.0`: Interactive prompts with arrow key support
- `json-repair>=0.30.0`: Robust JSON parsing and repair

### Code Style

- Use existing patterns for configuration management
- Follow Click conventions for command definitions
- Maintain backward compatibility for config file format
- Use type hints where appropriate

### Shell Integration Testing

When testing shell integration:

```bash
# Test shell wrapper generation
cs init

# Verify generated files
ls -la ~/.claude-switch/

# Test environment loading
source ~/.claude-switch/cs-wrapper.sh
cs current --export
```