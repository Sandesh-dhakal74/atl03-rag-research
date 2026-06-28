import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from atl03_rag.config import (
    PROCESSED_DIR,
    EMBED_MODEL,
    EMBEDDING_DIM,
    EMBED_BATCH_SIZE,
    EMBED_SLEEP_SECONDS,
)
from atl03_rag.embedder import embed_texts


SOURCES = {
    "sample": {
        "input": "atl03_test_sample_retrieval_chunks.json",
        "output": "atl03_test_sample_embedded_chunks.json",
    },
    "dictionary": {
        "input": "atl03_data_dictionary_retrieval_chunks.json",
        "output": "atl03_data_dictionary_embedded_chunks.json",
    },
    # We will use this later after ATBD extraction/chunking is ready
    "atbd": {
        "input": "atl03_atbd_retrieval_chunks.json",
        "output": "atl03_atbd_embedded_chunks.json",
    },
}


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    source_name = sys.argv[1] if len(sys.argv) > 1 else "sample"

    if source_name not in SOURCES:
        print("Invalid source.")
        print("Use:")
        print("  python scripts\\embed_chunks.py sample")
        print("  python scripts\\embed_chunks.py dictionary")
        print("  python scripts\\embed_chunks.py atbd")
        return

    input_path = PROCESSED_DIR / SOURCES[source_name]["input"]
    output_path = PROCESSED_DIR / SOURCES[source_name]["output"]

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find input file: {input_path}\n"
            "Run chunking first."
        )

    chunks = load_json(input_path)

    # If output already exists, load it so we can resume
    if output_path.exists():
        embedded_chunks = load_json(output_path)
        print(f"Resuming from existing file: {output_path}")
    else:
        embedded_chunks = []

    embedded_by_id = {
        chunk["chunk_id"]: chunk
        for chunk in embedded_chunks
        if "embedding" in chunk
    }

    missing_chunks = [
        chunk for chunk in chunks
        if chunk["chunk_id"] not in embedded_by_id
    ]

    print("\nEmbedding chunks")
    print("----------------")
    print(f"Source: {source_name}")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Already embedded: {len(embedded_by_id)}")
    print(f"Missing chunks: {len(missing_chunks)}")
    print(f"Model: {EMBED_MODEL}")
    print(f"Expected dimension: {EMBEDDING_DIM}")
    print(f"Batch size: {EMBED_BATCH_SIZE}")
    print(f"Sleep seconds: {EMBED_SLEEP_SECONDS}")

    if not missing_chunks:
        print("\nNothing to embed. All chunks are already embedded.")
        return

    for start in range(0, len(missing_chunks), EMBED_BATCH_SIZE):
        batch = missing_chunks[start : start + EMBED_BATCH_SIZE]
        texts = [chunk["content"] for chunk in batch]

        batch_number = start // EMBED_BATCH_SIZE + 1

        print("\nEmbedding batch")
        print("---------------")
        print(f"Batch number: {batch_number}")
        print(f"Batch size: {len(batch)}")
        print(f"Progress: {len(embedded_by_id)} / {len(chunks)} already embedded")

        try:
            embeddings = embed_texts(texts)
        except Exception as e:
            print("\nEmbedding failed during this batch.")
            print("Progress has already been saved up to the previous batch.")
            print("Error:")
            print(e)
            print("\nWait a minute and rerun the same command.")
            return

        if len(embeddings) != len(batch):
            raise ValueError(
                f"Expected {len(batch)} embeddings, but got {len(embeddings)}"
            )

        for chunk, embedding in zip(batch, embeddings):
            if len(embedding) != EMBEDDING_DIM:
                raise ValueError(
                    f"Expected embedding dimension {EMBEDDING_DIM}, "
                    f"but got {len(embedding)}"
                )

            embedded_chunk = dict(chunk)
            embedded_chunk["embedding"] = embedding
            embedded_chunk["embedding_model"] = EMBED_MODEL
            embedded_chunk["embedding_dim"] = EMBEDDING_DIM

            embedded_by_id[chunk["chunk_id"]] = embedded_chunk

        # Save after every batch
        saved_chunks = [
            embedded_by_id[chunk["chunk_id"]]
            for chunk in chunks
            if chunk["chunk_id"] in embedded_by_id
        ]

        save_json(output_path, saved_chunks)

        print(f"Saved progress: {len(saved_chunks)} / {len(chunks)} chunks embedded")

        if len(saved_chunks) < len(chunks):
            print(f"Sleeping {EMBED_SLEEP_SECONDS} seconds to avoid rate limit...")
            time.sleep(EMBED_SLEEP_SECONDS)

    print("\nEmbedding complete")
    print("------------------")
    print(f"Saved to: {output_path}")
    print(f"Embedded chunks: {len(embedded_by_id)}")
    print("Done.")


if __name__ == "__main__":
    main()