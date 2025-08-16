# Asta Summarizer Service

A flexible text summarization service that supports multiple AI providers including OpenAI-compatible APIs and HuggingFace Inference endpoints
with a consistent tone used for Asta.

## Features

- **Multiple Provider Support**: Works with both OpenAI-compatible APIs and HuggingFace Inference clients
- **Flexible Summarization Types**: Support for different summarization styles (default, thread titles, etc.)
- **Customizable Length**: Configure summary length to meet your needs

## Installation

```bash
pip install asta-summarizer
```

## Quick Start

### Using with OpenAI-compatible API

```python
import asyncio
from asta_summarizer import SummarizerService, SummarizationType

async def main():
    # Initialize with base_url for OpenAI-compatible API
    service = SummarizerService(
        base_url="https://your-api-endpoint.com/v1",
        model="your-model-name",
        api_key="your-api-key"  # or set SUMMARIZER_API_KEY environment variable
    )

    text = "Your long text to summarize..."

    summary = await service.summarize(
        text=text,
        length=100,
        summarization_type=SummarizationType.DEFAULT
    )

    print(summary)

if __name__ == "__main__":
    asyncio.run(main())
```

### Using with HuggingFace Provider

```python
import asyncio
from asta_summarizer import SummarizerService, SummarizationType

async def main():
    # Initialize with provider for HuggingFace Inference
    service = SummarizerService(
        provider="huggingface",  # or other supported providers
        model="your-model-name",
        api_key="your-hf-token"  # or set SUMMARIZER_API_KEY environment variable
    )

    text = "Your long text to summarize..."

    summary = await service.summarize(
        text=text,
        length=200,
        summarization_type=SummarizationType.THREAD_TITLE
    )

    print(summary)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Initialization Parameters

- **model** (required): The model name to use for summarization
- **base_url** (optional): Base URL for OpenAI-compatible APIs (mutually exclusive with provider)
- **provider** (optional): Provider name for HuggingFace Inference (mutually exclusive with base_url)
- **api_key** (optional): API key for authentication (defaults to `SUMMARIZER_API_KEY` environment variable)

### Summarization Types

The service supports different summarization styles via the `SummarizationType` enum:

- `SummarizationType.DEFAULT`: Standard summarization. Pass in your own prompt alongside the text to summarize in the `text` field.
- `SummarizationType.THREAD_TITLE`: Optimized for creating thread titles

### Environment Variables

Set your API key as an environment variable:

```bash
export SUMMARIZER_API_KEY="your-api-key-here"
```

## Development

### Installing Dependencies

For development work:

```bash
# Install package in editable mode with development dependencies
pip install -e ".[dev]"
```

Or install dependencies manually:

```bash
# Core dependencies
pip install huggingface-hub>=0.20.0 openai>=1.0.0

# Development dependencies
pip install pytest>=7.0.0 pytest-asyncio>=0.21.0 black>=23.0.0 isort>=5.12.0 mypy>=1.0.0
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy asta_summarizer/
```

## Publication

You can publish a new version from your branch before merging to main, or from main after merging.

Edit the `version.txt` file with the new version, then run

```
export AI2_NORA_PYPI_TOKEN=<SECRET IN NORA VAULT>
make publish
```

This will publish the summarizer with the version number contained in `version.txt`

## License

MIT License - see [LICENSE](LICENSE) file for details.
