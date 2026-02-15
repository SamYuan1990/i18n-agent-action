# Run as Desktop app or mobile app

## Support platform

| macOS (x86) | macOS (arm) | Windows | Linux (x86?) | iOS | Android |
| ----------- | ----------- | ------- | ------------ | --- | ------- |
| ✅      | ✅       | call for test | call for test | call for test | call for test |

## Download from GHA

Go to [link](https://github.com/SamYuan1990/i18n-agent-action/actions/workflows/release.yml?query=event%3Aschedule)

Find the latest build
![](../img/install_step1.png)  

Find your package
![](../img/install_step2.png)  

## Usage

> My personal computer is a Mac x86, so I will use it as a reference.

1. Download and install the software.  

> You may encounter trust issues with the signature. Try a few times if needed, or if you are a developer, `
sudo xattr -d com.apple.quarantine ~/i18n-agent-action.app 
codesign --force --deep --sign - --preserve-metadata=entitlements --options runtime ~/i18n-agent-action.app`
may help.

2. Configure a DeepSeek API key.  
Please refer to https://api-docs.deepseek.com/zh-cn/ or create one via the web platform.  
![](../img/step1.png)  


> Of course, everyone is also welcome to use their existing OpenAI-format large language models to expand the testing scope.  

3. Configure the large language model access information and save it.  
![](../img/step2.png) 

4. Enter the content to be translated and click "Translate" to wait for the result (note: voice output is enabled by default).  
![](../img/step3.png) 

5. Optional feature: Reserved words.  
Back to Step 1, add reserved words and proceed to step 4.