# Auto-évaluation de l'invite

Grâce au papier 2507.21046v3

## Montrez-moi le code

Pour que notre agent de traduction s'auto-évalue, nous pouvons essayer avec la détection automatique des noms propres.
La PR pour ce dépôt à [lien](https://github.com/SamYuan1990/i18n-agent-action/pull/53)

L'idée centrale est que l'invite contient une partie dynamique comme les noms propres, et si nous demandons au LLM de détecter automatiquement de nouveaux noms propres et nous les fusionnons ensemble dans le prochain tour/tronçon de tâches ?

## Conception Configurable

Comme il s'agit d'un agent i18n, pour une adoption facile avec différents projets, lors des phases de conception, il a gardé `MOT RÉSERVÉ` comme `Glossaire`.

Dans les étapes d'assurance qualité de l'invite, nous avons défini :
```
Étapes d'assurance qualité
...
- Lorsque vous rencontrez des termes techniques ambigus ou des noms propres, fournissez de brèves explications entre parenthèses (veuillez référencer le mot réservé fourni par l'utilisateur)
```

Lorsqu'il traite une traduction de contenu, il communique avec le LLM comme suit :
```bash
#Invite système
LLM_Client.get_config()["prompts"]["translator"],
#Contenu
Veuillez aider à traduire le contenu suivant en chinois, mot réservé : mot réservé 0, mot réservé 1...mot réservé n en anglais.
Ceci est la partie 1 sur 10 du document.
Exemple de format de sortie JSON :
{
        "content": "texte traduit ici...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
Contenu à traduire :
"Hello Transformer"
```

## Avantage de la conception Configurable, "Transformer" est un film ou ... Attention is all you need ?

Avant d'implémenter l'invite d'auto-évaluation, disons que nous avons le dépôt A et le dépôt B à traduire.
Le dépôt A est lié aux films, et le dépôt B est un dépôt de documentation LLM, donc le contenu est :

```bash
#Contenu
Veuillez aider à traduire le contenu suivant en chinois, mot réservé : LLM en anglais.
Ceci est la partie 1 sur 10 du document.
Exemple de format de sortie JSON :
{
        "content": "texte traduit ici...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
Contenu à traduire :
"Hello Transformer"
```

## Attention is all you need, n'est-ce pas ?

Attendez une minute... pouvons-nous améliorer le processus via "l'auto-attention" ?
Revenons à la tâche de traduction de document. Supposons que nous ayons 10 tronçons pour un document.
Au lieu de lire des fichiers **Glossaire** ou de configurer manuellement.
Ces termes de **Glossaire** apparaissent/utilisés dans le document, n'est-ce pas ?

```
Glossaire = Connaissances dans LLM + Configuration (soit dans un fichier Glossaire ou entrée manuelle) + Noms propres (apparaissent dans le document)
```

Pour la tâche de traduction, nous enverrons le document dans le LLM, n'est-ce pas.

---

# Et si nous demandions au LLM de récupérer les noms propres dans le tronçon précédent et d'utiliser ces noms propres comme Glossaire pour les tronçons suivants ?

---

## C'est parti

### Étape 0 Mettre à jour l'invite système

Dans la partie des étapes de tâche de l'invite système, demandez au LLM de récupérer les noms propres.
```
Méthodologie de traduction :
...
- Recherchez la terminologie spécifique au domaine dans la langue cible si nécessaire, listez tous les noms propres comme résultat.
```

### Étape 1 Ajouter une variable pour capturer les noms propres du LLM

Changez la structure de sortie pour être
```bash
Exemple de format de sortie JSON :
{
        "content": "texte traduit ici...",
        "metadata": {{"chunk": 
{i+1}, "total": {len(chunks)}}},
        "proper_nouns": "proper nouns 0, proper nouns 1..."
}

#### Test
Testé avec [diffuser](https://github.com/huggingface/diffusers/pull/12179)

La valeur de configuration manuelle est `Diffusers, stable_diffusion, consisid, colab`.

D'après le journal, nous voyons les noms propres détectés comme
`Diffusers, stable_diffusion, consisid, colab, diffusion, ModularPipeline, YiYiXu, modular-diffdiff, modular-diffdiff-0704, DiffDiffBlocks`
Que nous pouvons commencer l'étape 2 comme fusionner les noms propres en mot réservé.

### Étape 2 Fusionner les noms propres et le mot réservé

Voici un exemple d'implémentation de fonction pour fusionner les noms propres (comme réponse du LLM) et le mot réservé
```python
def MergePN(str1, str2):
    # Diviser et maintenir l'ordre avec suppression des doublons
    merged = list(OrderedDict.fromkeys(
        [item.strip() for item in str1.split(",")] + 
        [item.strip() for item in str2.split(",")]
    ))

    result = ", ".join(merged)
    return result
```

## Résultat

Revenons à notre histoire, voyons à partir du 1er morceau `"Hello Transformer"`, le LLM nous a répondu avec les noms propres comme `Transformer`, et dans le 2e morceau, la discussion ressemble à :
```bash
#Contenu
Veuillez aider à traduire le contenu suivant en chinois, mot réservé : Transformer, LLM en anglais.
Ceci est la partie 2 sur 10 du document.
Exemple de format de sortie JSON :
{
        "content": "texte traduit ici...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
Contenu à traduire :
"Transformer du papier attention is all you need, et largement utilisé comme LLM...."
```

### Capture d'écran du journal
![](../img/selfevaluate.png)
![](../img/selfevaluate2.png)

### Cas réel

Nous pouvons voir qu'il a automatiquement conservé DeepFloyd IF, au lieu de `DeepFloyd 如果` ou `深度弗洛伊德 如果`
![](../img/selfevaluate3.png)