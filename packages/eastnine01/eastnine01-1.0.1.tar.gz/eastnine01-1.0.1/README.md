# eastnine01

A sample MCP (Model Context Protocol) server that provides an echo tool.

## Features

- **Echo Tool**: Returns the input message with additional text

## Installation

```bash
pip install eastnine01
```

## Usage

Run the MCP server:

```bash
eastnine01
```

Or run as a module:

```bash
python -m eastnine01
```

## Tools

### echo

Returns the input message with additional Korean text.

**Parameters:**
- `message` (str): The message to echo

**Returns:**
- str: The input message with " 라는 메시지가 입력 되었습니다" appended

## Requirements

- Python >= 3.13
- mcp[cli] >= 1.12.4

## License

MIT