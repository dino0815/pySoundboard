import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class DrawingArea(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_content_width(200)
        self.set_content_height(200)
        
        # Event-Handler für Zeichnen
        self.set_draw_func(self.on_draw, None)
        
        # Event-Handler für Mausklicks
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.on_button_press)
    
    def on_draw(self, area, cr, width, height, data):
        # Hier können Sie zeichnen
        cr.set_source_rgb(0.5, 0.5, 0.5)  # Graue Farbe
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        # Beispiel: Kreis zeichnen
        cr.set_source_rgb(1, 0, 0)  # Rote Farbe
        cr.arc(width/2, height/2, 50, 0, 2 * 3.14159)
        cr.fill()
    
    def on_button_press(self, area, event):
        # Hier erhalten Sie die genauen Klickkoordinaten
        print(f"Klick bei x={event.x}, y={event.y}")
        return True
