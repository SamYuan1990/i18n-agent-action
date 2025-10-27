import asyncio
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import flet as ft
import requests


class FileDownloader:
    def __init__(self, page):
        self.page = page
        self.downloading = False
        self.cancelled = False
        self.downloaded_size = 0
        self.total_size = 0
        self.current_file = ""

        # 定义所有可下载的文件及其所属组
        self.all_files = {
            # Whisper 文件
            "whisper/base-encoder.onnx": {
                "url": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-encoder.onnx?download=true",
                "group": "whisper",
            },
            "whisper/base-decoder.onnx": {
                "url": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-decoder.onnx?download=true",
                "group": "whisper",
            },
            "whisper/base-tokens.txt": {
                "url": "https://hf-mirror.com/csukuangfj/sherpa-onnx-whisper-base/resolve/main/base-tokens.txt?download=true",
                "group": "whisper",
            },
            # senseVoice 文件
            "sensevoice/model.int8.onnx": {
                "url": "https://hf-mirror.com/csukuangfj/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09/resolve/main/model.int8.onnx?download=true",
                "group": "sensevoice",
            },
            "sensevoice/tokens.txt": {
                "url": "https://hf-mirror.com/csukuangfj/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09/blob/main/tokens.txt?download=true",
                "group": "sensevoice",
            },
            # vad 文件
            "vad/silero_vad.onnx": {
                "url": "https://hf-mirror.com/csukuangfj/vad/resolve/main/silero_vad_v5.onnx?download=true",
                "group": "vad",
            },
        }

        # 定义文件组
        self.file_groups = {
            "whisper_only": {
                "whisper/base-encoder.onnx": self.all_files[
                    "whisper/base-encoder.onnx"
                ]["url"],
                "whisper/base-decoder.onnx": self.all_files[
                    "whisper/base-decoder.onnx"
                ]["url"],
                "whisper/base-tokens.txt": self.all_files["whisper/base-tokens.txt"][
                    "url"
                ],
            },
            "sensevoice_only": {
                "sensevoice/model.int8.onnx": self.all_files[
                    "sensevoice/model.int8.onnx"
                ]["url"],
                "sensevoice/tokens.txt": self.all_files["sensevoice/tokens.txt"]["url"],
            },
            "whisper_vad": {
                "whisper/base-encoder.onnx": self.all_files[
                    "whisper/base-encoder.onnx"
                ]["url"],
                "whisper/base-decoder.onnx": self.all_files[
                    "whisper/base-decoder.onnx"
                ]["url"],
                "whisper/base-tokens.txt": self.all_files["whisper/base-tokens.txt"][
                    "url"
                ],
                "vad/silero_vad.onnx": self.all_files["vad/silero_vad.onnx"]["url"],
            },
            "sensevoice_vad": {
                "sensevoice/model.int8.onnx": self.all_files[
                    "sensevoice/model.int8.onnx"
                ]["url"],
                "sensevoice/tokens.txt": self.all_files["sensevoice/tokens.txt"]["url"],
                "vad/silero_vad.onnx": self.all_files["vad/silero_vad.onnx"]["url"],
            },
            "all": {
                "whisper/base-encoder.onnx": self.all_files[
                    "whisper/base-encoder.onnx"
                ]["url"],
                "whisper/base-decoder.onnx": self.all_files[
                    "whisper/base-decoder.onnx"
                ]["url"],
                "whisper/base-tokens.txt": self.all_files["whisper/base-tokens.txt"][
                    "url"
                ],
                "sensevoice/model.int8.onnx": self.all_files[
                    "sensevoice/model.int8.onnx"
                ]["url"],
                "sensevoice/tokens.txt": self.all_files["sensevoice/tokens.txt"]["url"],
                "vad/silero_vad.onnx": self.all_files["vad/silero_vad.onnx"]["url"],
            },
        }

        # 当前选择的文件组
        self.selected_file_group = "whisper_only"
        self.file_urls = self.file_groups[self.selected_file_group]

        self.current_file_index = 0
        self.total_files = 0
        self.total_all_files_size = 0  # 所有文件的总大小
        self.downloaded_all_files_size = 0  # 所有文件已下载的总大小
        self.file_sizes = {}  # 存储每个文件的大小
        self.executor = ThreadPoolExecutor(max_workers=1)

        # UI 组件
        self.download_group_dropdown = ft.Dropdown(
            label="选择下载范围",
            value="whisper_only",
            options=[
                ft.dropdown.Option("whisper_only", "只下载Whisper相关文件"),
                ft.dropdown.Option("sensevoice_only", "只下载senseVoice相关文件"),
                ft.dropdown.Option("whisper_vad", "下载Whisper和VAD相关文件"),
                ft.dropdown.Option("sensevoice_vad", "下载senseVoice和VAD相关文件"),
                ft.dropdown.Option("all", "下载所有文件"),
            ],
            on_change=self.on_download_group_change,
            width=300,
        )

        self.download_progress_bar = ft.ProgressBar(value=0, width=300)
        self.download_progress_text = ft.Text("0%")
        self.download_status_text = ft.Text("等待下载语音模型文件...")
        self.download_btn = ft.Button(
            "下载语音模型文件", icon=ft.Icons.DOWNLOAD, on_click=self.start_download
        )
        self.cancel_download_btn = ft.OutlinedButton(
            "取消下载", on_click=self.cancel_download
        )

    def on_download_group_change(self, e):
        """处理下载范围选择变化"""
        self.selected_file_group = self.download_group_dropdown.value
        self.file_urls = self.file_groups[self.selected_file_group]
        logging.info(
            f"选择下载范围: {self.selected_file_group}, 文件数量: {len(self.file_urls)}"
        )

    def get_content(self):
        """返回下载页面的内容"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("语音模型下载", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("下载语音识别模型文件"),
                    self.download_group_dropdown,
                    self.download_status_text,
                    self.download_progress_bar,
                    ft.Row(
                        [self.download_progress_text],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            self.download_btn,
                            self.cancel_download_btn,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
        )

    def start_download(self, e):
        """开始下载所有文件"""
        if not self.downloading:
            # 更新当前选择的文件组
            self.selected_file_group = self.download_group_dropdown.value
            self.file_urls = self.file_groups[self.selected_file_group]

            # 重置取消标志
            self.cancelled = False
            thread = threading.Thread(
                target=self.download_files,
                args=(self.file_urls,),
                daemon=True,
            )
            thread.start()

    def download_files(self, file_urls):
        """依次下载多个文件"""
        self.file_urls = file_urls
        self.total_files = len(file_urls)
        self.current_file_index = 0
        self.cancelled = False
        self.downloaded_all_files_size = 0
        self.total_all_files_size = 0

        # 首先获取所有文件的大小
        self.get_all_file_sizes()

        # 在线程中执行下载任务，避免阻塞UI
        self.executor.submit(self.download_files_thread)

    def get_all_file_sizes(self):
        """获取所有文件的大小"""
        for file_path, url in self.file_urls.items():
            try:
                response = requests.head(url)
                file_size = int(response.headers.get("content-length", 0))
                self.file_sizes[file_path] = file_size
                self.total_all_files_size += file_size
                logging.info(f"文件 {file_path} 大小: {file_size} bytes")
            except Exception as ex:
                logging.error(f"无法获取文件 {file_path} 大小: {str(ex)}")
                # 如果无法获取文件大小，使用估计值
                self.file_sizes[file_path] = 0

        # 如果无法获取任何文件大小，使用文件数量作为进度基准
        if self.total_all_files_size == 0:
            self.total_all_files_size = self.total_files
            logging.info("使用文件数量作为进度基准")

    def download_files_thread(self):
        """在后台线程中下载多个文件"""
        file_items = list(self.file_urls.items())

        for i, (file_path, url) in enumerate(file_items):
            if self.cancelled:
                break

            self.current_file = file_path
            self.current_file_index = i
            self.download_file(url, file_path)

        if not self.cancelled:
            asyncio.run_coroutine_threadsafe(
                self.update_ui("所有文件下载完成！", 1.0), self.page.loop
            )
        else:
            asyncio.run_coroutine_threadsafe(
                self.update_ui("下载已取消", 0), self.page.loop
            )

        self.downloading = False

    def download_file(self, url, file_path):
        """下载单个文件到指定路径"""
        temp_file_path = None
        file_size = self.file_sizes.get(file_path, 0)

        try:
            logging.info(f"开始下载: {file_path}")
            self.downloading = True
            self.downloaded_size = 0
            self.total_size = file_size

            # 创建存储目录
            storage_dir = os.getenv("FLET_APP_STORAGE_DATA")
            if not storage_dir:
                storage_dir = "./data"  # 默认目录

            # 构建完整的文件路径
            full_file_path = os.path.join(storage_dir, file_path)
            file_dir = os.path.dirname(full_file_path)

            # 确保目录存在
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)

            temp_file_path = full_file_path + ".download"
            logging.info(f"下载到临时文件: {temp_file_path}")

            # 检查文件是否已存在
            if os.path.exists(full_file_path):
                logging.info(f"文件已存在: {file_path}")
                # 更新已下载的总大小
                if file_size > 0:
                    self.downloaded_all_files_size += file_size
                else:
                    # 如果不知道文件大小，使用平均值
                    self.downloaded_all_files_size += 1

                # 计算整体进度
                overall_progress = (
                    self.downloaded_all_files_size / self.total_all_files_size
                )

                asyncio.run_coroutine_threadsafe(
                    self.update_ui(f"文件已存在: {file_path}", overall_progress),
                    self.page.loop,
                )
                return

            asyncio.run_coroutine_threadsafe(
                self.update_ui(
                    f"开始下载: {file_path}",
                    self.downloaded_all_files_size / self.total_all_files_size,
                ),
                self.page.loop,
            )

            # 发起请求
            logging.info(f"请求URL: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()  # 确保请求成功

            # 如果之前不知道文件大小，现在尝试获取
            content_length = response.headers.get("content-length")
            if content_length:
                file_size = int(content_length)
                self.total_size = file_size
                self.file_sizes[file_path] = file_size
                self.total_all_files_size += file_size
                logging.info(f"更新文件大小: {file_size} bytes")

            # 下载文件
            downloaded = 0
            with open(temp_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.cancelled:
                        break

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.downloaded_size = downloaded

                        # 更新整体进度
                        if self.total_all_files_size > 0:
                            # 计算当前文件的进度贡献
                            # file_progress = (
                            #    downloaded / file_size if file_size > 0 else 0
                            # )
                            # 计算已下载的总大小（包括之前文件的大小）
                            current_total_downloaded = (
                                self.downloaded_all_files_size + downloaded
                            )
                            # 计算整体进度
                            overall_progress = (
                                current_total_downloaded / self.total_all_files_size
                            )
                            # 每下载一定量更新一次UI
                            if downloaded % 81920 == 0 or downloaded == file_size:
                                asyncio.run_coroutine_threadsafe(
                                    self.update_ui(
                                        f"下载 {file_path}: {self.format_size(downloaded)}/"
                                        f"{self.format_size(file_size) if file_size > 0 else '未知'}",
                                        overall_progress,
                                    ),
                                    self.page.loop,
                                )

            # 检查下载是否完成
            if not self.cancelled:
                # 获取实际文件大小
                actual_size = os.path.getsize(temp_file_path)
                logging.info(f"实际下载大小: {actual_size} bytes")

                # 更新文件大小信息
                if file_size == 0:
                    file_size = actual_size
                    self.file_sizes[file_path] = file_size
                    self.total_all_files_size += file_size

                # 更新已下载的总大小
                self.downloaded_all_files_size += file_size

                # 重命名临时文件
                os.rename(temp_file_path, full_file_path)
                logging.info(f"文件下载完成并重命名: {full_file_path}")

                # 计算整体进度
                overall_progress = (
                    self.downloaded_all_files_size / self.total_all_files_size
                )

                # 更新UI
                asyncio.run_coroutine_threadsafe(
                    self.update_ui(f"下载完成: {file_path}", overall_progress),
                    self.page.loop,
                )
            else:
                # 取消下载，删除临时文件
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        except Exception as ex:
            logging.error(f"下载失败: {str(ex)}")
            # 删除临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            # 计算整体进度
            overall_progress = (
                self.downloaded_all_files_size / self.total_all_files_size
            )

            asyncio.run_coroutine_threadsafe(
                self.update_ui(f"下载失败 {file_path}: {str(ex)}", overall_progress),
                self.page.loop,
            )
        finally:
            self.downloading = False

    def format_size(self, size):
        """格式化文件大小显示"""
        if size == 0:
            return "0B"

        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"

    async def update_ui(self, status, progress):
        """更新UI"""
        if hasattr(self, "download_status_text"):
            self.download_status_text.value = status
        if hasattr(self, "download_progress_bar"):
            self.download_progress_bar.value = progress
        if hasattr(self, "download_progress_text"):
            self.download_progress_text.value = f"{progress * 100:.1f}%"

        # 直接调用page.update()，不需要await
        self.page.update()

    def cancel_download(self, e=None):
        """取消下载"""
        self.cancelled = True

    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=False)
