#!/usr/bin/env python3
"""
ingest.py — Ingestion de documents dans la base de connaissance RAG.

Étapes :
  1. Lecture des fichiers texte/markdown du dossier data/
  2. Découpage en chunks (avec recouvrement)
  3. Calcul de l'embedding de chaque chunk via Ollama (nomic-embed-text)
  4. Stockage (texte + vecteur) dans PostgreSQL/pgvector

Usage :
    python scripts/ingest.py [dossier_data]
    python scripts/ingest.py --reset      # vide la table avant ingestion
"""
import os
import sys
import glob
import requests
import psycopg2

from config import DB_CONFIG, OLLAMA_URL, EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Découpe le texte en morceaux de ~size caractères avec recouvrement.
    On coupe de préférence sur un saut de paragraphe/ligne proche pour rester lisible."""
    text = text.strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        # essaie de couper sur une fin de paragraphe/ligne dans la zone [start+size/2, end]
        if end < len(text):
            window = text.rfind("\n", start + size // 2, end)
            if window != -1:
                end = window
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, end) if end <= start else end - overlap
        if start < 0:
            start = end
    return chunks


def embed(text: str) -> list[float]:
    """Appelle Ollama pour obtenir l'embedding d'un texte."""
    resp = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def main():
    args = sys.argv[1:]
    reset = "--reset" in args
    args = [a for a in args if a != "--reset"]
    data_dir = args[0] if args else DATA_DIR

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    if reset:
        cur.execute("TRUNCATE documents RESTART IDENTITY;")
        conn.commit()
        print("[reset] Table 'documents' vidée.")

    files = sorted(glob.glob(os.path.join(data_dir, "*.md")) +
                   glob.glob(os.path.join(data_dir, "*.txt")))
    if not files:
        print(f"Aucun fichier .md/.txt trouvé dans {data_dir}")
        return

    total_chunks = 0
    for path in files:
        source = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for i, chunk in enumerate(chunks):
            vec = embed(chunk)
            cur.execute(
                "INSERT INTO documents (source, chunk_index, content, embedding) "
                "VALUES (%s, %s, %s, %s)",
                (source, i, chunk, vec),
            )
            total_chunks += 1
        conn.commit()
        print(f"[ok] {source}: {len(chunks)} chunks ingérés")

    cur.execute("SELECT count(*) FROM documents;")
    print(f"\nIngestion terminée. {total_chunks} chunks ajoutés. "
          f"Total en base : {cur.fetchone()[0]}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
