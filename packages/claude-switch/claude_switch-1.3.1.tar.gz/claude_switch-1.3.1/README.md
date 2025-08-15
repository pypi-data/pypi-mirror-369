# Claude Switch

A Python CLI tool for managing multiple Anthropic Claude API configurations with seamless environment switching.

## Features

- **Multi-configuration management**: Handle multiple Anthropic API configurations
- **One-click switching**: Switch between development, testing, and production environments
- **Dual authentication**: Support for both `auth_token` and `api_key` authentication methods
- **Multiple credentials input**: Support adding multiple keys at once (comma/space separated)
- **Enhanced add command**: Choose between creating new config or adding to existing ones
- **Automatic environment activation**: Environment variables automatically take effect after configuration switch
- **Secure storage**: Configuration file permission protection with encrypted credential storage
- **Interactive navigation**: Arrow key navigation with color highlighting
- **Backup mechanism**: Automatic configuration file backup to prevent data loss

## Installation

### uv Installation (Recommended)
```bash
# Global installation with uv (recommended)
uv tool install claude-switch

# Or run without installation using uvx
uvx claude-switch --help
```

### pip Installation
```bash
pip install claude-switch

# Or using pipx (recommended to avoid dependency conflicts)
pipx install claude-switch
```

### From Source
```bash
git clone https://github.com/elicc/claude-switch.git
cd claude-switch

# Using uv
uv pip install -e .

# Or using pip
pip install -e .
```

## Getting Started

### Initialization
After installation, initialize shell integration:
```bash
cs init
```

Initialization will:
- Automatically detect your shell environment (bash/zsh/fish)
- Generate dynamic shell configuration files
- Add configuration to your shell profile
- Optionally add the first configuration

Restart your terminal or run:
```bash
source ~/.claude-switch/cs-wrapper.sh
```

### Verification
```bash
# Check version
cs --version

# View help
cs --help

# Add first configuration
cs add
```

## Commands

### Interactive Operations
- `cs` - Interactive configuration selection (arrow key navigation)
- `cs add` - Create new configuration or add credentials to existing ones
- `cs css` - Quick credential addition (shortcut command)

### Management Commands
- `cs list` - List all configurations
- `cs use <name>` - Switch to specified configuration
- `cs current` - Display current configuration
- `cs edit <name>` - Edit configuration information
- `cs remove <name>` - Remove configuration
- `cs add-credential [config]` - Add credentials to specified configuration (or select interactively)

### Environment Export
- `cs current --export` - Output executable export commands

## Usage Examples

### Adding a Configuration
```bash
# Interactive configuration addition with options
cs add
# Choose: Create new configuration OR add credentials to existing

# Quick credential addition
cs css
# Select configuration and add credentials

# Add multiple credentials at once
cs add-credential work
# Input: sk-ant-xxx|prod,sk-ant-yyy|dev,sk-ant-zzz|staging
# Or: sk-ant-xxx|prod sk-ant-yyy|dev sk-ant-zzz|staging
```

### Viewing and Managing Configurations
```bash
# View all configurations
cs list
# Output:
# → work - 工作账号 [https://api.anthropic.com] (0tokens, 1keys) [key1]
#   personal - 个人账号 [https://api.anthropic.com] (1tokens, 0keys) [token1]

# Interactive selection
cs
# Use arrow keys to select, press Enter to confirm

# Quick switch
cs use work
```

### Configuration Management
```bash
# Edit configuration information
cs edit work

# View current configuration
cs current
# Output: 当前配置: work - 工作账号 [https://api.anthropic.com] (0tokens, 1keys) [key1]

# Export environment variables
cs current --export
# Output: export ANTHROPIC_BASE_URL="..."; export ANTHROPIC_API_KEY="..."
```

## Configuration Structure

Configuration is stored in `~/.claude-switch/config.json`:

```json
{
  "version": "2.0",
  "active": "work",
  "configs": {
    "work": {
      "base_url": "https://api.anthropic.com",
      "api_keys": ["sk-xxx"],
      "auth_tokens": [],
      "note": "工作账号",
      "active_key": 0,
      "active_auth": -1
    },
    "personal": {
      "base_url": "https://api.anthropic.com",
      "api_keys": [],
      "auth_tokens": ["sk-yyy"],
      "note": "个人账号",
      "active_key": -1,
      "active_auth": 0
    }
  }
}
```

## Interactive Interface Features

- **Cursor highlighting**: Current selection line highlighted in green
- **Status indicators**: Green arrow (→) indicates active configuration
- **Rich information**: Shows configuration name, description, URL, credential count and type
- **Arrow navigation**: Supports up/down arrow key selection with Enter confirmation

## Security Features

- **File permissions**: Configuration file automatically set to 0o600 (user-readable only)
- **Sensitive information masking**: Automatic credential masking during display
- **Automatic backup**: Automatic backup creation when configuration file is corrupted
- **Version compatibility**: Automatic configuration version upgrade handling

## Advanced Usage

### Manual Configuration Editing
You can directly edit the configuration file `~/.claude-switch/config.json`. The system automatically handles format errors and creates backups.

### Environment Variable Settings
```bash
# Automatic activation (requires initialization)
cs use production

# Manual activation
eval $(cs current --export)
```

### Shell Integration
After initialization, the following aliases are automatically available:
- `cs` - Main command
- `csu` - Quick configuration switching
- `csc` - View current configuration
- `css` - Manual environment variable reload

## Troubleshooting

### Installation Issues

**Problem: cs command not found**
```bash
# Check if installed correctly
pip list | grep claude-switch

# Check PATH settings
echo $PATH

# Reinstall
pip install --force-reinstall claude-switch
```

**Problem: Permission errors**
```bash
# Use user installation with pip
pip install --user claude-switch

# Or use uv (recommended)
uv pip install --user claude-switch

# Or use pipx
pipx install claude-switch
```

### Initialization Issues

**Problem: Shell integration not working**
```bash
# Manually source configuration file
source ~/.claude-switch/cs-wrapper.sh

# Check if configuration files exist
ls -la ~/.claude-switch/

# Reinitialize
cs init
```

**Problem: Environment variables not taking effect**
```bash
# Manually load environment variables
source ~/.claude-switch/env.sh

# Or use export command
eval $(cs current --export)
```

## Compatibility

- **Supported Python versions**: 3.8+
- **Supported operating systems**: macOS, Linux, Windows
- **Supported shells**: bash, zsh, fish
- **Supported installation methods**: pip, pipx, conda, uv

## Getting Help

If you encounter issues:
1. View `cs --help` for command assistance
2. Check configuration files in `~/.claude-switch/` directory
3. Submit an Issue on GitHub: https://github.com/elicc/claude-switch/issues

## License

MIT License