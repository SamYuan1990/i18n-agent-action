# 📋 Paramètres d'Entrée

Toutes les méthodes d'exécution prennent en charge les paramètres unifiés suivants :

| Paramètre d'Entrée | Obligatoire | Valeur par Défaut | Description |
|-----------------|----------|---------------|-------------|
| `apikey`        | Oui      | -             | Clé API pour le service LLM |
| `base_url`      | Non       | DeepSeek             | URL du point de terminaison du service LLM |
| `model`         | Non       | DeepSeek v3            | Nom/identifiant du modèle pour le service LLM |
| `RESERVED_WORD` | Oui      | -             | Termes/phrases réservés à exclure de la traduction |
| `DOCS_FOLDER`   | Oui      | -             | Chemin vers votre dossier de documentation |
| `CONFIG_FILE`   | Oui      | -             | Fichier de configuration pour les paramètres i18n du projet |
| `FILE_LIST`     | Non       | -             | Liste spécifique de fichiers à traiter (facultatif) |
| `workspace`     | Oui      | -             | Chemin vers votre espace de travail du dépôt de code |
| `target_language` | Non     | `'zh'`        | Code de langue cible pour la traduction (par exemple, `'zh'` pour le chinois) |
| `max_files`     | Non       | `'20'`        | Nombre maximum de fichiers à traiter |
| `dryRun`        | Non       | false             | Activer le mode simulation (simule l'exécution sans apporter de modifications) |
| `usecache`      | Non       | true             | Activer le cache pour les requêtes LLM |
| `disclaimers`   | Non       | true             | Afficher les avertissements à la fin de la traduction |