import flet as ft


def main(page: ft.Page):
    page.title = "Routes Example"

    def route_change(e):
        page.views.clear()

        def confirm_route_pop(e):
            print("on_confirm_pop")
            """ if page.route == "/":
                e.control.confirm_pop(True) """
            
            page.go("/test")
            e.control.confirm_pop(False)

        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text("Flet app"), bgcolor=ft.Colors.BLUE),
                        ft.Button("Visit Store", on_click=lambda _: page.go("/store")),
                    ],
                    #can_pop=,
                    #on_confirm_pop=confirm_route_pop,
                )
            )
        if page.route == "/store":
            page.views.append(
                ft.View(
                    "/store",
                    [
                        ft.AppBar(title=ft.Text("Store"), bgcolor=ft.Colors.RED),
                        ft.Button("Go Home", on_click=lambda _: page.go("/")),
                    ],
                    can_pop=False,
                    on_confirm_pop=confirm_route_pop,
                )
            )
        if page.route == "/test":
            page.views.append(
                ft.View(
                    "/test",
                    [
                        ft.AppBar(title=ft.Text("Test"), bgcolor=ft.Colors.GREEN),
                        ft.Button("Go Home", on_click=lambda _: page.go("/")),
                    ],
                    can_pop=False,
                    on_confirm_pop=confirm_route_pop,
                )
            )
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)


ft.app(main)
