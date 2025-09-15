import requests
import base64
import json

# 测试文本翻译
def test_text_translation():
    url = "http://localhost:8000/translate"
    data = {
        "text": "Hello, how are you?",
        "target_lang": "zh"
    }
    
    response = requests.post(url, json=data)
    print("Text Translation Result:")
    print(json.dumps(response.json(), indent=2))

# 测试音频翻译
def test_audio_translation():
    url = "http://localhost:8000/translate_audio"
    
    # 创建模拟音频数据
    fake_audio_data = b"fake audio data for testing"
    audio_base64 = base64.b64encode(fake_audio_data).decode('utf-8')
    
    data = {
        "audio_base64": audio_base64,
        "target_lang": "zh"
    }
    
    response = requests.post(url, json=data)
    print("Audio Translation Result:")
    print(json.dumps(response.json(), indent=2))

# 测试服务器信息
def test_server_info():
    url = "http://localhost:8000/"
    response = requests.get(url)
    print("Server Info:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_server_info()
    print()
    test_text_translation()
    print()
    test_audio_translation()