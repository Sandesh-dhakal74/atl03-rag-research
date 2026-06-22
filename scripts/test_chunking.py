import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from atl03_rag.models import ExtractedElement
from atl03_rag.chunker import build_chunks
from atl03_rag.config import PROCESSED_DIR


SOURCES = {
    "sample": {
        "input": "atl03_test_sample_extracted.json",
        "source_doc": "atl03_test_sample.pdf",
        "parents_output": "atl03_test_sample_parent_chunks.json",
        "retrieval_output": "atl03_test_sample_retrieval_chunks.json",
    },
    "dictionary": {
        "input": "atl03_data_dictionary_extracted.json",
        "source_doc": "atl03_data_dictionary_v07.pdf",
        "parents_output": "atl03_data_dictionary_parent_chunks.json",
        "retrieval_output": "atl03_data_dictionary_retrieval_chunks.json",
    },
}


def load_elements(path: Path) -> list[ExtractedElement]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [ExtractedElement(**item) for item in data]


def save_json(data, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    source_name = sys.argv[1] if len(sys.argv) > 1 else "sample"

    if source_name not in SOURCES:
        print("Invalid source.")
        print("Use:")
        print("  python scripts/test_chunking.py sample")
        print("  python scripts/test_chunking.py dictionary")
        return

    source = SOURCES[source_name]
    input_path = PROCESSED_DIR / source["input"]

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find extracted JSON: {input_path}\n"
            "Run extraction first."
        )

    elements = load_elements(input_path)

    parents, retrieval_chunks = build_chunks(
        elements=elements,
        source_doc=source["source_doc"],
    )

    parent_output_path = PROCESSED_DIR / source["parents_output"]
    retrieval_output_path = PROCESSED_DIR / source["retrieval_output"]

    save_json([parent.to_dict() for parent in parents], parent_output_path)
    save_json([chunk.to_dict() for chunk in retrieval_chunks], retrieval_output_path)

    print("\nChunking summary")
    print("----------------")
    print(f"Source:             {source_name}")
    print(f"Extracted elements: {len(elements)}")
    print(f"Parent chunks:      {len(parents)}")
    print(f"Retrieval chunks:   {len(retrieval_chunks)}")

    print("\nSaved parent chunks to:")
    print(parent_output_path)

    print("\nSaved retrieval chunks to:")
    print(retrieval_output_path)

    print("\nFirst 8 retrieval chunks")
    print("------------------------")

    for chunk in retrieval_chunks[:8]:
        print("\nChunk ID:", chunk.chunk_id)
        print("Parent ID:", chunk.parent_id)
        print("Type:", chunk.chunk_type)
        print("Page:", chunk.page_number)
        print("Section:", chunk.section_heading)
        print("Metadata:", chunk.metadata)
        print("Preview:", chunk.content[:500])


if __name__ == "__main__":
    main()