# Lizeur - PDF Content Extraction MCP Server

Lizeur is a Model Context Protocol (MCP) server that enables AI assistants to extract and read content from PDF documents using Mistral AI's OCR capabilities. It provides a simple interface for converting PDF files to markdown text that can be easily consumed by AI models.

## Features

- **PDF OCR Processing**: Uses Mistral AI's latest OCR model to extract text from PDF documents
- **Intelligent Caching**: Automatically caches processed documents to avoid re-processing
- **Markdown Output**: Returns clean markdown text for easy integration with AI workflows
- **FastMCP Integration**: Built with FastMCP for optimal performance and ease of use

## Prerequisites

- Python 3.10
- UV package manager
- Mistral AI API key

## Installation

### From pypi
```
pip install lizeur
```

And add the following configuration to your `mcp.json` file:

**Note:** Lizeur will be installed in the python3.10 folder. If this folder is not in your system PATH, your IDE may not be able to detect the lizeur binary.

**Solution:** You can add the full path to the lizeur binary in the command field to ensure your IDE can locate it.

```json
{
  "mcpServers": {
    "lizeur": {
      "command": "lizeur",
      "env": {
        "MISTRAL_API_KEY": "your-mistral-api-key-here",
        "CACHE_PATH": "your cache path",
      }
    }
  }
}
```

### Manual

#### 1. Clone the Repository

```bash
git clone https://github.com/SilverBzH/lizeur
cd lizeur
```

#### 2. Create and Activate Virtual Environment

```bash
# Create a virtual environment
uv venv --python 3.10

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
# .venv\Scripts\activate
```

#### 3. Install Dependencies and Build

```bash
# Install dependencies
uv sync

# Build the package
uv build
```

#### 4. Install System-Wide

```bash
# Install the package system-wide
uv pip install --system .
```

This will install the `lizeur` command globally on your system.

## Usage

Once configured, the MCP server provides two tools that can be used by AI assistants:

### Available Functions

#### `read_pdf`
- **Function**: `read_pdf`
- **Parameter**: `absolute_path` (string) - The absolute path to the PDF file
- **Returns**: Complete OCR response including all pages with markdown content, bounding boxes, and other OCR metadata

#### `read_pdf_text`
- **Function**: `read_pdf_text`
- **Parameter**: `absolute_path` (string) - The absolute path to the PDF file
- **Returns**: Markdown text content from all pages without the full OCR metadata (simpler for agents to process)

### Example Usage in AI Assistant

The AI assistant can now use the tools like this:

```
What the OP command looks like for this specific controller, here is the doc /path/to/document.pdf
```

The MCP server will:
1. Check if the document is already cached
2. If not cached, upload the PDF to Mistral AI for OCR processing **This will use your MISTRAL API key and cost money**
3. Extract the text and convert it to markdown
4. Cache the result for future use
5. Return the markdown content

**Note**: Use `read_pdf_text` when you only need the text content, or `read_pdf` when you need the complete OCR response with metadata. `read_pdf` can be confusion for some agent if the pdf file is big.

## Development

### Local Development Setup

```bash
# Install in development mode
uv pip install -e .

# Run the server directly
python main.py
```

### Project Structure

- `main.py` - Main server implementation with FastMCP integration
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions

## Dependencies

- `mcp[cli]>=1.12.4` - Model Context Protocol implementation
- `mistralai>=0.0.10` - Mistral AI Python client

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please refer to the project repository or contact the maintainers.
