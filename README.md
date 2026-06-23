# Projet RAG — Environnement IA local (Ollama + PostgreSQL/pgvector)

Implémentation complète d'un pipeline **RAG (Retrieval-Augmented Generation)** local :
une base de connaissance vectorielle (PostgreSQL + pgvector) alimente un LLM local
(Ollama / `gemma2:2b`) pour qu'il réponde sur des données métier privées qu'il n'a
jamais vues à l'entraînement.

La base de connaissance de démonstration porte sur une entreprise **fictive**,
*HelioniX SAS* (onduleurs photovoltaïques) — voir `data/`.

## Architecture

```
Machine hôte (Windows 11)
├── Scripts Python (venv 3.14)          ingest.py · query.py · demo.py
└── Docker Desktop (WSL 2)
    ├── rag-ollama   ollama/ollama        :11434   gemma2:2b + nomic-embed-text  [GPU]
    └── rag-db       pgvector/pgvector:pg16 :5433   table documents(embedding VECTOR(768))
```

## Prérequis

- Docker Desktop (backend WSL 2)
- Python 3.10+ (testé en 3.14)
- *(optionnel mais recommandé)* GPU NVIDIA + pilote récent → accélère fortement
  l'inférence. Le passthrough GPU est activé dans `docker-compose.yml`. **Sans GPU**,
  commenter le bloc `deploy:` du service `ollama` (l'inférence se fera sur CPU,
  nettement plus lente).

## Mise en route

```bash
# 1) Démarrer la base vectorielle et le moteur LLM
docker compose up -d
docker compose ps                       # rag-db "healthy", rag-ollama "up"

# 2) Télécharger les modèles dans Ollama
docker exec rag-ollama ollama pull nomic-embed-text     # embeddings (768 dim.)
docker exec rag-ollama ollama pull gemma2:2b            # génération

# 3) Environnement Python
python -m venv .venv
.venv\Scripts\activate                  # Windows  (Linux/macOS : source .venv/bin/activate)
pip install -r projet_cyber_rag/requirements.txt

# 4) Ingestion de la base de connaissance
python scripts/ingest.py --reset

# 5) Interrogation
python scripts/query.py "Quelle est la garantie de l'onduleur HX-Solar 5000 ?"
python scripts/query.py --no-rag "..."  # comparaison : LLM seul, sans la base
```

## Scripts

| Fichier | Rôle |
|---|---|
| `scripts/config.py` | Configuration partagée (connexion DB, URLs Ollama, paramètres RAG). |
| `scripts/ingest.py` | Lit `data/*.md`, découpe en chunks, calcule les embeddings, insère dans pgvector. |
| `scripts/query.py` | Vectorise la question, recherche les TOP_K chunks (cosine), génère la réponse. |
| `scripts/demo.py` | Batterie de questions de démonstration → `rapport/demo_resultats.{md,json}`. |
| `scripts/build_report.py` | Assemble le rapport `rapport/rapport_rag.html` à partir des résultats. |

## Générer le rapport PDF

```bash
python scripts/demo.py                   # exécute la démo, produit les résultats JSON/MD
python scripts/build_report.py           # assemble rapport/rapport_rag.html

# Conversion HTML -> PDF (Edge headless, Windows)
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=rapport/rapport_rag.pdf rapport/rapport_rag.html
```

## Paramètres RAG (`scripts/config.py`)

| Paramètre | Valeur | Description |
|---|---|---|
| `CHUNK_SIZE` | 600 | Taille cible d'un chunk (caractères). |
| `CHUNK_OVERLAP` | 100 | Recouvrement entre chunks (continuité sémantique). |
| `TOP_K` | 4 | Nombre de chunks récupérés par requête. |
| `EMBED_MODEL` | `nomic-embed-text` | Modèle d'embedding (vecteurs 768 dim.). |
| `GEN_MODEL` | `gemma2:2b` | Modèle de génération. |

Toutes ces valeurs sont surchargeables par variables d'environnement
(`PGHOST`, `OLLAMA_URL`, `GEN_MODEL`, …).
