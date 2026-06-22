import re
from atl03_rag.models import ExtractedElement, ParentChunk, RetrievalChunk

TABLE_CONTEXT_WINDOW = 4

def clean_chunk_text(text: str) -> str:
    return text.strip()


def make_safe_source_name(source_doc: str) -> str:
    return (
        source_doc
        .replace(" ", "_")
        .replace(".", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )


def make_parent_id(source_doc: str, index: int) -> str:
    safe_source = make_safe_source_name(source_doc)
    return f"{safe_source}_parent_{index:05d}"


def make_chunk_id(source_doc: str, index: int) -> str:
    safe_source = make_safe_source_name(source_doc)
    return f"{safe_source}_retrieval_{index:05d}"


def is_header_row(row: str) -> bool:
    """
    Skip table header rows as retrieval chunks.

    Header rows are useful as context, but they usually should not become
    searchable chunks by themselves.
    """
    lower = row.lower()

    header_patterns = [
        "variable | units | description",
        "name | type",
        "name | type(dims)",
        "standard name",
        "fillvalue",
    ]

    return any(pattern in lower for pattern in header_patterns)

def is_good_table_retrieval_row(row: str) -> bool:
    """
    Decide whether a table row is meaningful enough to become a retrieval chunk.

    Good:
    h_ph height | FLOAT(:) - | meters | Height of each received photon...

    Bad:
    h_ph
    signal_conf_ph
    with signal_conf_ph or weight_ph to identify
    Source: ATL03 ATBD...
    """
    row = row.strip()

    if is_bad_table_row(row):
        return False

    if is_header_row(row):
        return False

    # Must have table structure
    if "|" not in row:
        return False

    # Must be long enough to carry meaning
    if len(row) < 25:
        return False

    variable_name = guess_variable_name(row)

    # Variable name should look like a dataset/field name, not normal English
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", variable_name):
        return False

    # Avoid normal English fragments accidentally becoming variable names
    common_bad_starts = {
        "with",
        "from",
        "source",
        "the",
        "and",
        "or",
        "for",
        "to",
        "in",
        "of",
        "this",
        "that",
        "photons",
    }

    if variable_name.lower() in common_bad_starts:
        return False

    return True

def is_bad_table_row(row: str) -> bool:
    row = row.strip()

    if not row:
        return True

    if set(row.replace("|", "").strip()) <= {"-"}:
        return True

    return False


def split_table_into_rows(table_text: str) -> list[str]:
    """
    Split extracted table text into individual table rows.
    """
    rows = []

    for line in table_text.splitlines():
        line = clean_chunk_text(line)

        if not is_bad_table_row(line):
            rows.append(line)

    return rows


def guess_variable_name(row: str) -> str:
    """
    Try to guess the variable name from a table row.

    Example:
    h_ph height | FLOAT(:) - | meters | Height of each received photon
    returns: h_ph
    """
    first_cell = row.split("|")[0].strip()

    if not first_cell:
        return ""

    return first_cell.split()[0]


def make_table_parent_content(
    source_doc: str,
    element: ExtractedElement,
    rows: list[str],
    row_index: int,
) -> str:
    """
    Parent context for a table row.

    We include a few nearby rows so the LLM gets context, but not the
    entire 4-page table.
    """
    start = max(0, row_index - TABLE_CONTEXT_WINDOW)
    end = min(len(rows), row_index + TABLE_CONTEXT_WINDOW + 1)

    nearby_rows = rows[start:end]

    return (
        f"Source: {source_doc}\n"
        f"Section: {element.section_heading}\n"
        f"Page: {element.page_number}\n\n"
        f"Nearby table context:\n"
        + "\n".join(nearby_rows)
    )


def make_text_parent_content(source_doc: str, element: ExtractedElement) -> str:
    return (
        f"Source: {source_doc}\n"
        f"Section: {element.section_heading}\n"
        f"Page: {element.page_number}\n\n"
        f"{element.text.strip()}"
    )


def build_chunks(
    elements: list[ExtractedElement],
    source_doc: str,
) -> tuple[list[ParentChunk], list[RetrievalChunk]]:
    """
    Build parent-child chunks.

    RetrievalChunk:
    - small and precise
    - used later for embedding/search

    ParentChunk:
    - surrounding context
    - used later when generating the final answer
    """
    parents: list[ParentChunk] = []
    retrieval_chunks: list[RetrievalChunk] = []

    parent_counter = 1
    retrieval_counter = 1

    for element_index, element in enumerate(elements):
        if not element.text.strip():
            continue

        if element.element_type == "text":
            parent_id = make_parent_id(source_doc, parent_counter)
            chunk_id = make_chunk_id(source_doc, retrieval_counter)

            parent_content = make_text_parent_content(source_doc, element)

            retrieval_content = (
                f"Section: {element.section_heading}\n"
                f"Page: {element.page_number}\n\n"
                f"{element.text.strip()}"
            )

            parents.append(
                ParentChunk(
                    parent_id=parent_id,
                    source_doc=source_doc,
                    chunk_type="text_parent",
                    content=parent_content,
                    section_heading=element.section_heading,
                    page_start=element.page_number,
                    page_end=element.page_number,
                    metadata={
                        "element_type": element.element_type,
                        "element_index": element_index,
                    },
                )
            )

            retrieval_chunks.append(
                RetrievalChunk(
                    chunk_id=chunk_id,
                    parent_id=parent_id,
                    source_doc=source_doc,
                    chunk_type="text",
                    content=retrieval_content,
                    section_heading=element.section_heading,
                    page_number=element.page_number,
                    metadata={
                        "element_type": element.element_type,
                        "element_index": element_index,
                    },
                )
            )

            parent_counter += 1
            retrieval_counter += 1

        elif element.element_type == "table":
            rows = split_table_into_rows(element.text)

            for row_index, row in enumerate(rows):
                if not is_good_table_retrieval_row(row):
                    continue

                parent_id = make_parent_id(source_doc, parent_counter)
                chunk_id = make_chunk_id(source_doc, retrieval_counter)

                parent_content = make_table_parent_content(
                    source_doc=source_doc,
                    element=element,
                    rows=rows,
                    row_index=row_index,
                )

                variable_name = guess_variable_name(row)

                retrieval_content = (
                    f"Section: {element.section_heading}\n"
                    f"Page: {element.page_number}\n"
                    f"Table row:\n"
                    f"{row}"
                )

                parents.append(
                    ParentChunk(
                        parent_id=parent_id,
                        source_doc=source_doc,
                        chunk_type="table_context_parent",
                        content=parent_content,
                        section_heading=element.section_heading,
                        page_start=element.page_number,
                        page_end=element.page_number,
                        metadata={
                            "element_type": element.element_type,
                            "element_index": element_index,
                            "row_index": row_index,
                            "context_window": TABLE_CONTEXT_WINDOW,
                            "variable_name": variable_name,
                        },
                    )
                )

                retrieval_chunks.append(
                    RetrievalChunk(
                        chunk_id=chunk_id,
                        parent_id=parent_id,
                        source_doc=source_doc,
                        chunk_type="table_row",
                        content=retrieval_content,
                        section_heading=element.section_heading,
                        page_number=element.page_number,
                        metadata={
                            "element_type": element.element_type,
                            "element_index": element_index,
                            "row_index": row_index,
                            "variable_name": variable_name,
                        },
                    )
                )

                parent_counter += 1
                retrieval_counter += 1

    return parents, retrieval_chunks