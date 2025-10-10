import json
import logging
import os
import sys
from typing import List, Dict, Any, Optional

import flet as ft
from App_model import configure_app
from flet.security import decrypt, encrypt

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)


class PromptConfig:
    def __init__(self, page):
        self.page = page
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        # 获取提示词配置存储路径
        self.config_file_path = os.path.join(self.app_data_path, "prompt_config.json")

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
        self.role_field = ft.TextField(
            label="角色设定",
            value=saved_config.get("role", "You are a professional translator and a versatile expert with knowledge spanning various specialized fields, capable of handling technical, professional, and general content"),
            hint_text="设定AI的角色身份",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.PURPLE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
        )

        self.situation_field = ft.TextField(
            label="情境背景",
            value=saved_config.get("situation", "translating diverse content types including technical documentation, professional reports, academic materials, and general texts"),
            hint_text="描述当前的使用情境",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.PURPLE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
        )

        self.action_field = ft.TextField(
            label="行动指令",
            value=saved_config.get("action", "accurately preserve the original meaning, context, and nuance during translation while maintaining specialized terminology, proper nouns, command syntax, and special content fragments unchanged"),
            hint_text="AI需要执行的具体行动",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.PURPLE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
        )

        self.task_steps_field = ft.TextField(
            label="任务步骤 (最多7条)",
            value=self._list_to_string(saved_config.get("task_steps", [
                "Analyze the source text to identify specialized terms, special formatting, and structural elements",
                "Research appropriate expressions for proper nouns and terminology in the target language when necessary, and list all retained items in the result",
                "Translate explanatory text while ensuring professional accuracy",
                "Maintain terminology consistency and fully preserve all terminology and related content",
                "Adapt culturally specific examples as needed to facilitate target audience understanding",
                "Preserve all identified proper nouns and provide brief explanations in parentheses for ambiguous specialized terms or proper nouns",
                "Ensure code syntax, commands, and technical examples remain functional and unchanged",
            ])),
            hint_text="每一步骤用换行分隔，最多7条",
            multiline=True,
            min_lines=3,
            max_lines=8,
            border_color=ft.Colors.PURPLE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
            on_change=self._validate_task_steps
        )

        self.quality_assurance_field = ft.TextField(
            label="质量保证 (最多7条)",
            value=self._list_to_string(saved_config.get("quality_assurance", [
                "Do not add any extra explanations or markings",
                "Do not include any document chunking information (e.g., 'This is Part X')",
                "Strictly preserve the original formatting and structure",
                "Ensure all specialized terms are accurately translated or retained in their original form",
                "Verify that code syntax, commands, and technical examples remain functional",
                "Check that formatting and document structure are consistent",
                "Confirm that the translation maintains the same level of professional detail and accuracy as the original",
            ])),
            hint_text="质量检查要点，用换行分隔，最多7条",
            multiline=True,
            min_lines=3,
            max_lines=8,
            border_color=ft.Colors.PURPLE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
            on_change=self._validate_quality_assurance
        )

        self.output_structure_field = ft.TextField(
            label="输出结构（暂不开放修改）",
            value=json.dumps(saved_config.get("output_structure", {
                "content": "complete and accurate translation preserving all original elements",
                "proper_nouns": "list of all retained proper nouns and specialized terminology"
            }), indent=2, ensure_ascii=False),
            hint_text="期望的输出JSON结构",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.PURPLE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
            read_only=True,
        )

        self.use_custom_prompt_switch = ft.Switch(
            label="使用自定义系统提示词",
            value=saved_config.get("use_custom_sys_prompt", False),
            active_color=ft.Colors.PURPLE_600,
            disabled=True,
        )

        self.custom_prompt_field = ft.TextField(
            label="自定义系统提示词(暂不开放)",
            value=saved_config.get("custom_sys_prompt", ""),
            hint_text="输入完整的系统提示词（将覆盖以上所有设置）",
            multiline=True,
            min_lines=4,
            max_lines=8,
            border_color=ft.Colors.PURPLE_400,
            border_radius=10,
            filled=True,
            fill_color=ft.Colors.WHITE,
            expand=True,
            visible=self.use_custom_prompt_switch.value,
        )

        # 绑定开关变化事件
        self.use_custom_prompt_switch.on_change = self.on_custom_prompt_toggle

    def _list_to_string(self, value):
        """将列表转换为字符串格式"""
        if isinstance(value, list):
            return "\n".join(value)
        return str(value)

    def _string_to_list(self, value):
        """将字符串转换为列表，并限制最多7条"""
        if not value:
            return []
        lines = [line.strip() for line in value.split('\n') if line.strip()]
        return lines[:7]  # 限制最多7条

    def _validate_task_steps(self, e):
        """验证任务步骤不超过7条"""
        lines = self._string_to_list(self.task_steps_field.value)
        if len(lines) > 7:
            # 如果超过7条，截断并更新字段
            self.task_steps_field.value = "\n".join(lines[:7])
            self.page.update()
            # 显示警告
            self._show_warning("任务步骤最多只能有7条")

    def _validate_quality_assurance(self, e):
        """验证质量保证不超过7条"""
        lines = self._string_to_list(self.quality_assurance_field.value)
        if len(lines) > 7:
            # 如果超过7条，截断并更新字段
            self.quality_assurance_field.value = "\n".join(lines[:7])
            self.page.update()
            # 显示警告
            self._show_warning("质量保证要点最多只能有7条")

    def _show_warning(self, message):
        """显示警告信息"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.ORANGE,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def on_custom_prompt_toggle(self, e):
        """切换自定义提示词显示/隐藏"""
        self.custom_prompt_field.visible = self.use_custom_prompt_switch.value
        self.page.update()

    def get_content(self):
        """返回提示词配置界面的内容"""
        # 创建配置内容
        config_content = ft.Container(
            content=ft.Column(
                [
                    # 标题
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.EDIT, color=ft.Colors.PURPLE_700, size=24
                                ),
                                ft.Text(
                                    "提示词配置",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.PURPLE_900,
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=ft.Padding(bottom=20, top=10, left=0, right=0),
                    ),
                    
                    # 自定义提示词开关
                    ft.Container(
                        content=self.use_custom_prompt_switch,
                        padding=ft.Padding(bottom=15, top=0, left=0, right=0),
                    ),
                    
                    # 自定义提示词字段（条件显示）
                    ft.Container(
                        content=self.custom_prompt_field,
                        padding=ft.Padding(bottom=15, top=0, left=0, right=0),
                    ),
                    
                    # 基础配置字段（条件隐藏）
                    ft.Column(
                        [
                            # 角色和情境在同一行
                            ft.Row(
                                [
                                    ft.Container(
                                        content=self.role_field,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=self.situation_field,
                                        expand=True,
                                    ),
                                ],
                                spacing=15,
                            ),
                            
                            # 行动指令
                            ft.Container(
                                content=self.action_field,
                                padding=ft.Padding(bottom=15, top=0, left=0, right=0),
                            ),
                            
                            # 任务步骤和质量保证在同一行
                            ft.Row(
                                [
                                    ft.Container(
                                        content=self.task_steps_field,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=self.quality_assurance_field,
                                        expand=True,
                                    ),
                                ],
                                spacing=15,
                            ),
                            
                            # 输出结构
                            ft.Container(
                                content=self.output_structure_field,
                                padding=ft.Padding(bottom=15, top=0, left=0, right=0),
                            ),
                        ],
                        visible=not self.use_custom_prompt_switch.value,
                    ),
                    
                    # 保存按钮
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Button(
                                    "保存提示词配置",
                                    icon=ft.Icons.SAVE,
                                    on_click=self.save_settings,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.PURPLE_600,
                                        padding=ft.Padding(20, 15, 20, 15),
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                    ),
                                ),
                                ft.Button(
                                    "重置为默认",
                                    icon=ft.Icons.RESTORE,
                                    on_click=self.reset_to_default,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.PURPLE_600,
                                        bgcolor=ft.Colors.WHITE,
                                        padding=ft.Padding(20, 15, 20, 15),
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
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
                    # 配置内容
                    ft.Container(
                        content=config_content,
                        width=700,
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
                colors=[ft.Colors.PURPLE_50, ft.Colors.WHITE],
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
            logging.info(f"加载提示词配置时出错: {e}")

        logging.info("从提示词配置文件加载数据")
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
            logging.info(f"保存提示词配置时出错: {e}")
            return False

    def save_settings(self, e):
        """保存设置按钮的点击事件处理函数"""
        # 收集所有配置值
        config = {
            "role": self.role_field.value,
            "situation": self.situation_field.value,
            "action": self.action_field.value,
            "task_steps": self._string_to_list(self.task_steps_field.value),
            "quality_assurance": self._string_to_list(self.quality_assurance_field.value),
            "output_structure": json.loads(self.output_structure_field.value),
            "use_custom_sys_prompt": self.use_custom_prompt_switch.value,
            "custom_sys_prompt": self.custom_prompt_field.value,
        }
        # 保存配置到文件
        if self.save_config(config):
            # 显示保存成功的提示
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("提示词配置已保存!", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()

            logging.info("=== 提示词配置已保存 ===")
            logging.info(config)
            logging.info(f"角色: {self.role_field.value}")
            logging.info(f"任务步骤: {len(config['task_steps'])}条")
            logging.info(f"质量保证: {len(config['quality_assurance'])}条")
            logging.info(f"使用自定义提示词: {self.use_custom_prompt_switch.value}")
            logging.info("=======================")
        else:
            # 显示保存失败的提示
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("保存提示词配置失败!", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
            )
            self.page.snack_bar.open = True
            self.page.update()

    def reset_to_default(self, e):
        """重置为默认配置"""
        default_config = {
            "role": "You are a professional translator and a versatile expert with knowledge spanning various specialized fields, capable of handling technical, professional, and general content",
            "situation": "translating diverse content types including technical documentation, professional reports, academic materials, and general texts",
            "action": "accurately preserve the original meaning, context, and nuance during translation while maintaining specialized terminology, proper nouns, command syntax, and special content fragments unchanged",
            "task_steps": [
                "Analyze the source text to identify specialized terms, special formatting, and structural elements",
                "Research appropriate expressions for proper nouns and terminology in the target language when necessary, and list all retained items in the result",
                "Translate explanatory text while ensuring professional accuracy",
                "Maintain terminology consistency and fully preserve all terminology and related content",
                "Adapt culturally specific examples as needed to facilitate target audience understanding",
                "Preserve all identified proper nouns and provide brief explanations in parentheses for ambiguous specialized terms or proper nouns",
                "Ensure code syntax, commands, and technical examples remain functional and unchanged",
            ],
            "quality_assurance": [
                "Do not add any extra explanations or markings",
                "Do not include any document chunking information (e.g., 'This is Part X')",
                "Strictly preserve the original formatting and structure",
                "Ensure all specialized terms are accurately translated or retained in their original form",
                "Verify that code syntax, commands, and technical examples remain functional",
                "Check that formatting and document structure are consistent",
                "Confirm that the translation maintains the same level of professional detail and accuracy as the original",
            ],
            "output_structure": {
                "content": "complete and accurate translation preserving all original elements",
                "proper_nouns": "list of all retained proper nouns and specialized terminology"
            },
            "use_custom_sys_prompt": False,
            "custom_sys_prompt": "",
        }

        # 更新界面字段
        self.role_field.value = default_config["role"]
        self.situation_field.value = default_config["situation"]
        self.action_field.value = default_config["action"]
        self.task_steps_field.value = self._list_to_string(default_config["task_steps"])
        self.quality_assurance_field.value = self._list_to_string(default_config["quality_assurance"])
        self.output_structure_field.value = json.dumps(default_config["output_structure"], indent=2, ensure_ascii=False)
        self.use_custom_prompt_switch.value = default_config["use_custom_sys_prompt"]
        self.custom_prompt_field.value = default_config["custom_sys_prompt"]
        self.custom_prompt_field.visible = False

        # 更新页面
        self.page.update()

        # 显示重置成功的提示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("已重置为默认配置!", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLUE,
        )
        self.page.snack_bar.open = True
        self.page.update()
