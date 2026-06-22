import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

retrieval_path = PROJECT_ROOT / "data" / "processed" / "atl03_data_dictionary_retrieval_chunks.json"
parent_path = PROJECT_ROOT / "data" / "processed" / "atl03_data_dictionary_parent_chunks.json"

terms = ["h_ph", "lat_ph", "lon_ph", "delta_time", "quality_ph", "signal_conf_ph"]


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
    print(f"Exact variable search: {term}")
    print("=" * 80)

    matches = [
        chunk for chunk in retrieval_chunks
        if chunk.get("metadata", {}).get("variable_name") == term
    ]

    print(f"Exact matches found: {len(matches)}")

    for chunk in matches[:5]:
        print("\nRetrieval chunk")
        print("----------------")
        print("Chunk ID:", chunk["chunk_id"])
        print("Parent ID:", chunk["parent_id"])
        print("Page:", chunk["page_number"])
        print("Section:", chunk["section_heading"])
        print("Variable:", chunk["metadata"].get("variable_name"))
        print("Content:")
        print(chunk["content"])

        parent = parents_by_id.get(chunk["parent_id"])

        if parent:
            print("\nParent context")
            print("--------------")
            print(parent["content"][:1000])