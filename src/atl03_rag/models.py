from dataclasses import dataclass, asdict, field


@dataclass
class ExtractedElement:
    element_type: str
    text: str
    page_number: int
    section_heading: str = ""
    formatted_content: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ParentChunk:
    parent_id: str
    source_doc: str
    chunk_type: str
    content: str
    section_heading: str
    page_start: int
    page_end: int
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RetrievalChunk:
    chunk_id: str
    parent_id: str
    source_doc: str
    chunk_type: str
    content: str
    section_heading: str
    page_number: int
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)