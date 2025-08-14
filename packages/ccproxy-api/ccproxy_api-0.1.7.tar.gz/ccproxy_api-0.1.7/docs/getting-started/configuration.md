# Configuration

Configure CCProxy API Server for your local setup and preferences.

## Configuration Methods

The server supports multiple configuration methods with the following priority order:

1. **Command-line arguments** (highest priority - when using CLI)
2. **Environment Variables**
3. **TOML Configuration Files** (`.ccproxy.toml`, `ccproxy.toml`, or `~/.config/ccproxy/config.toml`)
4. **Default Values** (lowest priority)

## Environment Variables

The proxy supports both flat and nested environment variable syntax. For a comprehensive reference, see [CLAUDE.md](/CLAUDE.md).

### Environment Variable Syntax

#### Flat Syntax (Simple)
```bash
PORT=8080
HOST=0.0.0.0
LOG_LEVEL=DEBUG
SECURITY__AUTH_TOKEN=your-token
```

#### Nested Syntax (Recommended)
Uses `__` (double underscore) as delimiter for nested configuration:
```bash
SERVER__PORT=8080
SERVER__HOST=0.0.0.0
SERVER__LOG_LEVEL=DEBUG
SECURITY__AUTH_TOKEN=your-token
```

### Server Configuration

| Variable | Nested Variable | Description | Default | Example |
|----------|----------------|-------------|---------|---------|
| `PORT` | `SERVER__PORT` | Server port | `8000` | `PORT=8080` |
| `HOST` | `SERVER__HOST` | Server host | `127.0.0.1` | `HOST=0.0.0.0` |
| `LOG_LEVEL` | `SERVER__LOG_LEVEL` | Logging level | `INFO` | `LOG_LEVEL=DEBUG` |
| `WORKERS` | `SERVER__WORKERS` | Worker processes | `1` | `WORKERS=4` |
| `RELOAD` | `SERVER__RELOAD` | Auto-reload | `false` | `RELOAD=true` |
| - | `SERVER__LOG_FORMAT` | Log format | `auto` | `SERVER__LOG_FORMAT=json` |
| - | `SERVER__LOG_FILE` | Log file path | - | `SERVER__LOG_FILE=/var/log/app.log` |

### Security Configuration

| Variable | Nested Variable | Description | Default | Example |
|----------|----------------|-------------|---------|---------|
| `SECURITY__AUTH_TOKEN` | `SECURITY__AUTH_TOKEN` | Authentication token for API access | None | `SECURITY__AUTH_TOKEN=abc123xyz789...` |

The proxy accepts authentication tokens in multiple header formats:
- **Anthropic Format**: `x-api-key: <token>` (takes precedence)
- **OpenAI/Bearer Format**: `Authorization: Bearer <token>`

All formats use the same configured `SECURITY__AUTH_TOKEN` value.

### Claude CLI Configuration

| Variable | Nested Variable | Description | Default | Example |
|----------|----------------|-------------|---------|---------|
| `CLAUDE_CLI_PATH` | `CLAUDE__CLI_PATH` | Path to Claude CLI | Auto-detected | `CLAUDE_CLI_PATH=/usr/local/bin/claude` |

### Special Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CONFIG_FILE` | Path to custom TOML config | `CONFIG_FILE=/etc/ccproxy/config.toml` |
| `CCPROXY_CONFIG_OVERRIDES` | JSON config overrides | `CCPROXY_CONFIG_OVERRIDES='{"server":{"port":9000}}'` |
| `CCPROXY_VERBOSE_API` | Verbose API logging | `CCPROXY_VERBOSE_API=true` |
| `CCPROXY_VERBOSE_STREAMING` | Verbose streaming logs | `CCPROXY_VERBOSE_STREAMING=true` |
| `CCPROXY_REQUEST_LOG_DIR` | Request/response log directory | `CCPROXY_REQUEST_LOG_DIR=/tmp/logs` |
| `CCPROXY_JSON_LOGS` | Force JSON logging | `CCPROXY_JSON_LOGS=true` |
| `CCPROXY_TEST_MODE` | Enable test mode | `CCPROXY_TEST_MODE=true` |

### Example Environment Setup

```bash
# .env file
PORT=8080
HOST=0.0.0.0
LOG_LEVEL=INFO
SECURITY__AUTH_TOKEN=abc123xyz789abcdef...  # Optional authentication
CLAUDE_CLI_PATH=/opt/claude/bin/claude

# Advanced settings using nested syntax
SERVER__LOG_FORMAT=json
SERVER__LOG_FILE=/var/log/ccproxy/app.log
SCHEDULER__ENABLED=true
PRICING__UPDATE_ON_STARTUP=true
```

## TOML Configuration (Recommended)

TOML configuration files provide a more readable and structured format. Files are searched in this order:

1. `.ccproxy.toml` in the current directory
2. `ccproxy.toml` in the git repository root
3. `config.toml` in `~/.config/ccproxy/`

### Example TOML Configuration

```toml
# Server settings
host = "127.0.0.1"
port = 8080
log_level = "DEBUG"
workers = 2

# Security settings
cors_origins = ["https://example.com", "https://app.com"]
auth_token = "your-auth-token"

# Docker settings
[docker_settings]
docker_image = "custom-claude-image"
docker_volumes = ["/host/data:/container/data"]
docker_environment = {CLAUDE_ENV = "production"}

# Scheduler settings  
[scheduler]
enabled = true
max_concurrent_tasks = 10
pricing_update_interval_hours = 24
pricing_update_enabled = false     # Default: false (privacy-first)
version_check_enabled = false      # Default: false (privacy-first)

# Pricing settings
[pricing]
cache_ttl_hours = 24
update_on_startup = true
enable_cost_tracking = true

# Claude Code options
[claude_code_options]
model = "claude-3-5-sonnet-20241022"
max_thinking_tokens = 30000
```

## JSON Configuration File

Create a `config.json` file in the project root for advanced configuration:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "reload": false
  },
  "security": {
    "auth_token": "your-secure-token-here"
  },
  "claude": {
    "cli_path": "/path/to/claude",
    "default_model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "timeout": 30
  },
  "logging": {
    "level": "INFO",
    "format": "json",
    "file": "logs/app.log"
  },

  "cors": {
    "enabled": true,
    "allow_origins": ["*"],
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["*"]
  },
  "health": {
    "check_claude_cli": true,
    "detailed_response": false
  }
}
```

## Configuration Sections

### Server Configuration

Controls the FastAPI server behavior:

```json
{
  "server": {
    "host": "0.0.0.0",           // Bind address
    "port": 8000,                // Port number
    "workers": 4,                // Number of worker processes
    "reload": false,             // Auto-reload on file changes (dev only)
    "access_log": true,          // Enable access logging
    "proxy_headers": true        // Trust proxy headers
  }
}
```


### Claude Configuration

Controls Claude CLI integration:

```json
{
  "claude": {
    "cli_path": "/path/to/claude",              // Custom CLI path
    "default_model": "claude-3-5-sonnet-20241022", // Default model
    "max_tokens": 4096,                         // Default max tokens
    "timeout": 30,                              // Request timeout (seconds)
    "auto_detect_path": true,                   // Auto-detect CLI path
    "search_paths": [                           // Custom search paths
      "/usr/local/bin/claude",
      "/opt/claude/bin/claude"
    ]
  }
}
```

### Logging Configuration

Controls application logging:

```json
{
  "logging": {
    "level": "INFO",                    // Log level (DEBUG, INFO, WARNING, ERROR)
    "format": "json",                   // Log format (json, text)
    "file": "logs/app.log",            // Log file path (optional)
    "rotation": "1 day",               // Log rotation (optional)
    "retention": "30 days",            // Log retention (optional)
    "structured": true,                // Enable structured logging
    "include_request_id": true         // Include request IDs
  }
}
```


### CORS Configuration

Configure Cross-Origin Resource Sharing:

```json
{
  "cors": {
    "enabled": true,                   // Enable CORS
    "allow_origins": ["*"],            // Allowed origins
    "allow_methods": ["GET", "POST"],  // Allowed methods
    "allow_headers": ["*"],            // Allowed headers
    "allow_credentials": false,        // Allow credentials
    "max_age": 86400                   // Preflight cache duration
  }
}
```

### Security Configuration

Configure API authentication and security features:

```json
{
  "security": {
    "auth_token": "your-secure-token-here",    // Authentication token for API access
    "enabled": true                            // Enable/disable auth
  }
}
```

**Authentication Headers:** The proxy accepts tokens in multiple formats:
- **Anthropic Format**: `x-api-key: <token>` (takes precedence)
- **OpenAI/Bearer Format**: `Authorization: Bearer <token>`

All formats use the same configured `auth_token` value.

**Note:** When `auth_token` is not set or is null, authentication is disabled.

### Health Check Configuration

Configure health monitoring:

```json
{
  "health": {
    "check_claude_cli": true,          // Check Claude CLI availability
    "detailed_response": false,        // Include detailed health info
    "timeout": 5,                      // Health check timeout
    "include_version": true,           // Include version in response
    "include_metrics": false           // Include basic metrics
  }
}
```

### Privacy & Network Configuration

CCProxy respects your privacy by disabling network calls by default. The following features make external network connections:

- **Version Update Checks**: Disabled by default (checks GitHub API for new releases)
- **Pricing Data Updates**: Disabled by default (downloads pricing data from GitHub)

#### Controlling Network Features

**Via Environment Variables:**
```bash
# Disable all network features
SCHEDULER__VERSION_CHECK_ENABLED=false
SCHEDULER__PRICING_UPDATE_ENABLED=false

# Enable specific features if needed
SCHEDULER__VERSION_CHECK_ENABLED=true      # Enable version checks
SCHEDULER__PRICING_UPDATE_ENABLED=true      # Enable pricing updates
```

**Via CLI Flags:**
```bash
# Disable all network calls
ccproxy serve --no-network-calls

# Disable specific features
ccproxy serve --disable-version-check
ccproxy serve --disable-pricing-updates

# Enable features (override defaults)
SCHEDULER__VERSION_CHECK_ENABLED=true ccproxy serve
```

**Via TOML Configuration:**
```toml
[scheduler]
version_check_enabled = false      # Default: false
pricing_update_enabled = false     # Default: false
```

**Note:** Network features are disabled by default for privacy. You must explicitly enable them if desired.

## Claude CLI Auto-Detection

The server automatically searches for Claude CLI in these locations:

1. **Environment PATH**
2. **Common installation paths:**
   - `~/.claude/local/claude`
   - `~/node_modules/.bin/claude`
   - `./node_modules/.bin/claude`
   - `/usr/local/bin/claude`
   - `/opt/homebrew/bin/claude`
   - `/usr/bin/claude`

### Custom CLI Path

If Claude CLI is installed in a custom location:

```bash
# Environment variable
export CLAUDE_CLI_PATH=/custom/path/to/claude

# Configuration file
{
  "claude": {
    "cli_path": "/custom/path/to/claude"
  }
}
```

## Docker Configuration for Personal Use

### Environment Variables

```yaml
version: '3.8'
services:
  ccproxy-api:
    image: ccproxy
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - HOST=0.0.0.0
      - LOG_LEVEL=INFO
      - CLAUDE_CLI_PATH=/usr/local/bin/claude
    volumes:
      - ~/.config/claude:/root/.config/claude:ro
```

### Volume Mounting for Personal Setup

Mount your Claude configuration and local settings:

```yaml
version: '3.8'
services:
  ccproxy-api:
    image: ccproxy
    ports:
      - "8000:8000"
    volumes:
      - ./config.json:/app/config.json:ro
      - ./logs:/app/logs
      - ~/.config/claude:/root/.config/claude:ro
```

## Personal Use Configuration

### Recommended Settings for Local Development

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "workers": 2,
    "reload": true,
    "access_log": true,
    "proxy_headers": false
  },
  "logging": {
    "level": "INFO",
    "format": "text",
    "file": "./logs/app.log",
    "rotation": "1 day",
    "retention": "7 days"
  },

  "cors": {
    "enabled": true,
    "allow_origins": ["http://localhost:*", "http://127.0.0.1:*"],
    "allow_credentials": false
  },
  "health": {
    "check_claude_cli": true,
    "detailed_response": true
  }
}
```

## Configuration Validation

The server validates configuration on startup and will report errors for:

- Invalid port numbers
- Missing Claude CLI binary
- Invalid log levels
- Malformed JSON configuration
- Network binding issues

### Validation Example

```bash
# Check configuration without starting server
uv run python -m ccproxy.config.validate config.json
```

## Personal Use Scenarios

### Development & Testing

```json
{
  "server": {
    "host": "127.0.0.1",
    "reload": true,
    "workers": 1
  },
  "logging": {
    "level": "DEBUG",
    "format": "text"
  },

}
```

### Daily Personal Use

```json
{
  "server": {
    "host": "127.0.0.1",
    "reload": false,
    "workers": 2
  },
  "logging": {
    "level": "INFO",
    "format": "text"
  },

}
```

### Isolated Docker Setup

```json
{
  "server": {
    "host": "0.0.0.0",
    "reload": false,
    "workers": 2
  },
  "logging": {
    "level": "INFO",
    "format": "json",
    "file": "/app/logs/app.log"
  },

}
```

## Configuration Best Practices for Personal Use

1. **Use environment variables** for local customization and preferences
2. **Use configuration files** for structured settings you want to persist
3. **Validate configuration** before starting the server
4. **Keep backups** of your working configuration files
5. **Use different configurations** for development vs. daily use
6. **Start simple** - use defaults first, then customize as needed
7. **Secure your setup** - bind to localhost (127.0.0.1) for local-only access

## Troubleshooting Configuration

### Common Issues

1. **Server won't bind to port**
   - Check if port is already in use: `netstat -an | grep :8000`
   - Try a different port: `PORT=8001`
   - Check firewall settings

2. **Claude CLI not found**
   - Verify installation: `claude --version`
   - Check PATH: `echo $PATH`
   - Set explicit path: `CLAUDE_CLI_PATH=/path/to/claude`

3. **Configuration file not loaded**
   - Check file exists: `ls -la config.json`
   - Validate JSON syntax: `python -m json.tool config.json`
   - Check file permissions: `chmod 644 config.json`



## Advanced Configuration Reference

### Complete Configuration Options

#### .env File Reference

```bash
# Basic server configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
WORKERS=4
RELOAD=false

# Claude configuration
CLAUDE_CLI_PATH=/usr/local/bin/claude

# Security settings
SECURITY__AUTH_TOKEN=your-secure-token-here
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Advanced configuration using nested syntax
SERVER__LOG_FORMAT=json
SERVER__LOG_FILE=/var/log/ccproxy/app.log
SCHEDULER__ENABLED=true
SCHEDULER__PRICING_UPDATE_INTERVAL_HOURS=24
PRICING__UPDATE_ON_STARTUP=true
OBSERVABILITY__METRICS__ENABLED=false

# Special environment variables
CONFIG_FILE=/etc/ccproxy/config.toml
CCPROXY_VERBOSE_API=false
CCPROXY_JSON_LOGS=true
```

#### Complete JSON Configuration Schema

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "log_level": "INFO",
  "workers": 4,
  "reload": false,
  "cors_origins": ["https://yourdomain.com"],
  "claude_cli_path": "/usr/local/bin/claude",
  "docker_settings": {
    "docker_image": "claude-code-proxy:latest",
    "docker_volumes": [
      "$HOME/.config/claude:/data/home",
      "$PWD:/data/workspace"
    ],
    "docker_environment": {
      "CLAUDE_HOME": "/data/home",
      "CLAUDE_WORKSPACE": "/data/workspace"
    },
    "docker_additional_args": ["--network=host"],
    "docker_home_directory": "/home/user/.config/claude",
    "docker_workspace_directory": "/home/user/projects"
  },
  "claude_code_options": {
    "cwd": "/path/to/working/directory",
    "model": "claude-3-5-sonnet-20241022",
    "max_thinking_tokens": 30000
  },
  "scheduler": {
    "enabled": true,
    "max_concurrent_tasks": 10,
    "pricing_update_interval_hours": 24
  },
  "pricing": {
    "cache_ttl_hours": 24,
    "update_on_startup": true,
    "enable_cost_tracking": true
  }
}
```

### Configuration Validation

All configuration values are automatically validated:

- **Port**: Must be between 1-65535
- **Log Level**: Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL
- **CORS Origins**: Must be valid URLs or "*"
- **Claude CLI Path**: Must exist and be executable
- **Tools Handling**: Must be "error", "warning", or "ignore"

### Environment-Specific Configuration Files

#### Development Environment (`.env.development`)
```bash
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=DEBUG
RELOAD=true
WORKERS=1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Production Environment (`.env.production`)
```bash
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
RELOAD=false
WORKERS=4
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CLAUDE_CLI_PATH=/usr/local/bin/claude
TOOLS_HANDLING=error
CLAUDE_USER=claude
CLAUDE_GROUP=claude
```

### Advanced Configuration Patterns

#### Configuration with Environment Variable Substitution

```json
{
  "host": "${HOST:-0.0.0.0}",
  "port": "${PORT:-8000}",
  "claude_cli_path": "${CLAUDE_CLI_PATH}",
  "cors_origins": ["${CORS_ORIGIN:-*}"]
}
```

#### Multi-Environment Loading Script

```bash
#!/bin/bash
# scripts/load-env.sh

ENV=${1:-development}

case $ENV in
  "development")
    export $(cat .env.development | xargs)
    ;;
  "production")
    export $(cat .env.production | xargs)
    ;;
  *)
    echo "Unknown environment: $ENV"
    exit 1
    ;;
esac

echo "Loaded configuration for: $ENV"
```

### CLI Configuration Commands

```bash
# Display current configuration
ccproxy config

# Test Claude CLI integration
ccproxy claude -- --version

# Test with Docker
ccproxy claude --docker -- --version

# Specify custom configuration file
CONFIG_FILE=/path/to/custom/config.json ccproxy run
```

### Advanced Troubleshooting

#### Configuration Debugging

```bash
# Enable debug logging to see configuration loading
LOG_LEVEL=DEBUG ccproxy run

# Validate configuration without starting server
python -c "from ccproxy.config.settings import get_settings; print('Config valid')"

# Check Claude CLI path resolution
ccproxy claude -- --version
```

#### Common Advanced Issues

1. **Docker Volume Mount Issues**
   ```bash
   # Check volume permissions
   ls -la ~/.config/claude/

   # Fix permissions if needed
   chmod -R 755 ~/.config/claude/
   ```

2. **Environment Variable Substitution**
   ```bash
   # Test variable expansion
   echo "Host: ${HOST:-0.0.0.0}"
   echo "Port: ${PORT:-8000}"
   ```

3. **Complex CORS Configuration**
   ```bash
   # Multiple origins
   CORS_ORIGINS="https://app1.example.com,https://app2.example.com"

   # Development with multiple ports
   CORS_ORIGINS="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"
   ```
