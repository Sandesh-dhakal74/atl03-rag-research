import re
import json
from pathlib import Path

import pdfplumber

from atl03_rag.models import ExtractedElement


def clean_text(text: str) -> str:
    """Normalize whitespace."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def looks_like_section(line: str) -> bool:
    """
    Detect simple section headings.

    Examples:
    1.0 ATL03 Overview
    1.1 Key Variables
    Group: /gtx/heights
    """
    line = line.strip()

    if line.startswith("Group:"):
        return True

    if re.match(r"^\d+(\.\d+)*\s+Group:", line):
        return True

    if re.match(r"^\d+(\.\d+)*\s+[A-Z]", line):
        return True

    return False


def word_inside_bbox(word: dict, bbox: tuple[float, float, float, float]) -> bool:
    """
    Check whether the center of a word is inside a table bounding box.

    pdfplumber bbox format:
    (x0, top, x1, bottom)
    """
    x0, top, x1, bottom = bbox

    word_x_center = (word["x0"] + word["x1"]) / 2
    word_y_center = (word["top"] + word["bottom"]) / 2

    return (
        x0 <= word_x_center <= x1
        and top <= word_y_center <= bottom
    )


def extract_lines_outside_tables(page, table_bboxes: list[tuple]) -> list[str]:
    """
    Extract page text, but remove words that are inside table areas.
    This prevents table text from appearing twice.
    """
    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3,
        keep_blank_chars=False,
    )

    non_table_words = []

    for word in words:
        inside_any_table = any(
            word_inside_bbox(word, bbox)
            for bbox in table_bboxes
        )

        if not inside_any_table:
            non_table_words.append(word)

    # Sort words in reading order
    non_table_words.sort(key=lambda w: (w["top"], w["x0"]))

    lines = []
    current_line = []
    current_top = None

    for word in non_table_words:
        word_top = word["top"]

        if current_top is None:
            current_top = word_top
            current_line.append(word["text"])

        elif abs(word_top - current_top) <= 3:
            current_line.append(word["text"])

        else:
            lines.append(clean_text(" ".join(current_line)))
            current_line = [word["text"]]
            current_top = word_top

    if current_line:
        lines.append(clean_text(" ".join(current_line)))

    return [line for line in lines if line]


def clean_table(table: list[list[str]]) -> list[list[str]]:
    """
    Remove empty rows and empty columns from extracted tables.
    This reduces noisy output like | | | |.
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

    # Remove fully empty rows
    cleaned_rows = [
        row for row in cleaned_rows
        if any(cell.strip() for cell in row)
    ]

    if not cleaned_rows:
        return []

    # Make all rows the same length
    max_cols = max(len(row) for row in cleaned_rows)

    for row in cleaned_rows:
        while len(row) < max_cols:
            row.append("")

    # Remove fully empty columns
    non_empty_cols = []

    for col_index in range(max_cols):
        has_content = any(
            row[col_index].strip()
            for row in cleaned_rows
        )

        if has_content:
            non_empty_cols.append(col_index)

    cleaned_rows = [
        [row[col_index] for col_index in non_empty_cols]
        for row in cleaned_rows
    ]

    return cleaned_rows


def table_to_markdown(table: list[list[str]]) -> str:
    """
    Convert a cleaned table into markdown-style text.
    """
    cleaned_rows = clean_table(table)

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


def flush_paragraph(
    paragraph_buffer: list[str],
    elements: list[ExtractedElement],
    page_number: int,
    section_heading: str,
) -> list[str]:
    """
    Save buffered lines as one text element, then clear the buffer.
    """
    if paragraph_buffer:
        paragraph = clean_text(" ".join(paragraph_buffer))

        if paragraph:
            elements.append(
                ExtractedElement(
                    element_type="text",
                    text=paragraph,
                    page_number=page_number,
                    section_heading=section_heading,
                )
            )

    return []


def extract_elements_from_pdf(pdf_path: Path) -> list[ExtractedElement]:
    """
    Clean extraction version.

    This version:
    - finds table areas first
    - extracts non-table text only
    - extracts tables separately
    - preserves page number
    - tracks section heading
    """
    elements: list[ExtractedElement] = []
    current_section = "Document"

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):

            # 1. Find tables first
            found_tables = page.find_tables()
            table_bboxes = [table.bbox for table in found_tables]

            # 2. Extract text outside table areas
            lines = extract_lines_outside_tables(page, table_bboxes)

            paragraph_buffer = []

            for line in lines:
                line = clean_text(line)

                if not line:
                    continue

                # Skip page labels like "Page 1-36"
                if re.match(r"^Page\s+\d+-\d+$", line):
                    continue

                if looks_like_section(line):
                    paragraph_buffer = flush_paragraph(
                        paragraph_buffer=paragraph_buffer,
                        elements=elements,
                        page_number=page_index,
                        section_heading=current_section,
                    )

                    current_section = line

                else:
                    paragraph_buffer.append(line)

            paragraph_buffer = flush_paragraph(
                paragraph_buffer=paragraph_buffer,
                elements=elements,
                page_number=page_index,
                section_heading=current_section,
            )

            # 3. Extract tables separately
            for table_obj in found_tables:
                table = table_obj.extract()
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