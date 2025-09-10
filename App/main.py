import logging
import os
from logging.handlers import RotatingFileHandler

import flet as ft
from TranslationApp import TranslationApp

logging.basicConfig(level=logging.INFO)

# 创建文件handler并设置级别
app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
log_file_path = os.path.join(app_data_path, "app.log")
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=1024 * 1024, backupCount=2, encoding="utf-8"  # 1MB
)
file_handler.setLevel(logging.DEBUG)

# 创建formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 将formatter添加到handler
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)


def main(page: ft.Page):
    # app = TranslationApp(page)
    TranslationApp(page)


ft.app(target=main, upload_dir=app_data_path)
