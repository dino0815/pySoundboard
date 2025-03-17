#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo

class DrawingAreaWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Drawing Area Test")
        
        # Box für Padding erstellen
        self.box = Gtk.Box()
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        
        # Drawing Area erstellen
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(300, 200)
        
        # Event-Handler für Zeichnen
        self.drawing_area.connect("draw", self.on_draw)
        
        # Event-Handler für Mausklicks
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button-press-event", self.on_button_press)
        
        # Drawing Area zur Box hinzufügen
        self.box.add(self.drawing_area)
        
        # Box zum Fenster hinzufügen
        self.add(self.box)
        
        # Fenster-Eigenschaften
        self.set_default_size(340, 240)  # Größe angepasst für Padding
        self.connect("destroy", Gtk.main_quit)
        
    def rounded_rectangle(self, cr, x, y, width, height, radius):
        # Hilfsfunktion zum Zeichnen eines abgerundeten Rechtecks
        degrees = 3.14159 / 180.0
        
        cr.new_sub_path()
        cr.arc(x + width - radius, y + radius, radius, -90 * degrees, 0)
        cr.arc(x + width - radius, y + height - radius, radius, 0, 90 * degrees)
        cr.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
        cr.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
        cr.close_path()
        
    def on_draw(self, widget, cr):
        # Abgerundetes Rechteck als Hintergrund zeichnen
        cr.set_source_rgb(0.8, 0.8, 0.8)  # Hellgrau
        self.rounded_rectangle(cr, 0, 0, 300, 200, 15)  # Radius 15px
        cr.fill()
        
        # Einen Button-ähnlichen Kreis zeichnen
        cr.set_source_rgb(0.2, 0.4, 0.8)  # Blau
        cr.arc(150, 100, 50, 0, 2 * 3.14159)
        cr.fill()
        
        # Text auf dem Button
        cr.set_source_rgb(1, 1, 1)  # Weiß
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(20)
        cr.move_to(130, 110)
        cr.show_text("Klick mich!")
        
        return False
    
    def on_button_press(self, widget, event):
        # Berechne die Distanz vom Klickpunkt zum Zentrum des Buttons
        center_x, center_y = 150, 100
        distance = ((event.x - center_x) ** 2 + (event.y - center_y) ** 2) ** 0.5
        
        # Wenn der Klick innerhalb des Buttons war
        if distance <= 50:
            print(f"Button wurde geklickt! Position: x={event.x}, y={event.y}")
            # Hier können Sie weitere Aktionen hinzufügen
        else:
            print(f"Außerhalb des Buttons geklickt: x={event.x}, y={event.y}")
        
        return True

win = DrawingAreaWindow()
win.show_all()
Gtk.main() 