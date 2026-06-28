import sys
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from atl03_rag.config import PROCESSED_DIR
from atl03_rag.embedder import embed_single


BENCHMARK_QUESTIONS = [
    {
        "id": "Q001",
        "question": "What does h_ph measure?",
        "expected_variable": "h_ph",
    },
    {
        "id": "Q002",
        "question": "What does lat_ph mean?",
        "expected_variable": "lat_ph",
    },
    {
        "id": "Q003",
        "question": "What does lon_ph mean?",
        "expected_variable": "lon_ph",
    },
    {
        "id": "Q004",
        "question": "Is delta_time UTC time?",
        "expected_variable": "delta_time",
    },
    {
        "id": "Q005",
        "question": "What does quality_ph indicate?",
        "expected_variable": "quality_ph",
    },
    {
        "id": "Q006",
        "question": "What is signal_conf_ph?",
        "expected_variable": "signal_conf_ph",
    },
]


def cosine_similarity(vec1, vec2):
    return sum(a * b for a, b in zip(vec1, vec2))


def extract_possible_variables(query: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", query)


def score_chunk(query_embedding, query_terms, chunk):
    vector_score = cosine_similarity(query_embedding, chunk["embedding"])

    metadata = chunk.get("metadata", {})
    variable_name = metadata.get("variable_name", "")

    content = chunk.get("content", "").lower()
    query_terms_lower = [term.lower() for term in query_terms]

    exact_variable_boost = 0.0
    keyword_boost = 0.0

    if variable_name and variable_name.lower() in query_terms_lower:
        exact_variable_boost = 0.20

    for term in query_terms_lower:
        if "_" in term and term in content:
            keyword_boost += 0.05

    final_score = vector_score + exact_variable_boost + keyword_boost

    return final_score


def retrieve(query, chunks, top_k=5):
    query_terms = extract_possible_variables(query)
    query_embedding = embed_single(query)

    scored_chunks = []

    for chunk in chunks:
        score = score_chunk(query_embedding, query_terms, chunk)
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    return scored_chunks[:top_k]


def main():
    embedded_path = PROCESSED_DIR / "atl03_data_dictionary_embedded_chunks.json"

    if not embedded_path.exists():
        raise FileNotFoundError(
            f"Could not find {embedded_path}. Run dictionary embedding first."
        )

    with open(embedded_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    results = []

    hit_at_1 = 0
    hit_at_3 = 0
    hit_at_5 = 0

    print("\nRetrieval Benchmark")
    print("-------------------")
    print(f"Chunks loaded: {len(chunks)}")
    print(f"Questions: {len(BENCHMARK_QUESTIONS)}")

    for item in BENCHMARK_QUESTIONS:
        question_id = item["id"]
        question = item["question"]
        expected_variable = item["expected_variable"]

        top_results = retrieve(question, chunks, top_k=5)

        rank_found = None

        for rank, (_, chunk) in enumerate(top_results, start=1):
            variable_name = chunk.get("metadata", {}).get("variable_name", "")

            if variable_name == expected_variable:
                rank_found = rank
                break

        if rank_found == 1:
            hit_at_1 += 1

        if rank_found is not None and rank_found <= 3:
            hit_at_3 += 1

        if rank_found is not None and rank_found <= 5:
            hit_at_5 += 1

        top_variable = top_results[0][1].get("metadata", {}).get("variable_name", "")

        results.append(
            {
                "id": question_id,
                "question": question,
                "expected_variable": expected_variable,
                "top_variable": top_variable,
                "rank_found": rank_found,
            }
        )

        print("\n" + question_id)
        print(f"Question: {question}")
        print(f"Expected variable: {expected_variable}")
        print(f"Top result variable: {top_variable}")
        print(f"Rank found: {rank_found}")

    total = len(BENCHMARK_QUESTIONS)

    print("\nSummary")
    print("-------")
    print(f"Recall@1: {hit_at_1}/{total} = {hit_at_1 / total:.2f}")
    print(f"Recall@3: {hit_at_3}/{total} = {hit_at_3 / total:.2f}")
    print(f"Recall@5: {hit_at_5}/{total} = {hit_at_5 / total:.2f}")

    output_path = PROCESSED_DIR / "retrieval_benchmark_results.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved results to: {output_path}")


if __name__ == "__main__":
    main()