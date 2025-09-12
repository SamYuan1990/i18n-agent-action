# 作为桌面应用或移动应用运行

## 支持平台

| macOS (x86) | macOS (arm) | Windows | Linux (x86?) | iOS | Android |
| ----------- | ----------- | ------- | ------------ | --- | ------- |
| ✅      | ✅       | 招募测试 | 招募测试 | 招募测试 | 招募测试 |

## 从GHA下载

访问 
https://github.com/SamYuan1990/i18n-agent-action/actions/workflows/release.yml?query=event%3Aschedule

找到最新的构建
![](../img/install_step1.png)  

找到您的包
![](../img/install_step2.png)  

## 使用说明

> 我的个人电脑是Mac x86，所以我会以它作为参考。

1. 下载并安装软件。  

> 您可能会遇到签名信任问题。如果遇到，可以尝试几次，或者如果您是开发者，可以尝试 `sudo xattr -d com.apple.quarantine ~/i18n-agent-action.app 
codesign --force --deep --sign - --preserve-metadata=entitlements --options runtime ~/i18n-agent-action.app` 来帮助解决。

2. 配置DeepSeek API密钥。  
请参考 https://api-docs.deepseek.com/zh-cn/ 或通过网页平台创建一个。  
![](../img/step1.png)  


> 当然，也欢迎大家使用自己现有的OpenAI格式大语言模型来扩展测试范围。  

3. 配置大语言模型访问信息并保存。  
![](../img/step2.png) 

4. 输入要翻译的内容，点击“翻译”等待结果（注意：默认启用语音输出）。  
![](../img/step3.png) 

5. 可选功能：保留字。  
回到步骤1，添加保留字并重复到步骤4。