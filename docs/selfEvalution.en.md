# Self evaluate prompt

Thanks to paper 2507.21046v3

## Show me the code

To make our translate agent self evaluate, we can try with auto detect proper nouns.
The PR for this repo at [link](https://github.com/SamYuan1990/i18n-agent-action/pull/53)

The core idea as prompt contains dynamic part as proper nouns, what if we ask LLM to auto detect new proper nouns and we merge them together in next round/chunk of tasks?

## Configable Design

As this is an i18n agent, for easy adopt with different projects, at Design phases, it kept `RESERVED WORD` as `Glossary`.

In prompt's `Quality assurance` we defined as:
```
Quality assurance steps
...
- When encountering ambiguous technical terms or proper nouns, provide brief explanations in parentheses (please reference provided reserved word from user)
```

When deal with a content translation, it talks to LLM as:
```bash
#System prompt
LLM_Client.get_config()["prompts"]["translator"],
#Content
Please help translate the following content into Chinese, reserved word: reserved word 0, reserved word 1...reserved word n in English.
This is part 1 of 10 of the document.
Example json output format:
{
        "content": "translated text here...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
Content to translate:
"Hello Transformer"
```

## Benefit for Configable design, "Transformer" is movie or ... Attention is all you need?

Before we impls Self evaluate prompt, let's say we have repo A and repo B need to translate.
Repo A is movie related, and repo B is a LLM doc repo, so the content is:

```bash
#Content
Please help translate the following content into Chinese, reserved word: LLM in English.
This is part 1 of 10 of the document.
Example json output format:
{
        "content": "translated text here...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
Content to translate:
"Hello Transformer"
```

## Attention is all you need, isn't it?

Wait a min... can we improve the process via "self attention"?
Let's back to the task of document translate. Assume we have 10 chunks for a document.
Instead of reading **Glossary** files or manual config.
Those **Glossary** wording, appear/used in the document right?

```
Glossary = Knowledges in LLM + Config(either in Glossary file or manual input) + Proper nouns(appears in document)
```

For translate task, we will send document into LLM right.

---

# What if we ask LLM pick up Proper nouns in previous chunk and used those Proper nouns as Glossary for following chunks?

---

## Here we go

### Step 0 Update system prompt

In task steps part of system prompt, ask LLM to pick up proper nouns.
```
Translation methodology:
...
- Research domain-specific terminology in the target language when needed, list any proper nouns as result.
```

### Step 1 Add a var to capture proper nouns from LLM

Change the structure output to be
```bash
Example json output format:
{
        "content": "translated text here...",
        "metadata": {{"chunk": 
Example JSON output format:
{
    "content": "translated text here...",
    "metadata": {"chunk": 2, "total": 2},
    "proper_nouns": "proper nouns 0, proper nouns 1..."
}

Content to translate:
{"chunk": {i+1}, "total": {len(chunks)}}},
"proper_nouns": "proper nouns 0, proper nouns 1..."
}

#### Test
Tested with [diffuser](https://github.com/huggingface/diffusers/pull/12179)

The manual config value is `Diffusers, stable_diffusion, consisid, colab`.

From log, we see detected proper nouns as
`Diffusers, stable_diffusion, consisid, colab, diffusion, ModularPipeline, YiYiXu, modular-diffdiff, modular-diffdiff-0704, DiffDiffBlocks`
Which we can start step 2 as merge proper nouns with reserved word.

### Step 2 Merge the proper nouns and reserved word

Here is a sample function implementation to merge proper nouns (as response from LLM) and reserved word
```python
def MergePN(str1, str2):
    # Split and deduplicate while preserving order
    merged = list(OrderedDict.fromkeys(
        [item.strip() for item in str1.split(",")] + 
        [item.strip() for item in str2.split(",")]
    ))

    result = ", ".join(merged)
    return result
```

## Result

Back to our story, let's see from 1st chunk `"Hello Transformer"`, LLM responded with proper nouns as `Transformer`, and in 2nd chunk, the talk looks like:
```bash
#Content
Please help translate the following content into Chinese, reserved word: Transformer, LLM in English.
This is part 2 of 10 of the document.
Example json output format:
{
    "content": "translated text here...",
    "metadata": {"chunk": {i+1}, "total": {len(chunks)}}},
}
Content to translate:
"Transformer from paper attention is all you need, and widely used as LLM...."
```

### Log screenshot
![](./img/selfevaluate.png)
![](./img/selfevaluate2.png)

### Real world case

We can see it automatically kept DeepFloyd IF, instead of `DeepFloyd 如果` or `深度弗洛伊德 如果`
![](./img/selfevaluate3.png)