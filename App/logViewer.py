import flet as ft
import os
import logging

class LogViewer:
    """日志查看器类"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.log_contents = []
        # 创建日志弹窗
        self.dialog = ft.AlertDialog(
            title=ft.Text("查看日志"),
            content=ft.Text(""),
            on_dismiss=lambda e: logging.info("Dialog dismissed!"),
            title_padding=ft.Padding.all(25),
        )
        self.page.overlay.append(self.dialog)
    
    def show_logs(self, e):
        """显示日志对话框"""
        # 读取日志文件并显示最近30条
        app_tmp_path = os.getenv("FLET_APP_STORAGE_TEMP")
        log_file_path = (
            os.path.join(app_tmp_path, "app.log") if app_tmp_path else "app.log"
        )

        self.log_contents = []
        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                # 获取最后30行
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                self.log_contents = [
                    ft.Text(line.strip(), size=10) for line in recent_lines
                ]
            except Exception as e:
                self.log_contents = [
                    ft.Text(f"读取日志文件出错: {str(e)}", size=10, color=ft.Colors.RED)
                ]
        else:
            self.log_contents = [
                ft.Text("日志文件不存在", size=12, color=ft.Colors.RED)
            ]

        self.dialog.content.value = str(self.log_contents)
        self.dialog.update()
        self.page.show_dialog(self.dialog)

