from kivy.graphics import Color, RoundedRectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import datetime
from kivy.uix.screenmanager import ScreenManager, Screen

Window.clearcolor = (0.05, 0.05, 0.08, 1)
Window.size = (500, 800)

#Login Screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20,
                           size_hint=(0.8, 0.6), pos_hint={"center_x": 0.5, "center_y": 0.5})

        layout.add_widget(Label(text="Login", font_size=32, size_hint=(1, 0.2)))

        self.username = TextInput(hint_text="Username", multiline=False,
                                  font_size=24, size_hint_y=None, height=50)
        layout.add_widget(self.username)

        self.password = TextInput(hint_text="Password", multiline=False,
                                  password=True, font_size=24,
                                  size_hint_y=None, height=50)
        layout.add_widget(self.password)

        login_btn = Button(text="Login", font_size=24, size_hint=(1, 0.3))
        login_btn.bind(on_press=self.check_login)
        layout.add_widget(login_btn)

        reg_btn = Button(text="Register", font_size=24, size_hint=(1, 0.3))
        reg_btn.bind(on_press=self.go_register)
        layout.add_widget(reg_btn)

        self.message = Label(text="", font_size=20)
        layout.add_widget(self.message)

        self.add_widget(layout)

    def check_login(self, instance):
        if self.username.text.strip() == "admin" and self.password.text.strip() == "1234":
            self.message.text = "Login successful!"
            self.manager.current = "tracker"
        else:
            self.message.text = "Incorrect username or password"

    def go_register(self, instance):
        self.manager.current = "register"


#REGISTER SCREEN (NON-FUNCTIONAL)
class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20,
                           size_hint=(0.8, 0.7), pos_hint={"center_x": 0.5, "center_y": 0.5})

        layout.add_widget(Label(text="Register", font_size=32, bold=True))

        #Username field
        self.reg_user = TextInput(hint_text="New Username", multiline=False,
                                  font_size=24, size_hint_y=None, height=50)
        layout.add_widget(self.reg_user)

        #Password field
        self.reg_pass = TextInput(hint_text="New Password", multiline=False,
                                  password=True, font_size=24,
                                  size_hint_y=None, height=50)
        layout.add_widget(self.reg_pass)

        #Confirm password field
        self.reg_pass2 = TextInput(hint_text="Confirm Password", multiline=False,
                                   password=True, font_size=24,
                                   size_hint_y=None, height=50)
        layout.add_widget(self.reg_pass2)

        #Placeholder for future MySQL logic
        register_btn = Button(text="Create Account (Not Functional Yet)",
                              font_size=20, size_hint=(1, 0.3))
        layout.add_widget(register_btn)

        #Back button
        back_btn = Button(text="Back to Login", font_size=22, size_hint=(1, 0.2))
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "Login"


#Sleep Tracker Screen
class SleepTracker(Screen):

    def update_timer(self, dt):
        if self.sleep_start:
            #10x faster time
            duration = (datetime.now().astimezone() - self.sleep_start) * 100
            hours = duration.total_seconds() / 3600
            self.sleep_label.text = f"Current session: {hours:.2f} hours"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sleep_start = None
        self.sleep_history = []  #store tuples of (start_time, hours)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.add_widget(layout)

        self.SleepTracker_Label = Label(text="Nyx - Sleep Tracker", font_size=40, bold=True,
                                        size_hint=(1, 0.2))
        layout.add_widget(self.SleepTracker_Label)

        self.sleep_label = Label(text="Press Start when you go to sleep", font_size=24)
        layout.add_widget(self.sleep_label)

        #Start Sleep Button
        self.start_btn = Button(text="Start Sleep", font_size=24, size_hint=(1, 0.3))
        self.start_btn.bind(on_press=self.start_sleep)
        layout.add_widget(self.start_btn)

        #Stop Sleep Button
        self.stop_btn = Button(text="Stop Sleep", font_size=24, size_hint=(1, 0.3))
        self.stop_btn.bind(on_press=self.stop_sleep)
        layout.add_widget(self.stop_btn)

        #Recent Sleep Sessions
        self.recent_label = Label(text="Recent Sleep Sessions:\nNone yet", font_size=20)
        layout.add_widget(self.recent_label)

        #Button for full history
        history_btn = Button(text="View All Sleep Sessions", font_size=22, size_hint=(1, 0.2))
        history_btn.bind(on_press=self.open_history)
        layout.add_widget(history_btn)

    def start_sleep(self, instance):
        self.sleep_start = datetime.now().astimezone()
        Clock.schedule_interval(self.update_timer, 1)
        self.sleep_label.text = f"Started sleeping at: {self.sleep_start.strftime('%I:%M:%S %p')}"

    def stop_sleep(self, instance):
        Clock.unschedule(self.update_timer)
        if self.sleep_start:
            #10x Accelerated time
            duration = (datetime.now().astimezone() - self.sleep_start) * 100
            hours = duration.total_seconds() / 3600
            self.sleep_label.text = f"You slept for {hours:.2f} hours"
            self.sleep_history.append((self.sleep_start, hours))

            #Update recent sessions
            self.update_recent_sessions()

            self.sleep_start = None
        else:
            self.sleep_label.text = "Sleep not started yet!"

    def update_recent_sessions(self):
        last_three = self.sleep_history[-3:][::-1]

        if not last_three:
            self.recent_label.text = "Recent Sleep Sessions:\nNone yet"
            return

        text = "Recent Sleep Sessions:\n"
        for start, hrs in last_three:
            text += f"• {start.strftime('%b %d %I:%M %p')} - {hrs:.2f} hrs\n"

        self.recent_label.text = text

    def open_history(self, instance):
        self.manager.get_screen("history").update_history(self.sleep_history)
        self.manager.current = "history"


#Full History Screen
class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.add_widget(layout)

        self.title = Label(text="All Sleep Sessions", font_size=28, bold=True)
        layout.add_widget(self.title)

        self.history_label = Label(text="No history yet", font_size=20)
        layout.add_widget(self.history_label)

        back_btn = Button(text="Back", font_size=22, size_hint=(1, 0.2))
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

    def update_history(self, history):
        if not history:
            self.history_label.text = "No sleep sessions yet"
            return

        text = ""
        for start, hrs in history[::-1]:
            text += f"• {start.strftime('%b %d %I:%M %p')} - {hrs:.2f} hrs\n"

        self.history_label.text = text

    def go_back(self, instance):
        self.manager.current = "tracker"


#App Manager
class NyxApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="Login"))
        sm.add_widget(RegisterScreen(name="register"))   # ADDED
        sm.add_widget(SleepTracker(name="tracker"))
        sm.add_widget(HistoryScreen(name="history"))
        return sm


if __name__ == "__main__":
    NyxApp().run()
