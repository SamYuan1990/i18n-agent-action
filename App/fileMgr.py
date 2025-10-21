import logging
import os

import flet as ft
from chatmessage import ChatMessage, Message
from translationbridge import translate_file  # noqa


class FileManager:
    """文件管理类，处理所有文件相关操作"""

    def __init__(self, page: ft.Page, chat):
        self.page = page
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.chat = chat
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
        if not files:
            return

        filename = files[0].name
        filepath = files[0].path
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

        # 添加加载提示
        loading_msg = Message(
            user_name="Agent",
            text="正在翻译文件...",
            message_type="text",
        )
        loading_chat_msg = ChatMessage(
            loading_msg,
            None,
            self.page,
            None,
        )
        self.chat.controls.append(loading_chat_msg)
        self.page.update()

        logging.info("send file to translation_bridge")

        # 使用 run_thread 在后台执行文件翻译
        self.page.run_thread(
            self._translate_file_and_update, filepath, filename, loading_chat_msg
        )

    def _translate_file_and_update(self, filepath, filename, loading_chat_msg):
        """在后台线程中执行文件翻译并更新结果"""
        try:
            result = translate_file(filepath, filename)
            translated_filename = f"translated_{filename}"
            translated_filepath = (
                os.path.join(self.app_data_path, translated_filename)
                if self.app_data_path
                else translated_filename
            )
            with open(translated_filepath, "w", encoding="utf-8") as f:
                f.write(result)

            # 在主线程中更新 UI
            def update_ui():
                # 移除加载消息
                if loading_chat_msg in self.chat.controls:
                    self.chat.controls.remove(loading_chat_msg)

                # 添加翻译结果
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

            # 使用 page 的方法确保 UI 更新在主线程执行
            self.page.run_task(update_ui)

        except Exception as e:
            error_msg = f"文件处理失败: {str(e)}"
            logging.error(error_msg)

            # 在主线程中显示错误
            def show_error():
                if loading_chat_msg in self.chat.controls:
                    self.chat.controls.remove(loading_chat_msg)

                error_message = Message(
                    user_name="Agent",
                    text=error_msg,
                    message_type="text",
                )
                error_chat_msg = ChatMessage(
                    error_message,
                    None,
                    self.page,
                    None,
                )
                self.chat.controls.append(error_chat_msg)
                self.page.update()

            self.page.run_task(show_error)
