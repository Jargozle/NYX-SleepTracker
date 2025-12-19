"""
Nyx Sleep Tracker - Automatic Project Setup Script
Run this script to automatically create all project files
"""

import os

# Create directories
os.makedirs('screens', exist_ok=True)
os.makedirs('assets', exist_ok=True)

# File contents
files = {
    'main.py': '''"""
Nyx Sleep Tracker - Main Application
Run this file to start the application
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.tracker_screen import TrackerScreen
from screens.stats_screen import StatsScreen
from screens.graph_screen import GraphScreen

Window.size = (500, 800)
Window.clearcolor = (0.05, 0.05, 0.08, 1)


class NyxApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(TrackerScreen(name="tracker"))
        sm.add_widget(StatsScreen(name="stats"))
        sm.add_widget(GraphScreen(name="graphs"))
        return sm


if __name__ == "__main__":
    NyxApp().run()
''',

    'components.py': '''"""
Reusable UI Components for Nyx Sleep Tracker
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle


class DarkCard(BoxLayout):
    """Dark themed card container with rounded corners"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 20
        self.spacing = 20
        self.orientation = 'vertical'

        with self.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            self.rect = RoundedRectangle(radius=[20])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


def create_stat_card(title, value):
    """Create a statistics card with title and value"""
    card = BoxLayout(orientation='vertical', padding=10, spacing=5, 
                     size_hint_y=None, height=60)
    
    with card.canvas.before:
        Color(0.12, 0.12, 0.18, 1)
        card.rect = RoundedRectangle(radius=[15])
    card.bind(pos=lambda *args: setattr(card.rect, 'pos', card.pos),
              size=lambda *args: setattr(card.rect, 'size', card.size))
    
    title_label = Label(
        text=title,
        font_size=12,
        color=(0.7, 0.7, 0.8, 1),
        size_hint=(1, None),
        height=15,
        halign='center',
        valign='middle'
    )
    title_label.bind(size=title_label.setter('text_size'))
    card.add_widget(title_label)
    
    value_label = Label(
        text=value,
        font_size=20,
        color=(0.9, 0.9, 1, 1),
        size_hint=(1, None),
        height=25,
        halign='center',
        valign='middle'
    )
    value_label.bind(size=value_label.setter('text_size'))
    card.add_widget(value_label)
    card.value_label = value_label
    
    return card
''',

    'screens/__init__.py': '''# This makes screens a Python package
''',

    'screens/login_screen.py': '''"""
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
''',

    'screens/register_screen.py': '''"""
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
''',

    'screens/tracker_screen.py': '''"""
Sleep Tracker Screen for Nyx Sleep Tracker
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from datetime import datetime
from components import DarkCard
import NyxDB as db


class TrackerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None
        self.sleep_start_time = None
        self.is_sleeping = False

        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        self.add_widget(root)

        # Top bar with profile
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.12),
            padding=[20, 10, 20, 10],
            spacing=15
        )
        
        with top_bar.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.top_rect = Rectangle()
        top_bar.bind(pos=self.update_top_rect, size=self.update_top_rect)
        
        self.profile_img = Image(
            source='assets/profile.png',
            size_hint=(None, 1),
            width=50,
            allow_stretch=True
        )
        top_bar.add_widget(self.profile_img)
        
        self.username_label = Label(
            text="Guest",
            font_size=20,
            color=(0.9, 0.9, 0.9, 1),
            halign='left',
            valign='middle'
        )
        self.username_label.bind(size=self.username_label.setter('text_size'))
        top_bar.add_widget(self.username_label)
        
        title = Label(
            text="Nyx",
            font_size=28,
            color=(0.8, 0.8, 1, 1),
            size_hint=(None, 1),
            width=80,
            halign='right'
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)

        # Main content
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        root.add_widget(content)

        self.time_label = Label(
            text=datetime.now().strftime("%I:%M %p"),
            font_size=48,
            color=(0.9, 0.9, 1, 1),
            size_hint=(1, 0.15)
        )
        content.add_widget(self.time_label)
        
        Clock.schedule_interval(self.update_time, 1)

        card = DarkCard(size_hint=(1, 0.65))
        content.add_widget(card)

        self.sleep_label = Label(
            text="Ready to track your sleep",
            font_size=22,
            color=(0.9, 0.9, 0.9, 1)
        )
        card.add_widget(self.sleep_label)

        self.duration_label = Label(
            text="",
            font_size=32,
            color=(0.8, 0.8, 1, 1)
        )
        card.add_widget(self.duration_label)

        self.start_btn = Button(
            text="Start Sleep",
            size_hint=(1, 0.3),
            background_color=(0.4, 0.3, 0.8, 1),
            font_size=24
        )
        self.start_btn.bind(on_press=self.toggle_sleep)
        card.add_widget(self.start_btn)

        # Bottom navigation
        root.add_widget(self._create_nav_bar())

    def _create_nav_bar(self):
        nav_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=20,
            padding=[20, 10]
        )
        
        with nav_bar.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.nav_rect = RoundedRectangle(radius=[30])
        nav_bar.bind(pos=self.update_nav_rect, size=self.update_nav_rect)
        
        tracker_btn = Button(
            text="Tracker",
            font_size=20,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        tracker_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'tracker'))
        nav_bar.add_widget(tracker_btn)
        
        stats_btn = Button(
            text="Statistics",
            font_size=20,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        stats_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'stats'))
        nav_bar.add_widget(stats_btn)
        
        return nav_bar

    def update_top_rect(self, *args):
        self.top_rect.pos = self.top_rect.pos[0], self.top_rect.pos[1]
        self.top_rect.size = self.size[0], self.size[1] * 0.12

    def update_nav_rect(self, *args):
        nav_bar = self.children[0].children[0]
        self.nav_rect.pos = nav_bar.pos
        self.nav_rect.size = nav_bar.size

    def update_time(self, dt):
        self.time_label.text = datetime.now().strftime("%I:%M %p")
        
        if self.is_sleeping and self.sleep_start_time:
            elapsed = datetime.now() - self.sleep_start_time
            hours = elapsed.total_seconds() / 3600
            self.duration_label.text = f"{hours:.1f} hours"

    def set_user(self, user):
        self.user = user
        self.username_label.text = user['username']
        if user.get('profile_pic'):
            try:
                self.profile_img.source = user['profile_pic']
            except:
                self.profile_img.source = 'assets/profile.png'

    def toggle_sleep(self, instance):
        if not self.is_sleeping:
            self.is_sleeping = True
            self.sleep_start_time = datetime.now()
            self.start_btn.text = "End Sleep"
            self.start_btn.background_color = (0.8, 0.3, 0.3, 1)
            self.sleep_label.text = "Sleep session in progress..."
        else:
            if self.sleep_start_time:
                end_time = datetime.now()
                elapsed = end_time - self.sleep_start_time
                hours = elapsed.total_seconds() / 3600
                
                if self.user:
                    db.add_sleep_session(
                        self.user['user_id'],
                        self.sleep_start_time.year,
                        self.sleep_start_time.month,
                        self.sleep_start_time.day,
                        round(hours, 2)
                    )
                
                self.sleep_label.text = f"Session complete! You slept for {hours:.1f} hours"
            
            self.is_sleeping = False
            self.sleep_start_time = None
            self.start_btn.text = "Start Sleep"
            self.start_btn.background_color = (0.4, 0.3, 0.8, 1)
            self.duration_label.text = ""
''',

    'screens/stats_screen.py': '''"""
Statistics Screen for Nyx Sleep Tracker
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from datetime import datetime
from components import create_stat_card
import NyxDB as db


class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None

        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        self.add_widget(root)

        # Top bar
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            padding=[20, 10]
        )
        
        with top_bar.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.top_rect = Rectangle()
        top_bar.bind(pos=self.update_top_rect, size=self.update_top_rect)
        
        top_bar.add_widget(Label(
            text="Statistics",
            font_size=32,
            color=(0.8, 0.8, 1, 1),
            halign='left'
        ))
        
        root.add_widget(top_bar)

        # Stats content
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        root.add_widget(content)

        # Summary cards
        summary = BoxLayout(orientation='vertical', spacing=8, size_hint=(1, 0.22))
        
        self.avg_card = create_stat_card("Average Sleep", "0.0 hrs")
        summary.add_widget(self.avg_card)
        
        self.total_card = create_stat_card("Total Sessions", "0")
        summary.add_widget(self.total_card)
        
        self.monthly_card = create_stat_card("This Month", "0.0 hrs")
        summary.add_widget(self.monthly_card)
        
        content.add_widget(summary)

        # Graph button
        graph_btn = Button(
            text="View Sleep Graphs",
            size_hint=(1, None),
            height=60,
            font_size=20,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        graph_btn.bind(on_press=self.open_graphs)
        content.add_widget(graph_btn)

        # Sleep sessions list
        sessions_label = Label(
            text="Recent Sleep Sessions",
            font_size=20,
            color=(0.8, 0.8, 1, 1),
            size_hint=(1, None),
            height=40
        )
        content.add_widget(sessions_label)

        scroll = ScrollView(size_hint=(1, 0.45))
        self.sessions_list = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=[0, 10]
        )
        self.sessions_list.bind(minimum_height=self.sessions_list.setter('height'))
        scroll.add_widget(self.sessions_list)
        content.add_widget(scroll)

        # Bottom navigation
        root.add_widget(self._create_nav_bar())

    def _create_nav_bar(self):
        nav_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=20,
            padding=[20, 10]
        )
        
        with nav_bar.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.nav_rect = RoundedRectangle(radius=[30])
        nav_bar.bind(pos=self.update_nav_rect, size=self.update_nav_rect)
        
        tracker_btn = Button(
            text="Tracker",
            font_size=20,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        tracker_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'tracker'))
        nav_bar.add_widget(tracker_btn)
        
        stats_btn = Button(
            text="Statistics",
            font_size=20,
            background_color=(0.4, 0.3, 0.8, 1)
        )
        stats_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'stats'))
        nav_bar.add_widget(stats_btn)
        
        return nav_bar

    def update_top_rect(self, *args):
        self.top_rect.pos = self.top_rect.pos[0], self.top_rect.pos[1]
        self.top_rect.size = self.size[0], self.size[1] * 0.1

    def update_nav_rect(self, *args):
        nav_bar = self.children[0].children[0]
        self.nav_rect.pos = nav_bar.pos
        self.nav_rect.size = nav_bar.size

    def set_user(self, user):
        self.user = user
        self.load_stats()

    def load_stats(self):
        if not self.user:
            return
        
        sessions = db.get_all_sessions(self.user['user_id'])
        
        if sessions:
            total_hours = sum(s['hours'] for s in sessions)
            avg_hours = total_hours / len(sessions)
            
            now = datetime.now()
            monthly_sessions = [s for s in sessions 
                              if s['year'] == now.year and s['month'] == now.month]
            monthly_hours = sum(s['hours'] for s in monthly_sessions)
            
            self.avg_card.value_label.text = f"{avg_hours:.1f} hrs"
            self.total_card.value_label.text = str(len(sessions))
            self.monthly_card.value_label.text = f"{monthly_hours:.1f} hrs"
            
            self.sessions_list.clear_widgets()
            for session in sessions[:10]:
                session_box = self._create_session_item(session)
                self.sessions_list.add_widget(session_box)

    def _create_session_item(self, session):
        session_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            padding=15,
            spacing=10
        )
        
        with session_box.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            session_box.rect = RoundedRectangle(radius=[10])
        session_box.bind(
            pos=lambda inst, val, sb=session_box: setattr(sb.rect, 'pos', sb.pos),
            size=lambda inst, val, sb=session_box: setattr(sb.rect, 'size', sb.size)
        )
        
        date_str = f"{session['year']}-{str(session['month']).zfill(2)}-{str(session['day']).zfill(2)}"
        
        session_box.add_widget(Label(
            text=date_str,
            font_size=16,
            color=(0.8, 0.8, 0.9, 1)
        ))
        
        session_box.add_widget(Label(
            text=f"{session['hours']:.1f} hrs",
            font_size=18,
            color=(0.6, 0.8, 0.6, 1),
            size_hint_x=0.4
        ))
        
        return session_box

    def on_pre_enter(self):
        self.load_stats()

    def open_graphs(self, instance):
        graph_screen = self.manager.get_screen('graphs')
        graph_screen.set_user(self.user)
        self.manager.current = 'graphs'
''',

    'screens/graph_screen.py': '''"""
Graph Screen for Nyx Sleep Tracker
Uses Plotly for data visualization
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from datetime import datetime
from collections import defaultdict
from PIL import Image as PILImage
from io import BytesIO
import plotly.graph_objects as go
import NyxDB as db


class GraphScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None

        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        self.add_widget(root)

        # Top bar
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            padding=[20, 10]
        )
        
        with top_bar.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.top_rect = Rectangle()
        top_bar.bind(pos=self.update_top_rect, size=self.update_top_rect)
        
        back_btn = Button(
            text="← Back",
            font_size=18,
            size_hint=(None, 1),
            width=100,
            background_color=(0.25, 0.25, 0.35, 1)
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        top_bar.add_widget(Label(
            text="Sleep Graphs",
            font_size=28,
            color=(0.8, 0.8, 1, 1)
        ))
        
        root.add_widget(top_bar)

        # Scrollable content for graphs
        scroll = ScrollView(size_hint=(1, 0.92))
        self.graph_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20,
            size_hint_y=None
        )
        self.graph_container.bind(minimum_height=self.graph_container.setter('height'))
        scroll.add_widget(self.graph_container)
        root.add_widget(scroll)

    def update_top_rect(self, *args):
        self.top_rect.pos = self.top_rect.pos[0], self.top_rect.pos[1]
        self.top_rect.size = self.size[0], self.size[1] * 0.08

    def set_user(self, user):
        self.user = user
        self.load_graphs()

    def load_graphs(self):
        if not self.user:
            return
        
        self.graph_container.clear_widgets()
        
        sessions = db.get_all_sessions(self.user['user_id'])
        
        if not sessions:
            self.graph_container.add_widget(Label(
                text="No sleep data available yet.\\nStart tracking to see graphs!",
                font_size=18,
                color=(0.7, 0.7, 0.8, 1),
                size_hint_y=None,
                height=200
            ))
            return
        
        # Create charts
        self.graph_container.add_widget(self.create_line_chart(sessions))
        self.graph_container.add_widget(self.create_weekday_chart(sessions))
        self.graph_container.add_widget(self.create_monthly_chart(sessions))

    def plotly_to_kivy_image(self, fig):
        """Convert Plotly figure to Kivy Image widget"""
        img_bytes = fig.to_image(format="png", width=450, height=300)
        pil_image = PILImage.open(BytesIO(img_bytes))
        
        img_data = pil_image.tobytes()
        texture = Texture.create(size=(pil_image.width, pil_image.height), colorfmt='rgb')
        texture.blit_buffer(img_data, colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical()
        
        img_widget = Image(texture=texture, size_hint_y=None, height=300)
        return img_widget

    def create_line_chart(self, sessions):
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=10)
        
        container.add_widget(Label(
            text="Sleep Duration Trend",
            font_size=20,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=None,
            height=30
        ))
        
        # Prepare data
        dates = []
        hours = []
        for session in sessions[-30:]:
            date = datetime(session['year'], session['month'], session['day'])
            dates.append(date)
            hours.append(session['hours'])
        
        # Create Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=hours,
            mode='lines+markers',
            line=dict(color='rgb(102, 77, 204)', width=3),
            marker=dict(size=8, color='rgb(128, 102, 255)')
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Date",
            yaxis_title="Hours",
            plot_bgcolor='rgb(20, 20, 30)',
            paper_bgcolor='rgb(20, 20, 30)',
            font=dict(color='rgb(200, 200, 220)'),
            margin=dict(l=40, r=20, t=20, b=40)
        )
        
        img_widget = self.plotly_to_kivy_image(fig)
        container.add_widget(img_widget)
        
        return container

    def create_weekday_chart(self, sessions):
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=10)
        
        container.add_widget(Label(
            text="Average Sleep by Day of Week",
            font_size=20,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=None,
            height=30
        ))
        
        # Group by weekday
        weekday_data = defaultdict(list)
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for session in sessions:
            date = datetime(session['year'], session['month'], session['day'])
            weekday = date.weekday()
            weekday_data[weekday].append(session['hours'])
        
        weekdays = []
        averages = []
        for i in range(7):
            if i in weekday_data:
                weekdays.append(weekday_names[i])
                averages.append(sum(weekday_data[i]) / len(weekday_data[i]))
        
        # Create Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weekdays,
            y=averages,
            marker=dict(color='rgb(102, 77, 204)')
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Day of Week",
            yaxis_title="Average Hours",
            plot_bgcolor='rgb(20, 20, 30)',
            paper_bgcolor='rgb(20, 20, 30)',
            font=dict(color='rgb(200, 200, 220)'),
            margin=dict(l=40, r=20, t=20, b=40)
        )
        
        img_widget = self.plotly_to_kivy_image(fig)
        container.add_widget(img_widget)
        
        return container

    def create_monthly_chart(self, sessions):
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=10)
        
        container.add_widget(Label(
            text="Monthly Average Sleep",
            font_size=20,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=None,
            height=30
        ))
        
        # Group by month
        monthly_data = defaultdict(list)
        for session in sessions:
            key = f"{session['year']}-{str(session['month']).zfill(2)}"
            monthly_data[key].append(session['hours'])
        
        months = sorted(monthly_data.keys())
        averages = [sum(monthly_data[m]) / len(monthly_data[m]) for m in months]
        
        # Create Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=months,
            y=averages,
            marker=dict(color='rgb(102, 77, 204)')
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Month",
            yaxis_title="Average Hours",
            plot_bgcolor='rgb(20, 20, 30)',
            paper_bgcolor='rgb(20, 20, 30)',
            font=dict(color='rgb(200, 200, 220)'),
            margin=dict(l=40, r=20, t=20, b=40)
        )
        
        img_widget = self.plotly_to_kivy_image(fig)
        container.add_widget(img_widget)
        
        return container

    def go_back(self, instance):
        self.manager.current = 'stats'

    def on_pre_enter(self):
        if self.user:
            self.load_graphs()
'''
}

# Write all files
print("🚀 Setting up Nyx Sleep Tracker project...")
print()

for filepath, content in files.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filepath}")

# Create a placeholder profile image notice
assets_readme = """# Assets Folder

Place your profile.png image here.

If you don't have one, the app will show an error. You can:
1. Add any PNG image named 'profile.png' here
2. Or modify the code to handle missing images gracefully
"""

with open('assets/README.txt', 'w') as f:
    f.write(assets_readme)

print()
print("="*60)
print("✨ Setup Complete!")
print("="*60)
print()
print("📂 Project structure created:")
print("   ├── main.py")
print("   ├── components.py")
print("   ├── screens/")
print("   │   ├── __init__.py")
print("   │   ├── login_screen.py")
print("   │   ├── register_screen.py")
print("   │   ├── tracker_screen.py")
print("   │   ├── stats_screen.py")
print("   │   └── graph_screen.py")
print("   └── assets/")
print("       └── README.txt")
print()
print("⚠️  DON'T FORGET:")
print("   1. Make sure NyxDB.py is in this directory")
print("   2. Add a profile.png image to the assets/ folder")
print("   3. Install dependencies:")
print("      pip install kivy plotly kaleido pillow")
print()
print("🎯 To run the app:")
print("   python main.py")
print()
