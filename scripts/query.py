#!/usr/bin/env python3
"""
query.py — Interrogation du LLM avec contextualisation RAG.

Étapes :
  1. Embedding de la question (Ollama nomic-embed-text)
  2. Recherche des TOP_K chunks les plus proches (pgvector, distance cosine)
  3. Construction d'un prompt enrichi (contexte + question)
  4. Génération de la réponse par le LLM local (Ollama gemma2:2b)

Usage :
    python scripts/query.py "Quelle est la garantie de l'onduleur HX-Solar 5000 ?"
    python scripts/query.py --no-rag "..."   # interroge le LLM SANS la base (comparaison)
"""
import sys
import requests
import psycopg2

from config import (DB_CONFIG, OLLAMA_URL, EMBED_MODEL, GEN_MODEL, TOP_K)

SYSTEM_PROMPT = (
    "Tu es un assistant qui répond UNIQUEMENT à partir du CONTEXTE fourni. "
    "Si l'information ne figure pas dans le contexte, réponds exactement : "
    "\"Je ne dispose pas de cette information dans ma base de connaissance.\" "
    "Réponds en français, de façon concise."
)


def embed(text: str) -> list[float]:
    resp = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def retrieve(question: str, k: int = TOP_K):
    """Renvoie les k chunks les plus proches sémantiquement de la question."""
    qvec = embed(question)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    # 1 - (embedding <=> q) = similarité cosine (1 = identique)
    cur.execute(
        """
        SELECT source, content, 1 - (embedding <=> %s::vector) AS score
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (qvec, qvec, k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def generate(prompt: str) -> str:
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": GEN_MODEL, "prompt": prompt, "stream": False,
              "options": {"temperature": 0.1}},
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["response"].strip()


def answer(question: str, use_rag: bool = True, verbose: bool = True) -> str:
    if use_rag:
        hits = retrieve(question)
        context = "\n\n".join(f"[Source: {s}]\n{c}" for s, c, _ in hits)
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"### CONTEXTE\n{context}\n\n"
            f"### QUESTION\n{question}\n\n### RÉPONSE\n"
        )
        if verbose:
            print("=" * 70)
            print(f"QUESTION : {question}")
            print("-" * 70)
            print("CHUNKS RÉCUPÉRÉS (RAG) :")
            for s, c, score in hits:
                preview = c.replace("\n", " ")[:90]
                print(f"  • [{score:.3f}] {s} :: {preview}...")
            print("-" * 70)
    else:
        prompt = (f"Réponds en français de façon concise.\n\nQUESTION : {question}\n\nRÉPONSE :")
        if verbose:
            print("=" * 70)
            print(f"QUESTION (SANS RAG) : {question}")
            print("-" * 70)

    rep = generate(prompt)
    if verbose:
        print(f"RÉPONSE : {rep}")
        print("=" * 70 + "\n")
    return rep


def main():
    args = sys.argv[1:]
    use_rag = "--no-rag" not in args
    args = [a for a in args if a != "--no-rag"]
    if not args:
        print('Usage: python scripts/query.py [--no-rag] "votre question"')
        sys.exit(1)
    answer(" ".join(args), use_rag=use_rag)


if __name__ == "__main__":
    main()
