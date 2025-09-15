# Guide d'Utilisation du Conteneur d'Application i18n Agent Action

## Aperçu
Il s'agit d'une application conteneurisée d'agent d'internationalisation (i18n) construite sur le framework Flet, offrant une interface web pour gérer et traiter les tâches liées à l'i18n.

## Démarrage Rapide

### 1. Télécharger l'Image
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:app
```

### 2. Exécuter le Conteneur
```bash
docker run -d -p 8550:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### 3. Accéder à l'Application
Ouvrez votre navigateur et naviguez vers : http://localhost:8550

## Options de Configuration

### Mappage de Port
Le port par défaut est 8550. Vous pouvez le mapper à n'importe quel port hôte :
```bash
docker run -d -p 8080:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### Variables d'Environnement
Vous pouvez configurer les variables d'environnement suivantes :

- `FLET_SECRET_KEY` : Clé secrète de l'application (par défaut : 123)
- `FLET_SERVER_PORT` : Port du serveur (par défaut : 8550)

Exemple :
```bash
docker run -d \
  -p 8550:8550 \
  -e FLET_SECRET_KEY=votre-clé-secrète \
  -e FLET_SERVER_PORT=8550 \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

### Persistance des Données
Pour la persistance des données, vous pouvez monter un volume :
```bash
docker run -d \
  -p 8550:8550 \
  -v ./i18n-data:/app/data \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

## Mode Développement

### Construire une Image Personnalisée
Si vous modifiez le code, vous pouvez reconstruire l'image :
```bash
docker build -f Dockerfile_App -t my-i18n-app .
```

### Exécuter la Version de Développement
```bash
docker run -d -p 8550:8550 --name my-i18n-app my-i18n-app
```

## Commandes Courantes

### Voir les Journaux du Conteneur
```bash
docker logs i18n-app
```

### Accéder au Shell du Conteneur
```bash
docker exec -it i18n-app /bin/bash
```

### Arrêter le Conteneur
```bash
docker stop i18n-app
```

### Redémarrer le Conteneur
```bash
docker restart i18n-app
```

### Supprimer le Conteneur
```bash
docker rm i18n-app
```

## Dépannage

1. **Conflit de Port** : Si le port 8550 est déjà utilisé, utilisez un port différent
2. **Échec du Démarrage du Conteneur** : Vérifiez les journaux avec `docker logs i18n-app`
3. **Impossible d'Accéder à l'Application** : Vérifiez les paramètres du pare-feu et le mappage de port

## Support

Pour les problèmes, veuillez consulter la documentation du projet ou soumettre un problème au dépôt GitHub.

---

**Note** : Ce conteneur est destiné uniquement aux environnements de développement et de test. Pour une utilisation en production, assurez-vous de configurer des mesures de sécurité appropriées.