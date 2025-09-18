import logging
import os

import flet as ft


class Message:
    def __init__(
        self,
        user_name: str,
        text: str,
        message_type: str,
        file_path: str = None,
        file_data: bytes = None,
    ):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.file_path = file_path  # 文件路径，如果是文件消息
        self.file_data = file_data  # 文件数据（字节）


class ChatMessage(ft.Row):
    def __init__(self, message, engine, page, file_picker):
        super().__init__()
        self.engine = engine
        self.text = message.text
        self.user_name = message.user_name
        self.message_type = message.message_type
        self.file_path = message.file_path
        self.file_data = message.file_data
        self._page = page
        self.file_picker = file_picker  # 使用共享的file_picker实例
        self.vertical_alignment = ft.CrossAxisAlignment.START

        # 保存当前文件数据和名称的临时变量
        self._current_file_data = None
        self._current_file_name = None

        # 根据消息类型创建不同的内容
        if self.message_type == "file":
            # 文件消息
            if self.file_path:
                file_name = os.path.basename(self.file_path)
            elif self.file_data:
                file_name = "received_file.dat"
            else:
                file_name = "未知文件"

            content = ft.Row(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(self.get_initials(message.user_name)),
                        color=ft.Colors.WHITE,
                        bgcolor=self.get_avatar_color(message.user_name),
                    ),
                    ft.Column(
                        [
                            ft.Text(message.user_name, weight="bold"),
                            ft.Text(f"发送了一个文件: {file_name}", selectable=True),
                            ft.Text(message.text, selectable=True),
                            ft.Text(
                                "点击下载文件",
                                size=12,
                                color=ft.Colors.BLUE,
                                italic=True,
                            ),
                        ],
                        tight=True,
                        spacing=5,
                    ),
                ]
            )
        else:
            # 文本消息
            content = ft.Row(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(self.get_initials(message.user_name)),
                        color=ft.Colors.WHITE,
                        bgcolor=self.get_avatar_color(message.user_name),
                    ),
                    ft.Column(
                        [
                            ft.Text(message.user_name, weight="bold"),
                            ft.Text(message.text, selectable=True),
                        ],
                        tight=True,
                        spacing=5,
                    ),
                ]
            )

        # 用GestureDetector包装内容以添加点击事件
        self.controls = [
            ft.GestureDetector(
                content=content,
                on_tap=self.on_tap,
            )
        ]

    def on_tap(self, e):
        if self.message_type == "file":
            # 文件消息：触发下载
            self.download_file()
        else:
            # 文本消息：朗读
            self.engine.say(self.text)
            self.engine.runAndWait()

    def download_file(self):
        """下载文件到用户选择的路径"""
        logging.info("download_file called")

        if self.file_path and os.path.exists(self.file_path):
            # 从文件路径读取数据
            try:
                with open(self.file_path, "rb") as f:
                    file_data = f.read()
                file_name = os.path.basename(self.file_path)
                self.initiate_download(file_data, file_name)
            except Exception as e:
                self.show_error(f"读取文件失败: {str(e)}")

        elif self.file_data:
            # 直接使用文件数据
            file_name = "downloaded_file.dat"
            self.initiate_download(self.file_data, file_name)
        else:
            self.show_error("文件数据不可用")

    def initiate_download(self, file_data: bytes, file_name: str):
        """初始化文件下载"""
        logging.info(f"initiate_download: {file_name}")

        try:
            # 保存文件数据和名称
            self._current_file_data = file_data
            self._current_file_name = file_name

            # 设置file_picker的回调
            self.file_picker.on_result = self.on_file_picked

            # 打开文件保存对话框
            logging.info("Calling save_file")
            self.file_picker.save_file(
                dialog_title="选择保存位置",
                file_name=file_name,
                file_type=ft.FilePickerFileType.ANY,
            )
            logging.info("save_file called successfully")

        except Exception as e:
            logging.error(f"初始化下载失败: {str(e)}")
            self.show_error(f"初始化下载失败: {str(e)}")

    def on_file_picked(self, e: ft.FilePickerUploadEvent):
        """文件选择完成后的回调"""
        logging.info(f"on_file_picked: {e.path}")

        if e.path and self._current_file_data is not None:
            try:
                # 使用Python内置方法写入文件
                with open(e.path, "wb") as f:
                    f.write(self._current_file_data)

                self.show_success(f"文件已保存到: {e.path}")

            except PermissionError:
                self.show_error("没有权限保存文件到该位置")
            except OSError as oe:
                self.show_error(f"系统错误: {str(oe)}")
            except Exception as ex:
                self.show_error(f"保存文件时出错: {str(ex)}")

            # 清理临时数据
            self._current_file_data = None
            self._current_file_name = None

        elif not e.path:
            # 用户取消了操作
            logging.info("用户取消了文件选择")
        else:
            self.show_error("文件数据不可用")

    def show_success(self, message: str):
        """显示成功消息"""
        self._page.snack_bar = ft.SnackBar(
            content=ft.Text(message), bgcolor=ft.Colors.GREEN
        )
        self._page.snack_bar.open = True
        self._page.update()

    def show_error(self, message: str):
        """显示错误消息"""
        self._page.snack_bar = ft.SnackBar(
            content=ft.Text(message), bgcolor=ft.Colors.RED
        )
        self._page.snack_bar.open = True
        self._page.update()

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]
