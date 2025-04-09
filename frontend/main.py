import flet as ft
from api.client import AuthAPI
from frontend.views.passo_views import AddPasswordPage, PasswordListPage, PasswordDetailPage
from views.auth_views import LoginRegisterPage, dashboard_page


def main(page: ft.Page):
    # Initialize API client
    auth_api = AuthAPI()

    # Configure page settings
    page.title = "Мое крутое приложение"
    page.padding = 30
    page.window_width = 400
    page.window_height = 600
    page.window_resizable = False

    # Routing system
    def route_change(e):
        page.views.clear()

        if e.route == "/dashboard":
            page.views.append(
                ft.View("/dashboard", [dashboard_page(page, auth_api)])
            )
        elif e.route.startswith("/password/"):
            entry_id = int(e.route.split("/")[-1])  # Извлекаем ID из URL
            page.views.append(
                ft.View(
                    e.route,
                    [PasswordDetailPage(page, entry_id).view],
                    padding=20,
                    appbar=ft.AppBar(
                        title=ft.Text("Детали пароля"),
                        leading=ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: page.go("/passwords")
                        )
                    )
                )
            )

        elif e.route == "/passwords":
            page.views.append(
                ft.View(
                    "/passwords",
                    [PasswordListPage(page, auth_api).view],
                    padding=20,
                    appbar=ft.AppBar(
                        title=ft.Text("Мои пароли"),
                        actions=[
                            ft.IconButton(
                                icon=ft.icons.ADD,
                                on_click=lambda _: page.go("/add_password"),
                                tooltip="Добавить пароль"
                            )
                        ]
                    )
                )
            )
        elif e.route == "/add_password":
            page.views.append(
                ft.View(
                    "/add_password",
                    [AddPasswordPage(page).view],
                    padding=20,
                    appbar=ft.AppBar(
                        title=ft.Text("Добавить новый пароль"),
                    )
                )
            )
        else:
            page.views.append(
                ft.View("/", [LoginRegisterPage(page, auth_api).view])
            )

        page.update()

    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)