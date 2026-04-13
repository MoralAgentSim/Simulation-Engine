# Social Simulation with Moral Agents

An evolutionary multi-agent simulation exploring how moral behaviors emerge through cooperation. LLM-powered agents with different moral frameworks (universal, reciprocal, kin-focused, selfish) interact in a resource-gathering environment — hunting, sharing, fighting, and reproducing — to test hypotheses about why morality might be favored by natural selection.

## Visualization

Live visualization: [Morality AI Web](https://morality-ai-web.vercel.app/)

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Git

### Installation

```bash
git clone https://github.com/TINKPA/Social-Simulation-with-Moral-Agents.git
cd Social-Simulation-with-Moral-Agents

# Install dependencies
uv sync

# Set up environment variables (API keys for LLM providers)
cp .env.example .env
# Edit .env and fill in your API keys
```

### Database (optional)

For checkpoint storage in PostgreSQL:

```bash
pip install "psycopg[binary]"
```

## Running the Simulation

```bash
# Start a fresh simulation
uv run python main.py run --config_dir configZ_major_v2

# Run with real-time dashboard
uv run python main.py run --config_dir configA_z8_easyHunting_visible --dashboard

# Resume from a checkpoint
uv run python main.py resume <RUN_ID> --config.world.max_life_steps 50

# Resume from a specific time step
uv run python main.py resume <RUN_ID> --time_step 10

# List available runs
uv run python main.py list-runs

# Estimate token usage and cost
uv run python main.py estimate-cost --config_dir configZ_major_v2

# Use Claude Code CLI as the LLM provider (requires `claude` installed)
uv run python main.py run --config_dir configZ_major_v2 --config.llm.provider claude --config.llm.chat_model claude-sonnet-4-20250514

# Combine with other flags
uv run python main.py run \
  --config_dir configZ_major_v4 \
  --config.llm.provider claude \
  --config.llm.chat_model haiku \
  --config.llm.async_config.max_concurrent_calls 2 \
  --config.world.max_life_steps 1 \
  --dashboard

# Run 4 kin-focused agents only (override agent count and ratios)
uv run python main.py run \
  --config_dir configZ_major_v4 \
  --config.llm.provider claude \
  --config.llm.chat_model haiku \
  --config.llm.async_config.max_concurrent_calls 20 \
  --config.agent.initial_count 4 \
  --config.agent.ratio.kin_focused_moral 1.0 \
  --config.agent.ratio.universal_group_focused_moral 0.0 \
  --config.agent.ratio.reciprocal_group_focused_moral 0.0 \
  --config.agent.ratio.reproductive_selfish 0.0 \
  --config.world.max_life_steps 3 \
  --dashboard
```

#### Available Claude models

| Alias | Full Model ID |
|-------|---------------|
| `sonnet` | `claude-sonnet-4-6` |
| `opus` | `claude-opus-4-6` |
| `haiku` | `claude-haiku-4-5-20251001` |

Aliases resolve to the latest version automatically. Older versions (e.g. `claude-sonnet-4-20250514`) also work.

### CLI Subcommands

| Subcommand | Description |
|------------|-------------|
| `run` | Start a fresh simulation (`--config_dir` required) |
| `resume <RUN_ID>` | Resume from a checkpoint |
| `list-runs` | List available simulation runs |
| `estimate-cost` | Estimate token usage and cost (`--config_dir` required) |

### Shared Flags (for `run` and `resume`)

| Flag | Description |
|------|-------------|
| `--checkpoint_dir` | Checkpoint save location (default: `./data`) |
| `--dashboard` | Enable Rich Live real-time dashboard |
| `--log_level` | `debug`, `info`, `warning`, `error`, `critical` |
| `--debug_responses` | Save raw LLM responses on validation errors |
| `--no_db` | Disable database, file-only checkpoints |
| `--config.*` | Override any nested config field (auto-generated from Pydantic model) |

**Common config overrides:**

| Override | Description |
|----------|-------------|
| `--config.world.max_life_steps N` | Max simulation steps |
| `--config.world.communication_and_sharing_steps N` | Communication frequency |
| `--config.llm.provider` | LLM provider: `openai`, `deepseek`, `tongyuan`, `alibaba`, `openrouter`, `claude` |
| `--config.llm.chat_model` | LLM model (e.g., `gpt-4o-mini`, `claude-sonnet-4-20250514`) |
| `--config.llm.async_config.max_concurrent_calls N` | Max concurrent LLM calls (default: 10) |
| `--config.agent.initial_count N` | Number of starting agents |

## Architecture

The simulation runs an **async three-phase step loop**:

1. **Phase 1 — Parallel LLM Decisions**: All alive agents query the LLM concurrently (frozen checkpoint state). Returns pure `AgentDecisionResult` objects with no side effects.
2. **Phase 2 — Sequential Action Application**: Decisions are applied one-by-one. A stale-action guard catches `ValueError` for race conditions (e.g., two agents hunting the same prey).
3. **Phase 3 — Environment Updates**: Social and physical environment updates (plant regrowth, prey respawn).

### Agent Actions

Agents choose from 8 action types each step: `Collect`, `Allocate`, `Hunt`, `Fight`, `Rob`, `Reproduce`, `Communicate`, `DoNothing`.

### Morality Types

Agents are assigned one of 5 moral frameworks that shape their LLM prompts:
- **Universal group-focused moral** — cooperates broadly
- **Reciprocal group-focused moral** — tit-for-tat cooperation
- **Kin-focused moral** — prioritizes family/offspring
- **Reproductive selfish** — self-interested, reproduces aggressively
- **Reproduction-averse selfish** — self-interested, avoids reproduction costs

### Configuration

Each config directory under `config/` contains a `settings.json` (world params, agent ratios, resource settings, LLM config) and prompt templates. See existing configs for examples.

## Testing

```bash
# Run all tests
uv run pytest scr/tests/ -v

# Run a single test file
uv run pytest scr/tests/test_stale_action_guard.py -v

# Run a specific test
uv run pytest scr/tests/test_async_step.py::TestEventBus::test_publish_subscribe -v
```

Integration tests that require API keys will auto-skip when keys are unavailable.

## Project Structure

```
main.py                              # Entry point (async)
config/                              # Simulation configurations
scr/
  api/
    llm_api/                         # LLM client (litellm), config, providers
    db_api/                          # PostgreSQL checkpoint storage
  models/
    agent/                           # Agent, actions, responses, decision_result
    environment/                     # Physical & social environments
    simulation/                      # Checkpoint
    core/                            # Config, metadata, logs
    prompt_manager/                  # Prompt construction, messages
  simulation/
    runner/                          # simulation_step (3-phase), runner, resumer
    agent_decision/                  # Async LLM decision-making, retry
    act_manager/                     # Action dispatch + handlers
    env_manager/                     # Environment step logic
    cli/                             # CLI parsing + command execution
    event_bus.py                     # AsyncIO pub/sub
    dashboard.py                     # Rich Live dashboard
  utils/                             # Logging, checkpoint I/O, random
  tests/                             # Unit and integration tests
```
