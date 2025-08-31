import json
import logging
import os
import sys

import flet as ft
from flet.security import decrypt, encrypt

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from AgentUtils.clientInfo import clientInfo  # noqa: E402
from Business.translateConfig import TranslationContext  # noqa: E402


class LeftSidebar(ft.Container):
    def __init__(self, app, storage):
        super().__init__()
        self.app = app
        self.visible = True
        self.storage = storage
        self.Trans_History = []
        if "history" in self.storage:
            self.Trans_History = self.storage.get("history")

        # 获取应用数据存储路径
        self.config_file_path = os.path.join(app.app_data_path, "app_config.json")

        # 获取或创建加密密钥
        self.secret_key = os.getenv("MY_APP_SECRET_KEY")
        if not self.secret_key:
            # 如果没有设置环境变量，使用默认密钥（生产环境中应使用更安全的方式）
            self.secret_key = "DEFAULT_SECRET_KEY_CHANGE_IN_PRODUCTION"
            logging.info(
                "警告: 使用默认加密密钥，生产环境中应设置MY_APP_SECRET_KEY环境变量"
            )

        # 尝试加载保存的配置
        saved_config = self.load_config()

        # 创建输入字段的引用，并使用保存的值或默认值
        self.api_key_field = ft.TextField(
            password=True,
            can_reveal_password=True,
            value=saved_config.get("api_key", ""),  # 使用保存的值或空字符串
        )

        self.base_url_field = ft.TextField(
            value=saved_config.get(
                "base_url", "https://api.deepseek.com"
            ),  # 使用保存的值或默认值
        )

        self.model_field = ft.TextField(
            value=saved_config.get("model", "deepseek-chat"),  # 使用保存的值或默认值
        )

        self.target_language_field = ft.TextField(
            value=saved_config.get("target_language", "zh"),  # 使用保存的值或默认值
        )

        self.reserved_word_field = ft.TextField(
            value=saved_config.get("reserved_word", ""),  # 使用保存的值或空字符串
        )

        self.auto_detect_switch = ft.Switch(
            label="自动检测语言",
            value=saved_config.get("auto_detect", True),  # 使用保存的值或默认值
        )

        self.pronunciation_switch = ft.Switch(
            label="发音功能",
            value=saved_config.get("pronunciation", False),  # 使用保存的值或默认值
        )

        self.save_history_switch = ft.Switch(
            label="保存翻译历史",
            value=saved_config.get("save_history", True),  # 使用保存的值或默认值
        )

        # 创建导航项目
        self.nav_items = [
            ft.NavigationRailDestination(
                label_content=ft.Text("Settings"),
                label="Settings",
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
            ),
            ft.NavigationRailDestination(
                label_content=ft.Text("历史"),
                label="历史",
                icon=ft.Icons.HISTORY_OUTLINED,
                selected_icon=ft.Icons.HISTORY,
            ),
        ]

        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            on_change=self.nav_change,
            destinations=self.nav_items,
            bgcolor=ft.Colors.BLUE_GREY_50,
            extended=True,
            height=110,
        )

        # 创建设置内容 - 使用可滚动容器
        self.settings_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Settings", style=ft.TextThemeStyle.HEADLINE_SMALL),
                    ft.Divider(),
                    # API Key 输入框
                    ft.Text("API Key:"),
                    self.api_key_field,
                    # Base URL 输入框
                    ft.Text("Base URL:"),
                    self.base_url_field,
                    # Model 输入框
                    ft.Text("Model:"),
                    self.model_field,
                    # Target Language 输入框
                    ft.Text("Target Language:"),
                    self.target_language_field,
                    # Reserved Word 输入框
                    ft.Text("Reserved Word:"),
                    self.reserved_word_field,
                    # 保留的开关选项
                    self.auto_detect_switch,
                    self.pronunciation_switch,
                    self.save_history_switch,
                    # 保存按钮固定在底部
                    ft.Container(
                        content=ft.ElevatedButton(
                            "保存设置",
                            icon=ft.Icons.SAVE,
                            on_click=self.save_settings,
                            width=200,
                        ),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=20),
                    ),
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            # 添加滚动和最大高度限制
            height=500,  # 限制最大高度
        )

        # 创建历史内容
        self.history_content = ft.Column(
            [
                ft.Text("翻译历史", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Divider(),
                ft.ListView(
                    controls=[
                        ft.ListTile(
                            title=ft.Text(item["original"]),
                            subtitle=ft.Text(item["translated"]),
                            trailing=ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                on_click=lambda e, idx=index: self.delete_history_item(
                                    idx
                                ),
                            ),
                        )
                        for index, item in enumerate(self.Trans_History)
                    ],
                    expand=True,
                ),
            ],
            visible=False,
            scroll=ft.ScrollMode.AUTO,
        )

        # 切换侧边栏按钮
        self.toggle_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK, on_click=lambda e: self.app.toggle_left_sidebar()
        )

        # 主内容容器
        self.main_content = ft.Column(
            [
                ft.Row(
                    [ft.Text("Option"), self.toggle_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                self.nav_rail,
                ft.Divider(),
                self.settings_content,
                self.history_content,
            ],
            expand=True,
        )

        super().__init__(
            content=self.main_content,
            padding=ft.padding.all(15),
            margin=ft.margin.all(0),
            width=300,  # 稍微增加宽度以容纳更多内容
            bgcolor=ft.Colors.BLUE_GREY_50,
            expand=True,
        )

    def AppendHistory(self, text, translate):
        self.Trans_History.append({"original": text, "translated": translate})
        self.storage["history"] = self.Trans_History
        self.update_history_display()

    def update_history_display(self):
        # 清空现有控件
        self.history_content.controls[2].controls.clear()

        # 重新生成所有历史记录项
        for index, item in enumerate(self.Trans_History):
            self.history_content.controls[2].controls.append(
                ft.ListTile(
                    title=ft.Text(item["original"]),
                    subtitle=ft.Text(item["translated"]),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=lambda e, idx=index: self.delete_history_item(idx),
                    ),
                )
            )

        # 刷新页面
        self.page.update()

    def load_config(self):
        """从本地文件加载配置，如果文件不存在则返回空字典"""
        config = {}
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, "r") as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        # 解密配置数据
                        decrypted_data = decrypt(encrypted_data, self.secret_key)
                        config = json.loads(decrypted_data)
        except Exception as e:
            logging.info(f"加载配置时出错: {e}")

        logging.info("load data from config file.")
        return config

    def save_config(self, config):
        """将配置保存到本地文件，使用加密"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)

            # 加密配置数据
            config_json = json.dumps(config)
            encrypted_data = encrypt(config_json, self.secret_key)

            # 写入文件
            with open(self.config_file_path, "w") as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            logging.info(f"保存配置时出错: {e}")
            return False

    def nav_change(self, e):
        index = e.control.selected_index
        if index == 0:  # 设置
            self.settings_content.visible = True
            self.history_content.visible = False
        elif index == 1:  # 历史
            self.settings_content.visible = False
            self.history_content.visible = True
        self.update()

    def save_settings(self, e):
        """保存设置按钮的点击事件处理函数"""
        # 收集所有配置值
        config = {
            "api_key": self.api_key_field.value,
            "base_url": self.base_url_field.value,
            "model": self.model_field.value,
            "target_language": self.target_language_field.value,
            "reserved_word": self.reserved_word_field.value,
            "auto_detect": self.auto_detect_switch.value,
            "pronunciation": self.pronunciation_switch.value,
            "save_history": self.save_history_switch.value,
        }

        # 保存配置到文件
        if self.save_config(config):
            # 显示保存成功的提示
            if self.app.page:
                self.app.page.snack_bar = ft.SnackBar(ft.Text("设置已保存!"))
                self.app.page.snack_bar.open = True
                self.app.page.update()

            logging.info("=== 配置已保存 ===")
            logging.info(f"Base URL: {self.base_url_field.value}")
            logging.info(f"Model: {self.model_field.value}")
            logging.info(f"Target Language: {self.target_language_field.value}")
            logging.info(f"Reserved Word: {self.reserved_word_field.value}")
            logging.info(f"自动检测语言: {self.auto_detect_switch.value}")
            logging.info(f"发音功能: {self.pronunciation_switch.value}")
            logging.info(f"保存翻译历史: {self.save_history_switch.value}")
            logging.info("=================")
        else:
            # 显示保存失败的提示
            if self.app.page:
                self.app.page.snack_bar = ft.SnackBar(ft.Text("保存设置失败!"))
                self.app.page.snack_bar.open = True
                self.app.page.update()

    def GenClient(self):
        LLM_Client = clientInfo(
            api_key=self.api_key_field.value,
            base_url=self.base_url_field.value,
            model=self.model_field.value,
            dryRun=False,
            local_cache=self.storage,
            usecache=True,
        )
        logging.info(f"自动检测语言: {self.auto_detect_switch.value}")
        logging.info(f"发音功能: {self.pronunciation_switch.value}")
        logging.info("=================")
        return LLM_Client

    def get_storage(self):
        return self.storage

    def getTranslationContext(self):
        context = TranslationContext(
            target_language=self.target_language_field.value,
            file_list="",
            configfile_path="",
            doc_folder="",
            reserved_word=self.reserved_word_field.value,
            max_files=20,
            disclaimers=False,
        )
        return context
