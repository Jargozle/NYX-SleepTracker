"""
Graph Screen for Nyx Sleep Tracker
Uses Matplotlib with Kivy Garden for visualization
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from datetime import datetime
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle as MPLRectangle
import numpy as np
from kivy_garden.matplotlib import FigureCanvasKivyAgg
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
            text="Back",
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
        
        # Only create 2 graphs now
        self.graph_container.add_widget(self.create_day_of_week_chart(sessions))
        self.graph_container.add_widget(self.create_weekday_weekend_chart(sessions))

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
            day_name = date.strftime('%a')
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
            week_num = date.strftime('%Y-W%U')
            
            if date.weekday() < 5:
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
