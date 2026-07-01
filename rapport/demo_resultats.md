# Résultats de démonstration RAG

_Généré automatiquement par `scripts/demo.py`._


## Question 1

**Prompt :** Quelle est la garantie constructeur de l'onduleur HX-Solar 5000 ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.812)

**Réponse AVEC RAG** _(temps : 61.8 s)_ **:**

> 12 ans

**Réponse SANS RAG (LLM seul)** _(temps : 0.7 s)_ **:**

> La garantie constructeur de l'onduleur HX-Solar 5000 est de **10 ans** sur le matériel et **5 ans** sur les composants électroniques.


## Question 2

**Prompt :** Que signifie le code d'erreur E-204 sur le HX-Solar 5000 ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.787)

**Réponse AVEC RAG** _(temps : 0.6 s)_ **:**

> Le code d'erreur E-204 signale une surchauffe du transformateur.

**Réponse SANS RAG (LLM seul)** _(temps : 0.7 s)_ **:**

> Le code d'erreur E-204 sur le HX-Solar 5000 indique un **défaut de communication avec la batterie**.


## Question 3

**Prompt :** Combien de jours de télétravail par semaine sont autorisés chez HelioniX, et quel jour est obligatoirement travaillé au bureau ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.803)

**Réponse AVEC RAG** _(temps : 9.3 s)_ **:**

> HelioniX autorise jusqu'à 3 jours de télétravail par semaine pour les postes éligibles. Le mardi est un jour de présence obligatoire au bureau pour toutes les équipes (réunion hebdomadaire « SunSync »).

**Réponse SANS RAG (LLM seul)** _(temps : 0.6 s)_ **:**

> HelioniX n'a pas fixé de nombre de jours de télétravail maximum par semaine.  Un jour de travail au bureau est obligatoire chaque semaine.


## Question 4

**Prompt :** Quel est le rendement européen du HX-Solar 5000 et sur quel port TCP fonctionne le protocole SunLink v3 ?

**Chunks récupérés :** politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.786)

**Réponse AVEC RAG** _(temps : 0.6 s)_ **:**

> Le rendement européen du HX-Solar 5000 est de 97,8 %. Le protocole SunLink v3 fonctionne sur le port TCP 8770.

**Réponse SANS RAG (LLM seul)** _(temps : 0.7 s)_ **:**

> Le rendement européen du HX-Solar 5000 n'est pas spécifié publiquement.  Le protocole SunLink v3 fonctionne sur **port TCP 80**.


## Question 5

**Prompt :** Qui est la présidente de HelioniX et quel était le chiffre d'affaires 2024 ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.757)

**Réponse AVEC RAG** _(temps : 0.7 s)_ **:**

> Amélie Rouanet est la présidente de HelioniX. Le chiffre d'affaires 2024 était de 38,6 millions d'euros.

**Réponse SANS RAG (LLM seul)** _(temps : 1.0 s)_ **:**

> Je n'ai pas accès à des informations en temps réel, y compris les données financières spécifiques comme le chiffre d'affaires d'une entreprise.  Pour obtenir ces informations, je vous recommande de consulter le site web de HelioniX ou de contacter l'entreprise directement.


## Question 6

**Prompt :** Quelle est la valeur faciale du ticket restaurant et la prise en charge employeur chez HelioniX ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.778)

**Réponse AVEC RAG** _(temps : 0.7 s)_ **:**

> La valeur faciale du ticket restaurant est de 11 € et la prise en charge employeur est de 6,60 €.

**Réponse SANS RAG (LLM seul)** _(temps : 1.5 s)_ **:**

> Je n'ai pas accès aux informations spécifiques sur les politiques d'HelioniX, y compris la valeur faciale du ticket restaurant et la prise en charge employeur. 

**Pour obtenir ces informations, je vous recommande de consulter:**

* **Le site web d'HelioniX :**  Ils pourraient avoir une section dédiée aux conditions de travail ou à l'information des employés.
* **Contacter directement HelioniX :**  Vous pouvez les contacter par email ou téléphone pour demander des informations précises.


## Question 7

**Prompt :** Quelle est la capitale de l'Australie ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.597)

**Réponse AVEC RAG** _(temps : 7.1 s)_ **:**

> Je ne dispose pas de cette information dans ma base de connaissance.

**Réponse SANS RAG (LLM seul)** _(temps : 0.5 s)_ **:**

> Canberra 🇦🇺
