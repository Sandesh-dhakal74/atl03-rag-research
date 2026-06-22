import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

retrieval_path = PROJECT_ROOT / "data" / "processed" / "atl03_data_dictionary_retrieval_chunks.json"
parent_path = PROJECT_ROOT / "data" / "processed" / "atl03_data_dictionary_parent_chunks.json"

terms = ["h_ph", "lat_ph", "lon_ph", "delta_time", "quality_ph", "signal_conf_ph"]


def snippet_around(text: str, term: str, window: int = 500) -> str:
    lower_text = text.lower()
    lower_term = term.lower()

    index = lower_text.find(lower_term)

    if index == -1:
        return text[:window]

    start = max(0, index - window // 2)
    end = min(len(text), index + window // 2)

    return text[start:end]


with open(retrieval_path, "r", encoding="utf-8") as f:
    retrieval_chunks = json.load(f)

with open(parent_path, "r", encoding="utf-8") as f:
    parent_chunks = json.load(f)

parents_by_id = {
    parent["parent_id"]: parent
    for parent in parent_chunks
}

for term in terms:
    print("\n" + "=" * 80)
    print(f"Searching retrieval chunks for: {term}")
    print("=" * 80)

    matches = [
        chunk for chunk in retrieval_chunks
        if term.lower() in chunk["content"].lower()
    ]

    print(f"Matches found: {len(matches)}")

    for chunk in matches[:3]:
        print("\nRetrieval chunk")
        print("----------------")
        print("Chunk ID:", chunk["chunk_id"])
        print("Parent ID:", chunk["parent_id"])
        print("Type:", chunk["chunk_type"])
        print("Page:", chunk["page_number"])
        print("Section:", chunk["section_heading"])
        print("Metadata:", chunk["metadata"])
        print("Content:")
        print(snippet_around(chunk["content"], term))

        parent = parents_by_id.get(chunk["parent_id"])

        if parent:
            print("\nParent context")
            print("--------------")
            print(snippet_around(parent["content"], term))