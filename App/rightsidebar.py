import flet as ft


class RightSidebar(ft.Container):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.visible = True
        self.translate_count = 3

        # 切换侧边栏按钮
        self.toggle_button = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            on_click=lambda e: self.app.toggle_right_sidebar(),
        )

        super().__init__(
            content=ft.Column(
                [
                    ft.Row(
                        [ft.Text("统计信息"), self.toggle_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    ft.Text("总翻译次数: " + str(self.translate_count)),
                    ft.Text("请求大模型总耗时: " + str(self.translate_count)),
                    ft.Text("命中本地cache次数: " + str(self.translate_count)),
                    ft.Text("Token使用情况: " + str(self.translate_count)),
                    ft.Text("最近使用情况:"),
                    ft.Text("常用翻译语言:"),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("语言")),
                            ft.DataColumn(ft.Text("次数")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("英语")),
                                    ft.DataCell(ft.Text("280")),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("日语")),
                                    ft.DataCell(ft.Text("9")),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("韩语")),
                                    ft.DataCell(ft.Text("5")),
                                ]
                            ),
                        ],
                    ),
                ],
                spacing=15,
            ),
            padding=ft.padding.all(15),
            margin=ft.margin.all(0),
            width=250,
            bgcolor=ft.Colors.BLUE_GREY_50,
        )
