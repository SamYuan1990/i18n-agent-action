import logging
import os

import flet as ft


class LogViewer:
    """日志查看器类"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.log_display = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    def load_logs(self):
        """加载并显示日志内容"""
        # 读取日志文件
        app_tmp_path = os.getenv("FLET_APP_STORAGE_DATA")
        log_file_path = (
            os.path.join(app_tmp_path, "app.log") if app_tmp_path else "app.log"
        )

        self.log_display.controls.clear()
        
        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                # 获取最后50行
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                for line in recent_lines:
                    self.log_display.controls.append(
                        ft.Text(line.strip(), size=12, selectable=True)
                    )
            except Exception as e:
                self.log_display.controls.append(
                    ft.Text(f"读取日志文件出错: {str(e)}", size=12, color=ft.Colors.RED)
                )
        else:
            self.log_display.controls.append(
                ft.Text("日志文件不存在", size=12, color=ft.Colors.RED)
            )
        
        self.log_display.update()

    def get_content(self):
        """返回日志查看器的内容区域"""
        # 首次加载时读取日志
        # self.load_logs()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("应用日志", size=20, weight=ft.FontWeight.BOLD),
                    ft.Button(
                        "刷新日志",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e: self.load_logs()
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=self.log_display,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    padding=15,
                    expand=True
                )
            ], expand=True),
            padding=20,
            expand=True
        )