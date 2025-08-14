# Claude MPM Project Guidelines

This document provides guidelines for working with the claude-mpm project.

## Project Overview

Claude MPM (Multi-Agent Project Manager) is a framework for Claude that enables multi-agent workflows and extensible capabilities.

## Key Resources

- 📁 **Project Structure**: See [docs/STRUCTURE.md](docs/STRUCTURE.md) for file organization
- 🧪 **Quality Assurance**: See [docs/QA.md](docs/QA.md) for testing guidelines
- 🚀 **Deployment**: See [docs/DEPLOY.md](docs/DEPLOY.md) for versioning and deployment
- 📊 **Logging**: See [docs/RESPONSE_LOGGING_CONFIG.md](docs/RESPONSE_LOGGING_CONFIG.md) for response logging configuration
- 🔢 **Versioning**: See [docs/VERSIONING.md](docs/VERSIONING.md) for version management
- 🧠 **Memory System**: See [docs/MEMORY.md](docs/MEMORY.md) for agent memory management
- 🤖 **Local Agents**: See [docs/PROJECT_AGENTS.md](docs/PROJECT_AGENTS.md) for local agent deployment
- 🔧 **PM Architecture**: See [docs/developer/02-core-components/pm-architecture.md](docs/developer/02-core-components/pm-architecture.md) for PM instruction system
- 📝 **Agent Response Format**: See [docs/developer/12-responses/TECHNICAL_REFERENCE.md](docs/developer/12-responses/TECHNICAL_REFERENCE.md) for structured response requirements

## Development Guidelines

### Critical Principles

**🔴 NEVER ASSUME - ALWAYS VERIFY**
- **NEVER assume** file locations, configurations, or implementations
- **ALWAYS verify** by reading actual files and checking current state
- **ALWAYS check** existing code patterns before implementing
- **NEVER guess** at directory structures or file contents
- **ALWAYS confirm** dependencies and imports exist before using them

### Before Making Changes

1. **Understand the structure**: Always refer to `docs/STRUCTURE.md` when creating new files
   - **Scripts**: ALL scripts go in `/scripts/`, NEVER in project root
   - **Tests**: ALL tests go in `/tests/`, NEVER in project root
   - **Python modules**: Always under `/src/claude_mpm/`
2. **Run tests**: Execute E2E tests after significant changes using `./scripts/run_e2e_tests.sh`
3. **Check imports**: Ensure all imports use the full package name: `from claude_mpm.module import ...`
4. **Verify assumptions**: NEVER assume - always check actual files, read configs, verify dependencies

### Testing Requirements

**After significant changes, always run:**
```bash
# Quick E2E tests
./scripts/run_e2e_tests.sh

# Full test suite
./scripts/run_all_tests.sh
```

See [docs/QA.md](docs/QA.md) for detailed testing procedures.

### Key Components

1. **Agent System** (`src/claude_mpm/agents/`)
   - Templates for different agent roles
   - Dynamic discovery via `AgentRegistry`
   - Three-tier precedence: PROJECT > USER > SYSTEM
   - Local project agents in `.claude-mpm/agents/`
   - **Capabilities Discovery**: Agent capabilities read from deployed agents in `.claude/agents/` to ensure consistency with Claude Code

2. **Memory System** (`src/claude_mpm/services/`)
   - Persistent agent learning and knowledge storage
   - Memory management, routing, optimization, and building
   - See [docs/MEMORY.md](docs/MEMORY.md) for comprehensive guide

3. **Hook System** (`src/claude_mpm/hooks/`)
   - Extensibility through pre/post hooks
   - **Response Logging**: Hook-based capture of `SubagentStop` and `Stop` events
   - **Structured Agent Responses**: JSON format for proper logging and memory integration

4. **Services** (`src/claude_mpm/services/`)
   - Business logic layer
   - Hook service, agent management, etc.

5. **CLI System** (`src/claude_mpm/cli/`)
   - Modular command structure
   - Centralized argument parsing
   - See [CLI Architecture](src/claude_mpm/cli/README.md) for details

## Quick Start

```bash
# Interactive mode
./claude-mpm

# Non-interactive mode
./claude-mpm run -i "Your prompt here" --non-interactive

# Create a local project agent (supports JSON, YAML, or MD formats)
mkdir -p .claude-mpm/agents
cat > .claude-mpm/agents/custom_engineer.json << 'EOF'
{
  "agent_id": "custom_engineer",
  "version": "2.0.0",
  "metadata": {
    "name": "Custom Engineer Agent",
    "description": "Custom engineer for this project"
  },
  "capabilities": {
    "tools": ["project_tools", "custom_debugger"],
    "model": "claude-sonnet-4-20250514"
  },
  "instructions": "# Custom Engineer Agent\n\nThis engineer has specific knowledge about our project architecture."
}
EOF

# List agents by tier to see which version is being used
./claude-mpm agents list --by-tier

# Deploy specific agents (exclude others for performance)
cat > .claude-mpm/configuration.yaml << 'EOF'
agent_deployment:
  excluded_agents:
    - research
    - data_engineer
    - ops
  case_sensitive: false
EOF

# Deploy agents with exclusions (automatically skips excluded agents)
./claude-mpm agents deploy

# Or deploy all agents, ignoring exclusions
./claude-mpm agents deploy --include-all
```

## Local Agent Deployment

Claude MPM supports project-specific agents that take precedence over system and user agents:

### Agent Precedence (Highest to Lowest)
1. **PROJECT** - `.claude-mpm/agents/` in your project (**JSON format only**)
2. **USER** - `~/.claude-mpm/agents/` in your home directory (any format)
3. **SYSTEM** - Built-in framework agents

### Creating Local Agents

Create project-specific agents to:
- Override system agents with project-specific knowledge
- Add custom agents for your domain/workflow
- Test new agent configurations before promoting them

**Important**: Project agents in `.claude-mpm/agents/` must be JSON format. They're automatically converted to Markdown in `.claude/agents/` for Claude Desktop compatibility.

```bash
# Create project agents directory
mkdir -p .claude-mpm/agents

# Example: Custom QA agent with project-specific rules (JSON format only)
cat > .claude-mpm/agents/qa.json << 'EOF'
{
  "agent_id": "qa",
  "version": "2.0.0",
  "metadata": {
    "name": "Project QA Agent",
    "description": "QA agent with project-specific testing protocols",
    "tags": ["qa", "project-specific"]
  },
  "capabilities": {
    "model": "claude-sonnet-4-20250514",
    "tools": ["custom_test_runner", "project_validator"],
    "resource_tier": "standard"
  },
  "instructions": "# Project QA Agent\n\nYou are a QA specialist for this specific project..."
}
EOF

# Check which agents are available at each tier
./claude-mpm agents list --by-tier
```

## Common Issues

1. **Import Errors**: Ensure virtual environment is activated and PYTHONPATH includes `src/`
2. **Hook Service Errors**: Check port availability (8080-8099)
3. **Version Errors**: Run `pip install -e .` to ensure proper installation

## Contributing

1. Follow the structure in `docs/STRUCTURE.md`
2. Add tests for new features
3. Run QA checks per `docs/QA.md`
4. Update documentation as needed
5. Use [Conventional Commits](https://www.conventionalcommits.org/) for automatic versioning:
   - `feat:` for new features (minor version bump)
   - `fix:` for bug fixes (patch version bump)
   - `feat!:` or `BREAKING CHANGE:` for breaking changes (major version bump)

## Deployment

See [docs/DEPLOY.md](docs/DEPLOY.md) for the complete deployment process, including:
- Version management with `./scripts/manage_version.py`
- Building and publishing to PyPI
- Creating GitHub releases
- Post-deployment verification