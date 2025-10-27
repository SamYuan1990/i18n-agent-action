import logging

import flet as ft
from chatlist import ChatList


class FileManager:
    """文件管理类，处理所有文件相关操作"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.chat = ChatList.getChatList(self.page)
        # 创建文件选择器
        self.file_picker = ft.FilePicker()
        self.page._services.append(self.file_picker)
        self.upload_button = ft.IconButton(
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.pick_files,
        )

    async def pick_files(self, e):
        # open pick files dialog
        files = await self.file_picker.pick_files()
        # print("Picked files:", files)
        # print("Picked files:", )
        filename = files[0].name
        filepath = files[0].path
        logging.info(filename)
        logging.info(filepath)
        # 添加文件消息到聊天
        self.chat.Add_newFileMsg(filename, filepath)
