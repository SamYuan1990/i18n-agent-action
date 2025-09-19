# Guide de l'utilisateur du serveur MCP i18n

## Informations sur l'image
- **Nom de l'image** : `ghcr.io/samyuan1990/i18n-agent-action:mcp`
- **Image de base** : Python 3.12
- **Répertoire de travail** : `/app`

## Description
Il s'agit d'un serveur Model Context Protocol (MCP) conçu pour les tâches d'internationalisation (i18n), offrant des fonctionnalités liées à la traduction avec prise en charge de modèles ONNX personnalisés.

## Démarrage rapide

### Tirer l'image
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### Exécuter le conteneur
```bash
docker run -p 8080:8080 -e api_key="VOTRE_CLÉ_API" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### Configuration des variables d'environnement
- `api_key` : (Obligatoire) Clé API du service de traduction
- `encoder` : (Optionnel) Chemin vers le fichier de modèle ONNX de l'encodeur (par défaut : `/tmp/base-encoder.onnx`)
- `decoder` : (Optionnel) Chemin vers le fichier de modèle ONNX du décodeur (par défaut : `/tmp/base-decoder.onnx`)
- `tokens` : (Optionnel) Chemin vers le fichier de modèle ONNX des tokens (par défaut : `/tmp/base-tokens.onnx`)

Exemple avec des modèles personnalisés :
```bash
docker run -p 8080:8080 \
  -e api_key="votre-clé-api-de-traduction" \
  -e encoder="/app/models/custom-encoder.onnx" \
  -e decoder="/app/models/custom-decoder.onnx" \
  -e tokens="/app/models/custom-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## Montage de modèles ONNX personnalisés
Vous pouvez monter vos propres fichiers de modèle ONNX dans le conteneur en utilisant des volumes Docker :

```bash
docker run -p 8080:8080 \
  -e api_key="votre-clé-api" \
  -v /chemin/vers/vos/models:/app/models \
  -e encoder="/app/models/votre-encoder.onnx" \
  -e decoder="/app/models/votre-decodeur.onnx" \
  -e tokens="/app/models/votre-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

```
{
    "method": "docker run",
    "args": [
        "-p", "8080:8080",
        "-e", "api_key=your-api-key",
        "-v", "/path/to/your/models:/app/models",
        "-e", "encoder=/app/models/your-encoder.onnx",
        "-e", "decoder=/app/models/your-decoder.onnx",
        "-e", "tokens=/app/models/your-tokens.onnx",
        "ghcr.io/samyuan1990/i18n-agent-action:mcp"
    ]
}
```

## Configuration du port
- Port exposé par défaut : **8080**
- Vous pouvez ajuster le mappage de port de l'hôte :
  ```bash
  docker run -p 3000:8080 [...] # Mappe le port hôte 3000 au port conteneur 8080
  ```

## Structure du projet
- Utilise Poetry pour la gestion des dépendances
- Code source situé dans le répertoire `/app` à l'intérieur du conteneur
- Installe automatiquement toutes les dépendances supplémentaires (y compris les dépendances de développement)

## Configuration personnalisée
Pour des personnalisations supplémentaires :

1. **Monter des fichiers de configuration** :
   ```bash
   docker run -v /chemin/vers/votre/config.yaml:/app/config.yaml [...]
   ```

2. **Utiliser des variables d'environnement** :
   ```bash
   docker run -e api_key="votre-clé" -e AUTRE_VAR="valeur" [...]
   ```

## Utilisation en développement
Si vous avez besoin de modifier le code ou de développer :

```bash
# Cloner le code source
git clone <votre-dépôt>
cd <répertoire-du-dépôt>

# Utiliser Docker Compose (recommandé)
# Ou utiliser docker run avec le code local monté
docker run -p 8080:8080 -v $(pwd):/app -e api_key="votre-clé" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## Vérification de santé
Après le démarrage du serveur, vous pouvez vérifier son statut en accédant à :
```bash
curl http://localhost:8080/health
```

## Notes
1. Assurez-vous de fournir une variable d'environnement `api_key` valide
2. Le conteneur supprime automatiquement le fichier config.yaml par défaut au démarrage
3. Pour une configuration persistante, montez
fichiers de configuration externes
4. Pour les modèles personnalisés, montez vos fichiers ONNX et définissez les variables d'environnement appropriées

## Support et Retour d'information
Si vous rencontrez des problèmes ou avez besoin d'assistance, veuillez soumettre un problème via le dépôt du projet ou contacter le mainteneur.