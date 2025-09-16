# share_manager.py
import webbrowser
from urllib.parse import quote

import flet as ft


class ShareManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.share_dialog = None
        self._create_share_dialog()

    def _create_share_dialog(self):
        """创建分享选项弹窗"""
        self.share_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("分享到社交媒体"),
            content=ft.Column(
                [
                    ft.Text("选择分享平台:", size=16),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CHAT,
                                icon_size=30,
                                tooltip="分享到微信",
                                on_click=self.share_to_wechat,
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE}, bgcolor={"": "#07C160"}
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.THUMB_UP,
                                icon_size=30,
                                tooltip="分享到微博",
                                on_click=self.share_to_weibo,
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE}, bgcolor={"": "#E6162D"}
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.TRENDING_UP,
                                icon_size=30,
                                tooltip="分享到Twitter/X",
                                on_click=self.share_to_twitter,
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE}, bgcolor={"": "#1DA1F2"}
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.PUBLIC,
                                icon_size=30,
                                tooltip="分享到Facebook",
                                on_click=self.share_to_facebook,
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE}, bgcolor={"": "#1877F2"}
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.WORK,
                                icon_size=30,
                                tooltip="分享到LinkedIn",
                                on_click=self.share_to_linkedin,
                                style=ft.ButtonStyle(
                                    color={"": ft.Colors.WHITE}, bgcolor={"": "#0077B5"}
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            actions=[ft.TextButton("取消", on_click=self.close_share_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def create_share_button(self):
        """创建分享按钮"""
        return ft.IconButton(
            icon=ft.Icons.SHARE,
            tooltip="分享到社交媒体",
            on_click=self.show_share_options,
        )

    def show_share_options(self, e):
        """显示分享选项弹窗"""
        self.share_dialog.open = True
        self.page.update()

    def close_share_dialog(self, e):
        """关闭分享弹窗"""
        self.share_dialog.open = False
        self.page.update()

    def share_to_wechat(self, e):
        """分享到微信"""
        share_url = "https://samyuan1990.github.io/i18n-agent-action/"
        webbrowser.open(
            f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={quote(share_url)}"
        )
        self.close_share_dialog(e)
        self._show_message("已生成微信分享二维码")

    def share_to_weibo(self, e):
        """分享到微博"""
        share_text = "我正在使用i18n agent翻译工具，非常强大！"
        share_url = "https://samyuan1990.github.io/i18n-agent-action/"
        webbrowser.open(
            f"https://service.weibo.com/share/share.php?title={quote(share_text)}&url={quote(share_url)}"
        )
        self.close_share_dialog(e)
        self._show_message("正在打开微博分享页面...")

    def share_to_twitter(self, e):
        """分享到Twitter/X"""
        share_text = "我正在使用i18n agent翻译工具，非常强大！https://samyuan1990.github.io/i18n-agent-action/"
        webbrowser.open(f"https://twitter.com/intent/tweet?text={quote(share_text)}")
        self.close_share_dialog(e)
        self._show_message("正在打开Twitter分享页面...")

    def share_to_facebook(self, e):
        """分享到Facebook"""
        share_url = "https://samyuan1990.github.io/i18n-agent-action/"
        webbrowser.open(
            f"https://www.facebook.com/sharer/sharer.php?u={quote(share_url)}"
        )
        self.close_share_dialog(e)
        self._show_message("正在打开Facebook分享页面...")

    def share_to_linkedin(self, e):
        """分享到LinkedIn"""
        share_url = "https://samyuan1990.github.io/i18n-agent-action/"
        webbrowser.open(
            f"https://www.linkedin.com/sharing/share-offsite/?url={quote(share_url)}"
        )
        self.close_share_dialog(e)
        self._show_message("正在打开LinkedIn分享页面...")

    def _show_message(self, message):
        """显示消息（可以被子类重写）"""
        # 这里可以根据需要实现消息显示逻辑
        # 例如通过页面snackbar或者更新状态文本
        print(message)  # 临时使用print，实际应用中应该使用页面通知机制

    def add_to_page_overlay(self):
        """将分享对话框添加到页面overlay"""
        self.page.overlay.append(self.share_dialog)
