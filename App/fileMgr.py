import os
from typing import Dict
import logging
import flet as ft
from chatmessage import ChatMessage, Message

class FileManager:
    """文件管理类，处理所有文件相关操作"""

    def __init__(self, page: ft.Page, app_data_path, chat, translation_bridge):
        self.page = page
        self.app_data_path = app_data_path
        self.chat = chat
        self.translation_bridge = translation_bridge
        # 创建文件选择器
        self.file_picker = ft.FilePicker()
        self.page._services.append(self.file_picker)
        self.upload_button = ft.Button(
                    "Pick files",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=self.pick_files,
                )
        self.save_but = ft.Button(
                    "Save file",
                    icon=ft.Icons.SAVE,
                    on_click=self.open_save_file_dialog)

    async def pick_files(self,e):
        # open pick files dialog
        files = await self.file_picker.pick_files()
        #print("Picked files:", files)
        #print("Picked files:", )
        filename=files[0].name
        filepath=files[0].path
        logging.info(filename)
        logging.info(filepath)
        # 添加文件消息到聊天
        file_message = Message(
            user_name="User", text=filename, message_type="file", file_path=filepath
        )
        chat_message = ChatMessage(
            file_message,
            None,
            self.page,
            None,
        )
        self.chat.controls.append(chat_message)
        self.page.update()
        try:
            result = self.translation_bridge.translate_file(filepath, filename)
            translated_filename = f"translated_{filename}"
            translated_filepath = (
                os.path.join(self.app_data_path, translated_filename)
                if self.app_data_path
                else translated_filename
            )
            with open(translated_filepath, "w", encoding="utf-8") as f:
                f.write(result)
            file_message = Message(
                user_name="Agent",
                text=result,
                message_type="file",
                file_path=translated_filepath,
            )
            chat_message = ChatMessage(
                file_message,
                None,
                self.page,
                self.file_picker,
            )
            self.chat.controls.append(chat_message)
            self.page.update()

        except Exception as e:
            error_msg = f"文件处理失败: {str(e)}"
            logging.error(error_msg)
            self.add_message(
                Message(user_name="System", text=error_msg, message_type="error")
            )        

    async def open_save_file_dialog(self,e):
        save_file_path = await self.file_picker.save_file()
        print("save_file_path files:", save_file_path)
