# Exécuter en tant qu'application de bureau ou application mobile

## Plateformes prises en charge

| macOS (x86) | macOS (arm) | Windows | Linux (x86?) | iOS | Android |
| ----------- | ----------- | ------- | ------------ | --- | ------- |
| ✅      | ✅       | appel à test | appel à test | appel à test | appel à test |

## Télécharger depuis GHA

Allez à 
https://github.com/SamYuan1990/i18n-agent-action/actions/workflows/release.yml?query=event%3Aschedule

Trouvez la dernière version
![](../img/install_step1.png)  

Trouvez votre paquet
![](../img/install_step2.png)  

## Utilisation

> Mon ordinateur personnel est un Mac x86, donc je vais l'utiliser comme référence.

1. Téléchargez et installez le logiciel.  

> Vous pouvez rencontrer des problèmes de confiance avec la signature. Essayez plusieurs fois si nécessaire, ou si vous étiez développeur, `
sudo xattr -d com.apple.quarantine ~/i18n-agent-action.app 
codesign --force --deep --sign - --preserve-metadata=entitlements --options runtime ~/i18n-agent-action.app`
peut aider.

2. Configurez une clé API DeepSeek.  
Veuillez vous référer à https://api-docs.deepseek.com/zh-cn/ ou en créer une via la plateforme web.  
![](../img/step1.png)  


> Bien sûr, tout le monde est également invité à utiliser leurs modèles de langage volumineux existants au format OpenAI pour élargir la portée des tests.  

3. Configurez les informations d'accès au modèle de langage volumineux et enregistrez-les.  
![](../img/step2.png) 

4. Entrez le contenu à traduire et cliquez sur "Traduire" pour attendre le résultat (note : la sortie vocale est activée par défaut).  
![](../img/step3.png) 

5. Fonctionnalité optionnelle : Mots réservés.  
Retournez à l'étape 1, ajoutez un mot réservé et reproduisez jusqu'à l'étape 4.