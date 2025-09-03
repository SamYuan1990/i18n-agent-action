## Adresses de test
[Adresse de test Mac ARM](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914330255)  
[Adresse de test Mac x86](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914407540)  
[Adresse de test Linux](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914313680)

## Objectifs de test  
1. Combien de langues DeepSeek peut-il prendre en charge pour la traduction ?  
![](./img/screenshort20250903Test001.png)  

2. La robustesse de l'invite système actuelle.  
https://github.com/SamYuan1990/i18n-agent-action/blob/main/Business/translateConfig.py#L67-L89  

3. La cohérence des frameworks de développement comme Flet sur différentes plateformes (Mac, Linux). Personnellement, je pense que les futurs agents IA prendront en charge diverses méthodes d'intégration. Par conséquent, si des frameworks comme Flet permettent une compilation et une construction multiplateformes à partir d'une base de code unique pour offrir une expérience utilisateur cohérente, ce serait un excellent choix.  

## Étapes et portée du test  

> Mon ordinateur personnel est un Mac x86, donc je l'utiliserai comme référence.

1. Télécharger et installer le logiciel.  

> Vous pourriez rencontrer des problèmes de confiance avec la signature. Essayez plusieurs fois si nécessaire.  

2. Configurer une clé API DeepSeek.  
Veuillez vous référer à https://api-docs.deepseek.com/zh-cn/ ou en créer une via la plateforme web.  
![](./img/step1.png)  


> Bien sûr, tout le monde est également invité à utiliser leurs modèles de langage volumineux existants au format OpenAI pour élargir la portée des tests.  

3. Configurer les informations d'accès au modèle de langage volumineux et les enregistrer.  
![](./img/step2.png)  

4. Entrer le contenu à traduire et cliquer sur "Traduire" pour attendre le résultat (note : la saisie vocale est activée par défaut).  
![](./img/step3.png)  

5. Fonctionnalité optionnelle : Mots réservés.  
Retour à l'étape 1, ajouter un mot réservé et reproduire jusqu'à l'étape 4.

## Si vous avez des compétences techniques et souhaitez essayer la reconnaissance vocale, veuillez me contacter. Actuellement, en raison de limitations techniques, seule une version de développement est disponible.