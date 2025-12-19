"""
Login Screen for Nyx Sleep Tracker
With show password and forgot password features
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
            spacing=15,
            size_hint=(0.85, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        layout.add_widget(Label(
            text="Nyx", 
            font_size=48,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=0.2
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
        
        # Password with show/hide button
        pass_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.password = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            font_size=20,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15]
        )
        pass_container.add_widget(self.password)
        
        self.show_pass_btn = Button(
            text="👁",
            size_hint=(None, 1),
            width=50,
            font_size=24,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        self.show_pass_btn.bind(on_press=self.toggle_password_visibility)
        pass_container.add_widget(self.show_pass_btn)
        layout.add_widget(pass_container)
        
        # Forgot Password as clickable text (invisible button)
        forgot_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=30
        )
        
        forgot_btn = Button(
            text="Forgot Password?",
            font_size=16,
            size_hint=(None, None),
            size=(200, 30),
            background_color=(0, 0, 0, 0),  # Completely transparent
            background_normal='',
            background_down='',
            border=(0, 0, 0, 0),
            color=(0.5, 0.7, 1, 1),  # Light blue
            halign='left',
            valign='middle',
            pos_hint={'x': 0, 'center_y': 0.5}
        )
        forgot_btn.bind(size=forgot_btn.setter('text_size'))
        forgot_btn.bind(on_press=self.go_forgot_password)
        
        forgot_container.add_widget(forgot_btn)
        forgot_container.add_widget(Label(size_hint_x=1))  # Spacer to push text left
        
        layout.add_widget(forgot_container)
        
        # Login button
        login_btn = Button(
            text="Login",
            font_size=22,
            size_hint_y=None,
            height=55,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        login_btn.bind(on_press=self.check_login)
        layout.add_widget(login_btn)
        
        # Separator with "Or"
        separator_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=30,
            spacing=10,
            padding=[0, 10]
        )
        
        separator_box.add_widget(Label(
            text="──────",
            font_size=18,
            color=(0.5, 0.5, 0.6, 1)
        ))
        
        separator_box.add_widget(Label(
            text="Or",
            font_size=18,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_x=0.3
        ))
        
        separator_box.add_widget(Label(
            text="──────",
            font_size=18,
            color=(0.5, 0.5, 0.6, 1)
        ))
        
        layout.add_widget(separator_box)
        
        # Register button
        reg_btn = Button(
            text="Register",
            font_size=20,
            size_hint_y=None,
            height=50,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        reg_btn.bind(on_press=self.go_register)
        layout.add_widget(reg_btn)
        
        # Message label
        self.message = Label(
            text="",
            font_size=16,
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30
        )
        layout.add_widget(self.message)
        
        self.add_widget(layout)
    
    def toggle_password_visibility(self, instance):
        self.password.password = not self.password.password
        self.show_pass_btn.text = "👁" if self.password.password else "👁‍🗨"
    
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
            self.password.password = True
            self.show_pass_btn.text = "👁"
            self.message.text = ""
        else:
            self.message.text = "Invalid username or password"
    
    def go_register(self, instance):
        self.manager.current = "register"
    
    def go_forgot_password(self, instance):
        self.manager.current = "forgot_password"
