import sys
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from atl03_rag.config import (
    ATL03_DATA_DICTIONARY,
    ATL03_TEST_SAMPLE,
    PROCESSED_DIR,
)
from atl03_rag.extractor import (
    extract_elements_from_pdf,
    save_elements_to_json,
)


SOURCES = {
    "sample": {
        "path": ATL03_TEST_SAMPLE,
        "output": "atl03_test_sample_extracted.json",
    },
    "dictionary": {
        "path": ATL03_DATA_DICTIONARY,
        "output": "atl03_data_dictionary_extracted.json",
    },
}


def main():
    # Default to the small test sample
    source_name = sys.argv[1] if len(sys.argv) > 1 else "sample"

    if source_name not in SOURCES:
        print("Invalid source.")
        print("Use one of:")
        print("  python scripts/test_extraction.py sample")
        print("  python scripts/test_extraction.py dictionary")
        return

    pdf_path = SOURCES[source_name]["path"]
    output_filename = SOURCES[source_name]["output"]

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"Could not find PDF at: {pdf_path}\n"
            "Make sure the file is inside data/raw/ and the filename matches config.py"
        )

    print(f"Extracting from: {pdf_path}")

    elements = extract_elements_from_pdf(pdf_path)

    counts = Counter(element.element_type for element in elements)

    print("\nExtraction summary")
    print("------------------")
    print(f"Source:         {source_name}")
    print(f"Total elements: {len(elements)}")
    print(f"Text elements:  {counts.get('text', 0)}")
    print(f"Table elements: {counts.get('table', 0)}")

    output_path = PROCESSED_DIR / output_filename
    save_elements_to_json(elements, output_path)

    print(f"\nSaved extracted elements to:")
    print(output_path)

    print("\nExtracted elements preview")
    print("--------------------------")

    # For the small sample, print everything.
    # For the full dictionary, print only first 5.
    preview_count = len(elements) if source_name == "sample" else 5

    for i, element in enumerate(elements[:preview_count], start=1):
        print(f"\nElement {i}")
        print(f"Type: {element.element_type}")
        print(f"Page: {element.page_number}")
        print(f"Section: {element.section_heading}")
        print(f"Text preview: {element.text[:500]}")


if __name__ == "__main__":
    main()