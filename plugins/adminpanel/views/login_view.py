import flet_easy as fs
import flet as ft
from plugins.fesl import services

class LoginView:
    def __init__(self, data:fs.Datasy):
        self.data = data
        self.plugin = self.data.page.session.get("plugin")
        #ft.ProgressRing(width=16, height=16, bgcolor=ft.Colors.with_opacity(0.0, ft.Colors.RED), color=ft.Colors.WHITE)
        self._filledButton_login = ft.FilledButton(expand=True, content=ft.Container(content=ft.Text("log in"), padding=ft.padding.symmetric(10, 12)), on_click=self.on_click_filledButton_login)

    async def on_click_filledButton_login(self, event):
        print(self.plugin.fesl)
        self.data.go("/")()

    def build(self):
        return ft.View(
            controls=[
                ft.Stack(
                    height=400,
                    controls=[
                        ft.Container(
                            content=ft.Card(
                                width=350,
                                height=280,
                                content=ft.Container(
                                    padding=ft.padding.all(15),
                                    content=ft.Column(
                                        controls=[
                                            ft.Row(controls=[ft.Text("Log in to system", theme_style=ft.TextThemeStyle.TITLE_LARGE, text_align=ft.TextAlign.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                            ft.Divider(),
                                            ft.TextField(label="Login", autofocus=True),
                                            ft.TextField(label="Password"),
                                            ft.Divider(),
                                            ft.Row(controls=[self._filledButton_login], alignment=ft.MainAxisAlignment.CENTER)
                                        ],
                                    ),
                                )
                            ),
                            alignment=ft.alignment.center
                        ),

                        ft.Container(
                            content=ft.Text("BattleNode", theme_style=ft.TextThemeStyle.DISPLAY_SMALL),
                            alignment=ft.alignment.top_center,
                            height=40
                        ),
                    ]
                )
            ],
            vertical_alignment="center",
            horizontal_alignment="center"
    )