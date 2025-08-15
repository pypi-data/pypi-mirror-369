---
layout: default
title: Configuration Guide
nav_order: 6
permalink: /configuration/
---

# Configuration Guide

nGPT uses a flexible configuration system that supports multiple profiles for different API providers and models. This guide explains how to configure and manage your nGPT settings.

## API Key Setup

### OpenAI API Key
1. Create an account at [OpenAI](https://platform.openai.com/)
2. Navigate to API keys: https://platform.openai.com/api-keys
3. Click "Create new secret key" and copy your API key
4. Configure nGPT with your key:
   ```bash
   ngpt --config
   # Enter provider: OpenAI
   # Enter API key: your-openai-api-key
   # Enter base URL: https://api.openai.com/v1/
   # Enter model: gpt-3.5-turbo (or other model)
   ```

### Google Gemini API Key
1. Create or use an existing Google account
2. Go to [Google AI Studio](https://aistudio.google.com/)
3. Navigate to API keys in the left sidebar (or visit https://aistudio.google.com/app/apikey)
4. Create an API key and copy it
5. Configure nGPT with your key:
   ```bash
   ngpt --config
   # Enter provider: Gemini
   # Enter API key: your-gemini-api-key
   # Enter base URL: https://generativelanguage.googleapis.com/v1beta/openai
   # Enter model: gemini-2.0-flash
   ```

### Setting Up Ollama
1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Run Ollama locally (it should be running on http://localhost:11434)
3. Configure nGPT to use Ollama:
   ```bash
   ngpt --config
   # Enter provider: Ollama-Local
   # Enter API key: (leave blank or press Enter)
   # Enter base URL: http://localhost:11434/v1/
   # Enter model: llama3 (or another model you've pulled in Ollama)
   ```

### Setting Up Groq
1. Create an account at [Groq](https://console.groq.com/)
2. Navigate to API Keys and create a new key
3. Configure nGPT with your Groq key:
   ```bash
   ngpt --config
   # Enter provider: Groq
   # Enter API key: your-groq-api-key
   # Enter base URL: https://api.groq.com/openai/v1/
   # Enter model: llama3-70b-8192 (or another Groq model)
   ```

## Configuration File Location

nGPT stores its configuration in a JSON file located at:

- **Linux**: `~/.config/ngpt/ngpt.conf` or `$XDG_CONFIG_HOME/ngpt/ngpt.conf`
- **macOS**: `~/Library/Application Support/ngpt/ngpt.conf`
- **Windows**: `%APPDATA%\ngpt\ngpt.conf`

## Configuration Structure

The configuration file uses a JSON list format that allows you to store multiple configurations. Each configuration entry is a JSON object with the following fields:

```json
[
  {
    "api_key": "your-openai-api-key",
    "base_url": "https://api.openai.com/v1/",
    "provider": "OpenAI",
    "model": "gpt-4o"
  },
  {
    "api_key": "your-groq-api-key-here",
    "base_url": "https://api.groq.com/openai/v1/",
    "provider": "Groq",
    "model": "llama3-70b-8192"
  },
  {
    "api_key": "your-optional-ollama-key",
    "base_url": "http://localhost:11434/v1/",
    "provider": "Ollama-Local",
    "model": "llama3"
  }
]
```

### Configuration Fields

- **api_key**: Your API key for the service
- **base_url**: The base URL for the API endpoint
- **provider**: A human-readable name for the provider (used for display purposes)
- **model**: The default model to use with this configuration

## Configuration Priority

nGPT determines configuration values in the following order (highest priority first):

1. **Command-line arguments**: When specified directly with `--api-key`, `--base-url`, `--model`, etc.
2. **Environment variables**: 
   - `OPENAI_API_KEY` 
   - `OPENAI_BASE_URL`
   - `OPENAI_MODEL`
3. **CLI configuration file**: Stored in ngpt-cli.conf (see CLI Configuration section)
4. **Main configuration file**: Selected configuration (by default, index 0)
5. **Default values**: Fall back to built-in defaults

### Checking Configuration Sources

Use `ngpt --show-config` to see which configuration values are being used and their sources:

```bash
# Example output showing command-line overrides
ngpt --api-key "" --base-url "http://localhost:1337/api/DeepInfra" --show-config

# Output:
# API Key: [Set] (from command line)
# Base URL: http://localhost:1337/api/DeepInfra (from command line)
# Model: deepseek-ai/DeepSeek-V3 (from command line)
# Note: command line arguments are overriding some configuration values.
```

This helps you understand exactly which configuration values are being used and where they're coming from.

## Interactive Configuration

You can configure nGPT interactively using the CLI:

```bash
# Add a new configuration
ngpt --config

# Edit an existing configuration at index 1
ngpt --config --config-index 1

# Edit an existing configuration by provider name
ngpt --config --provider Gemini

# Remove a configuration at index 2
ngpt --config --remove --config-index 2

# Remove a configuration by provider name
ngpt --config --remove --provider Gemini
```

The interactive configuration will prompt you for values and guide you through the process.

## Command-Line Configuration

You can set configuration options directly via command-line arguments:


```console
❯ ngpt -h

usage: ngpt [-h] [-v] [--api-key API_KEY] [--base-url BASE_URL] [--model MODEL] [--web-search] [--pipe]
            [--temperature TEMPERATURE] [--top_p TOP_P] [--max_tokens MAX_TOKENS] [--log [FILE]]
            [--preprompt PREPROMPT | --role ROLE] [--config [CONFIG]] [--config-index CONFIG_INDEX]
            [--provider PROVIDER] [--remove] [--show-config] [--list-models] [--cli-config [COMMAND ...]]
            [--role-config [ACTION ...]] [--plaintext] [--language LANGUAGE] [--rec-chunk] [--diff [FILE]]
            [--chunk-size CHUNK_SIZE] [--analyses-chunk-size ANALYSES_CHUNK_SIZE] [--max-msg-lines MAX_MSG_LINES]
            [--max-recursion-depth MAX_RECURSION_DEPTH] [--humanize] [-i | -s | -c | -t | -r | -g]
            [prompt]

nGPT - AI-powered terminal toolkit for code, commits, commands & chat

positional arguments::

[PROMPT]                            The prompt to send to the language model

Global Options::

-h, --help                          show this help message and exit
-v, --version                       Show version information and exit
--api-key API_KEY                   API key for the service
--base-url BASE_URL                 Base URL for the API
--model MODEL                       Model to use
--web-search                        Enable web search capability using DuckDuckGo to enhance prompts with relevant
                                    information
--pipe                              Read from stdin and use content with prompt. Use {} in prompt as placeholder
                                    for stdin content. Can be used with any mode option except --text and
                                    --interactive
--temperature TEMPERATURE           Set temperature (controls randomness, default: 0.7)
--top_p TOP_P                       Set top_p (controls diversity, default: 1.0)
--max_tokens MAX_TOKENS             Set max response length in tokens
--log [FILE]                        Set filepath to log conversation to, or create a temporary log file if no path
                                    provided
--preprompt PREPROMPT               Set custom system prompt to control AI behavior
--role ROLE                         Use a predefined role to set system prompt (mutually exclusive with
                                    --preprompt)

Configuration Options::

--config [CONFIG]                   Path to a custom config file or, if no value provided, enter interactive
                                    configuration mode to create a new config
--config-index CONFIG_INDEX         Index of the configuration to use or edit (default: 0)
--provider PROVIDER                 Provider name to identify the configuration to use
--remove                            Remove the configuration at the specified index (requires --config and
                                    --config-index or --provider)
--show-config                       Show the current configuration(s) and exit
--list-models                       List all available models for the current configuration and exit
--cli-config [COMMAND ...]          Manage CLI configuration (set, get, unset, list, help)
--role-config [ACTION ...]          Manage custom roles (help, create, show, edit, list, remove) [role_name]

Output Display Options::

--plaintext                         Disable streaming and markdown rendering (plain text output)

Code Mode Options::

--language LANGUAGE                 Programming language to generate code in (for code mode)

Git Commit Message Options::

--rec-chunk                         Process large diffs in chunks with recursive analysis if needed
--diff [FILE]                       Use diff from specified file instead of staged changes. If used without a path,
                                    uses the path from CLI config.
--chunk-size CHUNK_SIZE             Number of lines per chunk when chunking is enabled (default: 200)
--analyses-chunk-size ANALYSES_CHUNK_SIZE
                                    Number of lines per chunk when recursively chunking analyses (default: 200)
--max-msg-lines MAX_MSG_LINES       Maximum number of lines in commit message before condensing (default: 20)
--max-recursion-depth MAX_RECURSION_DEPTH
                                    Maximum recursion depth for commit message condensing (default: 3)

Rewrite Mode Options::

--humanize                          Transform AI-generated text into human-like content that passes AI detection
                                    tools

Modes (mutually exclusive)::

-i, --interactive                   Start an interactive chat session
-s, --shell                         Generate and execute shell commands
-c, --code                          Generate code
-t, --text                          Enter multi-line text input (submit with Ctrl+D)
-r, --rewrite                       Rewrite text from stdin to be more natural while preserving tone and meaning
-g, --gitcommsg                     Generate AI-powered git commit messages from staged changes or diff file

```

### Command Examples

```bash
# Example: Use specific API key, base URL, and model for a single command
ngpt --api-key "your-key" --base-url "https://api.example.com/v1/" --model "custom-model" "Your prompt here"

# Select a specific configuration by index
ngpt --config-index 2 "Your prompt here"

# Select a specific configuration by provider name
ngpt --provider Gemini "Your prompt here"

# Control response generation parameters
ngpt --temperature 0.8 --top_p 0.95 --max_tokens 300 "Write a creative story"

# Set a custom system prompt (preprompt)
ngpt --preprompt "You are a Linux command line expert. Focus on efficient solutions." "How do I find the largest files in a directory?"

# Log conversation to a specific file
ngpt --interactive --log conversation.log

# Create a temporary log file automatically
ngpt --log "Tell me about quantum computing"

# Process text from stdin using the {} placeholder
echo "What is this text about?" | ngpt --pipe "Analyze the following text: {}"

# Generate git commit message from staged changes
ngpt -g

# Generate git commit message from a diff file
ngpt -g --diff changes.diff
```

## Environment Variables

You can set the following environment variables to override configuration:

```bash
# Set API key
export OPENAI_API_KEY="your-api-key"

# Set base URL
export OPENAI_BASE_URL="https://api.alternative.com/v1/"

# Set model
export OPENAI_MODEL="alternative-model"
```

These will take precedence over values in the configuration file but can be overridden by command-line arguments.

## Checking Current Configuration

To see your current configuration:

```bash
# Show active configuration
ngpt --show-config

# Show all configurations
ngpt --show-config --all
```

## Listing Available Models

To see a list of available models for your active configuration:

```bash
# List models for active configuration
ngpt --list-models

# List models for configuration at index 1
ngpt --list-models --config-index 1

# List models for a specific provider
ngpt --list-models --provider OpenAI
```

## CLI Configuration

nGPT also supports a CLI configuration system for setting default parameter values. See the [CLI Configuration Guide](usage/cli_config.md) for details.

## Role Configuration

nGPT allows you to create and manage custom roles, which are saved system prompts that define specialized AI personas. Roles are stored in the following locations:

- **Linux**: `~/.config/ngpt/ngpt_roles/`
- **macOS**: `~/Library/Application Support/ngpt/ngpt_roles/`
- **Windows**: `%APPDATA%\ngpt\ngpt_roles\`

Each role is saved as a separate JSON file with the role name as the filename.

### Managing Roles

You can manage roles using the `--role-config` option:

```bash
# Show role configuration help
ngpt --role-config help

# Create a new role
ngpt --role-config create expert_coder

# List all available roles
ngpt --role-config list

# Show details of a specific role
ngpt --role-config show expert_coder

# Edit an existing role
ngpt --role-config edit expert_coder

# Remove a role
ngpt --role-config remove expert_coder
```

When creating or editing a role, nGPT opens a multiline editor where you can enter or modify the system prompt for that role. This makes it easy to define complex instructions that guide the AI's behavior.

### Using Roles

To use a role, specify it with the `--role` parameter:

```bash
# Use a role in standard chat mode
ngpt --role expert_coder "Create a function to parse JSON data"

# Use a role with code generation
ngpt --code --role python_expert "Create a class for managing user data"

# Use a role with shell command generation
ngpt --shell --role linux_expert "Find all large log files"

# Use a role in interactive mode
ngpt -i --role writing_assistant
```

The `--role` parameter is mutually exclusive with `--preprompt` since both set the system prompt.

For detailed documentation on creating and managing roles, including examples and best practices, see the [Custom Roles Guide](usage/roles.md).

## Troubleshooting

### Common Configuration Issues

**API Key Issues**
```bash
# Check if your API key is configured
ngpt --show-config

# Verify a connection to the API endpoint
curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/chat/completions

# Set a new API key temporarily
ngpt --api-key "your-key-here" "Test prompt"
```

**Model Availability Issues**
```bash
# Check which models are available
ngpt --list-models

# Try a different model
ngpt --model gpt-3.5-turbo "Test prompt"
```

**Base URL Issues**
```bash
# Check if your base URL is correct
ngpt --show-config

# Try an alternative base URL
ngpt --base-url "https://alternative-endpoint.com/v1/" "Test prompt"
```

### Securing Your Configuration

Your API keys are stored in the configuration file. To ensure they remain secure:

1. Ensure the configuration file has appropriate permissions: `chmod 600 ~/.config/ngpt/ngpt.conf`
2. For shared environments, consider using environment variables instead
3. Don't share your configuration file or API keys with others
4. If you suspect your key has been compromised, regenerate it from your API provider's console

## Next Steps

After configuring nGPT, explore:

- [CLI Usage Guide](usage/cli_usage.md) for general usage information
- [CLI Configuration Guide](usage/cli_config.md) for setting up default CLI options
- [Basic Examples](examples/basic.md) for common usage patterns