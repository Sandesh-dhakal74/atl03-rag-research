# ATL03 RAG Research

This project builds a manual Retrieval-Augmented Generation pipeline for NASA ICESat-2 ATL03 documentation.

The goal is to test whether RAG can reduce hallucination when answering questions from complex satellite dataset documentation.

## Planned Stack

- Python
- Gemini embeddings
- PostgreSQL + pgvector
- Grok LLM
- No LangChain

## Research Goal

The system should answer questions using only retrieved ATL03 documentation and provide citations to the source document, section, and page.

## Current Phase

Phase 1: Understand ATL03 documentation and prepare benchmark questions.