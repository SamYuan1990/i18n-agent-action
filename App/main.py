import logging
import os
from logging.handlers import RotatingFileHandler

import flet as ft
from App_model import get_app_model
from ChatApp import ChatApp
from FileDownloader import FileDownloader
from LLM_connect import LLM_config
from logViewer import LogViewer  # 添加LogViewer导入
from prompt_config import PromptConfig
from share_manager import ShareManager  # 导入ShareManager

logging.basicConfig(level=logging.INFO)

# 创建文件handler并设置级别
app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_tmp_path = os.getenv("FLET_APP_STORAGE_TEMP")
log_file_path = os.path.join(app_data_path, "app.log")
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=1024 * 1024, backupCount=2, encoding="utf-8"  # 1MB
)
file_handler.setLevel(logging.DEBUG)
os.environ["FLET_SECRET_KEY"] = "DEFAULT_SECRET_KEY_CHANGE_IN_PRODUCTION"
# 创建formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 将formatter添加到handler
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)
# end system config
# todo init app config, for code blocks below plays role as model level.
get_app_model()


# load UI, plays role as view level, the control logic impls via class itself.
def main(page: ft.Page):
    page.title = "i18n agent"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    file_downloader = FileDownloader(page)
    llm_config = LLM_config(page)
    prompt_config = PromptConfig(page)
    translation_app = ChatApp(page)
    log_viewer = LogViewer(page)  # 创建LogViewer实例
    share_manager = ShareManager(page)  # 创建ShareManager实例

    # 将分享对话框添加到页面overlay
    share_manager.add_to_page_overlay()

    # 当前选中的导航索引
    selected_index = 0

    # 创建内容区域
    content_area = ft.Container(content=translation_app.get_content(), expand=True)

    # 导航栏选择变化时的回调函数
    def navigate(e):
        nonlocal selected_index
        selected_index = e.control.selected_index

        # 根据选中的索引更新内容区域
        if selected_index == 0:
            content_area.content = translation_app.get_content()
        elif selected_index == 1:
            content_area.content = llm_config.get_content()
        elif selected_index == 2:
            content_area.content = prompt_config.get_content()
        elif selected_index == 3:
            content_area.content = file_downloader.get_content()
        elif selected_index == 4:
            # 分享页面 - 可以显示一些分享说明或直接打开分享对话框
            share_content = ft.Column(
                [
                    ft.Text("分享应用", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("将i18n agent分享给您的朋友和同事", size=16),
                    ft.Container(height=20),
                    ft.Button(
                        "打开分享选项",
                        icon=ft.Icons.SHARE,
                        on_click=share_manager.show_share_options,
                    ),
                    ft.Container(height=20),
                    ft.Text("支持的平台:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("• 微信", size=14),
                    ft.Text("• 微博", size=14),
                    ft.Text("• Twitter/X", size=14),
                    ft.Text("• Facebook", size=14),
                    ft.Text("• LinkedIn", size=14),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            )
            content_area.content = ft.Container(
                content=share_content,
                padding=20,
                expand=True,
            )
        elif selected_index == 5:  # 添加日志查看器选项
            content_area.content = log_viewer.get_content()

        page.update()

    # 创建导航栏
    navigation_rail = ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        # leading=ft.FloatingActionButton(
        #    icon=ft.Icons.MENU,
        #    content="菜单",
        #    on_click=lambda _: print("菜单按钮点击")
        # ),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CHAT,
                selected_icon=ft.Icons.CHAT,
                label="输入窗口",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS,
                selected_icon=ft.Icons.SETTINGS,
                label="设置LLM链接",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.EDIT_OUTLINED,
                selected_icon=ft.Icons.EDIT,
                label="设置Prompt",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.DOWNLOAD,
                selected_icon=ft.Icons.DOWNLOAD,
                label="下载语音识别",
            ),
            ft.NavigationRailDestination(  # 新增分享目的地
                icon=ft.Icons.SHARE,
                selected_icon=ft.Icons.SHARE,
                label="分享应用",
            ),
            ft.NavigationRailDestination(  # 添加日志查看器目的地
                icon=ft.Icons.LIST_ALT,
                selected_icon=ft.Icons.LIST_ALT,
                label="查看日志",
            ),
        ],
        on_change=navigate,
    )

    # 创建主布局
    page.add(
        ft.Row(
            [
                navigation_rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )


# 运行应用
ft.run(main)
