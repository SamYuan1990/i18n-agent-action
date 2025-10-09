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


class LLM_config:
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
            label="API密钥",
            password=True,
            can_reveal_password=True,
            value=saved_config.get("api_key", ""),  # 使用保存的值或空字符串
            hint_text="输入您的API密钥",
            border_color=ft.Colors.BLUE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
        )

        self.base_url_field = ft.TextField(
            label="API基础URL",
            value=saved_config.get(
                "base_url", "https://api.deepseek.com"
            ),  # 使用保存的值或默认值
            hint_text="输入API基础URL",
            border_color=ft.Colors.BLUE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
        )

        self.model_field = ft.TextField(
            label="模型名称",
            value=saved_config.get("model", "deepseek-chat"),  # 使用保存的值或默认值
            hint_text="输入模型名称",
            border_color=ft.Colors.BLUE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
        )

        self.target_language_field = ft.TextField(
            label="目标语言",
            value=saved_config.get("target_language", "zh"),  # 使用保存的值或默认值
            hint_text="输入目标语言代码",
            border_color=ft.Colors.BLUE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
        )

        configure_app(
            self.api_key_field.value,
            self.base_url_field.value,
            self.model_field.value,
            self.target_language_field.value,
        )

    def get_content(self):
        """返回导航栏的内容"""
        # 创建设置内容
        settings_content = ft.Container(
            content=ft.Column(
                [
                    # 标题
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.BLUE_700, size=24),
                                ft.Text(
                                    "模型配置",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_900,
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=ft.Padding(bottom=20, top=10, left=0, right=0),
                    ),
                    
                    # API Key 输入框
                    ft.Container(
                        content=self.api_key_field,
                        padding=ft.Padding(bottom=15, top=0, left=0, right=0),
                    ),
                    
                    # Base URL 输入框
                    ft.Container(
                        content=self.base_url_field,
                        padding=ft.Padding(bottom=15, top=0, left=0, right=0),
                    ),
                    
                    # 模型和语言在同一行
                    ft.Row(
                        [
                            ft.Container(
                                content=self.model_field,
                                expand=True,
                            ),
                            ft.Container(
                                content=self.target_language_field,
                                expand=True,
                            ),
                        ],
                        spacing=15,
                    ),
                    
                    # 保存按钮
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Button(
                                    "保存配置",
                                    icon=ft.Icons.SAVE,
                                    on_click=self.save_settings,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.BLUE_600,
                                        padding=ft.Padding(20, 15, 20, 15),
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding(top=20, bottom=10, left=0, right=0),
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=ft.Padding.all(25),
            margin=ft.Margin.all(10),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 0),
            ),
            expand=True,
        )

        # 主内容容器
        main_content = ft.Container(
            content=ft.Row(
                [
                    # 左侧空白
                    ft.Container(expand=1),
                    # 设置内容
                    ft.Container(
                        content=settings_content,
                        width=600,
                        expand=False,
                    ),
                    # 右侧空白
                    ft.Container(expand=1),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[ft.Colors.BLUE_50, ft.Colors.WHITE],
            ),
            padding=ft.Padding.all(0),
            margin=ft.Margin.all(0),
            expand=True,
        )

        return main_content

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
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("设置已保存!", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()

            logging.info("=== 配置已保存 ===")
            logging.info(f"Base URL: {self.base_url_field.value}")
            logging.info(f"Model: {self.model_field.value}")
            logging.info(f"Target Language: {self.target_language_field.value}")
            logging.info("=================")
        else:
            # 显示保存失败的提示
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("保存设置失败!", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
            )
            self.page.snack_bar.open = True
            self.page.update()