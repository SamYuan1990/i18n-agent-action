# ¿BLEU Puede Estar Obsoleto para Tareas de Traducción?

## ¿Qué es BLEU?

Esto fue idea de [Rico Sennrich](https://twitter.com/RicoSennrich/status/883246242763026433)
Originalmente escrito por Matt Post.
Nuevas características y soporte continuo proporcionados por Martin Popel (@martinpopel) y Ozan Caglayan (@ozancaglayan).

Si usas SacreBLEU, por favor cita lo siguiente:

```
@inproceedings{post-2018-call,
  title = "A Call for Clarity in Reporting {BLEU} Scores",
  author = "Post, Matt",
  booktitle = "Proceedings of the Third Conference on Machine Translation: Research Papers",
  month = oct,
  year = "2018",
  address = "Belgium, Brussels",
  publisher = "Association for Computational Linguistics",
  url = "https://www.aclweb.org/anthology/W18-6319",
  pages = "186--191",
}
```

## ¡Muéstrame el código!

Usé flores200 y elegí la primera oración en chino e inglés para probar.
Definí `sys` como el resultado de DeepSeek, y `sys_0`, **nota: `sys_0` está copiado de `ref`.**

```
from sacrebleu import BLEU, CHRF

refs = [
    [
        '史丹佛大學醫學院的科學家於週一宣布發明一項新型診斷工具，可依類型將細胞分類：這是一種細小的可列印芯片，使用標準噴墨印表機就能印出，每個芯片的成本大約一美分。'
        ,'周一，斯坦福大学医学院的科学家宣布，他们发明了一种可以将细胞按类型分类的新型诊断工具：一种可打印的微型芯片。这种芯片可以使用标准喷墨打印机制造，每片价格可能在一美分左右。'
        ,'週一，來自史丹福大學醫學院的科學家宣布發明了一種新的診症工具，可以對細胞進行分類：一種可以用標準噴墨打印機製造的微型可打印芯片，每塊芯片可能大概只需 1 美分。'
    ],
    [
        '主要研究人员表示，这可以让低收入国家/地区的患者尽早发现癌症、肺结核、艾滋病和疟疾。在这些国家/地区，乳腺癌等疾病的生存率可能仅为富裕国家的一半。'
        ,'主要研究人員表示，這或許可以讓低收入國家的癌症、肺結核、愛滋病毒及瘧疾病患早期發現病症。在這些國家，乳癌等疾病患者的存活率是較富裕國家的一半。'
        ,'主席研究員說，這可能會讓低收入國家的患者及早發現癌症、結核病、愛滋病病毒和瘧疾。在這些國家，乳癌等疾病的生存率可能只有富裕國家的一半。'
    ]
]
sys = [
    '斯坦福大学医学院的科学家于本周一宣布研发出一种新型细胞分型诊断工具——这种微型打印芯片可以用标准喷墨打印机生产，单件成本可能低至约1美分。',
    '主要研究人员表示,这项技术有望为低收入国家的患者提供癌症、结核病、艾滋病毒和疟疾的早期检测。在这些国家,乳腺癌等疾病的存活率可能只有富裕国家的一半。'
]
sys_0 = [
    '週一，來自史丹福大學醫學院的科學家宣布發明了一種新的診症工具，可以對細胞進行分類：一種可以用標準噴墨打印機製造的微型可打印芯片，每塊芯片可能大概只需 1 美分。',
    '主席研究員說，這可能會讓低收入國家的患者及早發現癌症、結核病、愛滋病病毒和瘧疾。在這些國家，乳癌等疾病的生存率可能只有富裕國家的一半。'
]

bleu = BLEU(lowercase=True,effective_order=True)
print(bleu.corpus_score(sys_0, refs))
print(bleu.corpus_score(sys, refs))
print(bleu.get_signature())
print("-----")
bleu = BLEU(tokenize='zh',lowercase=True,effective_order=True)
print(bleu.corpus_score(sys_0, refs))
print(bleu.corpus_score(sys, refs))
print(bleu.get_signature())
print("-----")
bleu = BLEU(tokenize='char',lowercase=True,effective_order=True)
print(bleu.corpus_score(sys_0, refs))
print(bleu.corpus_score(sys, refs))
print(bleu.get_signature())
print("-----")
bleu = BLEU(tokenize='intl',lowercase=True,effective_order=True)
print(bleu.corpus_score(sys_0, refs))
print(bleu.corpus_score(sys, refs))
print(bleu.get_signature())
print("-----")
bleu = BLEU(tokenize='flores101',lowercase=True,effective_order=True)
print(bleu.corpus_score(sys_0, refs))
print(bleu.corpus_score(sys, refs))
print(bleu.get_signature())
print("-----")
bleu = BLEU(tokenize='flores200',lowercase=True,effective_order=True)
print(bleu.corpus_score(sys_0, refs))
print(bleu.corpus_score(sys, refs))
print(bleu.get_signature())
print("-----")
chrf = CHRF()
```
print(chrf.corpus_score(sys_0, refs))
print(chrf.corpus_score(sys, refs))
print(chrf.get_signature())
```

## ¡Muéstrame el ambiente y el resultado!

Para mí, el resultado de la traducción es casi el mismo para esas oraciones, ya que nos enfocamos en las 5W-H como
`El lunes, científicos de la Escuela de Medicina de la Universidad de Stanford anunciaron la invención de una nueva herramienta de diagnóstico que puede clasificar células por tipo: un pequeño chip imprimible que puede fabricarse utilizando impresoras de inyección de tinta estándar por posiblemente alrededor de un centavo estadounidense cada uno.`

El lunes, científicos de la Escuela de Medicina de la Universidad de Stanford, anunciaron...

A continuación, veamos el comportamiento de BLEU:

```
BLEU = 0.00 0.0/0.0/0.0/0.0 (BP = 1.000 ratio = 2.000 hyp_len = 4 ref_len = 2)
BLEU = 0.00 0.0/0.0/0.0/0.0 (BP = 1.000 ratio = 3.000 hyp_len = 6 ref_len = 2)
nrefs:2|case:lc|eff:no|tok:13a|smooth:exp|version:2.5.1
-----
```
El resultado predeterminado no es bueno, ya que BLEU depende de la tokenización, lo cual tiene sentido.

```
BLEU = 38.75 80.0/49.0/29.8/21.6 (BP = 0.973 ratio = 0.973 hyp_len = 145 ref_len = 149)
BLEU = 17.42 60.8/29.1/12.2/4.4 (BP = 0.993 ratio = 0.993 hyp_len = 143 ref_len = 144)
nrefs:2|case:lc|eff:no|tok:zh|smooth:exp|version:2.5.1
-----
BLEU = 38.75 80.0/49.0/29.8/21.6 (BP = 0.973 ratio = 0.973 hyp_len = 145 ref_len = 149)
BLEU = 17.42 60.8/29.1/12.2/4.4 (BP = 0.993 ratio = 0.993 hyp_len = 143 ref_len = 144)
nrefs:2|case:lc|eff:no|tok:char|smooth:exp|version:2.5.1
-----
```
Bueno, zh equivale a tokenizar por carácter, y sí, depende del idioma. Pero, lo cual me hace pensar de manera extraña ya que `sys_0` no obtuvo una puntuación completa de 100.

```
BLEU = 8.91 50.0/9.1/5.0/2.8 (BP = 1.000 ratio = 1.091 hyp_len = 24 ref_len = 22)
BLEU = 2.98 31.6/2.9/1.7/1.0 (BP = 0.854 ratio = 0.864 hyp_len = 19 ref_len = 22)
nrefs:2|case:lc|eff:no|tok:intl|smooth:exp|version:2.5.1
-----
BLEU = 27.81 66.3/35.3/20.0/13.3 (BP = 0.990 ratio = 0.990 hyp_len = 104 ref_len = 105)
BLEU = 6.20 48.5/17.9/4.3/0.5 (BP = 0.921 ratio = 0.924 hyp_len = 97 ref_len = 105)
nrefs:2|case:lc|eff:no|tok:flores101|smooth:exp|version:2.5.1
-----
BLEU = 28.16 73.7/37.5/21.8/14.8 (BP = 0.916 ratio = 0.919 hyp_len = 114 ref_len = 124)
BLEU = 9.55 53.2/22.0/7.5/1.0 (BP = 1.000 ratio = 1.009 hyp_len = 111 ref_len = 110)
nrefs:2|case:lc|eff:no|tok:flores200|smooth:exp|version:2.5.1
-----
```
Como nuestro caso de prueba es de flores200, veamos el comportamiento de BLEU con flores200. Mmm, tampoco es perfecto.

```
80.0/49.0/29.8/21.6
73.7/37.5/21.8/14.8
```
Bueno, estos cuatro conjuntos de números representan la precisión de 1-gram, 2-gram, 3-gram y 4-gram, respectivamente.

## ¿Por qué puede estar desactualizado?

Lo cual significa que, si solo comparamos con la precisión de palabras... como 1-gram o 2-gram... lo cual parece bueno pero pierde el significado de la oración. Y al mismo tiempo, si cambiamos el tokenizador, influye demasiado en el resultado.