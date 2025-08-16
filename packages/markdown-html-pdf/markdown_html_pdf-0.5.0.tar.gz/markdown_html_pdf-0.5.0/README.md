# markdown-html-pdf

A powerful Python package to convert Markdown files to PDF with syntax highlighting and emoji support.

## Features

- ✨ Convert Markdown to PDF with beautiful formatting
- 🎨 Syntax highlighting for code blocks
- 😀 Full emoji support
- 🔧 GitHub-flavored Markdown support
- 📱 Responsive design optimized for print
- 🚀 Fast conversion using Playwright
- 💻 Command-line interface
- 🐍 Python API

## Installation

```bash
uv add markdown-html-pdf
```

After installation, you need to install Playwright browsers:

```bash
sudo $(which uv) run playwright install
```

### Linux Emoji Font Setup

For proper emoji rendering in PDFs on Linux systems, you need to install the Segoe UI Emoji font. This is required for emojis to display correctly in the generated PDFs.

```bash
sudo $(which uv) run install-emoji-fonts
```

**Note:** This step is only required on Linux systems and needs to be run once per system.

## Usage

### Command Line

```bash
# Basic conversion
uv run markdown-html-pdf input.md output.pdf
```

You can also use the shorter alias:

```bash
uv run md2pdf input.md output.pdf
```

### Available Commands

- `markdown-html-pdf` or `md2pdf`: Convert Markdown to PDF
- `install-emoji-fonts`: Install emoji fonts for Linux systems (requires sudo)

### Python API

```python
import asyncio
from markdown_html_pdf.tools import markdown_to_pdf

async def convert():
    await markdown_to_pdf(
        markdown_file_path="input.md",
        pdf_output_file_path="output.pdf"
    )

asyncio.run(convert())
```

## Requirements

- Python 3.9+
- Playwright (automatically installed)

## How it works

1. **Markdown to HTML**: Converts Markdown to HTML using `markdown-it-py` with GitHub-flavored Markdown support
2. **Syntax Highlighting**: Applies syntax highlighting to code blocks using Pygments
3. **HTML to PDF**: Uses Playwright to render HTML to PDF with optimized settings for text fidelity

## Supported Markdown Features

- Headers (H1-H6)
- **Bold** and _italic_ text
- `Inline code` and code blocks with syntax highlighting
- Links and images
- Tables
- Lists (ordered and unordered)
- Blockquotes
- Horizontal rules
- Emojis 😎

## Troubleshooting

### Emoji Rendering Issues on Linux

If emojis are not displaying correctly in your PDFs on Linux systems:

1. **Install emoji fonts**:

   - `sudo $(which uv) run install-emoji-fonts` (uses full path)

2. **Verify installation**: Check if fonts are installed with `fc-list | grep -i emoji`
3. **Restart applications**: Restart your terminal and any running applications
4. **Check permissions**: Ensure the font files have proper permissions (644)

### Browser Installation Issues

If you encounter issues with Playwright browsers:

1. **Manual installation**: Run `uv run playwright install`
2. **System dependencies**: Install system dependencies with `uv run playwright install-deps`
3. **Permissions**: Ensure you have proper permissions to install browsers

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
