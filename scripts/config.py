"""Configuration partagée pour le pipeline RAG (ingestion + interrogation)."""
import os

# --- Connexion PostgreSQL/pgvector ---
DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5433")),
    "dbname": os.getenv("PGDATABASE", "ragdb"),
    "user": os.getenv("PGUSER", "raguser"),
    "password": os.getenv("PGPASSWORD", "ragpass"),
}

# --- Ollama (LLM local) ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")  # dimension 768
GEN_MODEL = os.getenv("GEN_MODEL", "gemma2:2b")

# --- Paramètres RAG ---
CHUNK_SIZE = 600       # taille cible d'un chunk (caractères)
CHUNK_OVERLAP = 100    # recouvrement entre chunks (continuité sémantique)
TOP_K = 4              # nombre de chunks récupérés par requête
