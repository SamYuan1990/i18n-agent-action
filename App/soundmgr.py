import logging
import os
from typing import Callable, Optional

import flet as ft
import pyttsx3

# 导入音频录制库
try:
    import flet_audio_recorder as ftar

    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False
    logging.warning("flet_audio_recorder not available, audio recording disabled")


class SoundManager:
    """声音管理类，处理所有音频相关功能"""

    def __init__(self, page: ft.Page, app_data_path: str):
        self.page = page
        self.app_data_path = app_data_path
        self.engine = pyttsx3.init()
        self.recording_path = ""
        self.on_state_change_callback: Optional[Callable] = None

        # 初始化音频录制器（如果可用）
        if AUDIO_RECORDER_AVAILABLE:
            self.audio_rec = ftar.AudioRecorder(
                audio_encoder=ftar.AudioEncoder.WAV,
                on_state_changed=self.handle_state_change,
            )
            self.page.overlay.append(self.audio_rec)
        else:
            self.audio_rec = None

    def set_state_change_callback(self, callback: Callable):
        """设置状态变化回调函数"""
        self.on_state_change_callback = callback

    def handle_state_change(self, e):
        """处理音频录制状态变化"""
        state = e.data
        logging.info(f"Audio recorder state changed: {state}")

        if self.on_state_change_callback:
            self.on_state_change_callback(state)

    def start_recording(self):
        """开始录音"""
        if not self.audio_rec:
            logging.warning("Audio recording not available")
            return None

        self.recording_path = os.path.join(self.app_data_path, "test-audio-file.wav")
        logging.info(f"StartRecording: {self.recording_path}")

        try:
            self.audio_rec.start_recording(self.recording_path)
            return self.recording_path
        except Exception as e:
            logging.error(f"Error starting recording: {e}")
            return None

    def stop_recording(self):
        """停止录音"""
        if not self.audio_rec:
            logging.warning("Audio recording not available")
            return None

        logging.info("Stopping recording")
        try:
            output_path = self.audio_rec.stop_recording(wait_timeout=30)
            logging.info(f"StopRecording: {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error stopping recording: {e}")
            return None

    def speak_text(self, text):
        """使用文本转语音引擎朗读文本"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"语音合成失败: {str(e)}")

    def create_record_button(self, on_start_click, on_stop_click, visible=True):
        """创建录音按钮组件"""
        self.record_btn = ft.ElevatedButton(
            "开始录音",
            on_click=on_start_click,
            visible=visible and AUDIO_RECORDER_AVAILABLE,
        )
        self.stop_record_btn = ft.ElevatedButton(
            "停止录音",
            on_click=on_stop_click,
            visible=visible and AUDIO_RECORDER_AVAILABLE,
        )

        return ft.Row([self.record_btn, self.stop_record_btn])
