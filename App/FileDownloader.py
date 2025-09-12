import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import requests


class FileDownloader:
    def __init__(self, page, app_data_path):
        self.page = page
        self.app_data_path = app_data_path
        self.downloading = False
        self.cancelled = False
        self.downloaded_size = 0
        self.total_size = 0
        self.current_file = ""
        self.file_urls = {}
        self.current_file_index = 0
        self.total_files = 0
        self.total_all_files_size = 0  # 所有文件的总大小
        self.downloaded_all_files_size = 0  # 所有文件已下载的总大小
        self.file_sizes = {}  # 存储每个文件的大小
        self.executor = ThreadPoolExecutor(max_workers=1)

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
        for file_name, url in self.file_urls.items():
            try:
                response = requests.head(url)
                file_size = int(response.headers.get("content-length", 0))
                self.file_sizes[file_name] = file_size
                self.total_all_files_size += file_size
                logging.info(f"文件 {file_name} 大小: {file_size} bytes")
            except Exception as ex:
                logging.error(f"无法获取文件 {file_name} 大小: {str(ex)}")
                # 如果无法获取文件大小，使用估计值
                self.file_sizes[file_name] = 0

        # 如果无法获取任何文件大小，使用文件数量作为进度基准
        if self.total_all_files_size == 0:
            self.total_all_files_size = self.total_files
            logging.info("使用文件数量作为进度基准")

    def download_files_thread(self):
        """在后台线程中下载多个文件"""
        file_items = list(self.file_urls.items())

        for i, (file_name, url) in enumerate(file_items):
            if self.cancelled:
                break

            self.current_file = file_name
            self.current_file_index = i
            self.download_file(url, file_name)

        if not self.cancelled:
            asyncio.run_coroutine_threadsafe(
                self.update_ui("所有文件下载完成！", 1.0), self.page.loop
            )
        else:
            asyncio.run_coroutine_threadsafe(
                self.update_ui("下载已取消", 0), self.page.loop
            )

        self.downloading = False

    def download_file(self, url, filename):
        """下载单个文件"""
        temp_file_path = None
        file_size = self.file_sizes.get(filename, 0)

        try:
            logging.info(f"开始下载: {filename}")
            self.downloading = True
            self.downloaded_size = 0
            self.total_size = file_size

            # 创建存储目录
            storage_dir = self.app_data_path
            if not os.path.exists(storage_dir):
                os.makedirs(storage_dir)

            file_path = os.path.join(storage_dir, filename)
            temp_file_path = file_path + ".download"
            logging.info(f"下载到临时文件: {temp_file_path}")

            # 检查文件是否已存在
            if os.path.exists(file_path):
                logging.info(f"文件已存在: {filename}")
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
                    self.update_ui(f"文件已存在: {filename}", overall_progress),
                    self.page.loop,
                )
                return

            asyncio.run_coroutine_threadsafe(
                self.update_ui(
                    f"开始下载: {filename}",
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
                self.file_sizes[filename] = file_size
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
                            file_progress = (
                                downloaded / file_size if file_size > 0 else 0
                            )
                            # 计算已下载的总大小（包括之前文件的大小）
                            current_total_downloaded = (
                                self.downloaded_all_files_size + downloaded
                            )
                            # 计算整体进度
                            overall_progress = (
                                current_total_downloaded / self.total_all_files_size
                            )
                            #                             overall_progress = (self.current_file_index / self.total_files) + \
                            #                 (file_progress / self.total_files)
                            # 每下载一定量更新一次UI
                            if downloaded % 81920 == 0 or downloaded == file_size:
                                # logging.info(file_progress)
                                # logging.info(current_total_downloaded)
                                # logging.info(overall_progress)
                                asyncio.run_coroutine_threadsafe(
                                    self.update_ui(
                                        f"下载 {filename}: {self.format_size(downloaded)}/"
                                        f"{self.format_size(file_size) if file_size > 0 else '未知'}",
                                        file_progress,
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
                    self.file_sizes[filename] = file_size
                    self.total_all_files_size += file_size

                # 更新已下载的总大小
                self.downloaded_all_files_size += file_size

                # 重命名临时文件
                os.rename(temp_file_path, file_path)
                logging.info(f"文件下载完成并重命名: {file_path}")

                # 计算整体进度
                overall_progress = (
                    self.downloaded_all_files_size / self.total_all_files_size
                )

                # 更新UI
                asyncio.run_coroutine_threadsafe(
                    self.update_ui(f"下载完成: {filename}", overall_progress),
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
                self.update_ui(f"下载失败 {filename}: {str(ex)}", overall_progress),
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

    def cancel_download(self):
        """取消下载"""
        self.cancelled = True

    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=False)