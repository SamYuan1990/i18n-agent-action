# chat_list.py
import logging
import os
import flet as ft
from chatmessage import ChatMessage, Message
from translationbridge import translate_text,translate_file

class ChatList:
    _instance = None
    
    def __init__(self, page: ft.Page):
        self.page = page    
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")    
        # 创建 ListView 控件
        self.list_view = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )
    
    @classmethod
    def getChatList(cls, page: ft.Page):
        """全局单例方法，返回唯一的 ChatList 实例"""
        if cls._instance is None:
            cls._instance = cls(page)
            logging.info("Created new global ChatList instance")
        return cls._instance
    
    def get_widget(self):
        """返回 ListView 控件"""
        return self.list_view
    
    def add_message(self, message: Message):
        """添加消息到聊天列表"""
        # 创建聊天消息组件
        chat_message = ChatMessage(
                message, 
                self.page, 
                None
            )
            # 添加到控件列表和 ListView
        self.list_view.controls.append(chat_message)
        
        # 更新页面
        self.page.update()
    
    def clear_messages(self):
        """清空所有消息"""
        self.list_view.controls.clear()
        self.page.update()
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        self.list_view.scroll_to(offset=-1, duration=500)

    async def Add_newMsg(self,text):
        self.add_message(
            Message(
                user_name="User",
                text=text,
                message_type="chat_message",
            )
        )
        logging.info("send content to translation_bridge")
        result = translate_text(text)
        logging.info(result)
        self.add_message(
            Message(
                user_name="Agent",
                text=result,
                message_type="chat_message",
            )
        )

    async def Add_newFileMsg(self,filename,filepath):
        self.add_message(
            Message(
            user_name="User", text=filename, message_type="file", file_path=filepath
        )
        )
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
            self.add_message(
                Message(
                user_name="Agent",
                text=result,
                message_type="file",
                file_path=translated_filepath,
                )
            )

        except Exception as e:
            error_msg = f"文件处理失败: {str(e)}"
            logging.error(error_msg)