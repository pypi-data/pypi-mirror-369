"""Convert Markdown to HTML with syntax highlighting."""

import pathlib
import re
from typing import Union

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from markdown_html_pdf._constants import paths


def apply_syntax_highlighting(html_content: str) -> str:
    """Apply syntax highlighting to code blocks in HTML.

    Args:
        html_content: HTML content with code blocks to highlight

    Returns:
        HTML content with syntax highlighting applied
    """
    # Regex to find code blocks with specified language
    code_block_pattern = r'<pre><code class="language-(\w+)">(.*?)</code></pre>'

    def replace_code_block(match: re.Match[str]) -> str:
        lang = match.group(1)
        code = match.group(2)

        # Decode HTML entities
        code = code.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&quot;", '"')

        try:
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = HtmlFormatter(cssclass="highlight", style="github-dark", noclasses=False)
            result = highlight(code, lexer, formatter)
            return result
        except ClassNotFound:
            # If language not recognized, return original code block
            return match.group(0)

    # Apply the replacement
    html_content = re.sub(code_block_pattern, replace_code_block, html_content, flags=re.DOTALL)
    return html_content


def markdown_to_html(
    markdown_file_path: Union[str, pathlib.Path], html_output_file_path: Union[str, pathlib.Path], html_output_title: str
) -> None:
    """Convert Markdown file to HTML with syntax highlighting.

    Args:
        markdown_file_path: Path to the input Markdown file
        html_output_file_path: Path where the HTML file will be saved
        html_output_title: Title for the HTML document
    """
    # 1. Read the markdown file
    with open(markdown_file_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    # 2. Render to HTML using markdown-it
    md = MarkdownIt("gfm-like").enable(["table"])
    html_body = md.render(markdown_text)

    # 3. Apply syntax highlighting to code blocks
    html_body = apply_syntax_highlighting(html_body)

    # 4. Read the HTML template to render the markdown at github style
    with open(paths.HTML_DIR / "template.html", "r", encoding="utf-8") as f:
        html_template = f.read()

    # 5. Replace the placeholders with the actual content
    html_template = html_template.replace("||MARKDOWN_TO_BE_RENDERED_HERE||", html_body)
    html_template = html_template.replace("||TITLE_TO_BE_RENDERED_HERE||", html_output_title)

    # 6. Create output directory if it doesn't exist
    pathlib.Path(html_output_file_path).parent.mkdir(parents=True, exist_ok=True)

    # 7. Save the HTML file
    with open(html_output_file_path, "w", encoding="utf-8") as f:
        f.write(html_template)


if __name__ == "__main__":
    markdown_to_html(
        markdown_file_path=paths.MARKDOWN_DIR / "example.md",
        html_output_file_path=paths.HTML_DIR / "example.html",
        html_output_title="Example",
    )
