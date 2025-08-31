import logging
import os
import sys

import flet as ft
import pyttsx3
from leftsidebar import LeftSidebar
from rightsidebar import RightSidebar

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.ExpiringDictStorage import ExpiringDictStorage  # noqa: E402
from AgentUtils.span import Span_Mgr  # noqa: E402
from Business.translate import translateAgent  # noqa: E402


class TranslationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "i18n agent"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.setup_ui()
        self.log_contents = []

    def setup_ui(self):
        # 创建文本输入框
        self.text_input = ft.TextField(
            multiline=True,
            min_lines=5,
            max_lines=5,
            hint_text="请输入要翻译的文本...",
            expand=True,
            border_color=ft.Colors.BLUE_GREY_200,
        )

        # 创建翻译按钮
        self.translate_btn = ft.ElevatedButton(
            "Translate",
            icon=ft.Icons.TRANSLATE,
            on_click=self.translate_text,
            style=ft.ButtonStyle(padding=20),
        )

        # 创建左侧边栏切换按钮（放在主内容区域）
        self.left_sidebar_toggle = ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip="显示/隐藏设置",
            on_click=self.toggle_left_sidebar,
        )

        # 创建右侧边栏切换按钮（放在主内容区域）
        self.right_sidebar_toggle = ft.IconButton(
            icon=ft.Icons.BAR_CHART,
            tooltip="显示/隐藏统计",
            on_click=self.toggle_right_sidebar,
        )

        # 创建日志查看按钮（放在右侧边栏按钮的右边）
        self.log_view_toggle = ft.IconButton(
            icon=ft.Icons.LIST_ALT, tooltip="查看日志", on_click=self.show_logs
        )

        # 创建左侧边栏
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.storage_file_path = os.path.join(self.app_data_path, "data_store.json")
        self.storage = ExpiringDictStorage(
            filename=self.storage_file_path, expiry_days=7
        )
        self.left_sidebar = LeftSidebar(self, self.storage)

        # 创建右侧边栏
        self.right_sidebar = RightSidebar(self)

        # 创建主内容区域
        self.main_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("i18n agent", style=ft.TextThemeStyle.HEADLINE_LARGE),
                        ft.Row(
                            [
                                self.left_sidebar_toggle,
                                self.right_sidebar_toggle,
                                self.log_view_toggle,
                            ],
                            spacing=5,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.text_input,
                ft.Container(height=10),
                self.translate_btn,
                ft.Container(height=20),
                ft.Text("Translate result:", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Container(
                    content=ft.Text(
                        "Translate result...", style=ft.TextThemeStyle.BODY_LARGE
                    ),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
                    border_radius=5,
                    width=self.page.width,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )

        # 创建日志弹窗
        self.log_dialog = ft.AlertDialog(
            title=ft.Text("查看日志"),
            content=ft.Text(""),
            alignment=ft.alignment.center,
            on_dismiss=lambda e: logging.info("Dialog dismissed!"),
            title_padding=ft.padding.all(25),
        )

        self.page.overlay.append(self.log_dialog)

        # 设置页面布局
        self.page.add(
            ft.Row(
                [
                    self.left_sidebar,
                    ft.VerticalDivider(width=1, visible=False),
                    self.main_content,
                    ft.VerticalDivider(width=1, visible=False),
                    self.right_sidebar,
                ],
                expand=True,
            )
        )

    def toggle_left_sidebar(self, e=None):
        self.left_sidebar.visible = not self.left_sidebar.visible
        # 更新分割线的可见性
        self.page.controls[0].controls[1].visible = self.left_sidebar.visible
        # 更新按钮图标
        self.left_sidebar_toggle.icon = (
            ft.Icons.MENU if not self.left_sidebar.visible else ft.Icons.ARROW_BACK
        )
        self.page.update()

    def toggle_right_sidebar(self, e=None):
        self.right_sidebar.visible = not self.right_sidebar.visible
        # 更新分割线的可见性
        self.page.controls[0].controls[3].visible = self.right_sidebar.visible
        # 更新按钮图标
        self.right_sidebar_toggle.icon = (
            ft.Icons.BAR_CHART
            if not self.right_sidebar.visible
            else ft.Icons.ARROW_FORWARD
        )
        self.page.update()

    def show_logs(self, e):
        # 读取日志文件并显示最近30条
        app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        log_file_path = (
            os.path.join(app_data_path, "app.log") if app_data_path else "app.log"
        )

        self.log_contents = []
        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # 获取最后30行
                    recent_lines = lines[-10:] if len(lines) > 10 else lines
                    self.log_contents = [
                        ft.Text(line.strip(), size=5) for line in recent_lines
                    ]
            except Exception as e:
                self.log_contents = [
                    ft.Text(f"读取日志文件出错: {str(e)}", size=5, color=ft.Colors.RED)
                ]
        else:
            self.log_contents = [
                ft.Text("日志文件不存在", size=12, color=ft.Colors.RED)
            ]

        self.log_dialog.content.value = str(self.log_contents)
        self.log_dialog.update()
        self.page.open(self.log_dialog)

    def translate_text(self, e):
        # 模拟翻译功能
        LLM_client = self.left_sidebar.GenClient()
        storage = self.left_sidebar.get_storage()
        context = self.left_sidebar.getTranslationContext()
        span_mgr = Span_Mgr(storage)
        root_span = span_mgr.create_span("Root operation")
        TsAgent = translateAgent(LLM_client, span_mgr)
        text = self.text_input.value
        logging.info(text)
        engine = pyttsx3.init()

        if text:
            # 尝试找到匹配的模拟翻译
            result = TsAgent.translate(
                context, context.target_language, text, root_span
            )
            logging.info(result)
            # 更新翻译结果
            self.main_content.controls[-1].content.value = result
            self.page.update()
            self.left_sidebar.AppendHistory(text, result)
            engine.say(result)
            # play the speech
            engine.runAndWait()
