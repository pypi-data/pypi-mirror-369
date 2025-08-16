import os
import pathlib
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

import fitz

from markdown_html_pdf._constants import paths
from markdown_html_pdf._llms.fallback_llm import call_llm_with_fallback_robust


def extract_page_links(page: fitz.Page) -> List[Dict[str, Any]]:
    """
    Extract all links from a PDF page.

    Args:
        page: PyMuPDF page object

    Returns:
        List of dictionaries containing link information
    """
    links = []
    link_list = page.get_links()

    for link in link_list:
        link_info = {
            "type": "internal" if link.get("page") is not None else "external",
            "rect": link.get("from", {}),
            "uri": link.get("uri", ""),
            "page": link.get("page"),
            "text": "",  # Will be filled by extracting text from rect
        }

        # Extract text from link rectangle if available
        if link_info["rect"]:
            try:
                rect = fitz.Rect(link_info["rect"])

                # Try multiple methods to extract text from the link area
                # Method 1: Get text directly from the rectangle
                link_text = page.get_textbox(rect).strip()

                # Method 2: If text is empty or too short, expand the rectangle slightly
                if not link_text or len(link_text) < 3:
                    expanded_rect = fitz.Rect(rect.x0 - 2, rect.y0 - 2, rect.x1 + 2, rect.y1 + 2)
                    link_text = page.get_textbox(expanded_rect).strip()

                # Method 3: If still problematic, get text blocks and find overlapping ones
                if not link_text or len(link_text) < 3:
                    text_blocks = page.get_text("blocks")
                    for block in text_blocks:
                        if len(block) >= 5:  # Ensure block has enough elements
                            block_rect = fitz.Rect(block[0], block[1], block[2], block[3])
                            block_text = block[4].strip()

                            # Check if the block overlaps with the link rectangle
                            if rect.intersects(block_rect) and block_text:
                                # Clean up the text - remove excessive whitespace and newlines
                                cleaned_text = " ".join(block_text.split())
                                if len(cleaned_text) > len(link_text):
                                    link_text = cleaned_text

                # Clean up the final text
                if link_text:
                    # Remove excessive whitespace and newlines
                    link_text = " ".join(link_text.split())
                    # Limit length to avoid very long link texts
                    if len(link_text) > 100:
                        link_text = link_text[:97] + "..."
                    link_info["text"] = link_text
                else:
                    # Fallback: generate a generic link text
                    if link_info["uri"]:
                        # Try to extract a meaningful name from the URI
                        uri_parts = link_info["uri"].split("/")
                        domain_or_path = uri_parts[2] if len(uri_parts) > 2 else link_info["uri"]
                        link_info["text"] = f"Link to {domain_or_path}"
                    else:
                        link_info["text"] = "Internal Link"

            except Exception:
                # Fallback for any extraction errors
                if link_info["uri"]:
                    link_info["text"] = "External Link"
                elif link_info["page"] is not None:
                    link_info["text"] = f"Go to Page {link_info['page'] + 1}"
                else:
                    link_info["text"] = "Link"

        links.append(link_info)

    return links


def extract_page_annotations(page: fitz.Page) -> List[Dict[str, Any]]:
    """
    Extract all annotations from a PDF page.

    Args:
        page: PyMuPDF page object

    Returns:
        List of dictionaries containing annotation information
    """
    annotations = []

    for annot in page.annots():
        annot_info = {
            "type": annot.type[1],  # Get annotation type name
            "content": annot.info.get("content", ""),
            "author": annot.info.get("title", ""),
            "rect": list(annot.rect),
            "page": page.number,
        }

        # Extract text covered by annotation if it's a markup annotation
        if annot.type[0] in [0, 1, 2, 3]:  # Highlight, Underline, StrikeOut, Squiggly
            try:
                covered_text = page.get_textbox(annot.rect)
                annot_info["covered_text"] = covered_text.strip()
            except Exception:
                annot_info["covered_text"] = ""

        annotations.append(annot_info)

    return annotations


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract URLs from plain text using regex patterns.

    Args:
        text: Plain text content

    Returns:
        List of URLs found in the text
    """
    # URL pattern to match http/https URLs and common domain patterns
    url_patterns = [
        r'https?://[^\s<>"{}|\\^`\[\]]+',  # Standard HTTP/HTTPS URLs
        r"www\.[a-zA-Z0-9][-a-zA-Z0-9]*[a-zA-Z0-9]\.[a-zA-Z]{2,}(?:/[^\s]*)?",  # www.domain.com
        r"[a-zA-Z0-9][-a-zA-Z0-9]*[a-zA-Z0-9]\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?(?:/[^\s]*)?",  # domain.com
    ]

    urls = []
    for pattern in url_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            url = match.group().strip(".,;:!?")  # Remove trailing punctuation
            if url not in urls:
                urls.append(url)

    return urls


def extract_enhanced_text_content(page: fitz.Page) -> Dict[str, Any]:
    """
    Extract enhanced text content with formatting information.

    Args:
        page: PyMuPDF page object

    Returns:
        Dictionary containing various text extractions
    """
    plain_text = page.get_text()

    content = {
        "plain_text": plain_text,
        "blocks": page.get_text("blocks"),
        "dict_content": page.get_text("dict"),
        "html_content": page.get_text("html"),
        "links": extract_page_links(page),
        "annotations": extract_page_annotations(page),
        "urls_in_text": extract_urls_from_text(plain_text),  # Extract URLs from plain text
    }

    return content


def format_urls_as_markdown(urls: List[str]) -> str:
    """
    Format URLs found in plain text as Markdown.

    Args:
        urls: List of URLs found in text

    Returns:
        Formatted Markdown string for URLs
    """
    if not urls:
        return ""

    markdown_urls = ["### URLs Found in Text\n"]

    for url in urls:
        # Clean up URL
        clean_url = url.strip()

        # Add protocol if missing
        if not clean_url.startswith(("http://", "https://")):
            if clean_url.startswith("www."):
                clean_url = "https://" + clean_url
            else:
                # For domain-only URLs, add https://
                clean_url = "https://" + clean_url

        # Create a readable display name
        display_name = url
        if len(display_name) > 60:
            display_name = display_name[:57] + "..."

        markdown_urls.append(f"- [{display_name}]({clean_url})")

    return "\n".join(markdown_urls) + "\n\n"


def format_links_as_markdown(links: List[Dict[str, Any]]) -> str:
    """
    Format extracted links as Markdown.

    Args:
        links: List of link dictionaries

    Returns:
        Formatted Markdown string for links
    """
    if not links:
        return ""

    markdown_links = ["## 🔗 Links Found on This Page\n"]

    # Group links by type for better organization
    external_links = [link for link in links if link["type"] == "external" and link["uri"]]
    internal_links = [link for link in links if link["type"] == "internal" and link["page"] is not None]

    # Add external links
    if external_links:
        markdown_links.append("### Clickable Links\n")
        for i, link in enumerate(external_links, 1):
            link_text = link["text"]
            uri = link["uri"]

            # Clean up link text
            if not link_text or link_text == "External Link":
                # Generate better text from URI
                try:
                    from urllib.parse import urlparse

                    parsed = urlparse(uri)
                    if parsed.netloc:
                        link_text = f"Link to {parsed.netloc}"
                    else:
                        link_text = f"External Link {i}"
                except Exception:
                    link_text = f"External Link {i}"

            # Ensure link text is not too long or malformed
            if len(link_text) > 80:
                link_text = link_text[:77] + "..."

            # Remove problematic characters from link text
            link_text = link_text.replace("\n", " ").replace("\r", " ")
            link_text = " ".join(link_text.split())  # Normalize whitespace

            markdown_links.append(f"- [{link_text}]({uri})")

        markdown_links.append("")  # Empty line

    # Add internal links
    if internal_links:
        markdown_links.append("### Internal Links\n")
        for link in internal_links:
            link_text = link["text"]
            page_num = link["page"] + 1

            # Clean up link text
            if not link_text or link_text == "Internal Link":
                link_text = f"Go to Page {page_num}"
            elif len(link_text) > 60:
                link_text = link_text[:57] + "..."

            # Remove problematic characters from link text
            link_text = link_text.replace("\n", " ").replace("\r", " ")
            link_text = " ".join(link_text.split())  # Normalize whitespace

            markdown_links.append(f"- **{link_text}** → Page {page_num}")

        markdown_links.append("")  # Empty line

    return "\n".join(markdown_links) + "\n"


def format_annotations_as_markdown(annotations: List[Dict[str, Any]]) -> str:
    """
    Format extracted annotations as Markdown.

    Args:
        annotations: List of annotation dictionaries

    Returns:
        Formatted Markdown string for annotations
    """
    if not annotations:
        return ""

    markdown_annotations = ["## 📝 Annotations Found on This Page\n"]

    for annot in annotations:
        annot_type = annot["type"]
        content = annot["content"]
        author = annot["author"]
        covered_text = annot.get("covered_text", "")

        if content or covered_text:
            markdown_annotations.append(f"### {annot_type.title()} Annotation")

            if author:
                markdown_annotations.append(f"**Author:** {author}")

            if covered_text:
                markdown_annotations.append(f"**Highlighted Text:** {covered_text}")

            if content:
                markdown_annotations.append(f"**Comment:** {content}")

            markdown_annotations.append("")  # Empty line between annotations

    return "\n".join(markdown_annotations) + "\n"


def pdf_to_pixmaps_bytes(pdf_path: pathlib.Path, dpi: int = 150) -> List[bytes]:
    """
    Convert PDF pages to pixmap bytes in memory.

    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution (dots per inch)

    Returns:
        List of bytes representing each page as JPEG image
    """
    doc = fitz.open(str(pdf_path))
    pixmaps_bytes: List[bytes] = []

    # Scale adjustment: 72 DPI is default, so we calculate scale factor
    mat = fitz.Matrix(dpi / 72, dpi / 72)

    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        # Convert pixmap to JPEG bytes
        img_bytes = pix.tobytes("jpeg")
        pixmaps_bytes.append(img_bytes)

    doc.close()
    return pixmaps_bytes


def process_page_image(page_data: Tuple[int, bytes, str]) -> Tuple[int, str]:
    """
    Process a single page image with LLM using fallback providers.

    Args:
        page_data: Tuple of (page_number, image_bytes, prompt)

    Returns:
        Tuple of (page_number, markdown_content)
    """
    page_number, image_bytes, prompt = page_data

    try:
        result = call_llm_with_fallback_robust(
            prompt=prompt,
            images=[image_bytes],
            max_tokens=4096,  # Increase token limit for detailed analysis
            temperature=0.2,
            retry_delay=1,  # 1 second delay between attempts
            max_retries_per_provider=2,  # Try each provider twice before moving to next
        )
        return (page_number, result)
    except Exception as e:
        error_msg = f"Error processing page {page_number + 1}: {str(e)}"
        print(error_msg)
        return (page_number, f"# Page {page_number + 1} - Processing Error\n\n{error_msg}\n\n")


def pdf_to_markdown(input_pdf_path: str | pathlib.Path, output_md_path: str | pathlib.Path) -> None:
    """
    Convert PDF to Markdown using comprehensive extraction with LLM vision analysis.

    Args:
        input_pdf_path: Path to input PDF file
        output_md_path: Path to output Markdown file
    """
    start_time = time.time()

    # Convert paths to pathlib objects
    pdf_path = pathlib.Path(input_pdf_path)
    md_path = pathlib.Path(output_md_path)

    # Validate input file exists
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {input_pdf_path}")

    doc = fitz.open(str(pdf_path))

    # Create output directory if it doesn't exist
    md_path.parent.mkdir(parents=True, exist_ok=True)

    # Load the analysis prompt
    prompt_path = paths.MARKDOWN_DIR / "extract_for_rag_prompt.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt = file.read()

    print(f"📄 Converting PDF: {pdf_path.name}")
    print(f"📝 Output will be saved to: {md_path}")

    # Extract document metadata
    metadata = doc.metadata
    print(f"📊 Document info: Title='{metadata.get('title', 'N/A')}', Author='{metadata.get('author', 'N/A')}'")

    # Convert PDF pages to bytes
    print("🔄 Converting PDF pages to images...")
    pixmaps_bytes = pdf_to_pixmaps_bytes(pdf_path)
    total_pages = len(pixmaps_bytes)
    print(f"📊 Total pages to process: {total_pages}")

    # Extract comprehensive content from each page
    print("📋 Extracting comprehensive content from pages...")
    page_contents = []
    for i in range(total_pages):
        page = doc.load_page(i)
        enhanced_content = extract_enhanced_text_content(page)
        page_contents.append(enhanced_content)

    # Prepare data for threading
    page_data_list = [(i, img_bytes, prompt) for i, img_bytes in enumerate(pixmaps_bytes)]

    # Determine optimal number of threads
    max_workers = min(total_pages, os.cpu_count() or 4, 10)  # Max 10 threads to avoid API limits
    print(f"🧵 Using {max_workers} threads for processing")

    # Process pages with threading
    print("🚀 Starting parallel processing...")
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_page = {executor.submit(process_page_image, page_data): page_data[0] for page_data in page_data_list}

        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_page):
            page_number, content = future.result()
            results[page_number] = content
            completed += 1
            print(f"✅ Completed page {page_number + 1}/{total_pages} ({completed}/{total_pages})")

    # Combine results in correct order
    print("📝 Combining results into final Markdown...")
    final_markdown = []

    # Add document header with metadata
    final_markdown.append(f"# {metadata.get('title') or pdf_path.stem}\n\n")
    final_markdown.append(f"*Converted from PDF: {pdf_path.name}*\n")
    if metadata.get("author"):
        final_markdown.append(f"*Author: {metadata['author']}*\n")
    if metadata.get("subject"):
        final_markdown.append(f"*Subject: {metadata['subject']}*\n")
    final_markdown.append(f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
    final_markdown.append("---\n\n")

    # Add each page in order with comprehensive content
    for i in range(total_pages):
        page_content_data = page_contents[i]

        # Add page header
        final_markdown.append(f"# 📄 PAGE {i + 1}\n\n")

        # Add raw text content
        final_markdown.append("## 📝 Raw Text Content\n\n")
        final_markdown.append(f"```text\n{page_content_data['plain_text']}\n```\n\n")

        # Add all links and URLs in an organized way
        links = page_content_data.get("links", [])
        urls_in_text = page_content_data.get("urls_in_text", [])

        if links or urls_in_text:
            final_markdown.append("## 🔗 Links and URLs Found on This Page\n\n")

            # Group links by type
            external_links = [link for link in links if link["type"] == "external" and link["uri"]]
            internal_links = [link for link in links if link["type"] == "internal" and link["page"] is not None]

            # Add clickable links
            if external_links:
                final_markdown.append("### Clickable Links\n\n")
                for link_idx, link in enumerate(external_links, 1):
                    link_text = link["text"]
                    uri = link["uri"]

                    # Clean up link text
                    if not link_text or link_text == "External Link":
                        try:
                            from urllib.parse import urlparse

                            parsed = urlparse(uri)
                            if parsed.netloc:
                                link_text = f"Link to {parsed.netloc}"
                            else:
                                link_text = f"External Link {link_idx}"
                        except Exception:
                            link_text = f"External Link {link_idx}"

                    # Ensure link text is not too long or malformed
                    if len(link_text) > 80:
                        link_text = link_text[:77] + "..."

                    # Remove problematic characters from link text
                    link_text = link_text.replace("\n", " ").replace("\r", " ")
                    link_text = " ".join(link_text.split())

                    final_markdown.append(f"- [{link_text}]({uri})\n")

                final_markdown.append("\n")

            # Add internal links
            if internal_links:
                final_markdown.append("### Internal Navigation\n\n")
                for link in internal_links:
                    link_text = link["text"]
                    page_num = link["page"] + 1

                    if not link_text or link_text == "Internal Link":
                        link_text = f"Go to Page {page_num}"
                    elif len(link_text) > 60:
                        link_text = link_text[:57] + "..."

                    link_text = link_text.replace("\n", " ").replace("\r", " ")
                    link_text = " ".join(link_text.split())

                    final_markdown.append(f"- **{link_text}** → Page {page_num}\n")

                final_markdown.append("\n")

            # Add URLs found in text (that are not already in clickable links)
            text_only_urls = []
            for url in urls_in_text:
                clean_url = url.strip()
                if not clean_url.startswith(("http://", "https://")):
                    if clean_url.startswith("www."):
                        clean_url = "https://" + clean_url
                    else:
                        clean_url = "https://" + clean_url

                # Check if this URL is not already in clickable links
                if clean_url not in [link["uri"] for link in external_links]:
                    text_only_urls.append((url, clean_url))

            if text_only_urls:
                final_markdown.append("### URLs Found in Text\n\n")
                for original_url, clean_url in text_only_urls:
                    display_name = original_url
                    if len(display_name) > 60:
                        display_name = display_name[:57] + "..."
                    final_markdown.append(f"- [{display_name}]({clean_url})\n")

                final_markdown.append("\n")

        # Add annotations if present
        annotations_markdown = format_annotations_as_markdown(page_content_data["annotations"])
        if annotations_markdown.strip():
            final_markdown.append(annotations_markdown)

        # Add LLM-analyzed content
        llm_content = results.get(i, f"# Page {i + 1} - Content Missing\n\nError: Page content not available.\n\n")
        cleaned_content = llm_content.replace("/n", "\n").strip()

        final_markdown.append("## 🤖 AI-Enhanced Content Analysis\n\n")
        final_markdown.append(f"{cleaned_content}\n\n")

        # Add visual separator between pages (except for the last page)
        if i < total_pages - 1:
            final_markdown.append("---\n\n")

    # Write final markdown file
    final_content = "".join(final_markdown)

    with open(md_path, "w", encoding="utf-8") as file:
        file.write(final_content)

    doc.close()
    end_time = time.time()
    processing_time = end_time - start_time

    print("✨ Conversion completed successfully!")
    print(f"📄 Pages processed: {total_pages}")
    print(f"⏱️  Total processing time: {processing_time:.2f} seconds")
    print(f"⚡ Average time per page: {processing_time / total_pages:.2f} seconds")
    print(f"💾 Output saved to: {md_path}")


def main():
    """Example usage of the enhanced PDF to Markdown converter."""
    # Example paths - update these for your use case
    input_pdf = paths.PDF_DIR / "AWS Automotive Solutions Map.pdf"
    output_md = paths.MARKDOWN_DIR / "AWS Automotive Solutions Map.md"

    try:
        pdf_to_markdown(input_pdf, output_md)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
