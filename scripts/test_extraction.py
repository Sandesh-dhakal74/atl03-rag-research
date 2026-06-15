import sys
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from atl03_rag.config import ATL03_DATA_DICTIONARY, PROCESSED_DIR
from atl03_rag.extractor import extract_elements_from_pdf, save_elements_to_json


def main():
    if not ATL03_DATA_DICTIONARY.exists():
        raise FileNotFoundError(
            f"Could not find PDF at: {ATL03_DATA_DICTIONARY}\n"
            "Make sure the file is named atl03_data_dictionary_v07.pdf "
            "and placed inside data/raw/"
        )

    print(f"Extracting from: {ATL03_DATA_DICTIONARY}")

    elements = extract_elements_from_pdf(ATL03_DATA_DICTIONARY)

    counts = Counter(element.element_type for element in elements)

    print("\nExtraction summary")
    print("------------------")
    print(f"Total elements: {len(elements)}")
    print(f"Text elements:  {counts.get('text', 0)}")
    print(f"Table elements: {counts.get('table', 0)}")

    output_path = PROCESSED_DIR / "atl03_data_dictionary_extracted.json"
    save_elements_to_json(elements, output_path)

    print(f"\nSaved extracted elements to:")
    print(output_path)

    print("\nFirst 3 elements")
    print("----------------")
    for element in elements[:3]:
        print(f"\nType: {element.element_type}")
        print(f"Page: {element.page_number}")
        print(f"Section: {element.section_heading}")
        print(f"Text preview: {element.text[:300]}")


if __name__ == "__main__":
    main()