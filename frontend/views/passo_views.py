import flet as ft
from frontend.api.client import AuthAPI
from frontend.api.passo import PasswordManager
from frontend.utils.helpers import validate_email, show_snackbar


class PasswordListPage:
    def __init__(self, page: ft.Page, auth_api: AuthAPI):
        self.page = page
        self.auth_api = auth_api
        self.pm = PasswordManager()
        self.password_entries = []

        # Стили
        self.list_item_style = {
            "bgcolor": ft.colors.WHITE,
            "padding": 15,
            "border_radius": 10,
            "shadow": ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.GREY_300)
        }

        self.view = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Мои пароли", size=24, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            on_click=self.load_passwords
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.ListView(expand=True, spacing=10)
            ],
            spacing=20
        )

        self.load_passwords()

    def load_passwords(self, e=None):
        token = self.page.client_storage.get("token")
        if not token:
            return

        # ⏳ Показываем индикатор загрузки
        self.view.controls[1].controls = [ft.ProgressBar()]
        self.page.update()

        try:
            # 🔐 Получаем список паролей от PasswordManager
            self.password_entries = self.pm.get_passwords(token)

            list_items = []

            for entry in self.password_entries:
                # 📦 Один блок - одна строка с паролем
                list_items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                # 🔒 Иконка "замок"
                                ft.Icon(ft.icons.LOCK_OUTLINED),

                                # 🌐 Сайт и имя пользователя
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            entry['website'],
                                            weight=ft.FontWeight.BOLD,
                                            size=16,
                                            max_lines=1,
                                            overflow="ellipsis"
                                        ),
                                        ft.Text(
                                            entry.get('username') or "Без имени пользователя",
                                            size=14,
                                            color=ft.colors.GREY
                                        )
                                    ],
                                    spacing=2,
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),

                                # ↔️ Распределитель, чтобы кнопки ушли вправо
                                ft.Container(expand=True),

                                # 👁 и 🗑 кнопки действий
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.icons.VISIBILITY_OUTLINED,
                                            tooltip="Показать пароль",
                                            data=entry['id_entry'],
                                            on_click=self.show_password_details
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE_OUTLINED,
                                            icon_color=ft.colors.RED,
                                            tooltip="Удалить",
                                            data=entry['id_entry'],
                                            on_click=self.delete_password
                                        )
                                    ],
                                    spacing=5,
                                    alignment=ft.MainAxisAlignment.END
                                )
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15
                        ),
                        # 💅 Применяем стили: фон, тень, скругления
                        **self.list_item_style
                    )
                )

            # 🕳 Пустой список — показываем сообщение
            if not list_items:
                list_items = [
                    ft.Container(
                        content=ft.Text("Нет сохраненных паролей", italic=True),
                        alignment=ft.alignment.center,
                        height=100
                    )
                ]

            # 📥 Обновляем список в интерфейсе
            self.view.controls[1].controls = list_items

        except Exception as e:
            # ❗ Ошибка при загрузке — показываем уведомление
            show_snackbar(self.page, f"Ошибка загрузки: {str(e)}", "red")

        finally:
            self.page.update()

    def show_password_details(self, e):
        entry_id = e.control.data  # ID записи из data кнопки
        self.page.go(f"/password/{entry_id}")

    def delete_password(self, e):
        try:
            if self.pm.delete_password(self.page.client_storage.get("token"), e.control.data):
                show_snackbar(self.page, "Запись удалена", "green")
                self.load_passwords()
            else:
                show_snackbar(self.page, "Ошибка удаления", "red")
        except Exception as ex:
            show_snackbar(self.page, f"Ошибка: {str(ex)}", "red")


class AddPasswordPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.pm = PasswordManager()

        field_style = {
            "width": 300,
            "height": 45,
            "border_radius": 10,
            "border_color": ft.colors.GREY_400,
            "content_padding": 10
        }

        # Поля формы
        self.website_field = ft.TextField(label="Веб-сайт", **field_style)
        self.username_field = ft.TextField(label="Логин", **field_style)
        self.password_field = ft.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            **field_style
        )
        self.notes_field = ft.TextField(
            label="Заметки",
            multiline=True,
            min_lines=3,
            **field_style
        )

        self.view = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Добавить новый пароль", size=24, weight=ft.FontWeight.BOLD),
                    self.website_field,
                    self.username_field,
                    self.password_field,
                    self.notes_field,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Сохранить",
                                icon=ft.icons.SAVE,
                                on_click=self.save_password,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.BLUE_700,
                                    color=ft.colors.WHITE
                                )
                            ),
                            ft.TextButton(
                                "Отмена",
                                on_click=lambda _: self.page.go("/passwords")
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=30,
            bgcolor=ft.colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.colors.BLUE_100),
        )

    def save_password(self, e):
        try:
            data = {
                "website": self.website_field.value,
                "username": self.username_field.value,
                "password": self.password_field.value,
                "notes": self.notes_field.value
            }

            if not data['website'] or not data['password']:
                raise ValueError("Заполните обязательные поля")

            if self.pm.create_password(self.page.client_storage.get("token"), data):
                show_snackbar(self.page, "Пароль успешно сохранен", "green")
                self.page.go("/passwords")
            else:
                show_snackbar(self.page, "Ошибка при сохранении", "red")

        except Exception as ex:
            show_snackbar(self.page, str(ex), "red")


class PasswordDetailPage:
    def __init__(self, page: ft.Page, entry_id: int):
        self.page = page
        self.entry_id = entry_id
        self.pm = PasswordManager()
        self.password_visible = False
        self.edit_mode = False
        self.original_data = {}

        # Элементы интерфейса
        self.website_field = ft.TextField(
            label="Сайт",
            read_only=True,
            width=300,
            border_color=ft.colors.GREY_600
        )
        self.username_field = ft.TextField(
            label="Логин",
            read_only=True,
            width=300,
            border_color=ft.colors.GREY_600
        )
        self.password_field = ft.TextField(
            label="Пароль",
            password=not self.password_visible,
            can_reveal_password=True,
            width=300,
            border_color=ft.colors.GREY_600
        )
        self.notes_field = ft.TextField(
            label="Заметки",
            multiline=True,
            read_only=True,
            width=300,
            border_color=ft.colors.GREY_600
        )

        # Кнопки управления
        self.edit_button = ft.ElevatedButton(
            "Редактировать",
            icon=ft.icons.EDIT,
            on_click=self.toggle_edit_mode,
            width=150,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_700,
                color=ft.colors.WHITE
            )
        )


        # Основной layout
        self.view = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Детали записи",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                    self.website_field,
                    self.username_field,
                    self.password_field,
                    self.notes_field,
                    ft.Row(
                        [self.edit_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20
                    ),
                    ft.ElevatedButton(
                        "Назад",
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda _: self.page.go("/passwords"),
                        width=200
                    )
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=40,
            expand=True,
            alignment=ft.alignment.center
        )

        self.load_data()

    def load_data(self):
        token = self.page.client_storage.get("token")
        if not token:
            return

        entry = self.pm.get_password_details(token, self.entry_id)
        if entry:
            self.original_data = {
                "website": entry.get('website', ''),
                "username": entry.get('username', ''),
                "password": entry.get('password', ''),
                "notes": entry.get('notes', '')
            }
            self._update_fields(self.original_data)
            self.page.update()

    def _update_fields(self, data: dict):
        self.website_field.value = data['website']
        self.username_field.value = data['username']
        self.password_field.value = data['password']
        self.notes_field.value = data['notes']

    def toggle_edit_mode(self, e):
        self.edit_mode = not self.edit_mode

        # Переключаем режим редактирования
        for field in [self.website_field, self.username_field,
                      self.password_field, self.notes_field]:
            field.read_only = not self.edit_mode
            field.border_color = ft.colors.BLUE_ACCENT if self.edit_mode else ft.colors.GREY_600

        # Обновляем текст кнопки
        self.edit_button.text = "Сохранить" if self.edit_mode else "Редактировать"

        # При сохранении вызываем метод сохранения
        if not self.edit_mode:
            self.save_changes()

        self.page.update()

    def save_changes(self):
        token = self.page.client_storage.get("token")
        if not token:
            show_snackbar(self.page, "Ошибка авторизации", "red")
            return

        new_data = {
            "website": self.website_field.value.strip(),
            "username": self.username_field.value.strip(),
            "password": self.password_field.value.strip(),
            "notes": self.notes_field.value.strip()
        }

        # Валидация данных
        if not new_data['website']:
            show_snackbar(self.page, "Поле 'Сайт' обязательно для заполнения", "red")
            return

        if not new_data['password']:
            show_snackbar(self.page, "Поле 'Пароль' обязательно для заполнения", "red")
            return

        # Проверка изменений
        if new_data == self.original_data:
            show_snackbar(self.page, "Изменений не обнаружено", "blue")
            return

        # Отправка изменений на сервер
        try:
            if self.pm.update_password(token, self.entry_id, new_data):
                show_snackbar(self.page, "Изменения сохранены", "green")
                self.original_data = new_data
            else:
                show_snackbar(self.page, "Ошибка при сохранении", "red")
                self._update_fields(self.original_data)  # Восстанавливаем исходные данные
        except Exception as e:
            show_snackbar(self.page, f"Ошибка: {str(e)}", "red")
            self._update_fields(self.original_data)

        self.page.update()

    def confirm_delete(self, e):
        def delete_action(_):
            token = self.page.client_storage.get("token")
            if not token:
                show_snackbar(self.page, "Ошибка авторизации", "red")
                return

            try:
                if self.pm.delete_password(token, self.entry_id):
                    show_snackbar(self.page, "Запись удалена", "green")
                    self.page.go("/passwords")
                else:
                    show_snackbar(self.page, "Ошибка удаления", "red")
            except Exception as ex:
                show_snackbar(self.page, f"Ошибка: {str(ex)}", "red")

            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Подтверждение удаления"),
            content=ft.Text("Вы уверены, что хотите удалить эту запись?"),
            actions=[
                ft.TextButton("Да", on_click=delete_action),
                ft.TextButton("Отмена", on_click=lambda _: setattr(dialog, "open", False))
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()