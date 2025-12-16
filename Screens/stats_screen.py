"""
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
