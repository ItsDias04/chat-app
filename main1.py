from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton, MDRoundFlatButton
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.scrollview import MDScrollView

from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivy.metrics import dp
from kivymd.uix.card import MDCard

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from kivy.clock import mainthread

import client2


def func():
    return None


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.users_text_fields = []
        self.is_connected = False
        self.is_connected_to_chat = False
        self.functions = {
            "chat_created": self.chat_created,
            "chat_uncreated": self.chat_uncreated,
            "add_user": self.add_user_to_scroll,
            "connected": self.chat_created,
            "connect_rejected": self.chat_uncreated,
            "user_delete": self.user_delete_from_scroll,
            "get_my_name": self.get_my_name,
            "chat_disconnected": self.chat_disconnected,
            "add_message": self.add_message,
            "server_disconnected": self.server_disconnected,
            "show_alert_dialog": self.show_alert_dialog
        }

    def get_my_name(self):
        return self.text_login.text

    def start_generate(self, but):
        client2.start_generate_pk(self.client_socket)

    @mainthread
    def server_disconnected(self):
        self.scr_manager.current = "connect_to_server"
        self.scr_manager.transition.direction = "right"
        self.show_alert_dialog("Server disconnected")
        self.is_connected = False

    @mainthread
    def user_delete_from_scroll(self, user_name):
        for us in self.users_grid_info.children:
            if user_name == us.children[0].text:
                self.users_grid_info.remove_widget(us)

    @mainthread
    def add_user_to_scroll(self, users_req):
        self.users_grid_info.clear_widgets()
        for us in users_req:
            box = MDBoxLayout(orientation="vertical", adaptive_size=True)
            box.add_widget(MDRectangleFlatButton(text=us["name"], md_bg_color="orange", text_color="white"))
            self.users_grid_info.add_widget(box)
            self.users_grid_info.height += 100

    @mainthread
    def add_message(self, message, name):
        box = MDBoxLayout(orientation="vertical", adaptive_size=True)
        box.add_widget(MDLabel(text=name, adaptive_size=True))
        box.add_widget(MDRoundFlatButton(text=message, md_bg_color="orange", text_color="white"))
        self.messages_grid.add_widget(box)
        self.messages_grid.height += 100

    @mainthread
    def chat_created(self):
        self.is_connected_to_chat = True
        self.scr_manager.current = "chat"
        self.scr_manager.transition.direction = "left"

    @mainthread
    def chat_uncreated(self):
        self.scr_manager.current = "login"
        self.scr_manager.transition.direction = "right"

    @mainthread
    def chat_disconnected(self):
        self.scr_manager.current = "login"
        self.scr_manager.transition.direction = "right"
        self.users_grid_info.clear_widgets()
        self.messages_grid.clear_widgets()

    def send_message(self, but):
        if self.new_message.text != '':
            client2.send_message(self.client_socket, self.text_login.text, self.new_message.text)
            self.new_message.text = ''

    def login(self, but):
        self.scr_manager.current = "loading_page"
        self.scr_manager.transition.direction = "left"

        client2.connect_to_chat(self.client_socket, self.text_chat_name.text, self.text_login.text)

    def go_to_create(self, but):
        self.scr_manager.current = "add_users"
        self.scr_manager.transition.direction = "left"

    def delete_user(self, but):
        self.users_grid.height -= 100
        self.users_grid.remove_widget(but.parent)

    def add_user(self, but):
        self.users_grid.height += 100
        widget = MDBoxLayout(orientation='horizontal', size_hint_y=None)
        text_users_inp = MDTextField(
            hint_text="User name",
            mode="rectangle",
            size_hint_x=0.5,
        )
        iconbut = MDIconButton(
            icon="delete",
            on_press=self.delete_user,
        )
        widget.add_widget(text_users_inp)
        widget.add_widget(iconbut)
        self.users_grid.add_widget(widget)
        self.users_text_fields.append(self.users_grid)

        self.list_users.clear_widgets()
        self.list_users.add_widget(self.users_grid)

    def to_login_page(self, but):
        self.scr_manager.current = "login"
        self.scr_manager.transition.direction = "right"

    def get_users_created(self):
        users_list = []
        for us in self.users_grid.children:
            users_list.append(us.children[1].text)
        return users_list

    def to_create_chat(self, but):
        self.scr_manager.current = "loading_page"
        self.scr_manager.transition.direction = "left"

        client2.create_chat(self.client_socket, self.text_login.text, self.text_chat_name.text, self.get_users_created)

    def disconnect_from_chat(self, but):
        self.scr_manager.current = "loading_page"
        self.scr_manager.transition.direction = "right"
        client2.disconnect_from_chat(self.client_socket, self.text_chat_name.text)

    @mainthread
    def show_alert_dialog(self, alert):
        self.dialog = MDDialog(
            text=alert,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color
                ),
            ],
        )

        self.dialog.buttons[0].bind(on_release=self.dialog.dismiss)
        self.dialog.open()

    def connect_to_server(self, but):
        ret = client2.connect_to_server_func(self.text_ip.text, self.text_port.text, self.functions)

        if ret:
            self.client_socket = ret
            self.is_connected = True
            self.scr_manager.current = "login"
            self.scr_manager.transition.direction = "left"
        else:
            self.is_connected = False

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Orange"
        self.scr_manager = ScreenManager()

        self.server_connect_screen = MDScreen(
            name="connect_to_server"
        )
        self._but_connect_server = MDRectangleFlatButton(
                text="Connect to server",
                pos_hint={"center_x": 0.5, "center_y": 0.4}
            )

        self._but_connect_server.bind(on_press=self.connect_to_server)

        self.server_connect_screen.add_widget(self._but_connect_server)
        self.text_ip = MDTextField(
            hint_text="Ip server",
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint_x=0.5,
            mode="rectangle"
        )
        self.server_connect_screen.add_widget(
            self.text_ip
        )

        self.text_port = MDTextField(
            hint_text="Port server",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint_x=0.5,
            mode="rectangle"
        )
        self.server_connect_screen.add_widget(
            self.text_port
        )

        self.login_screen = MDScreen(
            MDRectangleFlatButton(
                text="Connect to chat",
                     # "Create chat"
                pos_hint={"center_x": 0.4, "center_y": 0.4},
                on_press=self.login
            ),
            MDRectangleFlatButton(
                text="Create new chat",
                pos_hint={"center_x": 0.6, "center_y": 0.4},
                on_press=self.go_to_create
            ),
            name="login"
        )

        self.text_login = MDTextField(
                hint_text="Your name",
                pos_hint={"center_x": 0.5, "center_y": 0.6},
                size_hint_x=0.5,
                mode="rectangle"
            )
        self.login_screen.add_widget(
            self.text_login
        )

        self.text_chat_name = MDTextField(
            hint_text="Chat name",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint_x=0.5,
            mode="rectangle"
        )
        self.login_screen.add_widget(
            self.text_chat_name
        )

        self.add_users = MDScreen(name="add_users")

        self.list_users = MDScrollView(
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint=[.5, .8],
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        )

        self.users_grid = MDGridLayout(cols=1, size_hint_y=None, height=100)

        self.list_users.add_widget(self.users_grid)
        self.add_users.add_widget(self.list_users)
        self.add_users.add_widget(
            MDRectangleFlatButton(
                text="Back",
                pos_hint={"center_x": 0.1, "center_y": 0.1},
                on_press=self.to_login_page
            )
        )
        self.add_users.add_widget(
            MDRectangleFlatButton(
                text="Create chat",
                pos_hint={"center_x": 0.9, "center_y": 0.1},
                on_press=self.to_create_chat
            )
        )
        self.add_users.add_widget(
            MDRectangleFlatButton(
                text="Add user",
                pos_hint={"center_x": 0.5, "center_y": 0.1},
                on_press=self.add_user
            )
        )

        self.loading_screen = MDScreen(name="loading_page")

        self.loading_screen.add_widget(
            MDSpinner(
                size_hint=(None, None),
                pos_hint={'center_x': .5, 'center_y': .5},
                size=(dp(46), dp(46)),
                active=True
            )
        )
        self.loading_screen.add_widget(
            MDLabel(
                text="Waiting...",
                pos_hint={'center_x': .5, 'center_y': .4},
                halign="center"
            )
        )
        self.loading_screen.add_widget(
            MDRectangleFlatButton(
                text="Back",
                pos_hint={"center_x": 0.1, "center_y": 0.1},
                on_press=self.to_login_page
            )
        )

        self.theme_cls.material_style = "M3"
        self.chat_screen = MDScreen(name="chat")

        self.chat_screen.add_widget(
            MDCard(
                md_bg_color="#f6eeee",
                style="elevated",
                line_color=(0.2, 0.2, 0.2, 0.8),
                padding="4dp",
                size_hint=(0.7, 0.9),
                pos_hint={'center_x': .375, 'center_y': .5}
            )
        )

        self.list_messages = MDScrollView(
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint=[.675, .875],
            pos_hint={'center_x': .375, 'center_y': .5}
        )

        self.messages_grid = MDGridLayout(cols=1, size_hint_y=None, spacing="20px", padding="10px", height=100)

        self.list_messages.add_widget(self.messages_grid)
        self.chat_screen.add_widget(self.list_messages)

        self.new_message = MDTextField(
            hint_text="Your message",
            pos_hint={"center_x": 0.325, "center_y": 0.125},
            size_hint_x=0.55,
            mode="fill"
        )

        self.chat_screen.add_widget(self.new_message)

        self.chat_screen.add_widget(
            MDRectangleFlatButton(
                text="disconnect",
                pos_hint={"center_x": 0.875, "center_y": 0.1},
                on_press=self.disconnect_from_chat
            )
        )
        self.chat_screen.add_widget(
            MDRectangleFlatButton(
                text="send",
                pos_hint={"center_x": 0.652, "center_y": 0.125},
                on_press=self.send_message
            )
        )

        self.list_users_front = MDScrollView(
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint=(0.225, 0.65),
            pos_hint={'center_x': .8725, 'center_y': .6275}
        )

        self.users_grid_info = MDGridLayout(cols=1, size_hint_y=None, spacing="15px", padding="10px", height=100)

        self.chat_screen.add_widget(
            MDCard(
                md_bg_color="#f6eeee",
                style="elevated",
                line_color=(0.2, 0.2, 0.2, 0.8),
                padding="4dp",
                size_hint=(0.225, 0.65),
                pos_hint={'center_x': .8725, 'center_y': .6275}
            )
        )

        self.chat_screen.add_widget(
            MDRectangleFlatButton(
                text="Regenerate pk",
                pos_hint={"center_x": 0.875, "center_y": 0.2},
                on_press=self.start_generate
            )
        )

        self.list_users_front.add_widget(self.users_grid_info)
        self.chat_screen.add_widget(self.list_users_front)

        self.scr_manager.add_widget(self.server_connect_screen)
        self.scr_manager.add_widget(self.login_screen)
        self.scr_manager.add_widget(self.add_users)
        self.scr_manager.add_widget(self.chat_screen)
        self.scr_manager.add_widget(self.loading_screen)

        return self.scr_manager

    def on_stop(self):
        if self.is_connected:
            self.client_socket.close()


MainApp().run()
