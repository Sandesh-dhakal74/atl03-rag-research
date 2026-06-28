import sys
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from atl03_rag.config import PROCESSED_DIR
from atl03_rag.embedder import embed_single


def cosine_similarity(vec1, vec2):
    # Your vectors are normalized, so dot product = cosine similarity
    return sum(a * b for a, b in zip(vec1, vec2))


def extract_possible_variables(query: str) -> list[str]:
    """
    Find variable-like terms in the user question.
    Examples:
    h_ph, lat_ph, lon_ph, delta_time, signal_conf_ph
    """
    return re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", query)


def score_chunk(query_embedding, query_terms, chunk):
    vector_score = cosine_similarity(query_embedding, chunk["embedding"])

    metadata = chunk.get("metadata", {})
    variable_name = metadata.get("variable_name", "")

    content = chunk.get("content", "").lower()
    query_terms_lower = [term.lower() for term in query_terms]

    exact_variable_boost = 0.0
    content_keyword_boost = 0.0

    # Strong boost if the exact variable name matches metadata
    if variable_name and variable_name.lower() in query_terms_lower:
        exact_variable_boost = 0.20

    # Smaller boost if query variable appears in content
    for term in query_terms_lower:
        if "_" in term and term in content:
            content_keyword_boost += 0.05

    final_score = vector_score + exact_variable_boost + content_keyword_boost

    return final_score, vector_score, exact_variable_boost, content_keyword_boost


def main():
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What does h_ph measure?"

    embedded_path = PROCESSED_DIR / "atl03_data_dictionary_embedded_chunks.json"

    if not embedded_path.exists():
        raise FileNotFoundError(
            f"Could not find {embedded_path}. Run dictionary embedding first."
        )

    with open(embedded_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print("\nRetrieval test")
    print("--------------")
    print(f"Question: {query}")
    print(f"Chunks loaded: {len(chunks)}")

    query_terms = extract_possible_variables(query)
    print(f"Detected query terms: {query_terms}")

    query_embedding = embed_single(query)

    scored_chunks = []

    for chunk in chunks:
        final_score, vector_score, exact_boost, keyword_boost = score_chunk(
            query_embedding,
            query_terms,
            chunk,
        )

        scored_chunks.append(
            {
                "final_score": final_score,
                "vector_score": vector_score,
                "exact_boost": exact_boost,
                "keyword_boost": keyword_boost,
                "chunk": chunk,
            }
        )

    scored_chunks.sort(key=lambda item: item["final_score"], reverse=True)

    top_k = 5

    print(f"\nTop {top_k} results")
    print("----------------")

    for rank, item in enumerate(scored_chunks[:top_k], start=1):
        chunk = item["chunk"]

        print(f"\nRank {rank}")
        print(f"Final score: {item['final_score']:.4f}")
        print(f"Vector score: {item['vector_score']:.4f}")
        print(f"Exact variable boost: {item['exact_boost']:.4f}")
        print(f"Keyword boost: {item['keyword_boost']:.4f}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Page: {chunk['page_number']}")
        print(f"Section: {chunk['section_heading']}")
        print(f"Type: {chunk['chunk_type']}")

        metadata = chunk.get("metadata", {})
        if metadata:
            print(f"Metadata: {metadata}")

        print("\nContent:")
        print(chunk["content"][:1000])


if __name__ == "__main__":
    main()