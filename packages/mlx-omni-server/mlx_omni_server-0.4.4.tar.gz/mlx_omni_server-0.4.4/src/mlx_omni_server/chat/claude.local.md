# CLAUDE.md - Chat Module Architecture

This file provides guidance to Claude Code (claude.ai/code) when working with the chat module in MLX Omni Server.

## Chat Module Overview

The chat module provides conversational AI capabilities through two API-compatible interfaces (OpenAI and Anthropic) backed by Apple's MLX framework. It handles text generation, function calling, structured output, and reasoning capabilities.

## Architecture Components

### Core Layer (`mlx/`)

The MLX layer provides the foundational text generation capabilities:

- **`chat_generator.py`**: Core abstraction over mlx-lm with unified interface
  - Provides `generate()` and `generate_stream()` methods
  - Handles sampling parameters, logprobs, and tools integration
  - Factory method `ChatGenerator.create()` for simplified instantiation

- **`wrapper_cache.py`**: Centralized caching system for model instances
  - `WrapperCacheKey` uses (model_id, adapter_path, draft_model_id) for cache keys
  - `MLXWrapperCache` provides thread-safe LRU cache with TTL support
  - Global `wrapper_cache` instance shared across all API endpoints
  - Default: max 3 models, 5-minute TTL

- **`model_types.py`**: MLX model abstractions and loading utilities
- **`core_types.py`**: Type definitions for generation results and tool calls
- **`prompt_cache.py`**: KV-cache management for conversation context

### API Adapters

#### OpenAI Adapter (`openai/`)
- **`router.py`**: FastAPI endpoints for `/v1/chat/completions`
  - Supports both streaming and non-streaming responses
  - Uses `_create_text_model()` helper to get cached wrapper instance
- **`openai_adapter.py`**: Converts OpenAI requests to MLX generation calls
  - Handles request parameter mapping and response formatting
  - Manages chat message history and system prompts

#### Anthropic Adapter (`anthropic/`)
- **`router.py`**: FastAPI endpoints for `/anthropic/messages`
- **`anthropic_messages_adapter.py`**: Converts Anthropic Messages API to MLX calls
  - Handles system prompts, thinking blocks, and tool use formatting
  - Manages Anthropic-specific response structures

### Tool Parsing System (`mlx/tools/`)

Model-specific parsers handle function calling across different chat templates:

- **`base_tools.py`**: Abstract base class `BaseToolParser`
  - `extract_tools()` function for generic tool extraction
  - Common patterns for tool call parsing and validation

- **`llama3.py`**: `Llama3ToolParser` for Llama models
  - Uses `<|python_tag|>` markers for tool calls
  - Parses JSON-formatted function calls

- **`mistral.py`**: `MistralToolsParser` for Mistral models  
  - Uses `[TOOL_CALLS]` prefix with JSON array format
  - Handles both single and multiple tool calls

- **`qwen3_moe_tools_parser.py`**: `Qwen3MoeToolParser` for Qwen models
  - Uses XML-like `<tool_call>` tags with regex parsing
  - Handles malformed tool call formats gracefully

- **`hugging_face.py`**: Generic HuggingFace chat template handler
- **`chat_template.py`**: Chat template utilities and parsing logic

### Model Management (`openai/models/`)

- **`models_service.py`**: Contains `ModelCacheScanner` for model discovery
  - Scans HuggingFace cache for MLX-compatible models
  - Uses `MODEL_REMAPPING` for architecture compatibility (mistral → llama)
  - Provides model listing, deletion, and compatibility checking


## Key Data Flow

### Simplified Request Flow

```
Client Request
    ↓
FastAPI Router (openai/ or anthropic/)
    ↓
Cache Check (wrapper_cache.get_wrapper)
    ↓ (cache miss)
Model Loading (ChatGenerator.create) 
    ↓ (cache hit)
API Adapter (OpenAIAdapter/AnthropicMessagesAdapter)
    ↓
MLX Generation (generate/generate_stream)
    ↓
Response Formatting
    ↓
Client Response
```

### Core Components Interaction

- **Router Layer**: Handles HTTP requests and response formatting
- **Cache Layer**: Manages model instances with LRU + TTL eviction
- **Adapter Layer**: Converts API formats to/from MLX interface
- **Generation Layer**: MLX-LM text generation with tool support
- **Tool Parsing**: Model-specific parsers for function calling

### Performance Characteristics

- **Cold Start**: 10-30 seconds for model loading (first request)
- **Warm Cache**: ~100ms response time (subsequent requests)  
- **Memory Usage**: ~3 models cached simultaneously (configurable)
- **Cache TTL**: 5 minutes idle time before eviction

## Development Commands

```bash
# Run chat-specific tests
uv run pytest tests/chat/ -v

# Run MLX core tests
uv run pytest tests/chat/mlx/ -v

# Run tool parsing tests
uv run pytest tests/chat/mlx/tools/ -v

# Test specific chat completions
uv run pytest tests/chat/openai/test_chat_completions.py -v

# Test Anthropic messages
uv run pytest tests/chat/anthropic/ -v

# Run with logs for debugging model loading
uv run pytest tests/chat/ -s --log-cli-level=INFO
```

## Important Implementation Notes

### Model Loading and Caching
- Models are loaded on-demand when first requested
- Cache sharing enables the same model to serve both OpenAI and Anthropic APIs
- Cache eviction uses LRU + TTL to manage memory automatically
- Model loading can be slow (10-30 seconds) on first request

### Tool Calling Considerations
- Each model family uses different tool call formats (JSON, XML, custom tags)
- Tool parsers handle malformed outputs gracefully with fallback strategies
- Tool calling requires model-specific chat templates for proper formatting

### API Compatibility
- OpenAI compatibility covers chat completions, streaming, tools, structured output
- Anthropic compatibility includes Messages API, thinking blocks, system prompts
- Both APIs share the same underlying MLX generation layer via adapters

### Error Handling
- Model loading errors are logged and propagated to API responses
- Tool parsing errors fall back to text-only responses
- Cache eviction handles memory pressure gracefully

## Key Files for Chat Development

- **Entry Points**: `openai/router.py`, `anthropic/router.py`
- **Core Generation**: `mlx/chat_generator.py`
- **Caching**: `mlx/wrapper_cache.py` 
- **Tool Support**: `mlx/tools/` directory
- **Model Discovery**: `openai/models/models_service.py`
- **Type Definitions**: `mlx/core_types.py`, schema files

## Testing Architecture

Tests are organized by component:
- `tests/chat/openai/` - OpenAI API compatibility tests
- `tests/chat/anthropic/` - Anthropic Messages API tests  
- `tests/chat/mlx/` - Core MLX wrapper and caching tests
- `tests/chat/mlx/tools/` - Tool parsing and function calling tests