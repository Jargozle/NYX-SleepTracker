# celestial_overlay.py
"""
Simple celestial overlay for Nyx Sleep Tracker
Adds stars, moon, and clouds to any screen
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
import random
from kivy.properties import NumericProperty


class CelestialOverlay(Widget):
    """Simple overlay with stars, moon, and clouds"""
    
    star_count = NumericProperty(15)  # Number of stars
    cloud_count = NumericProperty(2)  # Number of clouds
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.draw_elements, pos=self.draw_elements)
        self.draw_elements()

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

    def draw_elements(self, *args):
        """Draw all celestial elements"""
        # Clear previous drawings
        self.canvas.clear()
        
        with self.canvas:
            # Draw stars
            for _ in range(self.star_count):
                self.draw_star()
            
            # Draw moon
            self.draw_moon()
            
            # Draw clouds
            for _ in range(self.cloud_count):
                self.draw_cloud()
    
    def draw_star(self):
        """Draw a single star at random position"""
        if self.width == 0 or self.height == 0:
            return
        
        x = random.uniform(20, self.width - 20)
        y = random.uniform(self.height * 0.4, self.height - 50)
        size = random.uniform(2, 4)
        brightness = random.uniform(0.7, 1.0)
        
        Color(brightness, brightness, brightness, random.uniform(0.6, 0.9))
        Ellipse(pos=(x, y), size=(size, size))
    
    def draw_moon(self):
        """Draw a crescent moon in top-right corner"""
        if self.width == 0 or self.height == 0:
            return
        
        moon_x = self.width - 80  # 20px from right
        moon_y = self.height - 80  # 20px from top
        moon_size = 40
        
        # Moon glow (subtle)
        Color(0.95, 0.95, 0.8, 0.3)
        Ellipse(pos=(moon_x - 5, moon_y - 5), 
                size=(moon_size + 10, moon_size + 10))
        
        # Moon body
        Color(0.98, 0.98, 0.9, 0.9)
        Ellipse(pos=(moon_x, moon_y), 
                size=(moon_size, moon_size))
        
        # Crescent shadow
        Color(0.05, 0.05, 0.15, 0.8)
        Ellipse(pos=(moon_x + 10, moon_y - 2), 
                size=(moon_size, moon_size))
    
    def draw_cloud(self):
        """Draw a fluffy cloud"""
        if self.width == 0 or self.height == 0:
            return
        
        cloud_x = random.uniform(20, self.width - 150)
        cloud_y = random.uniform(20, self.height * 0.3)
        cloud_size = random.uniform(80, 120)
        opacity = random.uniform(0.3, 0.5)
        
        Color(0.9, 0.9, 0.95, opacity)
        
        # Cloud is made of overlapping circles
        for i in range(3):
            offset_x = random.uniform(-15, 15)
            offset_y = random.uniform(-8, 8)
            part_size = cloud_size * random.uniform(0.4, 0.7)
            
            Ellipse(pos=(cloud_x + offset_x, cloud_y + offset_y), 
                   size=(part_size, part_size * 0.4))