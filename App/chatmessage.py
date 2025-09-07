import flet as ft

class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

class ChatMessage(ft.Row):
    def __init__(self, message, engine):
        super().__init__()
        self.engine = engine
        self.text = message.text  # 保存消息文本
        self.user_name = message.user_name  # 保存用户名
        self.vertical_alignment = ft.CrossAxisAlignment.START
        
        # 创建内容控件
        content = ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(message.user_name)),
                    color=ft.Colors.WHITE,
                    bgcolor=self.get_avatar_color(message.user_name),
                ),
                ft.Column(
                    [
                        ft.Text(message.user_name, weight="bold"),
                        ft.Text(message.text, selectable=True),
                    ],
                    tight=True,
                    spacing=5,
                ),
            ]
        )
        
        # 用GestureDetector包装内容以添加点击事件
        self.controls = [
            ft.GestureDetector(
                content=content,
                on_tap=self.on_tap,
            )
        ]

    def on_tap(self, e):
        # 点击时朗读消息文本
        self.engine.say(self.text)
        self.engine.runAndWait()

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]