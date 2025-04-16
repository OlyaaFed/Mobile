from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
import requests

Window.clearcolor = (0.96, 0.94, 0.90, 1)
Window.size = (360, 640)

API_URL = "http://127.0.0.1:5000"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        layout.add_widget(Label(text="Вход", font_size=32, color=(0, 0, 0, 1)))
        self.email_input = TextInput(hint_text="Email", multiline=False)
        self.password_input = TextInput(hint_text="Пароль", password=True, multiline=False)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)

        login_btn = Button(text="Войти", background_normal='', background_color=(0.7, 0.6, 0.45, 1), color=(1, 1, 1, 1), size_hint=(1, None), height=50)
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)

        reg_btn = Button(text="Регистрация", background_normal='', background_color=(0.9, 0.85, 0.7, 1), size_hint=(1, None), height=40)
        reg_btn.bind(on_press=self.go_register)
        layout.add_widget(reg_btn)

        self.add_widget(layout)

    def login(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        response = requests.post(f"{API_URL}/api/login", json={"email": email, "password": password})
        if response.status_code == 200:
            self.manager.get_screen('books').user_email = email
            self.manager.current = 'books'
        else:
            popup = Popup(title='Ошибка', content=Label(text='Неверный логин или пароль'), size_hint=(0.7, 0.4))
            popup.open()

    def go_register(self, instance):
        self.manager.current = 'register'


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        layout.add_widget(Label(text="Регистрация", font_size=32, color=(0, 0, 0, 1)))
        self.name_input = TextInput(hint_text="Имя", multiline=False)
        self.email_input = TextInput(hint_text="Email", multiline=False)
        self.password_input = TextInput(hint_text="Пароль", password=True, multiline=False)

        layout.add_widget(self.name_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)

        reg_btn = Button(text="Зарегистрироваться", background_normal='', background_color=(0.7, 0.6, 0.45, 1), color=(1, 1, 1, 1), size_hint=(1, None), height=50)
        reg_btn.bind(on_press=self.register)
        layout.add_widget(reg_btn)

        back_btn = Button(text="Назад", background_normal='', background_color=(0.9, 0.85, 0.7, 1), size_hint=(1, None), height=40)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def register(self, instance):
        data = {
            "name": self.name_input.text,
            "email": self.email_input.text,
            "password": self.password_input.text
        }
        response = requests.post(f"{API_URL}/registration", data=data)
        if response.status_code in [200, 302]:
            self.manager.current = 'login'
        else:
            popup = Popup(title='Ошибка', content=Label(text='Ошибка регистрации'), size_hint=(0.7, 0.4))
            popup.open()

    def go_back(self, instance):
        self.manager.current = 'login'


class BookItem(BoxLayout):
    def __init__(self, book, user_email, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=160, padding=10, spacing=12, **kwargs)
        self.book = book
        self.user_email = user_email

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[10], pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        image = AsyncImage(source=book['image'], size_hint=(None, None), size=(80, 110))

        info_box = BoxLayout(orientation='vertical', spacing=6)
        info_box.add_widget(Label(text=book['title'], color=(0, 0, 0, 1), bold=True, font_size=16))
        info_box.add_widget(Label(text=f"Автор: {book['author']}", color=(0.2, 0.2, 0.2, 1), font_size=13))

        add_btn = Button(
            text="Добавить на полку",
            background_normal='',
            background_color=(0.7, 0.6, 0.45, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=35
        )
        add_btn.bind(on_press=self.add_to_shelf)
        info_box.add_widget(add_btn)

        self.add_widget(image)
        self.add_widget(info_box)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def add_to_shelf(self, instance):
        data = {
            'email': self.user_email,
            'state': 'хочу прочитать'
        }
        try:
            response = requests.post(f"{API_URL}/add-to-shelf/{self.book['id']}", json=data)
            if response.status_code == 200:
                popup = Popup(title='Успех', content=Label(text='Добавлено на полку'), size_hint=(0.7, 0.4))
                popup.open()
            else:
                popup = Popup(title='Ошибка', content=Label(text='Ошибка добавления'), size_hint=(0.7, 0.4))
                popup.open()
        except Exception as e:
            popup = Popup(title='Сбой сети', content=Label(text=f'Ошибка: {str(e)}'), size_hint=(0.7, 0.4))
            popup.open()


class EditProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.name_input = TextInput(hint_text="Введите новое имя", multiline=False)

        # Блок кнопок "Назад" и "Сохранить"
        btns = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        save_btn = Button(text="Сохранить", background_color=(0.5, 0.7, 0.4, 1), color=(1, 1, 1, 1))
        save_btn.bind(on_press=self.save_profile)
        back_btn = Button(text="Назад", background_color=(0.7, 0.6, 0.45, 1), color=(1, 1, 1, 1))
        back_btn.bind(on_press=self.go_back)
        btns.add_widget(back_btn)
        btns.add_widget(save_btn)

        self.layout.add_widget(Label(text="Редактирование профиля", font_size=20))
        self.layout.add_widget(self.name_input)
        self.layout.add_widget(btns)
        self.add_widget(self.layout)

    def set_initial_data(self, name):
        self.name_input.text = name

    def save_profile(self, instance):
        # Получаем email из другого экрана (например, экрана "books")
        books_screen = self.manager.get_screen('books')
        email = books_screen.user_email

        new_name = self.name_input.text.strip()
        payload = {"email": email, "name": new_name}
        try:
            response = requests.post(f"{API_URL}/api/update_user", json=payload)
            if response.status_code == 200:
                popup = Popup(
                    title="Успех",
                    content=Label(text="Профиль успешно обновлён"),
                    size_hint=(0.7, 0.3),
                    auto_dismiss=True
                )
                popup.open()
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'about'), 1.5)
            else:
                self.show_error("Ошибка при сохранении профиля.")
        except Exception as e:
            print(f"Ошибка сохранения профиля: {e}")
            self.show_error("Не удалось подключиться к серверу.")

    def show_error(self, msg):
        popup = Popup(
            title="Ошибка",
            content=Label(text=msg),
            size_hint=(0.7, 0.3),
            auto_dismiss=True
        )
        popup.open()

    def go_back(self, instance):
        self.manager.current = 'about'
class AddBookScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        layout.add_widget(Label(text="Добавить книгу", font_size=32, color=(0, 0, 0, 1)))
        self.title_input = TextInput(hint_text="Название книги", multiline=False)
        self.author_input = TextInput(hint_text="Автор", multiline=False)
        self.genre_input = TextInput(hint_text="Жанр", multiline=False)
        self.year_input = TextInput(hint_text="Год публикации", multiline=False)
        self.pages_input = TextInput(hint_text="Количество страниц", multiline=False)
        self.description_input = TextInput(hint_text="Описание", multiline=True)

        layout.add_widget(self.title_input)
        layout.add_widget(self.author_input)
        layout.add_widget(self.genre_input)
        layout.add_widget(self.year_input)
        layout.add_widget(self.pages_input)
        layout.add_widget(self.description_input)

        add_btn = Button(text="Добавить книгу", background_normal='', background_color=(0.7, 0.6, 0.45, 1),
                         color=(1, 1, 1, 1), size_hint=(1, None), height=50)
        add_btn.bind(on_press=self.add_book)
        layout.add_widget(add_btn)

        back_btn = Button(text="Назад", background_normal='', background_color=(0.9, 0.85, 0.7, 1), size_hint=(1, None),
                          height=40)
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def add_book(self, instance):
        title = self.title_input.text
        author = self.author_input.text
        genre = self.genre_input.text
        publication_year = self.year_input.text
        pages = self.pages_input.text
        description = self.description_input.text

        # Отправляем данные на сервер
        data = {
            "title": title,
            "author": author,
            "genre_id": genre,  # Здесь должно быть значение ID жанра, которое передается через ваш API
            "publication_year": publication_year,
            "pages": pages,
            "description": description,
            "state": 'доступно',  # Пример, можно изменить в зависимости от состояния книги
            "pathtofile": "",  # Если есть путь к файлу, можно передать его
        }
        try:
            response = requests.post(f"{API_URL}/add-book", data=data)
            if response.status_code == 200:
                popup = Popup(title='Успех', content=Label(text='Книга добавлена!'), size_hint=(0.7, 0.4))
                popup.open()
            else:
                popup = Popup(title='Ошибка', content=Label(text='Ошибка добавления книги'), size_hint=(0.7, 0.4))
                popup.open()
        except Exception as e:
            popup = Popup(title='Сбой сети', content=Label(text=f'Ошибка: {str(e)}'), size_hint=(0.7, 0.4))
            popup.open()

    def go_back(self, instance):
        self.manager.current = 'books'


class BooksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_email = ""
        self.books_data = []
        self.layout = BoxLayout(orientation='vertical')

        with self.canvas.before:
            Color(0.96, 0.94, 0.90, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=[10, 10])
        title = Label(text="Книги", font_size=20, color=(0, 0, 0, 1), size_hint_x=0.8)
        menu_btn = Button(text="⋮", size_hint_x=0.2, on_press=self.open_menu)
        top_bar.add_widget(title)
        top_bar.add_widget(menu_btn)
        self.layout.add_widget(top_bar)

        # Поле поиска
        self.search_input = TextInput(
            hint_text="Поиск по названию, жанру или автору",
            size_hint_y=None,
            height=40,
            multiline=False,
            padding_y=[10, 10],
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.search_input.bind(text=self.on_search_text)
        self.layout.add_widget(self.search_input)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        add_book_btn = Button(
            text="Добавить книгу",
            background_normal='',
            background_color=(0.7, 0.6, 0.45, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=50
        )
        add_book_btn.bind(on_press=self.go_add_book)
        self.layout.add_widget(add_book_btn)

        self.add_widget(self.layout)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def open_menu(self, instance):
        dropdown = DropDown()
        for name, screen in [("О себе", "about"), ("Моя полка", "shelf"), ("Выход", "login")]:
            btn = Button(text=name, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.select_menu(btn.text))
            dropdown.add_widget(btn)
        dropdown.open(instance)

    def select_menu(self, selection):
        if selection == "Выход":
            self.manager.current = 'login'
        elif selection == "О себе":
            self.manager.current = 'about'
        elif selection == "Моя полка":
            self.manager.current = 'shelf'

    def go_add_book(self, instance):
        self.manager.current = 'add_book'

    def on_enter(self):
        self.grid.clear_widgets()
        try:
            response = requests.get(f"{API_URL}/api/books")
            if response.status_code == 200:
                self.books_data = response.json()
                self.display_books(self.books_data)
            else:
                self.grid.add_widget(Label(text="Не удалось загрузить книги"))
        except Exception as e:
            self.grid.add_widget(Label(text=f"Ошибка: {str(e)}"))

    def display_books(self, books):
        self.grid.clear_widgets()
        if books:
            for book in books:
                self.grid.add_widget(BookItem(book, self.user_email))
        else:
            self.grid.add_widget(Label(text="Нет доступных книг"))

    def on_search_text(self, instance, value):
        query = value.lower()
        filtered = [
            book for book in self.books_data
            if query in book['title'].lower()
            or query in book.get('genre', '').lower()
            or query in book.get('author', '').lower()
        ]
        self.display_books(filtered)
class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.96, 0.94, 0.90, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.add_widget(self.layout)

        # Фото (дефолтный путь к изображению)
        default_avatar_path = r"C:\Users\daria\OneDrive\Desktop\апии\static\photouser\8.jpg"
        self.avatar = AsyncImage(source=default_avatar_path, size_hint=(None, None), size=(120, 120))
        avatar_box = BoxLayout(size_hint=(1, None), height=130, padding=0, orientation='horizontal')
        avatar_box.add_widget(self.avatar)
        self.layout.add_widget(avatar_box)

        # Данные
        self.name_label = Label(text="Имя: -", font_size=18, color=(0.1, 0.1, 0.1, 1))
        self.email_label = Label(text="Email: -", font_size=18, color=(0.1, 0.1, 0.1, 1))
        self.count_label = Label(text="Книг на полке: -", font_size=18, color=(0.1, 0.1, 0.1, 1))

        self.layout.add_widget(self.name_label)
        self.layout.add_widget(self.email_label)
        self.layout.add_widget(self.count_label)

        # Кнопки
        btns = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        back_btn = Button(text="← Назад", background_normal='', background_color=(0.7, 0.6, 0.45, 1), color=(1, 1, 1, 1))
        back_btn.bind(on_press=self.go_back)
        edit_btn = Button(text="Редактировать", background_normal='', background_color=(0.5, 0.4, 0.3, 1), color=(1, 1, 1, 1))
        edit_btn.bind(on_press=self.edit_profile)
        btns.add_widget(back_btn)
        btns.add_widget(edit_btn)

        self.layout.add_widget(btns)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_pre_enter(self):
        self.load_user_data()

    def load_user_data(self):
        books_screen = self.manager.get_screen('books')
        email = books_screen.user_email
        try:
            response = requests.get(f"{API_URL}/api/user", params={"email": email})
            if response.status_code == 200:
                data = response.json()
                self.name_label.text = f"Имя: {data.get('name', '-')}"
                self.email_label.text = f"Email: {data.get('email', '-')}"
                self.count_label.text = "Книг на полке: загрузка..."

                # Получаем изображение
                new_avatar = data.get('profile_image', 'https://cdn-icons-png.flaticon.com/512/847/847969.png')
                if self.avatar.source != new_avatar:
                    self.avatar.source = ''
                    Clock.schedule_once(lambda dt: setattr(self.avatar, 'source', new_avatar), 0.1)
            else:
                self.email_label.text = f"Email: {email}"
        except Exception as e:
            self.email_label.text = f"Email: {email}"
            print(f"Ошибка при загрузке данных пользователя: {e}")

    def go_back(self, instance):
        self.manager.current = 'books'

    def edit_profile(self, instance):
        edit_screen = self.manager.get_screen('edit_profile')
        edit_screen.set_initial_data(name=self.name_label.text.replace("Имя: ", ""))
        self.manager.current = 'edit_profile'

class ShelfScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_email = ""
        self.selected_author = None
        self.selected_state = None

        layout = BoxLayout(orientation='vertical')

        top_bar = BoxLayout(size_hint_y=None, height=50, padding=10, spacing=10)
        top_bar.add_widget(Label(text="Моя полка", font_size=20, color=(0.1, 0.1, 0.1, 1)))

        back_btn = Button(
            text="←",
            size_hint=(None, 1), width=50,
            background_normal='',
            background_color=(0.7, 0.6, 0.45, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)

        # Spinner для авторов
        self.author_spinner = Spinner(
            text="Все авторы",
            values=["Все авторы"],
            size_hint=(None, None),
            size=(160, 40)
        )
        self.author_spinner.bind(text=self.filter_books)
        top_bar.add_widget(self.author_spinner)

        # Spinner для состояний (читаю, прочитано и т.п.)
        self.state_spinner = Spinner(
            text="Все состояния",
            values=["Все состояния", "Читаю", "Прочитано", "Хочу прочитать"],  # можно из API подтягивать
            size_hint=(None, None),
            size=(160, 40)
        )
        self.state_spinner.bind(text=self.filter_books)
        top_bar.add_widget(self.state_spinner)

        layout.add_widget(top_bar)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'books'

    def on_pre_enter(self):
        self.grid.clear_widgets()
        self.user_email = self.manager.get_screen("books").user_email
        self.load_authors()
        self.load_books()

    def load_authors(self):
        try:
            response = requests.get(f"{API_URL}/api/authors", params={"email": self.user_email})
            if response.status_code == 200:
                authors = response.json().get("authors", [])
                self.author_spinner.values = ["Все авторы"] + authors
            else:
                print("Не удалось загрузить авторов")
        except Exception as e:
            print(f"Ошибка при загрузке авторов: {e}")

    def filter_books(self, spinner, text):
        self.selected_author = self.author_spinner.text if self.author_spinner.text != "Все авторы" else None
        self.selected_state = self.state_spinner.text if self.state_spinner.text != "Все состояния" else None
        self.load_books()

    def load_books(self):
        self.grid.clear_widgets()

        try:
            params = {"email": self.user_email}
            if self.selected_author:
                params["author"] = self.selected_author
            if self.selected_state:
                params["state"] = self.selected_state

            response = requests.get(f"{API_URL}/api/shelf", params=params)
            print("Ответ сервера:", response.text)

            if response.status_code == 200:
                data = response.json()
                books = data.get("books", [])
                if books:
                    for book in books:
                        self.grid.add_widget(self.create_book_card(book))
                else:
                    self.grid.add_widget(Label(text="На полке пока пусто", font_size=16))
            else:
                self.grid.add_widget(Label(text="Ошибка загрузки полки"))
        except Exception as e:
            self.grid.add_widget(Label(text=f"Ошибка: {e}"))

    def create_book_card(self, book):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=140, spacing=10, padding=10)
        with box.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=box.pos, size=box.size, radius=[10])
        box.bind(pos=self.update_rect, size=self.update_rect)

        image = AsyncImage(source=book['image'], size_hint=(None, None), size=(80, 100))
        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(text=book['title'], font_size=16, color=(0, 0, 0, 1)))
        info.add_widget(Label(text=f"Автор: {book['author']}", font_size=14, color=(0.2, 0.2, 0.2, 1)))
        info.add_widget(Label(text=f"Статус: {book.get('state', 'неизвестно')}", font_size=14, color=(0.3, 0.3, 0.3, 1)))

        box.add_widget(image)
        box.add_widget(info)
        return box

    def update_rect(self, instance, value):
        instance.canvas.before.children[-1].pos = instance.pos
        instance.canvas.before.children[-1].size = instance.size

class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(BooksScreen(name='books'))
        sm.add_widget(AddBookScreen(name='add_book'))
        sm.add_widget(AboutScreen(name='about'))
        sm.add_widget(EditProfileScreen(name='edit_profile'))
        sm.add_widget(ShelfScreen(name='shelf'))
        return sm


if __name__ == '__main__':
    MainApp().run()
