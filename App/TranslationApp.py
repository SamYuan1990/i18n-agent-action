import logging
import os
import sys
import threading
import webbrowser
from urllib.parse import quote

import flet as ft
from chatmessage import ChatMessage, Message
from FileDownloader import FileDownloader
from fileMgr import FileManager
from leftsidebar import LeftSidebar
from soundmgr import SoundManager
from translationbridge import TranslationBridge

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.ExpiringDictStorage import ExpiringDictStorage  # noqa: E402

try:
    import onnxruntime  # noqa: F401
    import sherpa_onnx
    import soundfile as sf

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
        self.recognizer = None
        # 初始化存储
        self.storage_file_path = os.path.join(self.app_data_path, "data_store.json")
        logging.info(self.app_data_path)
        self.storage = ExpiringDictStorage(
            filename=self.storage_file_path, expiry_days=7
        )

        # 初始化翻译桥接器
        self.left_sidebar = LeftSidebar(self, self.storage)
        self.translation_bridge = TranslationBridge(self.left_sidebar)
        if not ONNX_AVAILABLE:
            try:
                import onnxruntime  # noqa: F401
            except ImportError:
                logging.info("onnxruntime not available, audio recording disabled")
            try:
                import sherpa_onnx  # noqa: F401
            except ImportError:
                logging.info("sherpa_onnx not available, audio recording disabled")
            try:
                import soundfile as sf  # noqa: F401
            except ImportError:
                logging.info("soundfile not available, audio recording disabled")
        self.setup_ui()

    def handle_audio_state_change(self, state):
        """处理音频状态变化"""
        logging.info(f"Audio state changed: {state}")
        # 可以在这里添加更多状态变化的处理逻辑

    def handle_start_recording(self, e):
        """处理开始录音"""
        self.sound_manager.start_recording()
        # if recording_path:
        #    self.add_message(
        #        Message(user_name="System", text="开始录音...", message_type="system")
        #    )

    def handle_stop_recording(self, e):
        """处理停止录音"""
        self.sound_manager.stop_recording()
        # if recording_path:
        # self.add_message(
        #    Message(
        #        user_name="System",
        #        text=f"录音已保存: {recording_path}",
        #        message_type="system",
        #    )
        # )
        # 这里可以添加录音文件的处理逻辑，比如自动转录和翻译
        if self.recognizer == None:  # noqa: E711
            self.recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
                encoder=os.path.join(self.app_data_path, "base-encoder.onnx"),
                decoder=os.path.join(self.app_data_path, "base-decoder.onnx"),
                tokens=os.path.join(self.app_data_path, "base-tokens.txt"),
                language="",
            )
        stream = self.recognizer.create_stream()
        self.recording_path = os.path.join(self.app_data_path, "test-audio-file.wav")
        audio, sample_rate = sf.read(
            self.recording_path, dtype="float32", always_2d=True
        )
        audio = audio[:, 0]
        stream.accept_waveform(sample_rate, audio)
        self.recognizer.decode_stream(stream)
        logging.info(stream.result.text)
        result = self.translation_bridge.translate_text(stream.result.text)
        logging.info(result)
        # 添加翻译结果到聊天
        self.add_message(
            Message(
                user_name="Agent",
                text=result,
                message_type="chat_message",
            )
        )

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

        # 创建日志查看按钮
        self.log_view_toggle = ft.IconButton(
            icon=ft.Icons.LIST_ALT, tooltip="查看日志", on_click=self.show_logs
        )
        
        # 创建分享按钮
        self.share_button = ft.IconButton(
            icon=ft.Icons.SHARE,
            tooltip="分享到社交媒体",
            on_click=self.show_share_options,
        )
        
        # 创建分享选项弹窗
        self.share_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("分享到社交媒体"),
            content=ft.Column(
                [
                    ft.Text("选择分享平台:", size=16),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CHAT,
                                icon_size=30,
                                tooltip="分享到微信",
                                on_click=lambda e: self.share_to_wechat(e),
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE},
                                    bgcolor={"": "#07C160"}
                                )
                            ),
                            ft.IconButton(
                                icon=ft.Icons.THUMB_UP,
                                icon_size=30,
                                tooltip="分享到微博",
                                on_click=lambda e: self.share_to_weibo(e),
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE},
                                    bgcolor={"": "#E6162D"}
                                )
                            ),
                            ft.IconButton(
                                icon=ft.Icons.TRENDING_UP,
                                icon_size=30,
                                tooltip="分享到Twitter/X",
                                on_click=lambda e: self.share_to_twitter(e),
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE},
                                    bgcolor={"": "#1DA1F2"}
                                )
                            ),
                            ft.IconButton(
                                icon=ft.Icons.PUBLIC,
                                icon_size=30,
                                tooltip="分享到Facebook",
                                on_click=lambda e: self.share_to_facebook(e),
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE},
                                    bgcolor={"": "#1877F2"}
                                )
                            ),
                            ft.IconButton(
                                icon=ft.Icons.WORK,
                                icon_size=30,
                                tooltip="分享到LinkedIn",
                                on_click=lambda e: self.share_to_linkedin(e),
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE},
                                    bgcolor={"": "#0077B5"}
                                )
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    )
                ],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            actions=[
                ft.TextButton("取消", on_click=self.close_share_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # 创建主内容区域
        if ONNX_AVAILABLE:
            self.main_content = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "i18n agent",
                                theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                            ),
                            ft.Text(
                                "Icons made by Good Ware from www.flaticon.com \nTranslation Content Generated by LLM",
                                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                            ),
                            ft.Row(
                                [
                                    self.left_sidebar_toggle,
                                    self.log_view_toggle,
                                    self.share_button,  # 添加分享按钮
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
                                        "模型文件下载",
                                        style=ft.TextThemeStyle.TITLE_MEDIUM,
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
                                "i18n agent",
                                theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                            ),
                            ft.Text(
                                "Icons made by Good Ware from www.flaticon.com \nTranslation Content Generated by LLM",
                                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                            ),
                            ft.Row(
                                [
                                    self.left_sidebar_toggle,
                                    self.log_view_toggle,
                                    self.share_button,  # 添加分享按钮
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
        self.page.overlay.append(self.share_dialog)

        # 设置页面布局
        self.page.add(
            ft.Row(
                [
                    self.left_sidebar,
                    ft.VerticalDivider(width=1, visible=False),
                    self.main_content,
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
        
    # 分享功能相关方法
    def show_share_options(self, e):
        """显示分享选项弹窗"""
        self.share_dialog.open = True
        self.page.update()
        
    def close_share_dialog(self, e):
        """关闭分享弹窗"""
        self.share_dialog.open = False
        self.page.update()
        
    def share_to_wechat(self, e):
        """分享到微信"""
        share_text = "我正在使用i18n agent翻译工具，非常强大！"
        share_url = "https://samyuan1990.github.io/i18n-agent-action/"  # 替换为实际URL
        webbrowser.open(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={quote(share_url)}")
        self.close_share_dialog(e)
        self.show_message("已生成微信分享二维码")
        
    def share_to_weibo(self, e):
        """分享到微博"""
        share_text = "我正在使用i18n agent翻译工具，非常强大！"
        share_url = "https://samyuan1990.github.io/i18n-agent-action/"  # 替换为实际URL
        webbrowser.open(f"https://service.weibo.com/share/share.php?title={quote(share_text)}&url={quote(share_url)}")
        self.close_share_dialog(e)
        self.show_message("正在打开微博分享页面...")
        
    def share_to_twitter(self, e):
        """分享到Twitter/X"""
        share_text = "我正在使用i18n agent翻译工具，非常强大！https://samyuan1990.github.io/i18n-agent-action/"
        webbrowser.open(f"https://twitter.com/intent/tweet?text={quote(share_text)}")
        self.close_share_dialog(e)
        self.show_message("正在打开Twitter分享页面...")
        
    def share_to_facebook(self, e):
        """分享到Facebook"""
        share_url = "https://samyuan1990.github.io/i18n-agent-action/"  # 替换为实际URL
        webbrowser.open(f"https://www.facebook.com/sharer/sharer.php?u={quote(share_url)}")
        self.close_share_dialog(e)
        self.show_message("正在打开Facebook分享页面...")
        
    def share_to_linkedin(self, e):
        """分享到LinkedIn"""
        share_url = "https://samyuan1990.github.io/i18n-agent-action/"  # 替换为实际URL
        webbrowser.open(f"https://www.linkedin.com/sharing/share-offsite/?url={quote(share_url)}")
        self.close_share_dialog(e)
        self.show_message("正在打开LinkedIn分享页面...")