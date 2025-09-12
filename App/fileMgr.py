import os
from typing import Dict

import flet as ft


class FileManager:
    """文件管理类，处理所有文件相关操作"""

    def __init__(self, page: ft.Page, app_data_path: str):
        self.page = page
        self.app_data_path = app_data_path
        self.prog_bars: Dict[str, ft.ProgressRing] = {}
        self.files_container = ft.Column()

        # 创建文件选择器
        self.file_picker = ft.FilePicker(
            on_result=self.file_picker_result, on_upload=self.on_upload_progress
        )
        self.file_picker_download = ft.FilePicker()
        self.page.overlay.extend([self.file_picker, self.file_picker_download])

    def file_picker_result(self, e: ft.FilePickerResultEvent):
        """处理文件选择结果"""
        if e.files is not None:
            self.prog_bars.clear()
            self.files_container.controls.clear()

            for f in e.files:
                prog = ft.ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                self.prog_bars[f.name] = prog
                self.files_container.controls.append(ft.Row([prog, ft.Text(f.name)]))

            self.page.update()
            self.upload_files(e.files)

    def on_upload_progress(self, e: ft.FilePickerUploadEvent):
        """处理文件上传进度"""
        if e.file_name in self.prog_bars:
            self.prog_bars[e.file_name].value = e.progress
            self.prog_bars[e.file_name].update()

    def upload_files(self, files):
        """上传文件"""
        uf = []
        for f in files:
            upload_url = self.page.get_upload_url(f.name, 600)
            uf.append(
                ft.FilePickerUploadFile(
                    f.name,
                    upload_url=upload_url,
                )
            )
        self.file_picker.upload(uf)

    def get_uploaded_file_path(self, filename):
        """获取上传文件的完整路径"""
        temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
        return os.path.join(temp_path, filename) if temp_path else filename
