import json
import logging
import os
import sys

import flet as ft
from App_model import configure_app
from flet.security import decrypt, encrypt

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)


class LeftSidebar:
    def __init__(self, page):
        self.page = page
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        # 获取应用数据存储路径
        self.config_file_path = os.path.join(self.app_data_path, "app_config.json")

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

        configure_app(
            self.api_key_field.value,
            self.base_url_field.value,
            self.model_field.value,
            self.target_language_field.value,
        )

    def get_content(self):
        """返回导航栏的内容"""
        # 创建设置内容 - 使用可滚动容器
        settings_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Settings", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
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
                    # 保存按钮固定在底部
                    ft.Container(
                        content=ft.Button(
                            "保存设置",
                            icon=ft.Icons.SAVE,
                            on_click=self.save_settings,
                            width=200,
                        ),
                    ),
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            height=500,  # 限制最大高度
        )

        # 创建导航栏
        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    label="Settings",
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                )
            ],
            bgcolor=ft.Colors.BLUE_GREY_50,
            extended=True,
            height=110,
        )

        # 主内容容器
        main_content = ft.Column(
            [
                ft.Row(
                    [ft.Text("Option")],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                nav_rail,
                ft.Divider(),
                settings_content,
            ],
            expand=True,
        )

        return ft.Container(
            content=main_content,
            padding=ft.Padding.all(15),
            margin=ft.Margin.all(0),
            width=300,  # 稍微增加宽度以容纳更多内容
            bgcolor=ft.Colors.BLUE_GREY_50,
            expand=True,
        )

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

    def save_settings(self, e):
        """保存设置按钮的点击事件处理函数"""
        # 收集所有配置值
        config = {
            "api_key": self.api_key_field.value,
            "base_url": self.base_url_field.value,
            "model": self.model_field.value,
            "target_language": self.target_language_field.value,
            "reserved_word": "",
        }
        configure_app(
            self.api_key_field.value,
            self.base_url_field.value,
            self.model_field.value,
            self.target_language_field.value,
        )

        # 保存配置到文件
        if self.save_config(config):
            # 显示保存成功的提示
            self.page.snack_bar = ft.SnackBar(ft.Text("设置已保存!"))
            self.page.snack_bar.open = True
            self.page.update()

            logging.info("=== 配置已保存 ===")
            logging.info(f"Base URL: {self.base_url_field.value}")
            logging.info(f"Model: {self.model_field.value}")
            logging.info(f"Target Language: {self.target_language_field.value}")
            logging.info("=================")
        else:
            # 显示保存失败的提示
            self.page.snack_bar = ft.SnackBar(ft.Text("保存设置失败!"))
            self.page.snack_bar.open = True
            self.page.update()
