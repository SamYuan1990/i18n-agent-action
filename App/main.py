import logging
import os
from logging.handlers import RotatingFileHandler

import flet as ft
from App_model import get_app_model
from FileDownloader import FileDownloader
from leftsidebar import LeftSidebar
from TranslationApp import TranslationApp

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
    left_sidebar = LeftSidebar(page)
    translation_app = TranslationApp(page)

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
            content_area.content = left_sidebar.get_content()
        elif selected_index == 2:
            content_area.content = file_downloader.get_content()
        # elif selected_index == 3:
        #    content_area.content = get_profile_content()

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
                label="翻译助手",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS,
                selected_icon=ft.Icons.SETTINGS,
                label="设置",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.DOWNLOAD,
                selected_icon=ft.Icons.DOWNLOAD,
                label="下载模型",
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
