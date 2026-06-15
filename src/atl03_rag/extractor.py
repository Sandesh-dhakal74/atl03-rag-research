import re
import json
from pathlib import Path

import pdfplumber

from atl03_rag.models import ExtractedElement


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def looks_like_section(line: str) -> bool:
    """
    Simple first version of section detection.
    We improve this later.
    """
    line = line.strip()

    if line.startswith("Group:"):
        return True

    if re.match(r"^\d+(\.\d+)*\s+Group:", line):
        return True

    if re.match(r"^\d+(\.\d+)*\s+[A-Z]", line):
        return True

    return False


def table_to_markdown(table: list[list[str]]) -> str:
    """
    Convert a pdfplumber table into markdown-like text.
    This is easier for humans and later easier for the LLM.
    """
    cleaned_rows = []

    for row in table:
        cleaned_row = []
        for cell in row:
            if cell is None:
                cleaned_row.append("")
            else:
                cleaned_row.append(clean_text(str(cell)))
        cleaned_rows.append(cleaned_row)

    if not cleaned_rows:
        return ""

    header = cleaned_rows[0]
    body = cleaned_rows[1:]

    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    for row in body:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def extract_elements_from_pdf(pdf_path: Path) -> list[ExtractedElement]:
    """
    Extract text and tables from a PDF.

    First version:
    - extracts page text
    - extracts tables
    - tracks page number
    - tries to track section heading
    """
    elements: list[ExtractedElement] = []
    current_section = "Document"

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):

            # 1. Extract text
            page_text = page.extract_text() or ""
            lines = page_text.split("\n")

            paragraph_buffer = []

            for line in lines:
                line = clean_text(line)

                if not line:
                    continue

                # Skip page labels like "Page 1-36"
                if re.match(r"^Page\s+\d+-\d+$", line):
                    continue

                if looks_like_section(line):
                    if paragraph_buffer:
                        paragraph = clean_text(" ".join(paragraph_buffer))
                        elements.append(
                            ExtractedElement(
                                element_type="text",
                                text=paragraph,
                                page_number=page_index,
                                section_heading=current_section,
                            )
                        )
                        paragraph_buffer = []

                    current_section = line
                else:
                    paragraph_buffer.append(line)

            if paragraph_buffer:
                paragraph = clean_text(" ".join(paragraph_buffer))
                elements.append(
                    ExtractedElement(
                        element_type="text",
                        text=paragraph,
                        page_number=page_index,
                        section_heading=current_section,
                    )
                )

            # 2. Extract tables
            tables = page.extract_tables()

            for table in tables:
                markdown_table = table_to_markdown(table)

                if markdown_table.strip():
                    elements.append(
                        ExtractedElement(
                            element_type="table",
                            text=clean_text(markdown_table),
                            page_number=page_index,
                            section_heading=current_section,
                            formatted_content=markdown_table,
                        )
                    )

    return elements


def save_elements_to_json(elements: list[ExtractedElement], output_path: Path) -> None:
    data = [element.to_dict() for element in elements]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)