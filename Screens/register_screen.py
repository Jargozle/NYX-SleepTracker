"""
Registration Screen for Nyx Sleep Tracker
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import NyxDB as db


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(
            orientation='vertical',
            padding=40,
            spacing=20,
            size_hint=(0.85, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        layout.add_widget(Label(
            text="Create Account",
            font_size=36,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=0.2
        ))
        
        self.reg_user = TextInput(
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
        layout.add_widget(self.reg_user)
        
        self.reg_pass = TextInput(
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
        layout.add_widget(self.reg_pass)
        
        self.reg_pass2 = TextInput(
            hint_text="Confirm Password",
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
        layout.add_widget(self.reg_pass2)
        
        register_btn = Button(
            text="Create Account",
            font_size=22,
            size_hint_y=None,
            height=55,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        register_btn.bind(on_press=self.register)
        layout.add_widget(register_btn)
        
        self.message = Label(
            text="",
            font_size=16,
            color=(1, 0.3, 0.3, 1)
        )
        layout.add_widget(self.message)
        
        back_btn = Button(
            text="Back to Login",
            font_size=20,
            size_hint_y=None,
            height=50,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def register(self, instance):
        username = self.reg_user.text.strip()
        password = self.reg_pass.text.strip()
        password2 = self.reg_pass2.text.strip()
        
        if not username or not password:
            self.message.text = "Username and password required"
            return
        
        if len(username) < 3:
            self.message.text = "Username must be at least 3 characters"
            return
        
        if len(password) < 6:
            self.message.text = "Password must be at least 6 characters"
            return
        
        if password != password2:
            self.message.text = "Passwords do not match"
            return
        
        existing_user = db.get_user_by_name(username)
        if existing_user:
            self.message.text = "Username already exists"
            return
        
        try:
            db.create_user(username, password)
            self.message.text = "Account created successfully!"
            self.message.color = (0.3, 1, 0.3, 1)
            Clock.schedule_once(lambda dt: self.go_back(None), 1.5)
        except Exception as e:
            self.message.text = f"Error: {str(e)}"
    
    def go_back(self, instance):
        self.reg_user.text = ""
        self.reg_pass.text = ""
        self.reg_pass2.text = ""
        self.message.text = ""
        self.message.color = (1, 0.3, 0.3, 1)
        self.manager.current = "login"
