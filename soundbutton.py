#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo

class SoundButton(Gtk.DrawingArea):
    def __init__(self, position=0, offset_x=0, offset_y=0):
        super().__init__()
        self.position = position  # Speichere die Position
        self.offset_x = offset_x  # X-Offset für die Position
        self.offset_y = offset_y  # Y-Offset für die Position
        self.set_size_request(300, 200)
        self.set_vexpand(False)
        self.set_hexpand(False)
        
        # Event-Handler für Zeichnen
        self.connect("draw", self.on_draw)
        
        # Event-Handler für Mausklicks
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_button_press)
        
        # Debug-Ausgabe
        print(f"SoundButton {self.position + 1} erstellt - Position: x={self.offset_x}, y={self.offset_y}")
        print(f"SoundButton {self.position + 1} - Offset: x={self.offset_x}, y={self.offset_y}")
    
    def set_offset(self, offset_x, offset_y):
        """Setzt den Offset des Buttons"""
        self.offset_x = offset_x
        self.offset_y = offset_y
        print(f"SoundButton {self.position + 1} - Offset aktualisiert: x={self.offset_x}, y={self.offset_y}")
        self.queue_draw()  # Neu zeichnen bei Änderung
    
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
        cr.show_text(f"Button {self.position + 1}")
        
        return False
    
    def on_button_press(self, widget, event):
        # Berechne die Distanz vom Klickpunkt zum Zentrum des Buttons
        # Die Klickkoordinaten sind bereits relativ zum Button
        center_x = 150  # Zentrum des Buttons
        center_y = 100
        distance = ((event.x - center_x) ** 2 + (event.y - center_y) ** 2) ** 0.5
        
        # Wenn der Klick innerhalb des Buttons war
        if distance <= 50:
            print(f"Button {self.position + 1} wurde geklickt! Position: x={event.x}, y={event.y}")
            # Hier können Sie weitere Aktionen hinzufügen
        else:
            print(f"Außerhalb von Button {self.position + 1} geklickt: x={event.x}, y={event.y}")
        
        return True 