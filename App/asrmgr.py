import asyncio
import logging
import os
from pathlib import Path

import flet as ft
import flet_sherpa_onnx as fso
from chatlist import ChatList


class ASRManager:
    """声音管理类，处理所有音频相关功能"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.chat = ChatList.getChatList(self.page)
        self.fso_service = fso.FletSherpaOnnx()
        self.page._services.append(self.fso_service)

        # 初始化状态
        self.Init_Recognizer = False
        self.is_recording = False  # 录音状态标志
        self.current_recognizer = "Whisper"  # 默认识别器
        self.use_vad = False  # 是否使用VAD

        # 检查VAD文件是否存在
        self.vad_file_exists = self._check_vad_file_exists()

        # UI组件
        self.record_btn = None
        self.recognizer_dropdown = None
        self.vad_checkbox = None
        self.status_text = None

    def _check_vad_file_exists(self):
        """检查VAD模型文件是否存在"""
        vad_path = Path(self.app_data_path) / "vad" / "silero_vad.onnx"
        exists = vad_path.exists()
        logging.info(f"VAD文件存在: {exists}, 路径: {vad_path}")
        return exists

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
        logging.info(
            f"开始录音，使用识别器: {self.current_recognizer}, VAD: {self.use_vad}"
        )
        self.is_recording = True

        # 更新UI状态
        await self._update_ui_for_recording_start()

        # 初始化识别器
        try:
            await self._initialize_recognizer()
            self.Init_Recognizer = True
            logging.info("识别器初始化成功")

            # 开始录音
            await self.fso_service.StartRecording()
            logging.info("录音已开始")
            # todo vad voice logic here
            if self.use_vad:
                self.page.run_task(self._vad_result)

        except Exception as ex:
            logging.error(f"开始录音时出错: {ex}")
            await self.reset_recording_state()

    async def _initialize_recognizer(self):
        """根据选择的识别器和VAD设置初始化识别器"""
        if self.current_recognizer == "Whisper":
            if self.use_vad and self.vad_file_exists:
                await self.fso_service.CreateRecognizer(
                    recognizer="Whisper",
                    encoder=self.app_data_path + "/whisper/base-encoder.onnx",
                    decoder=self.app_data_path + "/whisper/base-decoder.onnx",
                    tokens=self.app_data_path + "/whisper/base-tokens.txt",
                    silerovad=self.app_data_path + "/vad/silero_vad.onnx",
                )
            else:
                await self.fso_service.CreateRecognizer(
                    recognizer="Whisper",
                    encoder=self.app_data_path + "/whisper/base-encoder.onnx",
                    decoder=self.app_data_path + "/whisper/base-decoder.onnx",
                    tokens=self.app_data_path + "/whisper/base-tokens.txt",
                )

        elif self.current_recognizer == "senseVoice":
            if self.use_vad and self.vad_file_exists:
                await self.fso_service.CreateRecognizer(
                    recognizer="senseVoice",
                    model=self.app_data_path + "/sensevoice/model.int8.onnx",
                    tokens=self.app_data_path + "/sensevoice/tokens.txt",
                    silerovad=self.app_data_path + "/vad/silero_vad.onnx",
                )
            else:
                await self.fso_service.CreateRecognizer(
                    recognizer="senseVoice",
                    model=self.app_data_path + "/sensevoice/model.int8.onnx",
                    tokens=self.app_data_path + "/sensevoice/tokens.txt",
                )

    async def stop_recording_logic(self):
        """停止录音的逻辑"""
        logging.info("停止录音")

        try:
            # 停止录音并获取结果
            result = await self.fso_service.StopRecording()
            logging.info(f"识别结果: {result}")

            # 处理识别结果
            if result and result.strip():
                await self.chat.Add_newMsg(result)

            await self.reset_recording_state()

        except Exception as ex:
            logging.error(f"停止录音时出错: {ex}")
            await self.reset_recording_state()

    async def reset_recording_state(self):
        """重置录音状态"""
        self.is_recording = False
        await self._update_ui_for_recording_stop()
        self.page.update()

    async def _update_ui_for_recording_start(self):
        """更新UI为开始录音状态"""
        if self.record_btn:
            self.record_btn.content = ft.Text("停止录音")
            self.record_btn.icon = ft.Icons.STOP
            self.record_btn.style = ft.ButtonStyle(color=ft.Colors.RED)

        if self.recognizer_dropdown:
            self.recognizer_dropdown.disabled = True

        if self.vad_checkbox:
            self.vad_checkbox.disabled = True

        if self.status_text:
            self.status_text.value = f"录音中... ({self.current_recognizer}{' + VAD' if self.use_vad else ''})"

    async def _update_ui_for_recording_stop(self):
        """更新UI为停止录音状态"""
        if self.record_btn:
            self.record_btn.content = ft.Text("开始录音")
            self.record_btn.icon = ft.Icons.MIC
            self.record_btn.style = ft.ButtonStyle(color=ft.Colors.BLUE)

        if self.recognizer_dropdown:
            self.recognizer_dropdown.disabled = False

        if self.vad_checkbox:
            self.vad_checkbox.disabled = (
                not self.vad_file_exists
            )  # 只有在VAD文件存在时才不禁用

        if self.status_text:
            self.status_text.value = "就绪"

    async def switch_recognizer(self, e):
        """切换识别器"""
        if e.control.value:
            self.current_recognizer = e.control.value
            logging.info(f"切换到识别器: {self.current_recognizer}")
            # 重置识别器状态
            self.Init_Recognizer = False
            if self.status_text:
                self.status_text.value = f"已切换到: {self.current_recognizer}"
            self.page.update()

    def toggle_vad(self, e):
        """切换VAD设置"""
        if self.vad_file_exists:  # 只有在VAD文件存在时才允许切换
            self.use_vad = e.control.value
            logging.info(f"VAD状态: {self.use_vad}")
            # 重置识别器状态
            self.Init_Recognizer = False
            if self.status_text:
                self.status_text.value = f"VAD: {'启用' if self.use_vad else '禁用'}"
            self.page.update()
        else:
            # 如果VAD文件不存在，强制取消选择
            e.control.value = False
            self.page.update()

    def create_control_panel(self):
        """创建完整的控制面板"""
        # 识别器选择下拉菜单
        self.recognizer_dropdown = ft.Dropdown(
            label="选择识别器",
            options=[
                ft.dropdown.Option("Whisper"),
                ft.dropdown.Option("senseVoice"),
            ],
            value=self.current_recognizer,
            on_change=self.switch_recognizer,
            width=200,
        )

        # VAD复选框
        self.vad_checkbox = ft.Checkbox(
            label="启用VAD (Voice Activity Detection)"
            + ("" if self.vad_file_exists else " (VAD模型文件不存在)"),
            value=self.use_vad and self.vad_file_exists,  # 如果文件不存在，强制为False
            on_change=self.toggle_vad,
            disabled=not self.vad_file_exists,  # 文件不存在时禁用
        )

        # 录音按钮
        self.record_btn = ft.Button(
            content=ft.Text("开始录音"),
            icon=ft.Icons.MIC,
            on_click=self.toggle_recording,
            style=ft.ButtonStyle(color=ft.Colors.BLUE),
        )

        # 状态文本
        self.status_text = ft.Text("就绪", size=16)

        # 返回完整的控制面板
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.recognizer_dropdown],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row([self.vad_checkbox], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([self.record_btn], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([self.status_text], alignment=ft.MainAxisAlignment.CENTER),
                ]
            ),
            padding=20,
            border=ft.Border().all(1, ft.Colors.BLUE_100),
            border_radius=10,
            margin=10,
        )

    async def _vad_result(self):
        """VAD数据监听循环"""
        # 保存上一轮处理的VAD数据
        last_vad_data = [""] * 5  # 初始化为5个空字符串

        while self.is_recording:
            await asyncio.sleep(10)
            if not self.is_recording:
                return

            vad_data = await self.fso_service.GetVADData()

            # 检查vad_data是否为空或全为空字符
            if not vad_data or all(item == "" for item in vad_data):
                continue

            # 检查是否有新的数据（与上一轮比较）
            new_data_found = False
            current_formatted_data = ""

            if isinstance(vad_data, (list, tuple)) and len(vad_data) == 5:
                # 构建当前轮次的数据，只保留与上一轮不同的非空数据
                new_data_lines = []
                for i, current_item in enumerate(vad_data):
                    if (
                        i < len(last_vad_data)
                        and current_item != last_vad_data[i]
                        and current_item != ""
                    ):
                        new_data_lines.append(str(current_item))
                        new_data_found = True

                if new_data_lines:
                    current_formatted_data = "\n".join(new_data_lines)
            else:
                # 如果不是预期的数组格式，转换为字符串比较
                current_str = str(vad_data)
                last_str = "".join(str(x) for x in last_vad_data)
                if current_str != last_str and current_str != "":
                    current_formatted_data = current_str
                    new_data_found = True

            # 只有在有新数据时才发送
            if new_data_found and current_formatted_data:
                await self.chat.Add_newMsg(current_formatted_data)

            # 更新上一轮数据
            if isinstance(vad_data, (list, tuple)) and len(vad_data) == 5:
                last_vad_data = list(vad_data)  # 创建副本
            else:
                # 如果不是数组格式，清空上一轮数据
                last_vad_data = [""] * 5
