"""
Sleep Tracker Screen for Nyx Sleep Tracker with Bedtime & Alarm
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
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
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        root.add_widget(content)

        # Current time display
        self.time_label = Label(
            text=datetime.now().strftime("%I:%M %p"),
            font_size=48,
            color=(0.9, 0.9, 1, 1),
            size_hint=(1, None),
            height=70
        )
        content.add_widget(self.time_label)
        
        Clock.schedule_interval(self.update_time, 1)

        # Bedtime and Alarm Settings Card
        time_card = DarkCard(size_hint=(1, None), height=140)
        
        time_grid = BoxLayout(orientation='horizontal', spacing=15)
        
        # Bedtime section
        bedtime_box = BoxLayout(orientation='vertical', spacing=8)
        bedtime_box.add_widget(Label(
            text="Bedtime",
            font_size=16,
            color=(0.8, 0.8, 0.9, 1),
            size_hint_y=None,
            height=25
        ))
        
        bedtime_inputs = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=45)
        
        self.bedtime_hour = TextInput(
            text="10",
            multiline=False,
            input_filter='int',
            font_size=20,
            halign='center',
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[10, 12]
        )
        bedtime_inputs.add_widget(self.bedtime_hour)
        
        bedtime_inputs.add_widget(Label(text=":", font_size=24, color=(0.8, 0.8, 0.9, 1), size_hint_x=0.2))
        
        self.bedtime_minute = TextInput(
            text="00",
            multiline=False,
            input_filter='int',
            font_size=20,
            halign='center',
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[10, 12]
        )
        bedtime_inputs.add_widget(self.bedtime_minute)
        
        self.bedtime_ampm = Spinner(
            text='PM',
            values=('AM', 'PM'),
            size_hint_x=0.6,
            background_color=(0.4, 0.3, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=18
        )
        bedtime_inputs.add_widget(self.bedtime_ampm)
        
        bedtime_box.add_widget(bedtime_inputs)
        time_grid.add_widget(bedtime_box)
        
        # Alarm section
        alarm_box = BoxLayout(orientation='vertical', spacing=8)
        alarm_box.add_widget(Label(
            text="Alarm",
            font_size=16,
            color=(0.8, 0.8, 0.9, 1),
            size_hint_y=None,
            height=25
        ))
        
        alarm_inputs = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=45)
        
        self.alarm_hour = TextInput(
            text="06",
            multiline=False,
            input_filter='int',
            font_size=20,
            halign='center',
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[10, 12]
        )
        alarm_inputs.add_widget(self.alarm_hour)
        
        alarm_inputs.add_widget(Label(text=":", font_size=24, color=(0.8, 0.8, 0.9, 1), size_hint_x=0.2))
        
        self.alarm_minute = TextInput(
            text="30",
            multiline=False,
            input_filter='int',
            font_size=20,
            halign='center',
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[10, 12]
        )
        alarm_inputs.add_widget(self.alarm_minute)
        
        self.alarm_ampm = Spinner(
            text='AM',
            values=('AM', 'PM'),
            size_hint_x=0.6,
            background_color=(0.4, 0.3, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=18
        )
        alarm_inputs.add_widget(self.alarm_ampm)
        
        alarm_box.add_widget(alarm_inputs)
        time_grid.add_widget(alarm_box)
        
        time_card.add_widget(time_grid)
        content.add_widget(time_card)

        # Sleep tracker card
        card = DarkCard(size_hint=(1, 0.55))
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