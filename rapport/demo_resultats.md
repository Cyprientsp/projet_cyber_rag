# Résultats de démonstration RAG

_Généré automatiquement par `scripts/demo.py`._


## Question 1

**Prompt :** Quelle est la garantie constructeur de l'onduleur HX-Solar 5000 ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.812)

**Réponse AVEC RAG :**

> 12 ans

**Réponse SANS RAG (LLM seul) :**

> La garantie constructeur de l'onduleur HX-Solar 5000 est de **10 ans** sur le matériel et **5 ans** sur les composants électroniques.


## Question 2

**Prompt :** Que signifie le code d'erreur E-204 sur le HX-Solar 5000 ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.787)

**Réponse AVEC RAG :**

> Le code d'erreur E-204 signale une surchauffe du transformateur : il faut vérifier la ventilation et contacter le SAV HelioniX si le défaut persiste.

**Réponse SANS RAG (LLM seul) :**

> Le code d'erreur E-204 sur le HX-Solar 5000 indique un **défaut de communication avec la centrale solaire**.


## Question 3

**Prompt :** Combien de jours de télétravail par semaine sont autorisés chez HelioniX, et quel jour est obligatoirement travaillé au bureau ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.803)

**Réponse AVEC RAG :**

> HelioniX autorise jusqu'à 3 jours de télétravail par semaine pour les postes éligibles. Le mardi est un jour de présence obligatoire au bureau pour toutes les équipes (réunion hebdomadaire « SunSync »).


## Question 4

**Prompt :** Quel est le rendement européen du HX-Solar 5000 et sur quel port TCP fonctionne le protocole SunLink v3 ?

**Chunks récupérés :** politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.786)

**Réponse AVEC RAG :**

> Le rendement européen du HX-Solar 5000 est de 97,8 %. Le protocole SunLink v3 fonctionne sur le port TCP 8770.


## Question 5

**Prompt :** Qui est la présidente de HelioniX et quel était le chiffre d'affaires 2024 ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.757)

**Réponse AVEC RAG :**

> Amélie Rouanet est la présidente de HelioniX. Le chiffre d'affaires 2024 était de 38,6 millions d'euros.


## Question 6

**Prompt :** Quelle est la valeur faciale du ticket restaurant et la prise en charge employeur chez HelioniX ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.778)

**Réponse AVEC RAG :**

> La valeur faciale du ticket restaurant est de 11 € et la prise en charge employeur est de 6,60 €.


## Question 7

**Prompt :** Quelle est la capitale de l'Australie ?

**Chunks récupérés :** entreprise_helionix.md, politique_rh_helionix.md, produit_hx_solar_5000.md (meilleur score cosine = 0.597)

**Réponse AVEC RAG :**

> Je ne dispose pas de cette information dans ma base de connaissance.

**Réponse SANS RAG (LLM seul) :**

> Canberra 🇦🇺
