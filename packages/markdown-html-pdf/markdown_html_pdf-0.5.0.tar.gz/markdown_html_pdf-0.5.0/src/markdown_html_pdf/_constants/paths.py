import pathlib

# Points to the package directory (src/markdown_html_pdf/)
PACKAGE_DIR = pathlib.Path(__file__).parent.parent

# Resource directories within the package
DOCS_DIR = PACKAGE_DIR / "_docs"
HTML_DIR = DOCS_DIR / "html"
MARKDOWN_DIR = DOCS_DIR / "markdown"
PDF_DIR = DOCS_DIR / "pdf"
FONTS_DIR = PACKAGE_DIR / "_fonts"

# For backward compatibility during development
BASE_DIR = pathlib.Path(__file__).parent.parent.parent.parent
