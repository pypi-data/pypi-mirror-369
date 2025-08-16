# QwQ Tag

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Python library for parsing XML/HTML content into structured, type-safe objects using Pydantic models. **qwq-tag** provides a simple and intuitive way to work with XML/HTML data while maintaining strong type safety and validation.

## Features

- 🚀 **Simple API**: Parse XML/HTML strings with a single method call
- 🔒 **Type Safety**: Built on Pydantic for robust data validation and type hints
- 🌐 **Flexible Parsing**: Handles malformed XML/HTML with recovery parsing
- 📦 **Lightweight**: Minimal dependencies (only `lxml` and `pydantic`)
- 🎯 **Mixed Content Support**: Properly handles text and nested elements
- 🔄 **Multiple Root Elements**: Can parse fragments with multiple top-level elements
- 🧹 **Clean Output**: Automatically handles whitespace normalization

## Installation

### Using pip

```bash
pip install qwq-tag
```

### Using PDM

```bash
pdm add qwq-tag
```

### Requirements

- Python 3.10+
- lxml >= 6.0.0
- pydantic >= 2.11.7

## Quick Start

```python
from qwq_tag import QwqTag

# Parse simple XML
html = '<div class="container">Hello World</div>'
tags = QwqTag.from_str(html)

# Access the parsed content
tag = tags[0]
print(tag.name)           # "div"
print(tag.content)        # ["Hello World"]
print(tag.attr)           # {"class": "container"}
print(tag.content_text)   # "Hello World"
```

## Usage Examples

### Basic XML Parsing

```python
from qwq_tag import QwqTag

# Simple element with attributes
xml = '<p class="text" id="intro">Hello World</p>'
result = QwqTag.from_str(xml)

tag = result[0]
print(f"Tag: {tag.name}")                    # Tag: p
print(f"Content: {tag.content}")             # Content: ['Hello World']
print(f"Class: {tag.attr['class']}")         # Class: text
print(f"ID: {tag.attr['id']}")               # ID: intro
```

### Nested Elements

```python
# Nested structure
xml = """
<div class="container">
    <h1>Title</h1>
    <p>Paragraph content</p>
</div>
"""

result = QwqTag.from_str(xml)
div_tag = result[0]

print(f"Container has {len(div_tag.content)} children")
for child in div_tag.content:
    if isinstance(child, QwqTag):
        print(f"- {child.name}: {child.content_text}")
```

### Mixed Content (Text + Elements)

```python
# Mixed content with text and nested elements
xml = '<p>Before <strong>bold text</strong> and <em>italic</em> after</p>'
result = QwqTag.from_str(xml)

p_tag = result[0]
print("Content breakdown:")
for item in p_tag.content:
    if isinstance(item, str):
        print(f"  Text: '{item}'")
    else:
        print(f"  Element: <{item.name}>{item.content_text}</{item.name}>")

# Output:
# Text: 'Before'
# Element: <strong>bold text</strong>
# Text: 'and'
# Element: <em>italic</em>
# Text: 'after'
```

### Multiple Root Elements

```python
# Fragment with multiple root elements
xml = '<h1>Title</h1><p>First paragraph</p><p>Second paragraph</p>'
result = QwqTag.from_str(xml)

print(f"Found {len(result)} root elements:")
for tag in result:
    print(f"- {tag.name}: {tag.content_text}")

# Output:
# Found 3 root elements:
# - h1: Title
# - p: First paragraph
# - p: Second paragraph
```

### Error Recovery

```python
# Malformed XML/HTML
malformed = '<div><p>Unclosed paragraph<span>Text</div>'
try:
    result = QwqTag.from_str(malformed)
    print("Successfully parsed malformed XML!")
    print(str(result[0]))
except Exception as e:
    print(f"Parsing failed: {e}")
```

### Converting Back to String

```python
# Create a tag programmatically
tag = QwqTag(
    name="article",
    content=["Article content"],
    attr={"class": "post", "id": "123"}
)

print(str(tag))
# Output: <article class="post" id="123">Article content</article>
```
## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yanli/qwq-tag.git
cd qwq-tag

# Install PDM if you haven't already
pip install pdm

# Install dependencies
pdm install

# Install development dependencies
pdm install -G dev
```

### Running Tests

```bash
# Run all tests
pdm run test

# Run with coverage
pdm run pytest --cov=qwq_tag tests/

# Run specific test file
pdm run pytest tests/test_qwq_tag.py
```

### Code Quality

```bash
# Format code
pdm run fix

# Check code quality
pdm run check
```

### Available Scripts

- `pdm run test` - Run the test suite
- `pdm run fix` - Auto-fix code formatting and linting issues
- `pdm run check` - Check code formatting and linting without making changes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pdm run test`)
6. Check code quality (`pdm run check`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request
