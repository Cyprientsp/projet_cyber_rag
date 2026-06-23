#!/usr/bin/env python3
"""
build_report_tex.py — Génère la version LaTeX du rapport RAG (compilable sur Overleaf).

Lit rapport/demo_resultats.json (produit par demo.py) et écrit un document LaTeX
autonome rapport/rapport_rag.tex :
  - schémas TikZ (architecture + workflow) → aucune image externe à uploader ;
  - code en `listings` ; tableau prompt/réponse en `longtable`.

Compilation : déposer rapport_rag.tex sur Overleaf (moteur pdfLaTeX) et compiler,
ou en local : pdflatex rapport_rag.tex (deux passes).
"""
import os
import re
import json

HERE = os.path.dirname(__file__)
RAP_DIR = os.path.join(HERE, "..", "rapport")
JSON_IN = os.path.join(RAP_DIR, "demo_resultats.json")
TEX_OUT = os.path.join(RAP_DIR, "rapport_rag.tex")

# Emoji / symboles hors BMP (drapeaux, pictogrammes) à retirer pour pdfLaTeX.
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U0000FE00-\U0000FE0F]"
)

_LATEX_MAP = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def esc(s):
    """Échappe le texte pour LaTeX, retire les emoji, gère € et **gras** Markdown."""
    if s is None:
        return ""
    s = EMOJI.sub("", str(s))
    out = "".join(_LATEX_MAP.get(c, c) for c in s)
    out = out.replace("€", r"\texteuro{}")
    out = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", out)  # **gras** -> \textbf{}
    return out


# --------------------------------------------------------------------------- #
# Schémas TikZ (texte ASCII dans les nœuds pour une compilation sans souci)
# --------------------------------------------------------------------------- #
TIKZ_ARCHI = r"""
\begin{center}
\resizebox{0.98\textwidth}{!}{%
\begin{tikzpicture}[
  font=\small,
  cont/.style={draw=blue!55, fill=blue!4, rounded corners, align=left, inner sep=5pt},
  py/.style={draw=orange!70, fill=orange!12, rounded corners, align=left, inner sep=5pt},
  ar/.style={-{Latex[length=2.2mm]}, thick, draw=black!65},
]
  \node[cont] (ollama) {\textbf{rag-ollama} \texttt{ollama/ollama} (:11434)\\[2pt]
        \footnotesize gemma2:2b \textperiodcentered{} nomic-embed-text (768d) \textperiodcentered{} GPU};
  \node[cont, below=11mm of ollama] (db) {\textbf{rag-db} \texttt{pgvector/pgvector:pg16} (:5433)\\[2pt]
        \footnotesize table documents(embedding VECTOR(768)) \textperiodcentered{} index HNSW};
  \begin{scope}[on background layer]
    \node[draw=blue!40, fill=blue!2, rounded corners, fit=(ollama)(db), inner sep=6mm,
          label={[blue!55]above:\textbf{Docker Desktop (WSL 2)}}] (docker) {};
  \end{scope}
  \node[py, left=26mm of docker] (py) {\textbf{Scripts Python}\\[2pt]
        \footnotesize venv 3.14\\ \footnotesize ingest.py \textperiodcentered{} query.py};
  \begin{scope}[on background layer]
    \node[draw=black!55, rounded corners, fit=(py)(docker), inner sep=8mm,
          label={above:\textbf{Machine hote --- Windows 11}}] (host) {};
  \end{scope}
  \draw[ar] (py.east|-ollama.west) -- node[above,font=\scriptsize]{REST :11434} (ollama.west);
  \draw[ar] (py.east|-db.west) -- node[above,font=\scriptsize]{SQL :5433} (db.west);
\end{tikzpicture}%
}
\end{center}
"""

TIKZ_FLOW = r"""
\begin{center}
\resizebox{0.98\textwidth}{!}{%
\begin{tikzpicture}[
  font=\small, node distance=7mm,
  n/.style={draw=blue!55, fill=blue!4, rounded corners, align=center,
            minimum height=11mm, inner sep=3pt, text width=26mm},
  g/.style={n, draw=orange!70, fill=orange!12},
  ar/.style={-{Latex[length=2.2mm]}, thick, draw=black!65},
  lane/.style={font=\bfseries\footnotesize, anchor=west},
]
  % Lane A : ingestion
  \node[n] (d)  {Documents\\ \texttt{data/*.md}};
  \node[n, right=of d]  (ch) {Decoupage\\ chunks 600/100};
  \node[g, right=of ch] (em) {Embedding\\ nomic-embed-text};
  \node[n, right=of em] (ins){INSERT\\ pgvector};
  \draw[ar] (d)--(ch); \draw[ar] (ch)--(em); \draw[ar] (em)--(ins);
  \node[lane] at ([yshift=8mm]d.north west) {A. Ingestion (ingest.py) --- hors ligne};
  % Lane B : interrogation
  \node[n, below=18mm of d] (q)  {Question\\ utilisateur};
  \node[g, right=of q]  (qe) {Embedding\\ de la question};
  \node[n, right=of qe] (kn) {Recherche KNN\\ pgvector TOP\_K=4};
  \node[n, right=of kn] (pr) {Prompt enrichi\\ contexte + question};
  \draw[ar] (q)--(qe); \draw[ar] (qe)--(kn); \draw[ar] (kn)--(pr);
  \node[g, below=11mm of kn] (gen) {Generation LLM\\ gemma2:2b};
  \node[n, right=of gen] (rep) {Reponse\\ contextualisee};
  \draw[ar] (pr.south) |- (gen.east);
  \draw[ar] (gen)--(rep);
  \node[lane] at ([yshift=8mm]q.north west) {B. Interrogation (query.py) --- a chaque question};
\end{tikzpicture}%
}
\end{center}
"""

# --------------------------------------------------------------------------- #
# Extraits de code (commentaires ASCII pour listings + pdfLaTeX)
# --------------------------------------------------------------------------- #
INGEST_CODE = r"""def chunk_text(text, size, overlap):
    text = text.strip()
    if not text:
        return []
    chunks, start, n = [], 0, len(text)
    while start < n:
        end = min(start + size, n)
        if end < n:                       # coupe de preference sur un saut de ligne
            window = text.rfind("\n", start + size // 2, end)
            if window > start:
                end = window
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:                      # tout le texte consomme -> fin
            break
        start = max(end - overlap, start + 1)   # progression stricte

def embed(text):                          # embedding via Ollama (nomic-embed-text)
    r = requests.post(f"{OLLAMA_URL}/api/embeddings",
                      json={"model": EMBED_MODEL, "prompt": text}, timeout=120)
    return r.json()["embedding"]"""

QUERY_CODE = r'''def retrieve(question, k=TOP_K):
    qvec = embed(question)                        # 1) vectorise la question
    cur.execute("""
        SELECT source, content, 1 - (embedding <=> %s::vector) AS score
        FROM documents
        ORDER BY embedding <=> %s::vector          -- distance cosine (pgvector)
        LIMIT %s;""", (qvec, qvec, k))            # 2) TOP_K chunks les plus proches
    return cur.fetchall()

def answer(question):
    hits = retrieve(question)
    context = "\n\n".join(f"[Source: {s}]\n{c}" for s, c, _ in hits)
    prompt = f"{SYSTEM_PROMPT}\n\n### CONTEXTE\n{context}\n\n### QUESTION\n{question}"
    return generate(prompt)                        # 3) generation gemma2:2b (Ollama)'''

INSTALL_CODE = r"""# 1) Demarrer la base vectorielle et le moteur LLM
docker compose up -d
docker compose ps                      # rag-db "healthy", rag-ollama "up"

# 2) Telecharger les modeles dans Ollama
docker exec rag-ollama ollama pull nomic-embed-text    # embeddings (768 dim.)
docker exec rag-ollama ollama pull gemma2:2b           # generation

# 3) Environnement Python
python -m venv .venv
.venv\Scripts\activate                 # Windows
pip install -r projet_cyber_rag/requirements.txt

# 4) Ingestion puis interrogation
python scripts/ingest.py --reset
python scripts/query.py "Quelle est la garantie de l'onduleur HX-Solar 5000 ?"
python scripts/query.py --no-rag "..." # comparaison : LLM seul, sans la base
python scripts/demo.py                 # batterie de demonstration complete"""


def qa_rows(records):
    rows = []
    for i, r in enumerate(records, 1):
        n_src = len([s for s in r["sources"].split(",") if s.strip()])
        rep = r"\textbf{Avec RAG :} " + esc(r["rag_answer"])
        if r.get("compare") and r.get("no_rag_answer") is not None:
            rep += r"\newline\newline \textbf{Sans RAG :} " + esc(r["no_rag_answer"])
        src = f"{n_src} source(s)\\newline score {r['top_score']:.3f}"
        rows.append(
            f"{i} & {esc(r['question'])} & {src} & {rep} \\\\ \\hline"
        )
    return "\n".join(rows)


PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{lmodern}
\usepackage[a4paper,margin=2cm]{geometry}
\usepackage[table]{xcolor}
\usepackage{textcomp}
\usepackage{graphicx}
\usepackage{array}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, fit, backgrounds}
\usepackage{titlesec}
\usepackage[hidelinks]{hyperref}

\definecolor{titleblue}{HTML}{15314B}
\definecolor{accent}{HTML}{1D6FB8}
\definecolor{codebg}{HTML}{F4F6FB}
\definecolor{codecmt}{HTML}{55607A}
\definecolor{codekw}{HTML}{1D6FB8}
\definecolor{codestr}{HTML}{1A7F4B}

\titleformat{\section}{\Large\bfseries\color{titleblue}}{\thesection}{0.6em}{}
\titleformat{\subsection}{\large\bfseries\color{accent}}{\thesubsection}{0.6em}{}

\lstset{
  basicstyle=\ttfamily\footnotesize,
  backgroundcolor=\color{codebg},
  commentstyle=\color{codecmt}\itshape,
  keywordstyle=\color{codekw}\bfseries,
  stringstyle=\color{codestr},
  breaklines=true, breakatwhitespace=false,
  frame=single, framerule=0pt, framesep=6pt,
  xleftmargin=6pt, xrightmargin=6pt,
  showstringspaces=false, columns=fullflexible, keepspaces=true,
  literate={é}{{\'e}}1 {è}{{\`e}}1 {à}{{\`a}}1 {â}{{\^a}}1 {ê}{{\^e}}1
           {î}{{\^i}}1 {ô}{{\^o}}1 {û}{{\^u}}1 {ç}{{\c c}}1 {É}{{\'E}}1,
}

% Neutralise la ponctuation "active" de babel-french (:, ;, !, ?) : on saisit
% nous-mêmes les espaces. Indispensable pour que TikZ (label={above:...}) et
% listings compilent sans conflit de catcode.
\frenchsetup{AutoSpacePunctuation=false}
"""


def main():
    with open(JSON_IN, encoding="utf-8") as f:
        records = json.load(f)
    n_compare = sum(1 for r in records if r.get("compare"))
    rows = qa_rows(records)

    doc = PREAMBLE + r"""
\begin{document}

\begin{center}
  {\LARGE\bfseries\color{titleblue} Construire et manipuler un environnement IA avec RAG}\\[4pt]
  {\large Retrieval-Augmented Generation --- base vectorielle locale + LLM local}\\[6pt]
  {\small PostgreSQL/pgvector \textperiodcentered{} Ollama (gemma2:2b, nomic-embed-text)
   \textperiodcentered{} Docker \textperiodcentered{} Python 3.14}
\end{center}
\vspace{4pt}\hrule\vspace{10pt}

\section{Objectif}
Le but du projet est de construire, de bout en bout, un environnement d'intelligence
artificielle exploitant le principe du \textbf{RAG (Retrieval-Augmented Generation)} :
enrichir les reponses d'un grand modele de langage (LLM) avec une base de connaissance
personnalisee, afin qu'il reponde sur des donnees qu'il n'a jamais vues lors de son
entrainement. La demonstration s'appuie sur une entreprise \textbf{fictive}, HelioniX
SAS (onduleurs photovoltaiques), dont les documents internes servent de base de
connaissance.

\section{Environnement construit}
L'environnement repose sur la \textbf{virtualisation applicative (conteneurs Docker)}
plutot que sur une machine virtuelle complete : chaque outil tourne dans un conteneur
isole, orchestre par \texttt{docker compose}. Ce choix reduit l'empreinte et rend
l'environnement reproductible en une commande.

\begin{center}
\renewcommand{\arraystretch}{1.3}
\begin{tabular}{>{\raggedright\arraybackslash}p{2.6cm} >{\raggedright\arraybackslash}p{3.6cm} >{\raggedright\arraybackslash}p{8.4cm}}
\toprule
\textbf{Couche} & \textbf{Element} & \textbf{Detail} \\
\midrule
Machine hote & Windows 11 Pro (x86-64) & Execute Docker Desktop (backend WSL 2) et l'interpreteur Python \\
Virtualisation & Docker Desktop & Conteneurisation, orchestration via \texttt{docker-compose.yml} \\
Base vectorielle & conteneur \texttt{rag-db} & image \texttt{pgvector/pgvector:pg16} --- PostgreSQL 16 + extension \texttt{vector}, port \texttt{localhost:5433} \\
Moteur LLM & conteneur \texttt{rag-ollama} & image \texttt{ollama/ollama} --- embedding + generation, port \texttt{localhost:11434} \\
Modele d'embedding & \texttt{nomic-embed-text} & Texte vers vecteur de \textbf{768} dimensions \\
Modele de generation & \texttt{gemma2:2b} (Google) & LLM leger (environ 1,6 Go) adapte a une execution locale (GPU/CPU) \\
Scripts & Python 3.14 (venv) & \texttt{psycopg2-binary} (PostgreSQL) + \texttt{requests} (API Ollama) \\
\bottomrule
\end{tabular}
\end{center}

\subsection{Schema d'architecture}
""" + TIKZ_ARCHI + r"""
\begin{center}\footnotesize\itshape Figure 1 --- Architecture : scripts Python sur l'hote,
conteneurs Ollama et PostgreSQL/pgvector orchestres par Docker. Les scripts dialoguent
avec Ollama en REST (port 11434) et avec PostgreSQL en SQL (port 5433).\end{center}

\section{Workflow des traitements}
Le pipeline se decompose en deux phases : une phase d'\textbf{ingestion} (hors ligne,
executee une fois pour peupler la base) et une phase d'\textbf{interrogation} (rejouee a
chaque question de l'utilisateur).
""" + TIKZ_FLOW + r"""
\begin{center}\footnotesize\itshape Figure 2 --- Workflow : (A) ingestion des documents,
(B) interrogation contextualisee du LLM par recherche de similarite vectorielle.\end{center}

\newpage
\section{Procedure d'installation}
L'ensemble de l'environnement se deploie depuis le dossier du projet.
\begin{lstlisting}[language=bash]
""" + INSTALL_CODE + r"""
\end{lstlisting}
Au premier demarrage, le script \texttt{db/init.sql} est joue automatiquement : il active
l'extension \texttt{vector}, cree la table \texttt{documents} et son index HNSW.

\section{Scripts developpes}
\subsection{Ingestion : \texttt{ingest.py}}
Lit les documents, les decoupe en fragments (\textit{chunks}) d'environ 600 caracteres avec
100 de recouvrement, calcule l'embedding de chaque fragment via Ollama et l'insere dans
pgvector.
\begin{lstlisting}[language=Python]
""" + INGEST_CODE + r"""
\end{lstlisting}

\subsection{Interrogation : \texttt{query.py}}
Vectorise la question, recupere les \texttt{TOP\_K=4} fragments les plus proches (distance
cosine via l'operateur \texttt{<=>} de pgvector), construit un prompt contraint au
contexte puis genere la reponse avec \texttt{gemma2:2b}.
\begin{lstlisting}[language=Python]
""" + QUERY_CODE + r"""
\end{lstlisting}

\newpage
\section{Demonstration : couples prompt / reponse}
Le tableau ci-dessous met en evidence la \textbf{bonne prise en compte de la base de
connaissance} : les reponses \guillemotleft{} Avec RAG \guillemotright{} citent des faits
precis issus des documents
HelioniX. Pour """ + str(n_compare) + r""" questions, la reponse \guillemotleft{} Sans RAG \guillemotright{} (LLM seul) est
fournie en regard : le modele est alors incapable de repondre correctement, ce qui
demontre l'apport du RAG. La derniere question porte volontairement sur un sujet
\textbf{hors base} : le systeme repond qu'il ne dispose pas de l'information, prouvant
qu'il ne brode pas.

\renewcommand{\arraystretch}{1.25}
\begin{longtable}{|>{\raggedright\arraybackslash}p{0.4cm}
                  |>{\raggedright\arraybackslash}p{3.6cm}
                  |>{\raggedright\arraybackslash}p{2.2cm}
                  |>{\raggedright\arraybackslash}p{7.6cm}|}
\hline
\rowcolor{titleblue!12}
\textbf{\#} & \textbf{Prompt} & \textbf{Chunks} & \textbf{Reponse} \\ \hline
\endfirsthead
\hline
\rowcolor{titleblue!12}
\textbf{\#} & \textbf{Prompt} & \textbf{Chunks} & \textbf{Reponse} \\ \hline
\endhead
""" + rows + r"""
\end{longtable}

\section{Conclusion}
L'environnement repond aux trois objectifs du projet : \textbf{(1)} construction d'une
plateforme IA locale conteneurisee (Ollama + PostgreSQL/pgvector), \textbf{(2)} ingestion
d'un jeu de documents dans une base de connaissance vectorielle, et \textbf{(3)}
interrogation d'un LLM enrichi par cette base. La comparaison \guillemotleft{} avec / sans RAG \guillemotright{}
confirme que la base de connaissance est effectivement mobilisee et qu'elle ameliore
nettement la pertinence des reponses sur des donnees metier privees.

\end{document}
"""

    os.makedirs(RAP_DIR, exist_ok=True)
    with open(TEX_OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"Rapport LaTeX ecrit dans : {TEX_OUT}")


if __name__ == "__main__":
    main()
