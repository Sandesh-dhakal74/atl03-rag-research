import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
json_path = PROJECT_ROOT / "data" / "processed" / "atl03_data_dictionary_extracted.json"

terms = ["h_ph", "lat_ph", "lon_ph", "delta_time", "quality_ph", "signal_conf_ph"]


def snippet_around(text: str, term: str, window: int = 450) -> str:
    lower_text = text.lower()
    lower_term = term.lower()

    index = lower_text.find(lower_term)

    if index == -1:
        return text[:window]

    start = max(0, index - window // 2)
    end = min(len(text), index + window // 2)

    return text[start:end]


with open(json_path, "r", encoding="utf-8") as f:
    elements = json.load(f)

for term in terms:
    print("\n" + "=" * 80)
    print(f"Searching for: {term}")
    print("=" * 80)

    matches = [
        e for e in elements
        if term.lower() in e["text"].lower()
    ]

    print(f"Matches found: {len(matches)}")

    for match in matches[:3]:
        print("\nType:", match["element_type"])
        print("Page:", match["page_number"])
        print("Section:", match["section_heading"])
        print("Snippet around term:")
        print(snippet_around(match["text"], term))