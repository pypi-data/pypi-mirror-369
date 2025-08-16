"""Convert HTML to PDF using Playwright."""

import asyncio
import pathlib
from typing import Union

from playwright.async_api import async_playwright

from markdown_html_pdf._constants import paths


async def html_to_pdf(
    html_file_path: Union[str, pathlib.Path],
    pdf_output_file_path: Union[str, pathlib.Path],
) -> None:
    """Convert HTML file to PDF using Playwright.

    Args:
        html_file_path: Path to the input HTML file
        pdf_output_file_path: Path where the PDF file will be saved
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            # Removed font rendering args that interfere with text fidelity
            # Only keeping essential args for stability
            args=["--disable-gpu-sandbox"]
        )

        # Configure context with better settings for font rendering
        context = await browser.new_context(
            # Set device scale factor for better text rendering
            device_scale_factor=1.0,
            # Ensure consistent viewport
            viewport={"width": 1200, "height": 800},
        )

        page = await context.new_page()

        # Create pdf parent folder if not exists
        pathlib.Path(pdf_output_file_path).parent.mkdir(parents=True, exist_ok=True)

        # Load the HTML file
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Load HTML and wait for assets (fonts, emojis, graphics) to load
        await page.set_content(html_content, wait_until="networkidle")

        # Inject CSS to optimize text rendering
        await page.add_style_tag(
            content="""
            * {
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                text-rendering: optimizeLegibility;
            }
            
            /* Page break control */
            .no-break, .keep-together {
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }
            
            /* Prevent orphans and widows */
            p, div, section {
                orphans: 3;
                widows: 3;
            }
            
            /* Keep headings with following content */
            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid !important;
                break-after: avoid !important;
            }
            
            /* Avoid breaking tables, figures, code blocks */
            table, figure, pre, blockquote {
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }
        """
        )

        # Ensure screen CSS (not print) is applied for better font rendering
        await page.emulate_media(media="screen")

        # Wait for fonts to fully load, especially emoji fonts
        await page.wait_for_timeout(200)  # Increased timeout for better font loading

        # Ensure fonts are loaded by evaluating document fonts
        await page.evaluate("document.fonts.ready")

        # Force layout recalculation to ensure proper font rendering
        await page.evaluate("() => { document.body.offsetHeight; }")

        # Additional wait to ensure all fonts are properly rendered
        await page.wait_for_timeout(100)

        # Generate PDF with optimized settings for font fidelity
        await page.pdf(
            path=pdf_output_file_path,
            format="A4",
            scale=0.88,  # Maintaining scale for proportions
            print_background=True,  # Keep for colored graphics and emojis
            prefer_css_page_size=True,
            # Adding margin settings for better layout
            margin={"top": "0.25in", "bottom": "0.25in", "left": "0.25in", "right": "0.25in"},
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(
        html_to_pdf(
            html_file_path=paths.HTML_DIR / "example.html",
            pdf_output_file_path=paths.PDF_DIR / "example.pdf",
        )
    )
