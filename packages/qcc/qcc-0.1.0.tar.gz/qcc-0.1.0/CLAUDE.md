# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastCC (Fast Claude Config) is a modern Python CLI tool for managing Claude Code configurations with multi-profile support, cloud synchronization via GitHub Gist, and encrypted storage. It uses contemporary Python packaging with `uv`/`uvx` for zero-installation deployment and device flow authentication for enhanced security.

## Commands

### Development Commands
```bash
# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run directly with uv for development
uv run fastcc --help

# Install in development mode (optional)
uv pip install -e .

# Run with uvx (simulates user experience)
uvx --from . fastcc
```

### Testing FastCC End-User Experience
```bash
# Zero-installation smart launch (primary user workflow)
uvx fastcc

# Manual commands for testing
uvx fastcc add test "Test configuration"
uvx fastcc list
uvx fastcc status
uvx fastcc use test
```

### Core CLI Commands (uvx-based)
- `uvx fastcc` - 🚀 Smart launch with auto-download, auto-login, and intelligent profile selection
- `uvx fastcc add <name>` - Add new configuration profile
- `uvx fastcc list` - List all configuration profiles  
- `uvx fastcc use <name>` - Launch Claude Code with specific profile
- `uvx fastcc status` - Show FastCC system status
- `uvx fastcc sync` - Manual configuration synchronization

### Smart Launch Workflow
1. **Auto-download**: uvx automatically downloads latest FastCC version
2. **Dependency management**: uv handles all Python dependencies automatically
3. **GitHub Device Flow**: Secure authentication without local web server
4. **Profile selection**: 3-second timeout with intelligent defaults
5. **Claude integration**: Direct launch into Claude Code with applied configuration

## Code Architecture

### Modular Design
The project follows a layered architecture with clear separation of concerns:

```
fastcc/
├── core/           # Core business logic
│   └── config.py   # ConfigManager and ConfigProfile classes
├── storage/        # Storage backend implementations
│   ├── base.py     # StorageBackend abstract base class
│   └── github_gist.py  # GitHub Gist storage implementation
├── auth/           # Authentication modules
│   └── oauth.py    # GitHub OAuth flow implementation
├── utils/          # Utility modules
│   └── crypto.py   # Encryption/decryption utilities
└── cli.py          # Command-line interface using Click
```

### Key Components

#### CLI Interface (`cli.py`)
- **Click Framework**: Modern command-line interface with subcommands
- **Smart Launch**: Default behavior optimized for zero-config experience
- **uvx Integration**: Designed for seamless operation with uvx package runner
- **Interactive UI**: Uses `utils/ui.py` for timeout-based selections and status display

#### Storage Layer (`storage/`)
- **Abstract Interface**: `StorageBackend` defines common operations for extensibility
- **GitHub Gist Backend**: Primary implementation using private Gists for encrypted cloud storage
- **Error Handling**: Comprehensive exception handling for network and API failures

#### Authentication (`auth/oauth.py`)
- **Device Flow Protocol**: GitHub's device flow for CLI applications (no local server required)
- **Polling Mechanism**: Handles authorization_pending and slow_down responses
- **Token Persistence**: Secure local storage with proper file permissions (600)

#### Configuration Management (`core/config.py`)
- **Profile System**: Named configuration profiles with metadata (description, last_used)
- **Bi-directional Sync**: Local caching with cloud synchronization
- **Claude Integration**: Direct manipulation of `~/.claude/settings.json`
- **Encrypted Storage**: API keys encrypted before cloud upload using derived user keys

#### Utility Modules (`utils/`)
- **Cryptography**: End-to-end encryption with user-specific key derivation
- **User Interface**: Timeout-based prompts and cross-platform compatibility
- **Status Display**: Rich console output with icons and structured information

### Security Architecture

1. **User-Owned Data**: All configuration data stored in user's own GitHub Gist
2. **Encrypted Storage**: API keys encrypted before upload to cloud
3. **Secure Token Storage**: OAuth tokens stored with restricted file permissions
4. **No Shared Infrastructure**: No centralized database or shared storage

### Integration Points

- **Claude Code**: Updates `~/.claude/settings.json` to configure API settings
- **GitHub API**: Uses Gists for cloud storage and user authentication
- **Local Filesystem**: Caches configuration in `~/.fastcc/` directory

## Development Notes

### Modern Python Packaging
- **pyproject.toml**: Uses modern Python packaging standards with Hatchling build backend
- **uvx Compatibility**: Configured for zero-installation deployment via uvx
- **Entry Points**: Multiple CLI entry points (`nv`, `fastcc`) for user convenience
- **Version Management**: Dynamic versioning from `fastcc/__init__.py`

### Dependencies and Compatibility
- **Core Dependencies**: Click (CLI), requests (HTTP), cryptography (encryption)
- **Python 3.7+**: Broad compatibility while supporting modern features
- **Cross-Platform**: Works on macOS, Linux, and Windows with platform-specific adaptations
- **No Optional Dependencies**: All functionality included in base installation

### Authentication Implementation
- **Device Flow**: Replaces traditional OAuth web callback for better CLI UX
- **Public Client**: Uses GitHub CLI's established client ID for community trust
- **Graceful Degradation**: Handles network failures and authentication timeouts
- **Token Refresh**: Currently single-use tokens (consider refresh token implementation for production)

### Legacy Components
- **setup_claude_config.py**: Original simple configuration script (retained for reference)
- **requirements.txt**: Maintained for pip compatibility alongside pyproject.toml