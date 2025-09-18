import logging
import os
import shutil
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

    async def on_tap(self, e):
        if self.message_type == "file":
            # 文件消息：触发下载
            await self.download_file()
        else:
            # 文本消息：朗读
            self.engine.say(self.text)
            self.engine.runAndWait()

    async def download_file(self):
        """下载文件到用户选择的路径"""
        logging.info("download_file called")
        logging.info(self.file_path)
        save_file_path = await self.file_picker.save_file()
        logging.info(save_file_path)
        shutil.copy2(self.file_path, save_file_path)
        

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
