import logging
import os

import flet as ft
import flet_sherpa_onnx as fso
import pyttsx3


class SoundManager:
    """声音管理类，处理所有音频相关功能"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.engine = pyttsx3.init()
        self.fso_service = fso.FletSherpaOnnx()
        self.page._services.append(self.fso_service)
        self.Init_Recognizer = False

    async def start_recording(self):
        """开始录音"""
        if not self.Init_Recognizer:
            await self.fso_service.CreateRecognizer(
                encoder=self.app_data_path + "/base-encoder.onnx",
                decoder=self.app_data_path + "/base-decoder.onnx",
                tokens=self.app_data_path + "/base-tokens.txt",
            )
            self.Init_Recognizer = True
        await self.fso_service.StartRecording()

    async def stop_recording(self):
        """停止录音"""
        result = await self.fso_service.StopRecording()
        return result

    def speak_text(self, text):
        """使用文本转语音引擎朗读文本"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"语音合成失败: {str(e)}")

    def create_record_button(self, on_stop_click, visible=True):
        """创建录音按钮组件"""
        self.record_btn = ft.Button(
            "开始录音",
            on_click=self.start_recording,
        )
        self.stop_record_btn = ft.Button(
            "停止录音",
            on_click=on_stop_click,
        )

        return ft.Row([self.record_btn, self.stop_record_btn])
