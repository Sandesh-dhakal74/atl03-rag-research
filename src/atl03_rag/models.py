from dataclasses import dataclass, asdict


@dataclass
class ExtractedElement:
    element_type: str
    text: str
    page_number: int
    section_heading: str = ""
    formatted_content: str = ""

    def to_dict(self) -> dict:
        return asdict(self)