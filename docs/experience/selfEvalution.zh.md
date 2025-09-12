# 自我评估提示

感谢论文 2507.21046v3

## 给我看看代码

为了让我们的翻译代理自我评估，我们可以尝试自动检测专有名词。
该仓库的拉取请求在[链接](https://github.com/SamYuan1990/i18n-agent-action/pull/53)

核心想法是提示中包含动态部分作为专有名词，如果我们要求LLM自动检测新的专有名词，并在下一轮/任务块中合并它们呢？

## 可配置设计

由于这是一个i18n代理（i18n-agent-action），为了便于与不同项目集成，在设计阶段，它保留了`RESERVED WORD`作为`Glossary`。

在提示的`质量保证`部分，我们定义为：
```
质量保证步骤
...
- 当遇到模糊的技术术语或专有名词时，在括号中提供简要解释（请参考用户提供的保留词）
```

当处理内容翻译时，它与LLM对话如下：
```bash
#系统提示
LLM_Client.get_config()["prompts"]["translator"],
#内容
请帮助将以下内容翻译成中文，保留词：保留词0、保留词1...保留词n，以英文形式。
这是文档的第1部分，共10部分。
示例JSON输出格式：
{
        "content": "翻译后的文本在这里...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
要翻译的内容：
"Hello Transformer"
```

## 可配置设计的好处，“Transformer”是电影还是...注意力就是一切？

在我们实现自我评估提示之前，假设我们有仓库A和仓库B需要翻译。
仓库A与电影相关，仓库B是一个LLM文档仓库，因此内容是：
```bash
#内容
请帮助将以下内容翻译成中文，保留词：LLM，以英文形式。
这是文档的第1部分，共10部分。
示例JSON输出格式：
{
        "content": "翻译后的文本在这里...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
要翻译的内容：
"Hello Transformer"
```

## 注意力就是一切，不是吗？

等一下...我们能否通过“自注意力”改进这个过程？
让我们回到文档翻译的任务。假设我们有10个文档块。
而不是阅读**词汇表**文件或手动配置。
那些**词汇表**词汇，在文档中出现/使用，对吧？

```
词汇表 = LLM中的知识 + 配置（在词汇表文件中或手动输入）+ 专有名词（在文档中出现）
```

对于翻译任务，我们将文档发送到LLM，对吧。

---

# 如果我们要求LLM在前一个块中挑选专有名词，并将这些专有名词用作后续块的词汇表呢？

---

## 开始吧

### 步骤0 更新系统提示

在系统提示的任务步骤部分，要求LLM挑选专有名词。
```
翻译方法：
...
- 在需要时研究领域特定术语的目标语言，列出任何专有名词作为结果。
```

### 步骤1 添加一个变量来从LLM捕获专有名词

更改输出结构为
```bash
示例JSON输出格式：
{
        "content": "翻译后的文本在这里...",
        "metadata": {{"chunk": 
#### 测试
使用 [diffuser](https://github.com/huggingface/diffusers/pull/12179) 进行测试

手动配置值为 `Diffusers, stable_diffusion, consisid, colab`。

从日志中，我们看到检测到的专有名词为
`Diffusers, stable_diffusion, consisid, colab, diffusion, ModularPipeline, YiYiXu, modular-diffdiff, modular-diffdiff-0704, DiffDiffBlocks`
我们可以开始步骤2，将专有名词合并为保留词。

### 步骤2 合并专有名词和保留词

这是一个示例函数实现，用于合并专有名词（来自LLM的响应）和保留词
```python
def MergePN(str1, str2):
    # 分割并保持顺序去重
    merged = list(OrderedDict.fromkeys(
        [item.strip() for item in str1.split(",")] + 
        [item.strip() for item in str2.split(",")]
    ))

    result = ", ".join(merged)
    return result
```

## 结果

回到我们的故事，从第一个块 `"Hello Transformer"`，LLM 响应我们专有名词为 `Transformer`，在第二个块中，内容看起来像：
```bash
#内容
请帮助将以下内容翻译成中文，保留词：Transformer, LLM 使用英文。
这是文档的第2部分，共10部分。
示例JSON输出格式：
{
        "content": "翻译后的文本在这里...",
        "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
}
要翻译的内容：
"Transformer 来自论文 attention is all you need，并广泛用作 LLM...."
```

### 日志截图
![](../img/selfevaluate.png)
![](../img/selfevaluate2.png)

### 真实世界案例

我们可以看到它自动保留了 DeepFloyd IF，而不是 `DeepFloyd 如果` 或 `深度弗洛伊德 如果`
![](../img/selfevaluate3.png)