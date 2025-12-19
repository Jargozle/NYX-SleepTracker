"""
Sleep Tracker Screen for Nyx Sleep Tracker with Bedtime & Alarm
Windows-compatible version using win10toast for notifications
"""
print("🔥 NEW TRACKER SCREEN LOADED 🔥")

import random
from kivy.resources import resource_find
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from datetime import datetime, time
from celestial_overlay import CelestialOverlay
from components import DarkCard
import NyxDB as db
import os
import sys
from celestial_overlay import add_celestial_background

resource_add_path(os.path.join(os.path.dirname(__file__), '..'))
resource_add_path(os.path.join(os.path.dirname(__file__), '..', 'assets'))

# Try to import notification library
NOTIFICATIONS_AVAILABLE = False
try:
    if sys.platform == 'win32':
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        NOTIFICATIONS_AVAILABLE = True
        print("Windows notifications enabled (win10toast)")
except ImportError:
    print(" win10toast not installed.")
    print(" Notifications will be disabled, but alarms will still work.")

class AlarmOverlay(FloatLayout):
    """Full-screen alarm overlay with sound and stop button"""
    
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        
        # Semi-transparent dark background
        with self.canvas.before:
            Color(0, 0, 0, 0.85)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Center container
        center_box = BoxLayout(
            orientation='vertical',
            spacing=30,
            padding=40,
            size_hint=(0.8, None),
            height=350,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        with center_box.canvas.before:
            Color(0.15, 0.12, 0.25, 1)
            center_box.rect = RoundedRectangle(radius=[30])
        center_box.bind(
            pos=lambda inst, val: setattr(center_box.rect, 'pos', center_box.pos),
            size=lambda inst, val: setattr(center_box.rect, 'size', center_box.size)
        )
        
        # Alarm title
        center_box.add_widget(Label(
            text="WAKE UP!",
            font_size=48,
            color=(1, 0.9, 0.3, 1),
            bold=True,
            size_hint_y=0.3
        ))
        
        # Current time
        self.time_label = Label(
            text=datetime.now().strftime("%I:%M %p"),
            font_size=32,
            color=(0.9, 0.9, 1, 1),
            size_hint_y=0.2
        )
        center_box.add_widget(self.time_label)
        Clock.schedule_interval(self.update_time, 1)
        
        # Stop button
        stop_btn = Button(
            text="Stop Alarm",
            font_size=28,
            size_hint_y=0.3,
            background_color=(0.8, 0.3, 0.3, 1)
        )
        stop_btn.bind(on_press=self.stop_alarm)
        center_box.add_widget(stop_btn)
        
        self.add_widget(center_box)
        
        # Load and play alarm sound
        self.alarm_sound = None
        self.load_alarm_sound()
        
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def update_time(self, dt):
        self.time_label.text = datetime.now().strftime("%I:%M %p")
    
    def load_alarm_sound(self):
        """Load alarm sound - tries multiple common alarm sound paths"""
        sound_paths = [
            'assets/alarm.wav',
            'assets/alarm.mp3',
            'assets/alarm.ogg'
        ]
        
        for sound_path in sound_paths:
            if os.path.exists(sound_path):
                self.alarm_sound = SoundLoader.load(sound_path)
                if self.alarm_sound:
                    self.alarm_sound.loop = True
                    self.alarm_sound.play()
                    print(f"🔊 Playing alarm sound: {sound_path}")
                    break
        
        # If no sound file found, print warning
        if not self.alarm_sound:
            print("  No alarm sound found. Place an alarm sound file in assets/")
            print("  Supported formats: alarm.wav, alarm.mp3, alarm.ogg")
    
    def stop_alarm(self, instance):
        """Stop the alarm sound and close overlay"""
        if self.alarm_sound:
            self.alarm_sound.stop()
        Clock.unschedule(self.update_time)
        self.callback()


class TrackerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.user = None
        self.sleep_start_time = None
        self.is_sleeping = False
        self.bedtime_enabled = False
        self.alarm_enabled = False
        self.alarm_overlay = None
        self.last_alarm_trigger = None  # Prevent repeated triggers
        self.check_event = None  # Store the Clock event

        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        self.root_layout = root
        
        add_celestial_background(root, star_count=25, cloud_count=3)

        self.add_widget(root)
        
        # Top bar with responsive height
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.12),  # 12% of screen height
            padding=[20, 15],
            spacing=15
        )
        
        with top_bar.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.top_rect = Rectangle()
        top_bar.bind(pos=self.update_top_rect, size=self.update_top_rect)
        
        # Logo on the left
        logo_img = Image(
            source='assets/iconlogo.png',
            size_hint=(None, 1),
            width=80,
            keep_ratio=True,
            allow_stretch=True
        )
        top_bar.add_widget(logo_img)
        
        # Title next to logo
        title = Label(
            text="Nyx",
            font_size=28,
            color=(0.8, 0.8, 1, 1),
            size_hint=(None, 1),
            width=60,
            halign='left'
        )
        top_bar.add_widget(title)
        
        # Spacer to push username to the right
        top_bar.add_widget(Label(size_hint_x=1))
        
        # Username on the right
        self.username_label = Label(
            text="Guest",
            font_size=20,
            color=(0.9, 0.9, 0.9, 1),
            halign='right',
            valign='middle',
            size_hint=(None, 1),
            width=150
        )
        self.username_label.bind(size=self.username_label.setter('text_size'))
        top_bar.add_widget(self.username_label)
        
        logout_btn = Button(
            text="Logout",
            size_hint=(None, 1),
            width=80,
            font_size=18,
            color=(1, 1, 1, 1),
            background_color=(0.8, 0.3, 0.3, 1),
            background_normal='',
            background_down=''
        )
        logout_btn.bind(on_press=self.logout)
        top_bar.add_widget(logout_btn)

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
        time_card = DarkCard(size_hint=(1, None), height=160)
        
        time_grid = BoxLayout(orientation='horizontal', spacing=15)
        
        # Bedtime section
        bedtime_box = BoxLayout(orientation='vertical', spacing=8)
        
        # Bedtime header with checkbox
        bedtime_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, spacing=5)
        self.bedtime_checkbox = CheckBox(
            size_hint=(None, 1),
            width=25,
            active=False,
            color=(0.4, 0.3, 0.8, 1)
        )
        self.bedtime_checkbox.bind(active=self.on_bedtime_toggle)
        bedtime_header.add_widget(self.bedtime_checkbox)
        
        bedtime_header.add_widget(Label(
            text="Bedtimes",
            font_size=16,
            color=(0.8, 0.8, 0.9, 1),
            halign='left',
            valign='middle'
        ))
        bedtime_box.add_widget(bedtime_header)
        
        bedtime_inputs = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=45)
        
        self.bedtime_hour = TextInput(
            text="10",
            multiline=False,
            input_filter='int',
            font_size=20,
            halign='center',
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[10, 12],
            disabled=True
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
            padding=[10, 12],
            disabled=True
        )
        bedtime_inputs.add_widget(self.bedtime_minute)
        
        self.bedtime_ampm = Spinner(
            text='PM',
            values=('AM', 'PM'),
            size_hint_x=0.6,
            background_color=(0.4, 0.3, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=18,
            disabled=True
        )
        bedtime_inputs.add_widget(self.bedtime_ampm)
        
        bedtime_box.add_widget(bedtime_inputs)
        time_grid.add_widget(bedtime_box)
        
        # Alarm section
        alarm_box = BoxLayout(orientation='vertical', spacing=8)
        
        # Alarm header with checkbox
        alarm_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, spacing=5)
        self.alarm_checkbox = CheckBox(
            size_hint=(None, 1),
            width=25,
            active=False,
            color=(0.4, 0.3, 0.8, 1)
        )
        self.alarm_checkbox.bind(active=self.on_alarm_toggle)
        alarm_header.add_widget(self.alarm_checkbox)
        
        alarm_header.add_widget(Label(
            text="Alarm",
            font_size=16,
            color=(0.8, 0.8, 0.9, 1),
            halign='left',
            valign='middle'
        ))
        alarm_box.add_widget(alarm_header)
        
        alarm_inputs = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=45)
        
        self.alarm_hour = TextInput(
            text="06",
            multiline=False,
            input_filter='int',
            font_size=20,
            halign='center',
            background_color=(0.15, 0.15, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[10, 12],
            disabled=True
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
            padding=[10, 12],
            disabled=True
        )
        alarm_inputs.add_widget(self.alarm_minute)
        
        self.alarm_ampm = Spinner(
            text='AM',
            values=('AM', 'PM'),
            size_hint_x=0.6,
            background_color=(0.4, 0.3, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=18,
            disabled=True
        )
        alarm_inputs.add_widget(self.alarm_ampm)
        
        alarm_box.add_widget(alarm_inputs)
        time_grid.add_widget(alarm_box)
        
        time_card.add_widget(time_grid)
        content.add_widget(time_card)

        # Sleep tracker card
        card = DarkCard(size_hint=(1, 0.5))
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
            size_hint=(1, 0.16),
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
        self.top_rect.pos = self.pos[0], self.pos[1] + self.height - 90
        self.top_rect.size = self.width, 90

    def update_nav_rect(self, *args):
        nav_bar = self.children[0].children[0]
        self.nav_rect.pos = nav_bar.pos
        self.nav_rect.size = nav_bar.size

    def on_bedtime_toggle(self, checkbox, value):
        self.bedtime_enabled = value
        self.bedtime_hour.disabled = not value
        self.bedtime_minute.disabled = not value
        self.bedtime_ampm.disabled = not value
        
        # Save settings when changed
        self.save_user_settings()
        
        if value:
            self.start_notification_checker()
        else:
            self.stop_notification_checker()
        
    def on_alarm_toggle(self, checkbox, value):
        self.alarm_enabled = value
        self.alarm_hour.disabled = not value
        self.alarm_minute.disabled = not value
        self.alarm_ampm.disabled = not value
        
        # Save settings when changed
        self.save_user_settings()
        
        if value:
            self.start_notification_checker()
        else:
            self.stop_notification_checker()

    def start_notification_checker(self):
        """Start checking for bedtime and alarm notifications using Kivy's Clock"""
        if self.check_event is None:
            # Check every 30 seconds
            self.check_event = Clock.schedule_interval(self.check_notifications, 30)
            print("✅ Notification checker started")

    def stop_notification_checker(self):
        """Stop the notification checker if both alarms are disabled"""
        if not self.bedtime_enabled and not self.alarm_enabled:
            if self.check_event:
                Clock.unschedule(self.check_event)
                self.check_event = None
                print("⏹️ Notification checker stopped")

    def check_notifications(self, dt):
        """Check if it's time for bedtime or alarm notifications"""
        now = datetime.now()
        current_time = now.time()
        current_minute = f"{now.hour}:{now.minute}"
        
        # Check bedtime
        if self.bedtime_enabled:
            bedtime = self.get_time_from_inputs(
                self.bedtime_hour.text,
                self.bedtime_minute.text,
                self.bedtime_ampm.text
            )
            if bedtime and self.is_within_minute(current_time, bedtime):
                if self.last_alarm_trigger != f"bedtime_{current_minute}":
                    self.last_alarm_trigger = f"bedtime_{current_minute}"
                    self.send_bedtime_notification()
        
        # Check alarm
        if self.alarm_enabled and not self.alarm_overlay:
            alarm_time = self.get_time_from_inputs(
                self.alarm_hour.text,
                self.alarm_minute.text,
                self.alarm_ampm.text
            )
            if alarm_time and self.is_within_minute(current_time, alarm_time):
                if self.last_alarm_trigger != f"alarm_{current_minute}":
                    self.last_alarm_trigger = f"alarm_{current_minute}"
                    self.show_alarm_overlay()

    def send_bedtime_notification(self):
        """Send bedtime notification using Windows toast notifications"""
        if NOTIFICATIONS_AVAILABLE:
            try:
                # Run in a separate thread to avoid blocking
                from threading import Thread
                def show_toast():
                    toaster.show_toast(
                        "🌙 Bedtime Reminder",
                        "It's time to go to bed for a good night's sleep!",
                        duration=10,
                        threaded=True
                    )
                Thread(target=show_toast, daemon=True).start()
                print("✅ Bedtime notification sent")
            except Exception as e:
                print(f"⚠️ Notification error: {e}")
        else:
            print("🌙 Bedtime reminder (notifications not available)")

    def show_alarm_overlay(self):
        """Show the alarm overlay with sound"""
        if not self.alarm_overlay:
            self.alarm_overlay = AlarmOverlay(callback=self.close_alarm_overlay)
            self.add_widget(self.alarm_overlay)
            print("⏰ Alarm triggered!")

    def close_alarm_overlay(self):
        """Close the alarm overlay"""
        if self.alarm_overlay:
            self.remove_widget(self.alarm_overlay)
            self.alarm_overlay = None
            print("⏰ Alarm stopped")

    def get_time_from_inputs(self, hour_str, minute_str, ampm):
        """Convert time inputs to a time object"""
        try:
            hour = int(hour_str)
            minute = int(minute_str)
            
            # Validate inputs
            if not (1 <= hour <= 12):
                return None
            if not (0 <= minute <= 59):
                return None
            
            # Convert to 24-hour format
            if ampm == 'PM' and hour != 12:
                hour += 12
            elif ampm == 'AM' and hour == 12:
                hour = 0
            
            return time(hour, minute)
        except:
            return None

    def is_within_minute(self, current_time, target_time):
        """Check if current time is within the target minute"""
        return (current_time.hour == target_time.hour and 
                current_time.minute == target_time.minute)

    def update_time(self, dt):
        self.time_label.text = datetime.now().strftime("%I:%M %p")
        
        if self.is_sleeping and self.sleep_start_time:
            elapsed = datetime.now() - self.sleep_start_time
            hours = elapsed.total_seconds() / 3600
            self.duration_label.text = f"{hours:.1f} hours"

    def set_user(self, user):
        self.user = user
        self.username_label.text = user['username']
        
        # Load saved alarm settings
        self.load_user_settings()

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

    def logout(self, instance):
        """Handle user logout"""
        # Save settings before logout
        self.save_user_settings()
        
        # Stop notification checker
        self.stop_notification_checker()
        
        self.user = None
        self.username_label.text = "Guest"
        self.is_sleeping = False
        self.sleep_start_time = None
        self.start_btn.text = "Start Sleep"
        self.start_btn.background_color = (0.4, 0.3, 0.8, 1)
        self.duration_label.text = ""
        self.sleep_label.text = "Ready to track your sleep"
        
        # Reset checkboxes (will be restored on next login)
        self.bedtime_checkbox.active = False
        self.alarm_checkbox.active = False
        
        # Close alarm overlay if active
        if self.alarm_overlay:
            self.close_alarm_overlay()
        
        # Go back to login screen
        self.manager.current = 'login'
    
    def save_user_settings(self):
        """Save bedtime and alarm settings to database"""
        if not self.user:
            return
        
        try:
            db.save_user_settings(
                self.user['user_id'],
                bedtime_enabled=self.bedtime_enabled,
                bedtime_hour=self.bedtime_hour.text,
                bedtime_minute=self.bedtime_minute.text,
                bedtime_ampm=self.bedtime_ampm.text,
                alarm_enabled=self.alarm_enabled,
                alarm_hour=self.alarm_hour.text,
                alarm_minute=self.alarm_minute.text,
                alarm_ampm=self.alarm_ampm.text
            )
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_user_settings(self):
        """Load bedtime and alarm settings from database"""
        if not self.user:
            return
        
        try:
            settings = db.get_user_settings(self.user['user_id'])
            
            if settings:
                # Restore bedtime settings
                self.bedtime_enabled = settings.get('bedtime_enabled', False)
                self.bedtime_checkbox.active = self.bedtime_enabled
                self.bedtime_hour.text = settings.get('bedtime_hour', '10')
                self.bedtime_minute.text = settings.get('bedtime_minute', '00')
                self.bedtime_ampm.text = settings.get('bedtime_ampm', 'PM')
                
                # Restore alarm settings
                self.alarm_enabled = settings.get('alarm_enabled', False)
                self.alarm_checkbox.active = self.alarm_enabled
                self.alarm_hour.text = settings.get('alarm_hour', '06')
                self.alarm_minute.text = settings.get('alarm_minute', '30')
                self.alarm_ampm.text = settings.get('alarm_ampm', 'AM')
                
                # Start notification checker if any are enabled
                if self.bedtime_enabled or self.alarm_enabled:
                    self.start_notification_checker()
        except Exception as e:
            print(f"Error loading settings: {e}")
