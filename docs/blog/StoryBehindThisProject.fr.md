## Pourquoi nous avons cela

Cela a été discuté lors de KCD 2025 Beijing, Community Over Code 2025 China et nous avons finalement décidé de créer un agent pour gérer les travaux i18n pour la communauté.
Pour moi, je ne peux pas paralléliser dans [https://github.com/sustainable-computing-io/kepler-doc/issues/175](https://github.com/sustainable-computing-io/kepler-doc/issues/175) et la session de Community Over Code 2025.

## Dans le champ d'application et hors du champ d'application, et comment cela fonctionne

> Ne pas vouloir réinventer la roue.

- Le déclencheur n'est pas dans le champ d'application
  - laisser au manuel pour un rafraîchissement complet ou une action diff
  - API du modèle et point de terminaison du modèle
  > Les gens peuvent-ils sélectionner n'importe quel service LLM avec l'API OpenAI ?
  - point d'entrée de configuration
  > Nous devons connaître la langue par défaut et quelles sont les langues cibles, c'est dans le fichier de configuration.

--- champ d'application ---

- Phase un : à partir du fichier de configuration

> Sam en juillet 2025 : Je ne veux pas que le LLM scanne le projet, à cause du coût en tokens ou il pourrait se tromper. Demander simplement au mainteneur du document de fournir le fichier de configuration i18n, le point manuel vers le fichier de configuration sera 100% correct pour la configuration i18n.

- champ d'application des langues, comment obtenir le champ d'application des langues ?
  - = consommer les fichiers de configuration pour obtenir la liste des langues.
  - = langue par défaut - langue existante (un diff de fichier)

- sauvegarder le résultat dans le fichier spécifique

> Sam en juillet 2025 : après avoir le champ d'application de la traduction, nous devons aussi avoir des règles de nommage à partir des fichiers de configuration. (ou peut-être demander au LLM de le remarquer)

-- fin ici : obtenir une liste pour le fichier source, cible de traduction, langue.
> Sam en juillet 2025 : comme résultat de cette phase, nous devons avoir un champ d'application clair pour toutes les tâches.

-- Phase deux, une boucle for ici pour traduire

- Traduire demander de l'aide au LLM
  - comment obtenir un glossaire pour le mappage de contenu ?
  - Lacunes ? (ou juste rafraîchir tout)

> Sam en juillet 2025 : pour être spécifique.

--- hors du champ d'application ---

- créer PR laisser à l'action PR

> Ne pas vouloir réinventer la roue. car il y a déjà des actions PR pour ouvrir une PR pour un changement.