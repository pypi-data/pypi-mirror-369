# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

**CRITICAL: ALL Python commands MUST use `uv`**

### Core Development Workflow

```bash
# Install dependencies
uv sync --all-extras

# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/           # Unit tests
uv run pytest tests/rfc_compliance/ # RFC compliance tests
uv run pytest tests/integration/    # Integration tests

# Run single test file
uv run pytest tests/unit/email/imap/test_imap_client.py -v

# Type checking (required before commits)
uv run mypy src/

# Linting (required before commits)
uv run ruff check src/

# Format code
uv run ruff format src/

# Run examples
uv run python examples/websocket_realtime.py
uv run python examples/imap_demo.py
```

### RFC Compliance Testing

```bash
# Run RFC compliance tests for specific protocols
uv run pytest tests/rfc_compliance/websocket/ -v
uv run pytest tests/rfc_compliance/imap/ -v

# WebSocket Autobahn compliance testing
uv run python tests/websocket/compliance/autobahn_runner.py
```

## Architecture Overview

### Core Design Principles

1. **AnyIO-Only I/O**: ABSOLUTELY NO `asyncio` imports. All I/O uses AnyIO exclusively
2. **RFC Compliance First**: Every protocol implementation must pass comprehensive RFC test suites
3. **Complete Implementations**: No partial implementations - each protocol fully implements its RFC specification
4. **Structured Concurrency**: Uses AnyIO task groups and cancellation scopes throughout
5. **Type Safety**: Full mypy compliance with strict typing

### Package Architecture

```dir
src/anyrfc/
├── core/           # Shared infrastructure
│   ├── types.py    # Base classes: ProtocolClient, RFCCompliance, AuthenticationClient
│   ├── streams.py  # AnyIO stream helpers
│   ├── tls.py      # TLS configuration helpers
│   └── ...
├── websocket/      # RFC 6455 WebSocket (Phase 1 - COMPLETE)
├── email/          # Email protocols (Phase 2 - COMPLETE)
│   ├── imap/       # RFC 9051 IMAP4rev2 implementation
│   └── smtp/       # RFC 5321 SMTP implementation
├── auth/           # Authentication protocols (Phase 3)
│   ├── oauth2/     # RFC 6749/6750 OAuth 2.0
│   └── sasl/       # RFC 4422 SASL
└── ...
```

### Implementation Status

- **Phase 1 (WebSocket)**: ✅ COMPLETE - RFC 6455 compliant WebSocket client
- **Phase 2 (Email)**: ✅ COMPLETE - RFC 9051 IMAP client with extensions, SMTP foundation
- **Phase 3 (OAuth)**: 🚧 IN PROGRESS - OAuth 2.0 client framework
- **Phase 4+ (SSH/SFTP/etc)**: 📋 PLANNED

### Key Interfaces

All protocol clients inherit from `ProtocolClient[T]` and implement:

- `async def connect()` - Establish RFC-compliant connection
- `async def disconnect()` - Graceful RFC-compliant shutdown
- `async def send(message: T)` - Send message following RFC encoding
- `async def receive() -> AsyncIterator[T]` - Receive messages following RFC parsing
- `async def validate_compliance() -> Dict[str, bool]` - Run RFC compliance tests

## Critical Constraints

### AnyIO-Only I/O Policy

- **FORBIDDEN**: `import asyncio`, `asyncio.connect()`, `asyncio.create_task()`, etc.
- **REQUIRED**: `anyio.connect_tcp()`, `anyio.create_task_group()`, `anyio.Event()`, etc.
- **Exception**: Standard library compute operations (math, string processing, crypto) are allowed

### RFC Compliance Requirements

- Every protocol must achieve 100% compliance with its RFC specification
- Comprehensive test suites validate compliance using RFC test vectors
- Real-world interoperability testing against major server implementations
- Compliance testing framework in `tests/rfc_compliance/`

### Dependency Policy

- **Pre-approved**: `anyio`, `httpx`, `typing-extensions`
- **Development only**: `pytest`, `mypy`, `ruff`, testing utilities
- **Requires approval**: Any other third-party dependency must be explicitly justified

## Protocol-Specific Details

### WebSocket (RFC 6455) - COMPLETE

- **Location**: `src/anyrfc/websocket/`
- **Status**: Production ready, passes Autobahn test suite
- **Key files**: `client.py`, `frames.py`, `handshake.py`, `state_machine.py`
- **Extensions**: Per-message deflate support
- **Testing**: Real-server compatibility with major WebSocket services

### IMAP (RFC 9051) - COMPLETE

- **Location**: `src/anyrfc/email/imap/`
- **Status**: Complete implementation with extensions
- **Key files**: `client.py`, `commands.py`, `responses.py`, `extensions.py`, `mailbox.py`, `messages.py`
- **Extensions**: IDLE, SORT, THREAD, CONDSTORE, QRESYNC
- **Features**: Complete mailbox management, message handling, compliance testing

### Protocol State Management

All clients use structured state machines:

```python
class ProtocolState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    DISCONNECTING = "disconnecting"
    ERROR = "error"
```

### Structured Concurrency Pattern

```python
async def protocol_operation():
    async with anyio.create_task_group() as tg:
        tg.start_soon(connection_manager)
        tg.start_soon(message_processor)
        tg.start_soon(heartbeat_manager)
```

## Testing Strategy

### Test Organization

- **Unit tests**: `tests/unit/` - Test individual components
- **RFC compliance**: `tests/rfc_compliance/` - Validate RFC specifications
- **Integration**: `tests/integration/` - End-to-end protocol testing
- **Interop**: Real-server compatibility testing

### RFC Compliance Framework

Each protocol includes a compliance testing class:

```python
class RFC6455Compliance(RFCCompliance):
    async def validate_compliance(self) -> Dict[str, bool]:
        # Run comprehensive RFC test suite
        pass
```

### WebSocket Autobahn Testing

The WebSocket implementation passes the comprehensive Autobahn test suite:

```bash
uv run python tests/websocket/compliance/autobahn_runner.py
```

## Common Patterns

### Client Initialization

```python
# Always use context managers for resource management
async with IMAPClient("imap.gmail.com", use_tls=True) as client:
    await client.authenticate({"username": "user", "password": "pass"})
    # Client automatically disconnects on exit
```

### Extension Management

```python
# Check server capabilities
if client.has_capability("IDLE"):
    idle_ext = client.extensions.get_extension("IDLE")
    await idle_ext.start_idle(callback=handle_updates)
```

### Error Handling

All clients use proper AnyIO cancellation and structured exception handling:

```python
try:
    async with anyio.move_on_after(30):  # Timeout handling
        await client.connect()
except ConnectionError:
    # Handle connection failures
    pass
```

## Current Implementation Phase

The codebase is currently completing **Phase 2 (Email Infrastructure)**:

- ✅ IMAP client (RFC 9051) - Complete with extensions
- 🚧 SMTP client refinements
- 📋 Next: Phase 3 OAuth 2.0 implementation

When working on this codebase, always:

1. Use `uv run` for all Python commands
2. Ensure AnyIO-only I/O operations
3. Validate RFC compliance
4. Test against real servers when possible
5. Maintain type safety with mypy
