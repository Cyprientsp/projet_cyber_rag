-- Initialisation de la base de connaissance RAG
-- Joué automatiquement au premier démarrage du conteneur pgvector.

-- 1) Activer l'extension pgvector (stockage/recherche de vecteurs)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2) Table des chunks de documents + leur embedding
--    La dimension 768 correspond au modèle d'embedding "nomic-embed-text" (Ollama).
CREATE TABLE IF NOT EXISTS documents (
    id          BIGSERIAL PRIMARY KEY,
    source      TEXT        NOT NULL,          -- fichier/source d'origine
    chunk_index INT         NOT NULL,          -- position du chunk dans le doc
    content     TEXT        NOT NULL,          -- texte du chunk
    embedding   VECTOR(768) NOT NULL,          -- vecteur sémantique
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 3) Index ANN (cosine) pour accélérer la recherche de similarité
CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING hnsw (embedding vector_cosine_ops);
