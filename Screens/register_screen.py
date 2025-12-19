"""
Registration Screen for Nyx Sleep Tracker
With email and enhanced password requirements
"""

import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
import NyxDB as db
import re
from celestial_overlay import add_celestial_background


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        add_celestial_background(self, star_count=15, cloud_count=2)

        layout = BoxLayout(
            orientation='vertical',
            padding=40,
            spacing=15,
            size_hint=(0.85, 0.9),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        layout.add_widget(Label(
            text="Create Account",
            font_size=36,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=0.15
        ))
        
        # Username
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
        
        # Email
        self.reg_email = TextInput(
            hint_text="Email",
            multiline=False,
            font_size=20,
            size_hint_y=None,
            height=50,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15]
        )
        layout.add_widget(self.reg_email)
        
        # Password with show/hide using image
        pass_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.reg_pass = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            font_size=20,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15]
        )
        pass_container.add_widget(self.reg_pass)
        
        self.show_pass_btn = Button(
            size_hint=(None, 1),
            width=50,
            background_normal='assets/Eyeslash.jpg',
            background_down='assets/Eyeslash.jpg',
            border=(0, 0, 0, 0)
        )
        self.show_pass_btn.bind(on_press=self.toggle_password_visibility)
        pass_container.add_widget(self.show_pass_btn)
        layout.add_widget(pass_container)
        
        # Confirm Password with show/hide using image
        pass2_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.reg_pass2 = TextInput(
            hint_text="Confirm Password",
            multiline=False,
            password=True,
            font_size=20,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15]
        )
        pass2_container.add_widget(self.reg_pass2)
        
        self.show_pass2_btn = Button(
            size_hint=(None, 1),
            width=50,
            background_normal='assets/Eyeslash.jpg',
            background_down='assets/Eyeslash.jpg',
            border=(0, 0, 0, 0)
        )
        self.show_pass2_btn.bind(on_press=self.toggle_password2_visibility)
        pass2_container.add_widget(self.show_pass2_btn)
        layout.add_widget(pass2_container)
        
        # Password requirements label
        self.req_label = Label(
            text="Password must have:\n• 1 uppercase, 1 lowercase letter\n• 3 numbers\n• 1 special character (!@#$%^&*),",
            font_size=12,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=None,
            height=60,
            halign='left',
            valign='top'
        )
        self.req_label.bind(size=self.req_label.setter('text_size'))
        layout.add_widget(self.req_label)
        
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
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=40
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
    
    def toggle_password_visibility(self, instance):
        self.reg_pass.password = not self.reg_pass.password
        if self.reg_pass.password:
            self.show_pass_btn.background_normal = 'assets/Eyeslash.jpg'
            self.show_pass_btn.background_down = 'assets/Eyeslash.jpg'
        else:
            self.show_pass_btn.background_normal = 'assets/Eye.jpg'
            self.show_pass_btn.background_down = 'assets/Eye.jpg'
    
    def toggle_password2_visibility(self, instance):
        self.reg_pass2.password = not self.reg_pass2.password
        if self.reg_pass2.password:
            self.show_pass2_btn.background_normal = 'assets/Eyeslash.jpg'
            self.show_pass2_btn.background_down = 'assets/Eyeslash.jpg'
        else:
            self.show_pass2_btn.background_normal = 'assets/Eye.jpg'
            self.show_pass2_btn.background_down = 'assets/Eye.jpg'
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """
        Validate password requirements:
        - At least 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 3 numbers
        - At least 1 special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least 1 uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least 1 lowercase letter"
        
        # Count numbers
        numbers = re.findall(r'\d', password)
        if len(numbers) < 3:
            return False, "Password must contain at least 3 numbers"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least 1 special character"
        
        return True, "Valid"
    
    def register(self, instance):
        username = self.reg_user.text.strip()
        email = self.reg_email.text.strip()
        password = self.reg_pass.text.strip()
        password2 = self.reg_pass2.text.strip()
        
        if not username or not email or not password:
            self.message.text = "All fields are required"
            return
        
        if len(username) < 3:
            self.message.text = "Username must be at least 3 characters"
            return
        
        # Validate email
        if not self.validate_email(email):
            self.message.text = "Invalid email format"
            return
        
        # Validate password
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            self.message.text = msg
            return
        
        if password != password2:
            self.message.text = "Passwords do not match"
            return
        
        # Check if username exists
        existing_user = db.get_user_by_name(username)
        if existing_user:
            self.message.text = "Username already exists"
            return
        
        # Check if email exists
        existing_email = db.get_user_by_email(email)
        if existing_email:
            self.message.text = "Email already registered"
            return
        
        try:
            db.create_user(username, password, email)
            self.message.text = "Account created successfully!"
            self.message.color = (0.3, 1, 0.3, 1)
            Clock.schedule_once(lambda dt: self.go_back(None), 1.5)
        except Exception as e:
            self.message.text = f"Error: {str(e)}"
    
    def go_back(self, instance):
        self.reg_user.text = ""
        self.reg_email.text = ""
        self.reg_pass.text = ""
        self.reg_pass2.text = ""
        self.message.text = ""
        self.message.color = (1, 0.3, 0.3, 1)
        self.reg_pass.password = True
        self.reg_pass2.password = True
        self.manager.current = "login"
