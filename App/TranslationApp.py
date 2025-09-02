import logging
import os
import sys
import threading

import flet as ft
#import numpy as np

# import flet_audio_recorder as ftar
import pyttsx3
import sherpa_onnx
import sounddevice as sd
import soundfile as sf
from FileDownloader import FileDownloader
from leftsidebar import LeftSidebar
from rightsidebar import RightSidebar

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.ExpiringDictStorage import ExpiringDictStorage  # noqa: E402
from AgentUtils.span import Span_Mgr  # noqa: E402
from Business.translate import translateAgent  # noqa: E402


class TranslationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "i18n agent"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.log_contents = []
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.recording_path = ""
        self.recording_stream = None
        # self.audio_rec = ftar.AudioRecorder(
        #    audio_encoder=ftar.AudioEncoder.WAV,
        #    on_state_changed=self.handle_state_change,
        # )
        self.recognizer = self._create_recognizer()

        # 初始化文件下载器
        self.file_downloader = FileDownloader(page, self.app_data_path)

        # 定义需要下载的文件URL
        self.file_urls = {
            "base-encoder.onnx": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-encoder.onnx?download=true",  # 替换为实际URL1
            "base-decoder.onnx": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-decoder.onnx?download=true",  # 替换为实际URL2
            "base-tokens.txt": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-tokens.txt?download=true",  # 替换为实际URL3
        }

        self.setup_ui()

    def _create_recognizer(self):
        """创建并返回语音识别器"""
        # 检查文件是否存在，如果不存在则提示下载
        required_files = ["base-encoder.onnx", "base-decoder.onnx", "base-tokens.txt"]
        missing_files = []

        for file in required_files:
            file_path = os.path.join(self.app_data_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)

        if missing_files:
            logging.warning(f"缺少必要的模型文件: {missing_files}")
            # 这里可以添加自动下载逻辑或提示用户
            return None

        return sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=os.path.join(self.app_data_path, "base-encoder.onnx"),
            decoder=os.path.join(self.app_data_path, "base-decoder.onnx"),
            tokens=os.path.join(self.app_data_path, "base-tokens.txt"),
            language="",
        )

    def handle_state_change(self, e):
        print(f"State Changed: {e.data}")

    def audio_callback(self, indata, frames, time, status):
        """音频回调函数，实时收集音频数据"""
        if status:
            logging.warning(f"Audio stream status: {status}")
        if self.is_recording:
            self.recording.append(indata.copy())

    def handle_start_recording(self, e):
        self.recording_path = os.path.join(self.app_data_path, "test-audio-file.wav")
        logging.info(f"StartRecording: {self.recording_path}")
        self.recording = []
        self.is_recording = True
        self.recording_stream = sd.InputStream(
            samplerate=16000,
            channels=1,  # 单声道
            dtype="float32",
            callback=self.audio_callback,
        )
        self.recording_stream.start()
        # self.audio_rec.start_recording(self.recording_path)

    def handle_stop_recording(self, e):
        # try:
        #    output_path = self.audio_rec.stop_recording(wait_timeout=30)
        #    logging.info(f"StopRecording: {output_path}")
        # except Exception as ex:
        #    logging.info(f"Error stopping recording: {ex}")
        """停止录音并保存文件"""
        try:
            if self.recording_stream is not None:
                # 停止录音流
                self.recording_stream.stop()
                self.recording_stream.close()
                self.recording_stream = None

            self.is_recording = False

            if self.recording:
                # 合并所有录音数据
                #audio_data = np.concatenate(self.recording, axis=0)

                # 保存为WAV文件
                #sf.write(self.recording_path, audio_data, 16000)

                logging.info(f"StopRecording: {self.recording_path}")
                return self.recording_path
            else:
                logging.warning("No audio data was recorded")
                return None

        except Exception as ex:
            logging.error(f"Error stopping recording: {ex}")
            return None

    def handle_stt(self, e):
        # 检查必要的模型文件是否存在
        required_files = ["base-encoder.onnx", "base-decoder.onnx", "base-tokens.txt"]
        for file in required_files:
            file_path = os.path.join(self.app_data_path, file)
            if not os.path.exists(file_path):
                self.show_message(f"请先下载必要的模型文件: {file}")
                return

        self.recording_path = os.path.join(self.app_data_path, "test-audio-file.wav")
        audio, sample_rate = sf.read(
            self.recording_path, dtype="float32", always_2d=True
        )
        audio = audio[:, 0]
        if self.recognizer is None:
            self.recognizer = self._create_recognizer()
        stream = self.recognizer.create_stream()
        stream.accept_waveform(sample_rate, audio)
        self.recognizer.decode_stream(stream)
        self.text_input.value = stream.result.text
        logging.info(self.text_input.value)
        self.page.update()

    def start_download(self, e):
        """开始下载所有文件"""
        if not self.file_downloader.downloading:
            # 重置取消标志
            self.file_downloader.cancelled = False
            thread = threading.Thread(
                target=self.file_downloader.download_files,
                args=(self.file_urls,),
                daemon=True,
            )
            thread.start()

    def cancel_download(self, e):
        """取消下载"""
        if self.file_downloader.downloading:
            self.file_downloader.cancel_download()

    def show_message(self, message):
        """显示消息"""

        def _show():
            self.download_status_text.value = message
            self.page.update()

        self.page.run_task(_show)

    def setup_ui(self):
        # 创建下载相关的UI控件
        self.download_progress_bar = ft.ProgressBar(value=0, width=300)
        self.download_progress_text = ft.Text("0%")
        self.download_status_text = ft.Text("等待下载模型文件...")

        # 将UI控件关联到下载器
        self.file_downloader.download_progress_bar = self.download_progress_bar
        self.file_downloader.download_progress_text = self.download_progress_text
        self.file_downloader.download_status_text = self.download_status_text

        self.stt_btn = ft.ElevatedButton(
            "Start sound to text", on_click=self.handle_stt
        )

        self.record_btn = ft.ElevatedButton(
            "Start Audio Recorder", on_click=self.handle_start_recording
        )
        self.stp_record_btn = ft.ElevatedButton(
            "Stop Audio Recorder", on_click=self.handle_stop_recording
        )

        # 创建下载按钮
        self.download_btn = ft.ElevatedButton(
            "下载模型文件", icon=ft.Icons.DOWNLOAD, on_click=self.start_download
        )

        self.cancel_download_btn = ft.OutlinedButton(
            "取消下载", on_click=self.cancel_download
        )

        # 创建文本输入框
        self.text_input = ft.TextField(
            multiline=True,
            min_lines=5,
            max_lines=5,
            hint_text="请输入要翻译的文本...",
            expand=True,
            border_color=ft.Colors.BLUE_GREY_200,
        )

        # 创建翻译按钮
        self.translate_btn = ft.ElevatedButton(
            "Translate",
            icon=ft.Icons.TRANSLATE,
            on_click=self.translate_text,
            style=ft.ButtonStyle(padding=20),
        )

        # 创建左侧边栏切换按钮
        self.left_sidebar_toggle = ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip="显示/隐藏设置",
            on_click=self.toggle_left_sidebar,
        )

        # 创建右侧边栏切换按钮
        self.right_sidebar_toggle = ft.IconButton(
            icon=ft.Icons.BAR_CHART,
            tooltip="显示/隐藏统计",
            on_click=self.toggle_right_sidebar,
        )

        # 创建日志查看按钮
        self.log_view_toggle = ft.IconButton(
            icon=ft.Icons.LIST_ALT, tooltip="查看日志", on_click=self.show_logs
        )

        # 创建左侧边栏
        self.storage_file_path = os.path.join(self.app_data_path, "data_store.json")
        self.storage = ExpiringDictStorage(
            filename=self.storage_file_path, expiry_days=7
        )
        self.left_sidebar = LeftSidebar(self, self.storage)

        # 创建右侧边栏
        self.right_sidebar = RightSidebar(self)

        # 创建主内容区域
        self.main_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("i18n agent", style=ft.TextThemeStyle.HEADLINE_LARGE),
                        ft.Row(
                            [
                                self.left_sidebar_toggle,
                                self.right_sidebar_toggle,
                                self.log_view_toggle,
                            ],
                            spacing=5,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # 下载区域
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "模型文件下载", style=ft.TextThemeStyle.TITLE_MEDIUM
                                ),
                                self.download_status_text,
                                ft.Row(
                                    [
                                        self.download_progress_bar,
                                        self.download_progress_text,
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                ft.Row(
                                    [self.download_btn, self.cancel_download_btn],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=15,
                    )
                ),
                self.text_input,
                ft.Container(height=10),
                self.translate_btn,
                ft.Container(height=20),
                self.record_btn,
                self.stp_record_btn,
                self.stt_btn,
                ft.Text("Translate result:", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Container(
                    content=ft.Text(
                        "Translate result...", style=ft.TextThemeStyle.BODY_LARGE
                    ),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
                    border_radius=5,
                    width=self.page.width,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            spacing=15,
        )

        # 创建日志弹窗
        self.log_dialog = ft.AlertDialog(
            title=ft.Text("查看日志"),
            content=ft.Text(""),
            alignment=ft.alignment.center,
            on_dismiss=lambda e: logging.info("Dialog dismissed!"),
            title_padding=ft.padding.all(25),
        )

        self.page.overlay.append(self.log_dialog)
        # self.page.overlay.append(self.audio_rec)

        # 设置页面布局
        self.page.add(
            ft.Row(
                [
                    self.left_sidebar,
                    ft.VerticalDivider(width=1, visible=False),
                    self.main_content,
                    ft.VerticalDivider(width=1, visible=False),
                    self.right_sidebar,
                ],
                expand=True,
            )
        )

    def toggle_left_sidebar(self, e=None):
        self.left_sidebar.visible = not self.left_sidebar.visible
        self.page.controls[0].controls[1].visible = self.left_sidebar.visible
        self.left_sidebar_toggle.icon = (
            ft.Icons.MENU if not self.left_sidebar.visible else ft.Icons.ARROW_BACK
        )
        self.page.update()

    def toggle_right_sidebar(self, e=None):
        self.right_sidebar.visible = not self.right_sidebar.visible
        self.page.controls[0].controls[3].visible = self.right_sidebar.visible
        self.right_sidebar_toggle.icon = (
            ft.Icons.BAR_CHART
            if not self.right_sidebar.visible
            else ft.Icons.ARROW_FORWARD
        )
        self.page.update()

    def show_logs(self, e):
        app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        log_file_path = (
            os.path.join(app_data_path, "app.log") if app_data_path else "app.log"
        )

        self.log_contents = []
        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:] if len(lines) > 10 else lines
                    self.log_contents = [
                        ft.Text(line.strip(), size=5) for line in recent_lines
                    ]
            except Exception as e:
                self.log_contents = [
                    ft.Text(f"读取日志文件出错: {str(e)}", size=5, color=ft.Colors.RED)
                ]
        else:
            self.log_contents = [
                ft.Text("日志文件不存在", size=12, color=ft.Colors.RED)
            ]

        self.log_dialog.content.value = str(self.log_contents)
        self.log_dialog.update()
        self.page.open(self.log_dialog)

    def translate_text(self, e):
        # 检查必要的模型文件是否存在
        required_files = ["base-encoder.onnx", "base-decoder.onnx", "base-tokens.txt"]
        for file in required_files:
            file_path = os.path.join(self.app_data_path, file)
            if not os.path.exists(file_path):
                self.show_message(f"请先下载必要的模型文件: {file}")
                return

        # 模拟翻译功能
        LLM_client = self.left_sidebar.GenClient()
        storage = self.left_sidebar.get_storage()
        context = self.left_sidebar.getTranslationContext()
        span_mgr = Span_Mgr(storage)
        root_span = span_mgr.create_span("Root operation")
        TsAgent = translateAgent(LLM_client, span_mgr)
        text = self.text_input.value
        logging.info(text)
        engine = pyttsx3.init()

        if text:
            # 尝试找到匹配的模拟翻译
            result = TsAgent.translate(
                context, context.target_language, text, root_span
            )
            logging.info(result)
            # 更新翻译结果
            self.main_content.controls[-1].content.value = result
            self.page.update()
            self.left_sidebar.AppendHistory(text, result)
            engine.say(result)
            # play the speech
            engine.runAndWait()
