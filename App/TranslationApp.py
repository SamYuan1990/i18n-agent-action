import logging
import os
import sys
import threading

import flet as ft
from chatmessage import ChatMessage, Message
from FileDownloader import FileDownloader
from fileMgr import FileManager
from leftsidebar import LeftSidebar
from rightsidebar import RightSidebar
from soundmgr import SoundManager
from translationbridge import TranslationBridge

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.ExpiringDictStorage import ExpiringDictStorage  # noqa: E402

try:
    import onnxruntime
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.warning("onnxruntime not available, audio recording disabled")

class TranslationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "i18n agent"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.log_contents = []
        self.downloadzone = None
        # 初始化各个功能管理器
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.sound_manager = SoundManager(page, self.app_data_path)
        self.file_manager = FileManager(page, self.app_data_path)
        # 初始化文件下载器
        self.file_downloader = FileDownloader(page, self.app_data_path)
        # 定义需要下载的文件URL
        self.file_urls = {
            "base-encoder.onnx": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-encoder.onnx?download=true",  # 替换为实际URL1
            "base-decoder.onnx": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-decoder.onnx?download=true",  # 替换为实际URL2
            "base-tokens.txt": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-tokens.txt?download=true",  # 替换为实际URL3
        }
        # 设置音频状态变化回调
        self.sound_manager.set_state_change_callback(self.handle_audio_state_change)

        # 初始化存储
        self.storage_file_path = os.path.join(self.app_data_path, "data_store.json")
        logging.info(self.app_data_path)
        self.storage = ExpiringDictStorage(
            filename=self.storage_file_path, expiry_days=7
        )

        # 初始化翻译桥接器
        self.left_sidebar = LeftSidebar(self, self.storage)
        self.translation_bridge = TranslationBridge(self.left_sidebar)

        self.setup_ui()

    def handle_audio_state_change(self, state):
        """处理音频状态变化"""
        logging.info(f"Audio state changed: {state}")
        # 可以在这里添加更多状态变化的处理逻辑

    def handle_start_recording(self, e):
        """处理开始录音"""
        recording_path = self.sound_manager.start_recording()
        if recording_path:
            self.add_message(
                Message(user_name="System", text="开始录音...", message_type="system")
            )

    def handle_stop_recording(self, e):
        """处理停止录音"""
        recording_path = self.sound_manager.stop_recording()
        if recording_path:
            self.add_message(
                Message(
                    user_name="System",
                    text=f"录音已保存: {recording_path}",
                    message_type="system",
                )
            )
        
            # 这里可以添加录音文件的处理逻辑，比如自动转录和翻译

    def setup_ui(self):
        self.download_progress_bar = ft.ProgressBar(value=0, width=300)
        self.download_progress_text = ft.Text("0%")
        self.download_status_text = ft.Text("等待下载模型文件...")

        # 将UI控件关联到下载器
        if ONNX_AVAILABLE:
            self.file_downloader.download_progress_bar = self.download_progress_bar
            self.file_downloader.download_progress_text = self.download_progress_text
            self.file_downloader.download_status_text = self.download_status_text
            # 创建下载按钮
            self.download_btn = ft.ElevatedButton(
                "下载模型文件", icon=ft.Icons.DOWNLOAD, on_click=self.start_download
            )
            self.cancel_download_btn = ft.OutlinedButton(
                "取消下载", on_click=self.cancel_download
            )

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

        # 创建上传文件按钮
        self.upload_button = ft.IconButton(
            icon=ft.Icons.UPLOAD_FILE,
            tooltip="上传文件",
            on_click=lambda _: self.file_manager.file_picker.pick_files(
                allow_multiple=True
            ),
        )

        # 创建录音按钮
        self.record_buttons = self.sound_manager.create_record_button(
            self.handle_start_recording,
            self.handle_stop_recording,
            visible=True,  # 可以根据需要设置为False来隐藏录音按钮
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

        # 创建右侧边栏
        self.right_sidebar = RightSidebar(self)

        # 创建主内容区域
        if ONNX_AVAILABLE:
            self.main_content = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "i18n agent", theme_style=ft.TextThemeStyle.HEADLINE_LARGE
                            ),
                            ft.Text(
                                "Icons made by Good Ware from www.flaticon.com \nTranslation Content Generated by LLM",
                                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                            ),
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
                            self.upload_button,
                            self.send_button,
                        ]
                    ),
                    self.record_buttons,  # 添加录音按钮
                    self.file_manager.files_container,  # 显示文件上传进度
                    ft.Container(height=10),
                ],
                alignment=ft.MainAxisAlignment.START,
                expand=True,
            )
        else:
            self.main_content = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "i18n agent", theme_style=ft.TextThemeStyle.HEADLINE_LARGE
                            ),
                            ft.Text(
                                "Icons made by Good Ware from www.flaticon.com \nTranslation Content Generated by LLM",
                                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                            ),
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
                            self.upload_button,
                            self.send_button,
                        ]
                    ),
                    self.file_manager.files_container,  # 显示文件上传进度
                    ft.Container(height=10),
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

    def log_file_upload(self, filename):
        """记录文件上传日志并处理翻译"""
        filepath = self.file_manager.get_uploaded_file_path(filename)

        log_message = f"文件上传成功: {filename} -> {filepath}"
        logging.info(log_message)

        # 添加文件消息到聊天
        file_message = Message(
            user_name="User", text=filename, message_type="file", file_path=filepath
        )
        chat_message = ChatMessage(
            file_message,
            self.sound_manager.engine,
            self.page,
            self.file_manager.file_picker_download,
        )
        self.chat.controls.append(chat_message)
        self.page.update()

        try:
            # 执行文件翻译
            result = self.translation_bridge.translate_file(filepath, filename)

            # 创建临时文件保存翻译结果
            temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
            translated_filename = f"translated_{filename}"
            translated_filepath = (
                os.path.join(temp_path, translated_filename)
                if temp_path
                else translated_filename
            )

            with open(translated_filepath, "w", encoding="utf-8") as f:
                f.write(result)

            # 添加翻译结果到聊天
            file_message = Message(
                user_name="Agent",
                text=result,
                message_type="file",
                file_path=translated_filepath,
            )
            chat_message = ChatMessage(
                file_message,
                self.sound_manager.engine,
                self.page,
                self.file_manager.file_picker_download,
            )
            self.chat.controls.append(chat_message)
            self.page.update()

        except Exception as e:
            error_msg = f"文件处理失败: {str(e)}"
            logging.error(error_msg)
            self.add_message(
                Message(user_name="System", text=error_msg, message_type="error")
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
            m = ChatMessage(message, self.sound_manager.engine, self.page, None)
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
                    ft.Text(line.strip(), size=10) for line in recent_lines
                ]
            except Exception as e:
                self.log_contents = [
                    ft.Text(f"读取日志文件出错: {str(e)}", size=10, color=ft.Colors.RED)
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
            if isinstance(msg, ChatMessage) and msg.user_name == "User":
                user_message = msg.text
                break

        if not user_message:
            return

        # 执行翻译
        try:
            result = self.translation_bridge.translate_text(user_message)
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
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            logging.error(error_msg)
            self.add_message(
                Message(user_name="System", text=error_msg, message_type="error")
            )

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
