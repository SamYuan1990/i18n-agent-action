import logging
import os

import flet as ft
import flet_sherpa_onnx as fso
import pyttsx3
from chatmessage import ChatMessage, Message
from translationbridge import translate_text

class SoundManager:
    """声音管理类，处理所有音频相关功能"""

    def __init__(self, page: ft.Page, chat):
        self.page = page
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.engine = pyttsx3.init()
        self.chat = chat
        self.fso_service = fso.FletSherpaOnnx()
        self.page._services.append(self.fso_service)
        self.Init_Recognizer = False
        self.is_recording = False  # 录音状态标志
        self.record_btn = None  # 录音按钮

    async def toggle_recording(self, e):
        """切换录音状态：开始录音或停止录音"""
        if not self.is_recording:
            # 开始录音
            await self.start_recording_logic()
        else:
            # 停止录音
            await self.stop_recording_logic()

    async def start_recording_logic(self):
        """开始录音的逻辑"""
        logging.info("开始录音")
        self.is_recording = True
        
        # 更新按钮状态
        if self.record_btn:
            self.record_btn.content = ft.Text("停止录音")
            self.record_btn.icon = ft.Icons.STOP
            self.record_btn.style = ft.ButtonStyle(color=ft.Colors.RED)
        
        # 初始化识别器（如果尚未初始化）
        if not self.Init_Recognizer:
            try:
                await self.fso_service.CreateRecognizer(
                    recognizer="Whisper",
                    encoder=self.app_data_path + "/base-encoder.onnx",
                    decoder=self.app_data_path + "/base-decoder.onnx",
                    tokens=self.app_data_path + "/base-tokens.txt",
                )
                self.Init_Recognizer = True
                logging.info("识别器初始化成功")
            except Exception as ex:
                logging.error(f"识别器初始化失败: {ex}")
                await self.reset_recording_state()
                return
        
        # 开始录音
        try:
            await self.fso_service.StartRecording()
            logging.info("录音已开始")
        except Exception as ex:
            logging.error(f"开始录音时出错: {ex}")
            await self.reset_recording_state()

    async def stop_recording_logic(self):
        """停止录音的逻辑"""
        logging.info("停止录音")
        
        try:
            # 停止录音并获取结果
            result = await self.fso_service.StopRecording()
            logging.info(f"识别结果: {result}")
            
            # 处理识别结果
            if result and result.strip():
                await self.Add_newMsg(result)
            
            await self.reset_recording_state()
            
        except Exception as ex:
            logging.error(f"停止录音时出错: {ex}")
            await self.reset_recording_state()

    async def reset_recording_state(self):
        """重置录音状态"""
        self.is_recording = False
        
        # 更新按钮状态
        if self.record_btn:
            self.record_btn.content = ft.Text("开始录音")
            self.record_btn.icon = ft.Icons.MIC
            self.record_btn.style = ft.ButtonStyle(color=ft.Colors.BLUE)
        
        self.page.update()

    def speak_text(self, text):
        """使用文本转语音引擎朗读文本"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"语音合成失败: {str(e)}")

    def create_record_button(self):
        """创建录音按钮组件"""
        self.record_btn = ft.Button(
            content=ft.Text("开始录音"),
            icon=ft.Icons.MIC,
            on_click=self.toggle_recording,
            style=ft.ButtonStyle(color=ft.Colors.BLUE)
        )
        return self.record_btn

    def add_message(self, message: Message):
        """添加消息到聊天界面"""
        if message.message_type == "chat_message":
            m = ChatMessage(message, self.engine, self.page, None)
            self.chat.controls.append(m)
        self.page.update()

    async def Add_newMsg(self, text):
        """添加新消息（可全局调用）"""
        # 添加用户消息
        self.add_message(
            Message(
                user_name="User",
                text=text,
                message_type="chat_message",
            )
        )
        
        logging.info("send content to translation_bridge")    
        # 获取翻译结果
        result = translate_text(text)
        logging.info(result)
        
        # 添加代理回复
        self.add_message(
            Message(
                user_name="Agent",
                text=result,
                message_type="chat_message",
            )
        )