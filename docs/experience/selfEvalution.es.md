# Autoevaluación del prompt

Gracias al artículo 2507.21046v3

## Muéstrame el código

Para hacer que nuestro agente de traducción se autoevalúe, podemos intentar con la detección automática de nombres propios.
La PR para este repositorio en [enlace](https://github.com/SamYuan1990/i18n-agent-action/pull/53)

La idea central es que el prompt contiene una parte dinámica como nombres propios, ¿qué tal si le pedimos al LLM que detecte automáticamente nuevos nombres propios y los fusionamos juntos en la siguiente ronda/parte de tareas?

## Diseño configurable

Como este es un agente de i18n, para facilitar la adopción con diferentes proyectos, en las fases de Diseño, mantuvo `PALABRA RESERVADA` como `Glosario`.

En los pasos de `Aseguramiento de calidad` del prompt, definimos:
```
Pasos de aseguramiento de calidad
...
- Al encontrar términos técnicos ambiguos o nombres propios, proporcionar breves explicaciones entre paréntesis (por favor, referencia la palabra reservada proporcionada por el usuario)
```

Al tratar con una traducción de contenido, se comunica con el LLM como:
```bash
#Prompt del sistema
LLM_Client.get_config()["prompts"]["translator"],
#Contenido
Por favor, ayuda a traducir el siguiente contenido al chino, palabra reservada: palabra reservada 0, palabra reservada 1...palabra reservada n en inglés.
Esta es la parte 1 de 10 del documento.
Formato de salida json de ejemplo:
{
        "content": "texto traducido aquí...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
Contenido a traducir:
"Hola Transformer"
```

## Beneficio del diseño configurable, ¿"Transformer" es una película o ... Attention is all you need?

Antes de implementar el prompt de autoevaluación, digamos que tenemos el repositorio A y el repositorio B que necesitan traducción.
El repositorio A está relacionado con películas, y el repositorio B es un repositorio de documentos de LLM, por lo que el contenido es:

```bash
#Contenido
Por favor, ayuda a traducir el siguiente contenido al chino, palabra reservada: LLM en inglés.
Esta es la parte 1 de 10 del documento.
Formato de salida json de ejemplo:
{
        "content": "texto traducido aquí...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
Contenido a traducir:
"Hola Transformer"
```

## Attention is all you need, ¿no es así?

Espera un minuto... ¿podemos mejorar el proceso mediante "auto-atención"?
Volvamos a la tarea de traducción de documentos. Asumamos que tenemos 10 partes para un documento.
En lugar de leer archivos de **Glosario** o configuración manual.
Esas palabras del **Glosario**, ¿aparecen/usan en el documento, verdad?

```
Glosario = Conocimientos en LLM + Configuración (ya sea en archivo de Glosario o entrada manual) + Nombres propios (aparecen en el documento)
```

Para la tarea de traducción, enviaremos el documento al LLM, ¿verdad?

---

# ¿Qué tal si le pedimos al LLM que recoja nombres propios en la parte anterior y use esos nombres propios como Glosario para las siguientes partes?

---

## Aquí vamos

### Paso 0 Actualizar el prompt del sistema

En la parte de pasos de tarea del prompt del sistema, pedir al LLM que recoja nombres propios.
```
Metodología de traducción:
...
- Investigar terminología específica del dominio en el idioma objetivo cuando sea necesario, listar cualquier nombre propio como resultado.
```

### Paso 1 Añadir una variable para capturar nombres propios del LLM

Cambiar la estructura de salida a
```bash
Formato de salida json de ejemplo:
{
        "content": "texto traducido aquí...",
        "metadata": {{"chunk": 
{"chunk": {i+1}, "total": {len(chunks)}}},
        "proper_nouns": "proper nouns 0, proper nouns 1..."
}

#### Prueba
Probado con [diffuser](https://github.com/huggingface/diffusers/pull/12179)

El valor de configuración manual es `Diffusers, stable_diffusion, consisid, colab`.

Del registro, vemos que se detectaron nombres propios como
`Diffusers, stable_diffusion, consisid, colab, diffusion, ModularPipeline, YiYiXu, modular-diffdiff, modular-diffdiff-0704, DiffDiffBlocks`
Con lo cual podemos comenzar el paso 2 como fusionar nombres propios como palabra_reservada.

### Paso 2 Fusionar los nombres propios y la palabra reservada

Aquí hay una implementación de función de muestra para fusionar nombres propios (como respuesta de LLM) y palabra reservada
```python
def MergePN(str1, str2):
    # Dividir y mantener el orden sin duplicados
    merged = list(OrderedDict.fromkeys(
        [item.strip() for item in str1.split(",")] + 
        [item.strip() for item in str2.split(",")]
    ))

    result = ", ".join(merged)
    return result
```

## Resultado

Volviendo a nuestra historia, veamos desde el primer fragmento `"Hello Transformer"`, LLM nos respondió con nombres propios como `Transformer`, y en el segundo fragmento, la conversación luce así:
```bash
#Contenido
Por favor, ayude a traducir el siguiente contenido al chino, palabra reservada: Transformer, LLM en inglés.
Este es el fragmento 2 de 10 del documento.
Ejemplo de formato de salida json:
{
        "content": "texto traducido aquí...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
Contenido a traducir:
"Transformer del artículo attention is all you need, y ampliamente utilizado como LLM...."
```

### Captura de pantalla del registro
![](../img/selfevaluate.png)
![](../img/selfevaluate2.png)

### Caso del mundo real

Podemos ver que automáticamente mantuvo DeepFloyd IF, en lugar de `DeepFloyd 如果` o `深度弗洛伊德 如果`
![](../img/selfevaluate3.png)