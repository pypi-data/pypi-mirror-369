import asyncio
import random

import flet as ft

import flet_easy as fs

app = fs.FletEasy(route_init="/")


# remove animation on route change
@app.config
def config(page: ft.Page):
    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            windows=ft.PageTransitionTheme.NONE,
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
        ),
    )


# use in 'data.view'
@app.view
def config_view(data: fs.Datasy):
    def change_color(e: ft.ControlEvent):
        colors = [ft.Colors.RED, ft.Colors.GREEN, ft.Colors.BLUE, ft.Colors.YELLOW]
        appbar.bgcolor = random.choice(colors)
        data.page.update()

    appbar = ft.AppBar(
        bgcolor=ft.Colors.BLACK45,
        leading=ft.IconButton(
            icon=ft.Icons.RESTART_ALT_ROUNDED,
            icon_color=ft.Colors.WHITE,
            on_click=change_color,
        ),
        #automatically_imply_leading=False,
        actions=[
            ft.IconButton(
                icon=ft.Icons.RESTART_ALT_ROUNDED,
                icon_color=ft.Colors.WHITE,
                on_click=change_color,
            )
        ],
    )

    return ft.View(
        #appbar=appbar,
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.CODE, label="counter 1"),
                ft.NavigationBarDestination(icon=ft.Icons.SYNC_DISABLED, label="counter 2"),
                ft.NavigationBarDestination(
                    icon=ft.Icons.CODE,
                    label="counter 3",
                ),
            ],
            on_change=data.go_navigation_bar,
        ),
    )


# control custom
class Counter(ft.Container):
    def __init__(self, update, color: str):
        super().__init__()
        self.update = update

        self.number = ft.TextField(value="0", text_size=50, text_align="center")
        self.content = ft.Column(
            controls=[
                self.number,
                ft.FilledButton("start", on_click=self.start, height=50),
            ],
            horizontal_alignment="center",
        )
        self.width = 400
        self.bgcolor = color
        self.border_radius = 10
        self.padding = 20

    async def start(self, e):
        while True:
            self.number.value = str(int(self.number.value) + 1)
            self.update()
            await asyncio.sleep(1)


# add cache to the page
@app.page("/", title="Test 1", index=0, share_data=True, cache=True, page_clear=True)
async def index_page(data: fs.Datasy):
    page = data.page
    appbar = data.view.appbar

    appbar.title = ft.Text("Test 1xd")

    """ x = 1
    data.share.set("x", x)

    async def update_x():
        nonlocal x
        for i in range(100):
            x += 1
            data.share.set("x", x)
            await asyncio.sleep(1)

    async def update_title(e: ft.AppBar):
        e.title = ft.Text(data.share.get("x"))

    def update_color(e):
        colors = [ft.Colors.RED]
        e.bgcolor = random.choice(colors)

    data.page.run_task(update_x)

    data.dynamic_control(appbar, update_title)
    data.dynamic_control(appbar, update_color) """

    return ft.View(
        controls=[
            ft.Text("Counter 1", size=50),
            Counter(page.update, ft.Colors.RED),
        ],
        appbar=appbar,
        navigation_bar=data.view.navigation_bar,
        horizontal_alignment="center",
        vertical_alignment="center",
    )


@app.page("/test2", title="Test 2", index=1, share_data=True, cache=True, page_clear=True)
def test_page(data: fs.Datasy):
    page = data.page
    appbar = data.view.appbar

    appbar.title = ft.Text(data.share.get("x"))

    return ft.View(
        controls=[
            ft.Text("Counter 2 - (cache disabled)", size=50),
            Counter(page.update, ft.Colors.BLUE),
        ],
        appbar=appbar,
        navigation_bar=data.view.navigation_bar,
        vertical_alignment="center",
        horizontal_alignment="center",
    )


# add cache to the page
@app.page("/test3", title="Test 3", index=2, share_data=True, cache=True, page_clear=True)
async def test2_page(data: fs.Datasy):
    page = data.page
    appbar = data.view.appbar

    appbar.leading = ft.IconButton(ft.Icons.RESTART_ALT_ROUNDED, on_click=lambda e: page.update())

    data.dynamic_control(appbar, func_update=lambda e: setattr(e, "title", ft.Text("Test 3")))

    return ft.View(
        controls=[
            ft.Text("Counter 3", size=50),
            Counter(page.update, ft.Colors.GREEN),
        ],
        appbar=appbar,
        navigation_bar=data.view.navigation_bar,
        horizontal_alignment="center",
        vertical_alignment="center",
    )


app.run()
