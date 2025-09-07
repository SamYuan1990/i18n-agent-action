import logging
import os
import sys

import flet as ft

# import flet_audio_recorder as ftar
import pyttsx3
from chatmessage import ChatMessage, Message
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
        self.recording_path = ""
        # self.audio_rec = ftar.AudioRecorder(
        #     audio_encoder=ftar.AudioEncoder.WAV,
        #     on_state_changed=self.handle_state_change,
        # )
        self.setup_ui()

    def handle_state_change(self, e):
        print(f"State Changed: {e.data}")

    def handle_start_recording(self, e):
        self.recording_path = os.path.join(self.app_data_path, "test-audio-file.wav")
        logging.info(f"StartRecording: {self.recording_path}")
        # .start_recording(self.recording_path)

    def handle_stop_recording(self, e):
        logging.info("tbd")
        # try:
        #     output_path = self.audio_rec.stop_recording(wait_timeout=30)
        #     logging.info(f"StopRecording: {output_path}")
        # except Exception as ex:
        #     logging.info(f"Error stopping recording: {ex}")

    def setup_ui(self):
        # 创建聊天消息区域
        self.chat = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )

        # 创建消息输入框
        self.new_message = ft.TextField(
            hint_text="请输入要翻译的文本...",
            multiline=True,
            min_lines=1,
            max_lines=5,
            shift_enter=True,
            filled=True,
            expand=True,
            on_submit=self.send_message_click,
        )

        # 创建发送按钮
        self.send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            tooltip="发送翻译",
            on_click=self.send_message_click,
        )

        # 创建翻译按钮（保留原有功能）
        self.translate_btn = ft.ElevatedButton(
            "Translate",
            icon=ft.Icons.TRANSLATE,
            on_click=self.translate_text,
            style=ft.ButtonStyle(padding=20),
        )

        # 创建录音按钮（注释掉并隐藏）
        self.record_btn = ft.ElevatedButton(
            "Start Audio Recorder",
            on_click=self.handle_start_recording,
            visible=False,  # 隐藏录音按钮
        )
        self.stp_record_btn = ft.ElevatedButton(
            "Stop Audio Recorder",
            on_click=self.handle_stop_recording,
            visible=False,  # 隐藏停止录音按钮
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
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
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
                ft.Container(
                    content=self.chat,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=5,
                    padding=10,
                    expand=True,
                ),
                ft.Row(
                    [
                        self.new_message,
                        self.send_button,
                    ]
                ),
                ft.Container(height=10),
                self.translate_btn,
                ft.Container(height=20),
                self.record_btn,
                self.stp_record_btn,
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
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

    def send_message_click(self, e):
        if self.new_message.value != "":
            # 添加用户消息到聊天
            self.add_message(
                Message(
                    user_name="User",
                    text=self.new_message.value,
                    message_type="chat_message",
                )
            )

            # 调用翻译功能
            self.translate_text(e)

            self.new_message.value = ""
            self.new_message.focus()
            self.page.update()

    def add_message(self, message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        self.chat.controls.append(m)
        self.page.update()

    def toggle_left_sidebar(self, e=None):
        self.left_sidebar.visible = not self.left_sidebar.visible
        # 更新分割线的可见性
        self.page.controls[0].controls[1].visible = self.left_sidebar.visible
        # 更新按钮图标
        self.left_sidebar_toggle.icon = (
            ft.Icons.MENU if not self.left_sidebar.visible else ft.Icons.ARROW_BACK
        )
        self.page.update()

    def toggle_right_sidebar(self, e=None):
        self.right_sidebar.visible = not self.right_sidebar.visible
        # 更新分割线的可见性
        self.page.controls[0].controls[3].visible = self.right_sidebar.visible
        # 更新按钮图标
        self.right_sidebar_toggle.icon = (
            ft.Icons.BAR_CHART
            if not self.right_sidebar.visible
            else ft.Icons.ARROW_FORWARD
        )
        self.page.update()

    def show_logs(self, e):
        # 读取日志文件并显示最近30条
        app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        log_file_path = (
            os.path.join(app_data_path, "app.log") if app_data_path else "app.log"
        )

        self.log_contents = []
        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                # 获取最后30行
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
        # 获取最后一条用户消息
        user_message = None
        for msg in reversed(self.chat.controls):
            if (
                isinstance(msg, ChatMessage)
                and msg.controls[1].controls[0].value == "User"
            ):
                user_message = msg.controls[1].controls[1].value
                break

        if not user_message:
            return

        # 模拟翻译功能
        LLM_client = self.left_sidebar.GenClient()
        storage = self.left_sidebar.get_storage()
        context = self.left_sidebar.getTranslationContext()
        span_mgr = Span_Mgr(storage)
        root_span = span_mgr.create_span("Root operation")
        TsAgent = translateAgent(LLM_client, span_mgr)
        engine = pyttsx3.init()

        if user_message:
            # 尝试找到匹配的模拟翻译
            result = TsAgent.translate(
                context, context.target_language, user_message, root_span
            )
            logging.info(result)

            # 添加翻译结果到聊天
            self.add_message(
                Message(
                    user_name="Agent",
                    text=result,
                    message_type="chat_message",
                )
            )

            self.left_sidebar.AppendHistory(user_message, result)
            engine.say(result)
            # play the speech
            engine.runAndWait()
