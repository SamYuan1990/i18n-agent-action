## Test Addresses
[Mac ARM Test Address](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914330255)  
[Mac x86 Test Address](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914407540)  
[Linux Test Address](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914313680)

## Test Objectives  
1. How many languages can DeepSeek support for translation?  
![](./img/screenshort20250903Test001.png)  

2. The robustness of the current system prompt.  
https://github.com/SamYuan1990/i18n-agent-action/blob/main/Business/translateConfig.py#L67-L89  

3. Consistency of development frameworks like Flet across platforms (Mac, Linux). Personally, I believe future AI Agents will support various integration methods. Therefore, if frameworks like Flet can enable cross-platform compilation and building from a single codebase to deliver a consistent user experience, it would be a great choice.  

## Test Steps and Scope  

> My personal computer is a Mac x86, so I will use it as a reference.

1. Download and install the software.  

> You may encounter trust issues with the signature. Try a few times if needed.  

2. Configure a DeepSeek API key.  
Please refer to https://api-docs.deepseek.com/zh-cn/ or create one via the web platform.  
![](./img/step1.png)  


> Of course, everyone is also welcome to use their existing OpenAI-format large language models to expand the testing scope.  

3. Configure the large language model access information and save it.  
![](./img/step2.png) 

4. Enter the content to be translated and click "Translate" to wait for the result (note: voice input is enabled by default).  
![](./img/step3.png) 

5. Optional feature: Reserved words.  
Back to Step 1, adding reserved word and reproduce to step 4.

## If you have technical skills and would like to try speech-to-text, please contact me. Currently, due to technical limitations, only a development version is available.