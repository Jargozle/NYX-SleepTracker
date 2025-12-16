"""
Login Screen for Nyx Sleep Tracker
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import NyxDB as db


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(
            orientation='vertical',
            padding=40,
            spacing=20,
            size_hint=(0.85, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        layout.add_widget(Label(
            text="Nyx", 
            font_size=48,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=0.3
        ))
        
        self.username = TextInput(
            hint_text="Username",
            multiline=False,
            font_size=20,
            size_hint_y=None,
            height=50,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15]
        )
        layout.add_widget(self.username)
        
        self.password = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            font_size=20,
            size_hint_y=None,
            height=50,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15]
        )
        layout.add_widget(self.password)
        
        login_btn = Button(
            text="Login",
            font_size=22,
            size_hint_y=None,
            height=55,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        login_btn.bind(on_press=self.check_login)
        layout.add_widget(login_btn)
        
        reg_btn = Button(
            text="Register",
            font_size=20,
            size_hint_y=None,
            height=50,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        reg_btn.bind(on_press=self.go_register)
        layout.add_widget(reg_btn)
        
        self.message = Label(
            text="",
            font_size=16,
            color=(1, 0.3, 0.3, 1)
        )
        layout.add_widget(self.message)
        
        self.add_widget(layout)
    
    def check_login(self, instance):
        username = self.username.text.strip()
        password = self.password.text.strip()
        
        if not username or not password:
            self.message.text = "Please enter username and password"
            return
        
        user = db.validate_user(username, password)
        
        if user:
            self.message.text = "Login successful!"
            tracker = self.manager.get_screen("tracker")
            tracker.set_user(user)
            stats = self.manager.get_screen("stats")
            stats.set_user(user)
            self.manager.current = "tracker"
            self.username.text = ""
            self.password.text = ""
            self.message.text = ""
        else:
            self.message.text = "Invalid username or password"
    
    def go_register(self, instance):
        self.manager.current = "register"
