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

# Add to components.py

def add_celestial_background(widget, star_count=20, cloud_count=2):
    """Add celestial background to any widget"""
    from kivy.graphics import Color, Ellipse, Rectangle
    import random
    
    with widget.canvas.before:
        # Background
        Color(0.07, 0.07, 0.15, 1)
        widget.bg_rect = Rectangle(pos=widget.pos, size=widget.size)
        
        # Stars
        for _ in range(star_count):
            x = random.uniform(20, widget.width - 20)
            y = random.uniform(widget.height * 0.4, widget.height - 50)
            brightness = random.uniform(0.7, 1.0)
            Color(brightness, brightness, brightness, random.uniform(0.6, 0.9))
            size = random.uniform(2, 4)
            Ellipse(pos=(x, y), size=(size, size))
        
        # Moon
        moon_x = widget.width - 80
        moon_y = widget.height - 80
        Color(0.98, 0.98, 0.9, 0.9)
        Ellipse(pos=(moon_x, moon_y), size=(40, 40))
        
        # Clouds
        Color(0.9, 0.9, 0.95, 0.35)
        for i in range(cloud_count):
            cloud_x = random.uniform(20, widget.width - 150)
            cloud_y = random.uniform(20, 150)
            cloud_size = random.uniform(80, 120)
            for j in range(3):
                offset_x = random.uniform(-15, 15)
                offset_y = random.uniform(-8, 8)
                Ellipse(
                    pos=(cloud_x + offset_x + (j * 30), cloud_y + offset_y),
                    size=(cloud_size * random.uniform(0.4, 0.7), cloud_size * 0.4)
                )
    
    # Update on resize
    def update_bg(instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    widget.bind(size=update_bg, pos=update_bg)

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
