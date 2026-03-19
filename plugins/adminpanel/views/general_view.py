import flet_easy as fs
import flet as ft

class GeneralView:
    def __init__(self, data:fs.Datasy):
        self.data = data
        self.plugin = self.data.page.session.get("plugin")

    def build(self):
        return ft.View(
            controls=[
                ft.Text("1")
            ]
        )