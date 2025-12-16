"""
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
