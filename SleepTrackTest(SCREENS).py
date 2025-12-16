from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import datetime, timedelta
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from collections import defaultdict
from kivy.garden.matpotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle as MPLRectangle
import numpy as np
import NyxDB as db

Window.size = (500, 800)
Window.clearcolor = (0.05, 0.05, 0.08, 1)

class DarkCard(BoxLayout):
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
        
        # Check if username exists
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
        
        # Profile picture
        self.profile_img = Image(
            source='assets/profile.png',
            size_hint=(None, 1),
            width=50,
            allow_stretch=True
        )
        top_bar.add_widget(self.profile_img)
        
        # Username label
        self.username_label = Label(
            text="Guest",
            font_size=20,
            color=(0.9, 0.9, 0.9, 1),
            halign='left',
            valign='middle'
        )
        self.username_label.bind(size=self.username_label.setter('text_size'))
        top_bar.add_widget(self.username_label)
        
        # Nyx title (right side)
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

        # Main content area
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        root.add_widget(content)

        # Current time display
        self.time_label = Label(
            text=datetime.now().strftime("%I:%M %p"),
            font_size=48,
            color=(0.9, 0.9, 1, 1),
            size_hint=(1, 0.15)
        )
        content.add_widget(self.time_label)
        
        # Update time every second
        Clock.schedule_interval(self.update_time, 1)

        # Sleep tracker card
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
        
        root.add_widget(nav_bar)

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
            # Start sleep session
            self.is_sleeping = True
            self.sleep_start_time = datetime.now()
            self.start_btn.text = "End Sleep"
            self.start_btn.background_color = (0.8, 0.3, 0.3, 1)
            self.sleep_label.text = "Sleep session in progress..."
        else:
            # End sleep session
            if self.sleep_start_time:
                end_time = datetime.now()
                elapsed = end_time - self.sleep_start_time
                hours = elapsed.total_seconds() / 3600
                
                # Save to database
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
        
        self.avg_card = self.create_stat_card("Average Sleep", "0.0 hrs")
        summary.add_widget(self.avg_card)
        
        self.total_card = self.create_stat_card("Total Sessions", "0")
        summary.add_widget(self.total_card)
        
        self.monthly_card = self.create_stat_card("This Month", "0.0 hrs")
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
        
        root.add_widget(nav_bar)

    def create_stat_card(self, title, value):
        card = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint_y=None, height=60)
        
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
            # Calculate statistics
            total_hours = sum(s['hours'] for s in sessions)
            avg_hours = total_hours / len(sessions)
            
            # Current month stats
            now = datetime.now()
            monthly_sessions = [s for s in sessions 
                              if s['year'] == now.year and s['month'] == now.month]
            monthly_hours = sum(s['hours'] for s in monthly_sessions)
            
            # Update cards
            self.avg_card.value_label.text = f"{avg_hours:.1f} hrs"
            self.total_card.value_label.text = str(len(sessions))
            self.monthly_card.value_label.text = f"{monthly_hours:.1f} hrs"
            
            # Update sessions list
            self.sessions_list.clear_widgets()
            for session in sessions[:10]:  # Show last 10 sessions
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
                
                self.sessions_list.add_widget(session_box)

    def on_pre_enter(self):
        # Reload stats when entering screen
        self.load_stats()

    def open_graphs(self, instance):
        graph_screen = self.manager.get_screen('graphs')
        graph_screen.set_user(self.user)
        self.manager.current = 'graphs'

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
                text="No sleep data available yet.\nStart tracking to see graphs!",
                font_size=18,
                color=(0.7, 0.7, 0.8, 1),
                size_hint_y=None,
                height=200
            ))
            return
        
        # Graph 1: Line Chart - Daily sleep hours over time
        self.graph_container.add_widget(self.create_line_chart(sessions))
        
        # Graph 2: Bar Chart - Average sleep by day of week
        self.graph_container.add_widget(self.create_day_of_week_chart(sessions))
        
        # Graph 3: Stacked Bar - Weekday vs Weekend
        self.graph_container.add_widget(self.create_weekday_weekend_chart(sessions))

    def create_line_chart(self, sessions):
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=10)
        
        container.add_widget(Label(
            text="Daily Sleep Hours Trend",
            font_size=20,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=None,
            height=30
        ))
        
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#0C0C12')
        ax.set_facecolor('#1E1E2D')
        
        # Prepare data - last 30 days
        dates = []
        hours = []
        for session in sessions[-30:]:
            date = datetime(session['year'], session['month'], session['day'])
            dates.append(date)
            hours.append(session['hours'])
        
        if dates:
            ax.plot(dates, hours, color='#6650CC', linewidth=2.5, marker='o', 
                   markersize=6, markerfacecolor='#8B7BE8', markeredgecolor='#6650CC')
            
            # Add trend line
            if len(dates) > 1:
                z = np.polyfit(mdates.date2num(dates), hours, 1)
                p = np.poly1d(z)
                ax.plot(dates, p(mdates.date2num(dates)), "--", 
                       color='#FF6B9D', alpha=0.5, linewidth=2)
            
            ax.set_ylabel('Hours Slept', color='#E0E0E0', fontsize=11)
            ax.set_xlabel('Date', color='#E0E0E0', fontsize=11)
            ax.tick_params(colors='#E0E0E0', labelsize=9)
            ax.grid(True, alpha=0.2, color='#404060')
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Add average line
            avg = np.mean(hours)
            ax.axhline(y=avg, color='#4CAF50', linestyle=':', linewidth=2, 
                      label=f'Average: {avg:.1f}h')
            ax.legend(facecolor='#1E1E2D', edgecolor='#404060', 
                     labelcolor='#E0E0E0', fontsize=9)
        
        plt.tight_layout()
        canvas = FigureCanvasKivyAgg(fig)
        container.add_widget(canvas)
        
        return container

    def create_day_of_week_chart(self, sessions):
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=10)
        
        container.add_widget(Label(
            text="Average Sleep by Day of Week",
            font_size=20,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=None,
            height=30
        ))
        
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#0C0C12')
        ax.set_facecolor('#1E1E2D')
        
        # Calculate average by day of week
        day_data = defaultdict(list)
        for session in sessions:
            date = datetime(session['year'], session['month'], session['day'])
            day_name = date.strftime('%a')  # Mon, Tue, etc.
            day_data[day_name].append(session['hours'])
        
        # Order by weekday
        days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        days = []
        averages = []
        
        for day in days_order:
            if day in day_data:
                days.append(day)
                averages.append(np.mean(day_data[day]))
        
        if days:
            colors = ['#6650CC' if day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] 
                     else '#FF6B9D' for day in days]
            
            bars = ax.bar(days, averages, color=colors, edgecolor='#8B7BE8', linewidth=1.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}h',
                       ha='center', va='bottom', color='#E0E0E0', fontsize=9)
            
            ax.set_ylabel('Average Hours', color='#E0E0E0', fontsize=11)
            ax.set_xlabel('Day of Week', color='#E0E0E0', fontsize=11)
            ax.tick_params(colors='#E0E0E0', labelsize=9)
            ax.grid(True, alpha=0.2, axis='y', color='#404060')
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#6650CC', label='Weekday'),
                Patch(facecolor='#FF6B9D', label='Weekend')
            ]
            ax.legend(handles=legend_elements, facecolor='#1E1E2D', 
                     edgecolor='#404060', labelcolor='#E0E0E0', fontsize=9)
        
        plt.tight_layout()
        canvas = FigureCanvasKivyAgg(fig)
        container.add_widget(canvas)
        
        return container

    def create_weekday_weekend_chart(self, sessions):
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=350, spacing=10)
        
        container.add_widget(Label(
            text="Weekday vs Weekend Sleep Comparison",
            font_size=20,
            color=(0.8, 0.8, 1, 1),
            size_hint_y=None,
            height=30
        ))
        
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#0C0C12')
        ax.set_facecolor('#1E1E2D')
        
        # Group by week
        week_data = defaultdict(lambda: {'weekday': [], 'weekend': []})
        
        for session in sessions:
            date = datetime(session['year'], session['month'], session['day'])
            week_num = date.strftime('%Y-W%U')  # Year-Week format
            
            if date.weekday() < 5:  # Monday = 0, Friday = 4
                week_data[week_num]['weekday'].append(session['hours'])
            else:
                week_data[week_num]['weekend'].append(session['hours'])
        
        # Prepare data for last 8 weeks
        weeks = sorted(week_data.keys())[-8:]
        weekday_avgs = []
        weekend_avgs = []
        week_labels = []
        
        for i, week in enumerate(weeks):
            weekday_hours = week_data[week]['weekday']
            weekend_hours = week_data[week]['weekend']
            
            weekday_avgs.append(np.mean(weekday_hours) if weekday_hours else 0)
            weekend_avgs.append(np.mean(weekend_hours) if weekend_hours else 0)
            week_labels.append(f'W{i+1}')
        
        if week_labels:
            x = np.arange(len(week_labels))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, weekday_avgs, width, label='Weekday',
                          color='#6650CC', edgecolor='#8B7BE8', linewidth=1.5)
            bars2 = ax.bar(x + width/2, weekend_avgs, width, label='Weekend',
                          color='#FF6B9D', edgecolor='#FF8FB5', linewidth=1.5)
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{height:.1f}',
                               ha='center', va='bottom', color='#E0E0E0', fontsize=8)
            
            ax.set_ylabel('Average Hours', color='#E0E0E0', fontsize=11)
            ax.set_xlabel('Week', color='#E0E0E0', fontsize=11)
            ax.set_xticks(x)
            ax.set_xticklabels(week_labels)
            ax.tick_params(colors='#E0E0E0', labelsize=9)
            ax.legend(facecolor='#1E1E2D', edgecolor='#404060', 
                     labelcolor='#E0E0E0', fontsize=9)
            ax.grid(True, alpha=0.2, axis='y', color='#404060')
        
        plt.tight_layout()
        canvas = FigureCanvasKivyAgg(fig)
        container.add_widget(canvas)
        
        return container

    def go_back(self, instance):
        self.manager.current = 'stats'

    def on_pre_enter(self):
        if self.user:
            self.load_graphs()

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