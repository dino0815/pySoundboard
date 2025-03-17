#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo

class DrawingAreaWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Drawing Area Test")
        
        # Hauptcontainer (vertikale Box)
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Horizontale Box für Header
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Plus-Button erstellen
        self.plus_button = Gtk.Button(label="+")
        self.plus_button.set_size_request(30, 30)
        self.plus_button.connect("clicked", self.on_plus_clicked)
        
        # Plus-Button zum Header hinzufügen
        self.header_box.pack_end(self.plus_button, False, False, 5)
        
        # Header zur Hauptbox hinzufügen
        self.main_box.pack_start(self.header_box, False, False, 0)
        
        # ScrolledWindow für DrawingAreas erstellen
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled.set_vexpand(True)
        self.scrolled.set_hexpand(True)
        
        # Container für DrawingAreas (vertikale Box)
        self.areas_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.areas_container.set_margin_top(20)
        self.areas_container.set_margin_bottom(20)
        self.areas_container.set_margin_start(20)
        self.areas_container.set_margin_end(20)
        
        # Container zur ScrolledWindow hinzufügen
        self.scrolled.add(self.areas_container)
        
        # ScrolledWindow zur Hauptbox hinzufügen
        self.main_box.pack_start(self.scrolled, True, True, 0)
        
        # Hauptbox zum Fenster hinzufügen
        self.add(self.main_box)
        
        # Liste für DrawingAreas
        self.drawing_areas = []
        
        # Erste DrawingArea erstellen
        self.add_new_drawing_area()
        
        # Fenster-Eigenschaften
        self.set_default_size(640, 440)
        self.connect("destroy", Gtk.main_quit)
    
    def add_new_drawing_area(self):
        # Frame für die DrawingArea erstellen
        frame = Gtk.Frame()
        frame.set_margin_top(5)
        frame.set_margin_bottom(5)
        frame.set_margin_start(5)
        frame.set_margin_end(5)
        
        # Drawing Area erstellen
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(300, 200)
        drawing_area.set_vexpand(False)
        drawing_area.set_hexpand(False)
        
        # Event-Handler für Zeichnen
        drawing_area.connect("draw", self.on_draw)
        
        # Event-Handler für Mausklicks
        drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        drawing_area.connect("button-press-event", self.on_button_press)
        
        # Drawing Area zum Frame hinzufügen
        frame.add(drawing_area)
        
        # Frame zum Container hinzufügen
        self.areas_container.pack_start(frame, False, False, 0)
        
        # Drawing Area zur Liste hinzufügen
        self.drawing_areas.append(drawing_area)
        
        # Fenster neu zeichnen
        self.queue_draw()
        
        # ScrolledWindow anpassen
        total_height = (200 + 20) * len(self.drawing_areas) + 40  # Höhe pro Area + Abstand + Margins
        self.scrolled.set_min_content_height(total_height)
        
        # Debug-Ausgabe
        print(f"Neue DrawingArea hinzugefügt. Gesamtanzahl: {len(self.drawing_areas)}")
    
    def on_plus_clicked(self, button):
        print("Plus-Button wurde geklickt!")  # Debug-Ausgabe
        self.add_new_drawing_area()
        
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
        # Position der DrawingArea im Container ermitteln
        index = self.drawing_areas.index(widget)
        y_offset = index * 220  # 200px Höhe + 20px Abstand
        
        # Koordinatensystem verschieben
        cr.save()
        cr.translate(0, y_offset)
        
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
        
        # Koordinatensystem wiederherstellen
        cr.restore()
        
        return False
    
    def on_button_press(self, widget, event):
        # Position der DrawingArea im Container ermitteln
        index = self.drawing_areas.index(widget)
        y_offset = index * 220  # 200px Höhe + 20px Abstand
        
        # Berechne die Distanz vom Klickpunkt zum Zentrum des Buttons
        center_x, center_y = 150, 100
        distance = ((event.x - center_x) ** 2 + (event.y - center_y) ** 2) ** 0.5
        
        # Wenn der Klick innerhalb des Buttons war
        if distance <= 50:
            print(f"Button wurde geklickt! Position: x={event.x}, y={event.y}, Area: {index + 1}")
            # Hier können Sie weitere Aktionen hinzufügen
        else:
            print(f"Außerhalb des Buttons geklickt: x={event.x}, y={event.y}, Area: {index + 1}")
        
        return True

win = DrawingAreaWindow()
win.show_all()
Gtk.main() 