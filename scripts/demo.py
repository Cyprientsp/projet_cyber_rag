#!/usr/bin/env python3
"""
demo.py — Batterie de démonstration du pipeline RAG.

Pour chaque question de la liste DEMO_QUESTIONS :
  - récupère les chunks pertinents (pgvector) et la réponse du LLM AVEC RAG ;
  - pour les questions marquées `compare=True`, interroge aussi le LLM SANS RAG
    afin de mettre en évidence l'apport de la base de connaissance.

Les résultats sont affichés et écrits dans rapport/demo_resultats.md
(tableau prompt/réponse exploitable directement dans le rapport).

Usage :
    python scripts/demo.py
"""
import os
import sys
import json
import time

# Console Windows : force UTF-8 pour éviter les UnicodeEncodeError (cp1252).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from query import retrieve, generate, SYSTEM_PROMPT, answer  # noqa: F401

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "rapport")
OUT_FILE = os.path.join(OUT_DIR, "demo_resultats.md")
OUT_JSON = os.path.join(OUT_DIR, "demo_resultats.json")

# (question, comparer_sans_rag)
DEMO_QUESTIONS = [
    ("Quelle est la garantie constructeur de l'onduleur HX-Solar 5000 ?", True),
    ("Que signifie le code d'erreur E-204 sur le HX-Solar 5000 ?", True),
    ("Combien de jours de télétravail par semaine sont autorisés chez HelioniX, "
     "et quel jour est obligatoirement travaillé au bureau ?", True),
    ("Quel est le rendement européen du HX-Solar 5000 et sur quel port TCP "
     "fonctionne le protocole SunLink v3 ?", True),
    ("Qui est la présidente de HelioniX et quel était le chiffre d'affaires 2024 ?", True),
    ("Quelle est la valeur faciale du ticket restaurant et la prise en charge "
     "employeur chez HelioniX ?", True),
    ("Quelle est la capitale de l'Australie ?", True),  # hors base → doit refuser
]


def run_rag(question: str):
    t0 = time.time()
    hits = retrieve(question)
    context = "\n\n".join(f"[Source: {s}]\n{c}" for s, c, _ in hits)
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"### CONTEXTE\n{context}\n\n"
        f"### QUESTION\n{question}\n\n### RÉPONSE\n"
    )
    rep = generate(prompt)
    dt = time.time() - t0
    return hits, rep, dt


def run_no_rag(question: str):
    t0 = time.time()
    prompt = f"Réponds en français de façon concise.\n\nQUESTION : {question}\n\nRÉPONSE :"
    rep = generate(prompt)
    dt = time.time() - t0
    return rep, dt


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    lines = ["# Résultats de démonstration RAG\n",
             "_Généré automatiquement par `scripts/demo.py`._\n"]
    records = []

    for idx, (q, compare) in enumerate(DEMO_QUESTIONS, 1):
        print("=" * 78)
        print(f"[{idx}/{len(DEMO_QUESTIONS)}] {q}")
        hits, rag_rep, dt = run_rag(q)
        sources = ", ".join(sorted({s for s, _, _ in hits}))
        top_score = max((sc for _, _, sc in hits), default=0.0)
        print(f"  sources={sources}  top_score={top_score:.3f}  ({dt:.1f}s)")
        print(f"  RAG  -> {rag_rep}")

        lines.append(f"\n## Question {idx}\n")
        lines.append(f"**Prompt :** {q}\n")
        lines.append(f"**Chunks récupérés :** {sources} "
                     f"(meilleur score cosine = {top_score:.3f})\n")
        lines.append(f"**Réponse AVEC RAG** _(temps : {dt:.1f} s)_ **:**\n\n> {rag_rep}\n")

        rec = {"question": q, "sources": sources, "top_score": round(top_score, 3),
               "rag_answer": rag_rep, "rag_time_s": round(dt, 1),
               "no_rag_answer": None, "no_rag_time_s": None, "compare": compare}
        if compare:
            norag_rep, dt2 = run_no_rag(q)
            print(f"  NO-RAG -> {norag_rep}  ({dt2:.1f}s)")
            lines.append(f"**Réponse SANS RAG (LLM seul)** _(temps : {dt2:.1f} s)_ **:**\n\n> {norag_rep}\n")
            rec["no_rag_answer"] = norag_rep
            rec["no_rag_time_s"] = round(dt2, 1)
        records.append(rec)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print("=" * 78)
    print(f"Résultats écrits dans : {OUT_FILE}")
    print(f"JSON écrit dans       : {OUT_JSON}")


if __name__ == "__main__":
    main()
