# Nimble LLM Caller

A robust, multi-model LLM calling package with advanced prompt management, retry logic, and document assembly capabilities.

## Features

- **Multi-Model Support**: Call multiple LLM providers (OpenAI, Anthropic, Google, etc.) through LiteLLM
- **Batch Processing**: Submit multiple prompts to multiple models efficiently
- **Robust JSON Parsing**: Multiple fallback strategies for parsing LLM responses
- **Retry Logic**: Exponential backoff with jitter for handling rate limits and transient errors
- **Prompt Management**: JSON-based prompt templates with variable substitution
- **Document Assembly**: Built-in formatters for text, markdown, and LaTeX output
- **Reprompting Support**: Use results from previous calls as context for new prompts
- **Secret Management**: Secure handling of API keys via environment variables
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Installation

### From PyPI (when published)
```bash
pip install nimble-llm-caller
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/fredzannarbor/nimble-llm-caller.git
cd nimble-llm-caller

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Run setup script
python setup_dev.py setup
```

### Verify Installation
```bash
# Run the test CLI
python examples/cli_test.py

# Run specific tests
python examples/cli_test.py --test install
```

## Quick Start

### 1. Set up API Keys
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
```

### 2. Basic Usage
```python
from nimble_llm_caller import LLMContentGenerator

# Initialize with your prompts file
generator = LLMContentGenerator("examples/sample_prompts.json")

# Simple single prompt call
result = generator.call_single(
    prompt_key="summarize_text",
    model="gpt-4o",
    substitutions={"text": "Your text here"}
)

print(f"Result: {result.content}")
```

### 3. Batch Processing
```python
# Batch processing multiple prompts
results = generator.call_batch(
    prompt_keys=["summarize_text", "extract_keywords", "generate_title"],
    models=["gpt-4o", "claude-3-sonnet"],
    shared_substitutions={"content": "Your content here"}
)

print(f"Success rate: {results.success_rate:.1f}%")
```

### 4. Document Assembly
```python
# Assemble results into a document
document = generator.assemble_document(
    results, 
    format="markdown",
    output_filename="report.md"
)

print(f"Document created: {document.word_count} words")
```

## Configuration

Set your API keys in environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
```

## Prompt Format

Prompts are stored in JSON files with this structure:

```json
{
  "prompt_keys": ["summarize_text", "extract_keywords"],
  "summarize_text": {
    "messages": [
      {
        "role": "system",
        "content": "You are a professional summarizer."
      },
      {
        "role": "user", 
        "content": "Summarize this text: {text}"
      }
    ],
    "params": {
      "temperature": 0.3,
      "max_tokens": 1000
    }
  }
}
```

## Advanced Usage

See the [documentation](docs/) for advanced features including:
- Custom retry strategies
- Document templates
- Reprompting workflows
- Error handling
- Performance optimization