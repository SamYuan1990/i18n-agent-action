## 测试地址
[Mac ARM 测试地址](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914330255)  
[Mac x86 测试地址](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914407540)  
[Linux 测试地址](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914313680)

## 测试目标  
1. DeepSeek 可以支持多少种语言的翻译？  
![](./img/screenshort20250903Test001.png)  

2. 当前系统提示的鲁棒性。  
https://github.com/SamYuan1990/i18n-agent-action/blob/main/Business/translateConfig.py#L67-L89  

3. 开发框架（如 Flet）在不同平台（Mac、Linux）上的一致性。我个人认为，未来的 AI 代理将支持各种集成方式。因此，如果像 Flet 这样的框架能够实现跨平台编译和构建，从单一代码库提供一致的用户体验，那将是一个很好的选择。  

## 测试步骤和范围  

> 我的个人电脑是 Mac x86，因此我将以此作为参考。

1. 下载并安装软件。  

> 您可能会遇到签名信任问题。如果需要，请尝试几次。  

2. 配置 DeepSeek API 密钥。  
请参考 https://api-docs.deepseek.com/zh-cn/ 或通过网页平台创建一个。  
![](./img/step1.png)  


> 当然，也欢迎大家使用现有的 OpenAI 格式大语言模型来扩展测试范围。  

3. 配置大语言模型访问信息并保存。  
![](./img/step2.png)  

4. 输入要翻译的内容，点击“翻译”等待结果（注意：默认启用语音输入）。  
![](./img/step3.png)  

5. 可选功能：保留字。  
返回步骤 1，添加保留字并重现到步骤 4。

## 如果您有技术技能并想尝试语音转文本，请联系我。目前，由于技术限制，仅提供开发版本。