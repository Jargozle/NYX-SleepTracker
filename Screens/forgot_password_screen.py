"""
Forgot Password Screen for Nyx Sleep Tracker
Email verification and password reset
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
import NyxDB as db
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

from celestial_overlay import add_celestial_background


class ForgotPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        add_celestial_background(self, star_count=15, cloud_count=2)

        self.verification_code = None
        self.user_email = None
        self.step = 1  # 1: Enter email, 2: Enter code, 3: Reset password
        
        self.layout = BoxLayout(
            orientation='vertical',
            padding=40,
            spacing=20,
            size_hint=(0.85, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        self.add_widget(self.layout)
        self.show_email_step()
    
    def show_email_step(self):
        """Step 1: Enter email"""
        self.layout.clear_widgets()
        self.step = 1
        
        self.layout.add_widget(Label(
            text="Forgot Password",
            font_size=36,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=0.2
        ))
        
        self.layout.add_widget(Label(
            text="Enter your email to receive\na verification code",
            font_size=18,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=0.15
        ))
        
        self.email_input = TextInput(
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
        self.layout.add_widget(self.email_input)
        
        send_btn = Button(
            text="Send Verification Code",
            font_size=22,
            size_hint_y=None,
            height=55,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        send_btn.bind(on_press=self.send_verification_code)
        self.layout.add_widget(send_btn)
        
        self.message = Label(
            text="",
            font_size=16,
            color=(1, 0.3, 0.3, 1),
            size_hint_y=0.2
        )
        self.layout.add_widget(self.message)
        
        back_btn = Button(
            text="Back to Login",
            font_size=20,
            size_hint_y=None,
            height=50,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(back_btn)
    
    def show_code_step(self):
        """Step 2: Enter verification code"""
        self.layout.clear_widgets()
        self.step = 2
        
        self.layout.add_widget(Label(
            text="Enter Verification Code",
            font_size=36,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=0.2
        ))
        
        self.layout.add_widget(Label(
            text=f"A 6-digit code has been sent to\n{self.user_email}",
            font_size=16,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=0.15
        ))
        
        self.code_input = TextInput(
            hint_text="Verification Code",
            multiline=False,
            font_size=24,
            size_hint_y=None,
            height=50,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15],
            input_filter='int'
        )
        self.layout.add_widget(self.code_input)
        
        verify_btn = Button(
            text="Verify Code",
            font_size=22,
            size_hint_y=None,
            height=55,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        verify_btn.bind(on_press=self.verify_code)
        self.layout.add_widget(verify_btn)
        
        self.message = Label(
            text="",
            font_size=16,
            color=(1, 0.3, 0.3, 1),
            size_hint_y=0.2
        )
        self.layout.add_widget(self.message)
        
        resend_btn = Button(
            text="Resend Code",
            font_size=18,
            size_hint_y=None,
            height=45,
            background_color=(0.2, 0.2, 0.3, 1)
        )
        resend_btn.bind(on_press=lambda x: self.send_verification_code(x, resend=True))
        self.layout.add_widget(resend_btn)
        
        back_btn = Button(
            text="Back",
            font_size=20,
            size_hint_y=None,
            height=50,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        back_btn.bind(on_press=lambda x: self.show_email_step())
        self.layout.add_widget(back_btn)
    
    def show_reset_step(self):
        """Step 3: Reset password"""
        self.layout.clear_widgets()
        self.step = 3
        
        self.layout.add_widget(Label(
            text="Reset Password",
            font_size=36,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=0.15
        ))
        
        # New password with show/hide using image
        pass_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.new_pass = TextInput(
            hint_text="New Password",
            multiline=False,
            password=True,
            font_size=20,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15]
        )
        pass_container.add_widget(self.new_pass)
        
        self.show_pass_btn = Button(
            size_hint=(None, 1),
            width=50,
            background_normal='assets/Eyeslash.jpg',
            background_down='assets/Eyeslash.jpg',
            background_color=(0.6, 0.6, 0.7, 1),  # Light gray/blue color
            border=(0, 0, 0, 0)
        )
        self.show_pass_btn.bind(on_press=self.toggle_password_visibility)
        pass_container.add_widget(self.show_pass_btn)
        self.layout.add_widget(pass_container)
        
        # Confirm password with show/hide using image
        pass2_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.new_pass2 = TextInput(
            hint_text="Confirm Password",
            multiline=False,
            password=True,
            font_size=20,
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.8, 0.8, 1, 1),
            padding=[15, 15]
        )
        pass2_container.add_widget(self.new_pass2)
        
        self.show_pass2_btn = Button(
            size_hint=(None, 1),
            width=50,
            background_normal='assets/Eyeslash.jpg',
            background_down='assets/Eyeslash.jpg',
            background_color=(0.6, 0.6, 0.7, 1),  # Light gray/blue color
            border=(0, 0, 0, 0)
        )
        self.show_pass2_btn.bind(on_press=self.toggle_password2_visibility)
        pass2_container.add_widget(self.show_pass2_btn)
        self.layout.add_widget(pass2_container)
        
        # Password requirements
        self.layout.add_widget(Label(
            text="Password must have:\n• 1 uppercase, 1 lowercase\n• 3 numbers • 1 special character",
            font_size=12,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=None,
            height=60
        ))
        
        reset_btn = Button(
            text="Reset Password",
            font_size=22,
            size_hint_y=None,
            height=55,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        reset_btn.bind(on_press=self.reset_password)
        self.layout.add_widget(reset_btn)
        
        self.message = Label(
            text="",
            font_size=16,
            color=(1, 0.3, 0.3, 1),
            size_hint_y=0.15
        )
        self.layout.add_widget(self.message)
    
    def toggle_password_visibility(self, instance):
        self.new_pass.password = not self.new_pass.password
        if self.new_pass.password:
            self.show_pass_btn.background_normal = 'assets/Eyeslash.jpg'
            self.show_pass_btn.background_down = 'assets/Eyeslash.jpg'
        else:
            self.show_pass_btn.background_normal = 'assets/Eye.jpg'
            self.show_pass_btn.background_down = 'assets/Eye.jpg'
    
    def toggle_password2_visibility(self, instance):
        self.new_pass2.password = not self.new_pass2.password
        if self.new_pass2.password:
            self.show_pass2_btn.background_normal = 'assets/Eyeslash.jpg'
            self.show_pass2_btn.background_down = 'assets/Eyeslash.jpg'
        else:
            self.show_pass2_btn.background_normal = 'assets/Eye.jpg'
            self.show_pass2_btn.background_down = 'assets/Eye.jpg'
    
    def generate_code(self):
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_email(self, to_email, code):
        """Send verification code via email"""
        # IMPORTANT: Configure these with your email settings
        sender_email = "djcaguioa22@gmail.com"  # Replace with your email
        sender_password = "tbmi bdzt auar vnkv"   # Replace with your app password
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "Nyx Sleep Tracker - Password Reset Code"
        
        body = f"""
        Hello,
        
        Your password reset verification code is: {code}
        
        This code will expire in 15 minutes.
        
        If you didn't request this, please ignore this email.
        
        - Nyx Sleep Tracker Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # For Gmail, use app password: https://support.google.com/accounts/answer/185833
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def send_verification_code(self, instance, resend=False):
        email = self.email_input.text.strip() if not resend else self.user_email
        
        if not email:
            self.message.text = "Please enter your email"
            return
        
        # Validate email format
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            self.message.text = "Invalid email format"
            return
        
        # Check if email exists
        user = db.get_user_by_email(email)
        if not user:
            self.message.text = "Email not found"
            return
        
        # Generate and save code
        self.verification_code = self.generate_code()
        self.user_email = email
        db.save_reset_code(email, self.verification_code)
        
        # Send email
        self.message.text = "Sending code..."
        self.message.color = (0.8, 0.8, 0.3, 1)
        
        # Simulate email sending (replace with actual email sending)
        print(f"Verification code for {email}: {self.verification_code}")
        
        # For testing without email: just show success
        # In production, uncomment the email sending code above
        self.message.text = f"Code sent! (Test code: {self.verification_code})"
        self.message.color = (0.3, 1, 0.3, 1)
        Clock.schedule_once(lambda dt: self.show_code_step(), 2)
        
        # To actually send email, uncomment:
        if self.send_email(email, self.verification_code):
            self.message.text = "Code sent to your email!"
            self.message.color = (0.3, 1, 0.3, 1)
            Clock.schedule_once(lambda dt: self.show_code_step(), 2)
        else:
            self.message.text = "Failed to send email. Try again."
            self.message.color = (1, 0.3, 0.3, 1)
    
    def verify_code(self, instance):
        code = self.code_input.text.strip()
        
        if not code:
            self.message.text = "Please enter the verification code"
            return
        
        if db.verify_reset_code(self.user_email, code):
            self.message.text = "Code verified!"
            self.message.color = (0.3, 1, 0.3, 1)
            Clock.schedule_once(lambda dt: self.show_reset_step(), 1)
        else:
            self.message.text = "Invalid or expired code"
            self.message.color = (1, 0.3, 0.3, 1)
    
    def validate_password(self, password):
        """Validate password requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least 1 uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least 1 lowercase letter"
        
        numbers = re.findall(r'\d', password)
        if len(numbers) < 3:
            return False, "Password must contain at least 3 numbers"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least 1 special character"
        
        return True, "Valid"
    
    def reset_password(self, instance):
        password = self.new_pass.text.strip()
        password2 = self.new_pass2.text.strip()
        
        if not password:
            self.message.text = "Please enter a password"
            return
        
        # Validate password
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            self.message.text = msg
            return
        
        if password != password2:
            self.message.text = "Passwords do not match"
            return
        
        try:
            user = db.get_user_by_email(self.user_email)
            db.update_user_password(user['user_id'], password)
            db.delete_reset_code(self.user_email)
            
            self.message.text = "Password reset successful!"
            self.message.color = (0.3, 1, 0.3, 1)
            Clock.schedule_once(lambda dt: self.go_back(None), 2)
        except Exception as e:
            self.message.text = f"Error: {str(e)}"
            self.message.color = (1, 0.3, 0.3, 1)
    
    def go_back(self, instance):
        self.show_email_step()
        self.manager.current = "login"

