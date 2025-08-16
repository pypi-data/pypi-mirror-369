# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Install: `pip install -e .`
- Run TUI: `jrdev` (primary interface)
- Run CLI: `jrdev-cli` 
- Development: `python3 src/jrdev/ui/textual_ui.py` (TUI) or `python3 -m jrdev.terminal` (CLI)
- Help: `jrdev --help`
- Specify model: `jrdev --model llama-3.1-405b`

### Development Commands
- Linting: `flake8 src/`
- Type checking: `mypy --strict src/`
- Format code: `black src/`
- Import sorting: `isort src/`
- Run tests: `python3 -m unittest discover tests/`
- Run specific test: `python3 -m unittest tests.test_file_utils.TestFileUtils.test_specific_method`

## Architecture Overview

JrDev is an AI-powered development assistant with a layered architecture:

### Core Components
- **Application (`core/application.py`)**: Central orchestrator managing UI, state, and component initialization
- **AppState (`core/state.py`)**: Global state management including model selection, thread management, and API clients
- **CommandHandler (`core/commands.py`)**: Command routing and execution system
- **APIClients (`core/clients.py`)**: Multi-provider LLM API abstraction layer

### User Interfaces
- **Textual TUI (`ui/textual_ui.py`)**: Primary rich terminal interface with chat, file browser, and task monitoring
- **CLI Interface (`ui/cli/cli_app.py`)**: Basic command-line interface for scripting and automation

### Code Processing Pipeline
- **CodeProcessor (`code_processor.py`)**: Multi-step AI-driven code modification workflow
- **File Operations (`file_operations/`)**: Modular file manipulation system (add, replace, insert, delete operations)
- **Message Builder (`message_builder.py`)**: Context-aware prompt construction

### Context Management
- **ContextManager (`projectcontext/contextmanager.py`)**: File indexing and analysis caching
- **MessageThread (`messages/thread.py`)**: Conversation history and thread isolation
- **Project Analysis**: Auto-generates `jrdev_overview.md` and `jrdev_conventions.md` via `/init`

### Language Support
- **Language Parsers (`languages/`)**: Programming language-specific AST parsing and code manipulation
- **Supported**: Python, TypeScript, C++, Go, Java, Kotlin with extensible base class architecture

## Features
- **Message Threads**: Create and manage multiple conversation threads with isolated context using `/thread`
  - Create: `/thread new [--name NAME]`
  - List: `/thread list`
  - Switch: `/thread switch THREAD_ID`
  - Info: `/thread info`
  - View: `/thread view [--count COUNT]`

- **AI-Powered Coding (`/code`)**: Multi-step code generation with planning, review, and validation phases
- **Project Initialization (`/init`)**: Analyzes codebase structure and generates contextual summaries
- **Git Integration**: PR summaries and code reviews via Git Tools screen

## Configuration
- Create a `.env` file in the project root with your API keys:
  ```
  VENICE_API_KEY=your_venice_api_key_here
  OPENAI_API_KEY=your_openai_api_key_here
  ANTHROPIC_API_KEY=your_anthropic_api_key_here
  DEEPSEEK_API_KEY=your_deepseek_api_key_here
  OPEN_ROUTER_KEY=your_open_router_api_key_here
  ```

## Code Style
- Python 3.7+ compatibility required
- Type hints required on all functions and variables
- Docstrings for all modules, classes, and functions
- Async/await for asynchronous operations
- Error handling: use try/except for API calls and user interactions
- Naming conventions:
  - snake_case for variables and functions
  - CamelCase for classes
- Security: store API keys in .env file (accessed via dotenv)
- Imports: group by standard library, third-party, local
- Maximum line length: 88 characters (Black default)
- String formatting: use f-strings
- Terminal output: use terminal_print with appropriate PrintType

## Key Patterns
- **Command Pattern**: All user commands inherit from Command base class in `commands/`
- **Worker Pattern**: Long-running operations use Textual workers for non-blocking UI
- **Event-Driven UI**: Textual widgets communicate via custom events in `ui/textual_events.py`
- **Provider Abstraction**: Model providers abstracted through unified client interface
- **Modular File Operations**: File changes decomposed into atomic operations with rollback support

## Testing
- Unit tests in `tests/` directory using Python's built-in unittest framework
- Test files follow `test_*.py` naming convention
- Mock data in `tests/mock/` for complex scenarios
- Tests cover file operations, language parsers, and core utilities