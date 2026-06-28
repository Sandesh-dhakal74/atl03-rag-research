import logging
import time

from google import genai
from google.genai import types

from atl03_rag.config import (
    GEMINI_API_KEY,
    EMBED_MODEL,
    EMBEDDING_DIM,
    EMBED_BATCH_SIZE,
)


logger = logging.getLogger("atl03.rag.embedder")


if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")


client = genai.Client(api_key=GEMINI_API_KEY)


def _normalize_vector(vector: list[float]) -> list[float]:
    """
    Normalize vector length to 1.

    This is useful when using 768-dimensional embeddings from gemini-embedding-001.
    """
    norm = sum(value * value for value in vector) ** 0.5

    if norm == 0:
        return vector

    return [value / norm for value in vector]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed multiple texts using Gemini.

    Each text should be one RetrievalChunk content.
    Returns one embedding vector for each text.
    """
    if not texts:
        return []

    cleaned_texts = [
        text if text and text.strip() else " "
        for text in texts
    ]

    all_embeddings: list[list[float]] = []

    for i in range(0, len(cleaned_texts), EMBED_BATCH_SIZE):
        batch = cleaned_texts[i : i + EMBED_BATCH_SIZE]

        logger.info(
            "Embedding batch %s-%s of %s",
            i + 1,
            i + len(batch),
            len(cleaned_texts),
        )

        response = None

        # Retry up to 3 times if Gemini rate limit or network error happens
        for attempt in range(3):
            try:
                response = client.models.embed_content(
                    model=EMBED_MODEL,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=EMBEDDING_DIM,
                    ),
                )
                break

            except Exception as e:
                if attempt < 2:
                    wait_seconds = 30
                    logger.warning(
                        "Embedding batch failed on attempt %s. Retrying in %s seconds. Error: %s",
                        attempt + 1,
                        wait_seconds,
                        e,
                    )
                    time.sleep(wait_seconds)
                else:
                    raise

        if response is None:
            raise RuntimeError("Embedding failed and no response was returned.")

        batch_embeddings = [
            embedding.values
            for embedding in response.embeddings
        ]

        if len(batch_embeddings) != len(batch):
            raise ValueError(
                f"Expected {len(batch)} embeddings, "
                f"but got {len(batch_embeddings)}"
            )

        for embedding in batch_embeddings:
            if len(embedding) != EMBEDDING_DIM:
                raise ValueError(
                    f"Expected embedding dimension {EMBEDDING_DIM}, "
                    f"but got {len(embedding)}"
                )

            all_embeddings.append(_normalize_vector(embedding))

        # Small pause between Gemini embedding calls
        if i + EMBED_BATCH_SIZE < len(cleaned_texts):
            time.sleep(12)

    return all_embeddings


def embed_single(text: str) -> list[float]:
    """
    Embed one text string.
    """
    return embed_texts([text])[0]