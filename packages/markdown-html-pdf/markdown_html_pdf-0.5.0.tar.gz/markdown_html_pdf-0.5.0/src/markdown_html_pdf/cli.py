"""Command-line interface for markdown-html-pdf."""

import asyncio
import pathlib
import sys
from typing import Optional

import click
from playwright.async_api import async_playwright

from markdown_html_pdf.tools import markdown_to_pdf


async def install_browsers():
    """Install Playwright browsers."""
    async with async_playwright() as p:
        await p.chromium.launch()


def install_emoji_fonts_linux():
    """Install emoji fonts for Linux systems."""
    try:
        from markdown_html_pdf.scripts.install_emoji_font import EmojiFont

        installer = EmojiFont()
        return installer.install()
    except ImportError as e:
        click.echo(f"Error importing emoji font installer: {e}", err=True)
        return False
    except Exception as e:
        click.echo(f"Error during emoji font installation: {e}", err=True)
        return False


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=pathlib.Path))
@click.argument("output_file", type=click.Path(path_type=pathlib.Path))
@click.option("--title", "-t", default=None, help="Title for the PDF document")
@click.option("--install-browsers", is_flag=True, help="Install Playwright browsers before conversion")
@click.option("--install-emoji-fonts", is_flag=True, help="Install emoji fonts for Linux systems (requires sudo)")
def main(
    input_file: pathlib.Path,
    output_file: pathlib.Path,
    title: Optional[str],
    install_browsers: bool,
    install_emoji_fonts: bool,
) -> None:
    """Convert Markdown files to PDF with syntax highlighting and emoji support.

    INPUT_FILE: Path to the input Markdown file
    OUTPUT_FILE: Path where the PDF file will be saved
    """
    # Use filename as title if not provided
    if title is None:
        title = input_file.stem

    async def run_conversion():
        try:
            if install_emoji_fonts:
                click.echo("Installing emoji fonts for Linux...")
                try:
                    success = install_emoji_fonts_linux()
                    if success:
                        click.echo("✓ Emoji fonts installed successfully")
                    else:
                        click.echo("⚠ Emoji font installation failed")
                        click.echo("Continuing with conversion...")
                except Exception as e:
                    click.echo(f"⚠ Emoji font installation failed: {e}")
                    click.echo("Continuing with conversion...")

            if install_browsers:
                click.echo("Installing Playwright browsers...")
                try:
                    await install_browsers()
                    click.echo("✓ Browsers installed successfully")
                except Exception as e:
                    click.echo(f"⚠ Browser installation failed: {e}")
                    click.echo("Continuing with conversion...")

            click.echo(f"Converting {input_file} to {output_file}...")
            await markdown_to_pdf(
                markdown_file_path=input_file,
                pdf_output_file_path=output_file,
            )
            click.echo(f"✓ Successfully converted to {output_file}")

        except Exception as e:
            click.echo(f"✗ Conversion failed: {e}", err=True)
            sys.exit(1)

    # Run the async function
    asyncio.run(run_conversion())


@click.command()
def install_fonts():
    """Install emoji fonts for Linux systems (requires sudo privileges)."""
    click.echo("Installing emoji fonts for Linux systems...")

    try:
        success = install_emoji_fonts_linux()
        if success:
            click.echo("✓ Emoji fonts installed successfully")
            sys.exit(0)
        else:
            click.echo("✗ Emoji font installation failed")
            sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Emoji font installation failed: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
