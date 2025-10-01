import logging
import os
from typing import Callable, Optional

import flet as ft
import pyttsx3

import flet_audio_recorder as ftar
import soundfile as sf
import flet_sherpa_onnx as fso

class SoundManager:
    """声音管理类，处理所有音频相关功能"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.engine = pyttsx3.init()
        self.recording_path = ""
        self.on_state_change_callback: Optional[Callable] = None
        self.flet_sherpa_onnx = fso.FletSherpaOnnx()
        self.page._services.append(self.flet_sherpa_onnx)
        # 初始化音频录制器（如果可用）
        self.audio_rec = ftar.AudioRecorder()
            #ftar.AudioRecorderConfiguration(
            #        sample_rate=16000,
            #        channels=1,
            #        encoder=ftar.AudioEncoder.PCM16BITS
            #    )
        self.page._services.append(self.audio_rec)
        self.recording_path = os.path.join(self.app_data_path, "test-audio-file.wav")
        self.stt_path = os.path.join(self.app_data_path, "test-audio-file1.wav")

    async def start_recording(self):
        """开始录音"""
        if not self.audio_rec:
            logging.warning("Audio recording not available")
            return None
        logging.info(f"StartRecording: {self.recording_path}")

        try:
            await self.audio_rec.start_recording(self.recording_path)
            return self.recording_path
        except Exception as e:
            logging.error(f"Error starting recording: {e}")
            return None

    async def stop_recording(self):
        """停止录音"""
        if not self.audio_rec:
            logging.warning("Audio recording not available")
            return None

        logging.info("Stopping recording")
        try:
            output_path = await self.audio_rec.stop_recording()
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

    async def sound_to_text(self):
        await self.flet_sherpa_onnx.CreateRecognizer(
            encoder=self.app_data_path+"/base-encoder.onnx",
            decoder=self.app_data_path+"/base-decoder.onnx",
            tokens=self.app_data_path+"/base-tokens.txt"
        )
        audio, sample_rate = sf.read(self.recording_path, dtype="float32", always_2d=True)
        audio = audio[:, 0]
        sf.write(self.stt_path, audio, sample_rate, subtype='PCM_16', format='WAV')
        value = await flet_sherpa_onnx.STT(
            inputWav=self.stt_path
        )
        return value

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
