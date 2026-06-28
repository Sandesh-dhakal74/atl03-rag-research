import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from atl03_rag.config import PROCESSED_DIR
from atl03_rag.embedder import embed_single, embed_texts


def main():
    input_path = PROCESSED_DIR / "atl03_test_sample_retrieval_chunks.json"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find retrieval chunks file: {input_path}\n"
            "Run chunking first: python scripts\\test_chunking.py sample"
        )

    with open(input_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    first_chunk = chunks[0]

    print("\nEmbedding single chunk")
    print("----------------------")
    print("Chunk ID:", first_chunk["chunk_id"])
    print("Chunk type:", first_chunk["chunk_type"])
    print("Page:", first_chunk["page_number"])
    print("Section:", first_chunk["section_heading"])

    print("\nContent preview:")
    print(first_chunk["content"][:500])

    vector = embed_single(first_chunk["content"])

    print("\nSingle embedding result")
    print("-----------------------")
    print("Dimension:", len(vector))
    print("First 5 values:", vector[:5])

    print("\nEmbedding all sample chunks")
    print("---------------------------")

    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts)

    print("Chunks embedded:", len(vectors))
    print("First vector dimension:", len(vectors[0]))

    print("\nEmbedding test passed.")


if __name__ == "__main__":
    main()