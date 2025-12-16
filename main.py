"""
Nyx Sleep Tracker - Main Application
Run this file to start the application
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from Screens.login_screen import LoginScreen
from Screens.register_screen import RegisterScreen
from Screens.tracker_screen import TrackerScreen
from Screens.stats_screen import StatsScreen
from Screens.graph_screen import GraphScreen

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
