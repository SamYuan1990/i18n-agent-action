import pyttsx3

_instance = None

def getTTSManager():
    """获取TTSManager的单例实例"""
    global _instance
    if _instance is None:
        _instance = TTSManager()
    return _instance

# text to sound
class TTSManager:
    def __init__(self):
        self.engine = pyttsx3.init()

    def say(self, text):
        """播放文本语音"""
        self.engine.say(text)
        self.engine.runAndWait()