#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo
import json

class SoundButton(Gtk.Box):
    def __init__(self, position=0, offset_x=0, offset_y=0, config=None, on_delete=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.position = position  # Speichere die Position
        self.offset_x = offset_x  # X-Offset für die Position
        self.offset_y = offset_y  # Y-Offset für die Position
        self.config = config or self.load_config()
        self.on_delete = on_delete  # Callback für das Löschen
        
        # Button-spezifische Konfiguration laden
        self.button_config = self.get_button_config()
        
        # Größen aus der Konfiguration
        button_config = self.config['soundbutton']
        self.set_size_request(button_config['width'], button_config['height'])
        self.set_vexpand(False)
        self.set_hexpand(False)
        
        # DrawingArea für den Button
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(button_config['width'], button_config['button_height'])
        self.drawing_area.set_vexpand(False)
        self.drawing_area.set_hexpand(False)
        
        # Event-Handler für Zeichnen
        self.drawing_area.connect("draw", self.on_draw)
        
        # Event-Handler für Mausklicks
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button-press-event", self.on_button_press)
        
        # Schieberegler erstellen
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        scale_config = self.config['scale']
        self.scale.set_range(scale_config['min'], scale_config['max'])
        self.scale.set_value(self.button_config['scale_value'])
        self.scale.set_draw_value(True)
        self.scale.set_vexpand(False)
        self.scale.set_hexpand(False)
        self.scale.set_size_request(button_config['scale_width'], button_config['scale_height'])
        self.scale.connect("value-changed", self.on_scale_changed)
        
        # Widgets zum Container hinzufügen
        self.pack_start(self.drawing_area, False, False, 0)
        self.pack_start(self.scale, False, False, button_config['spacing'])
        
        # Debug-Ausgabe
        print(f"SoundButton {self.position + 1} erstellt - Position: x={self.offset_x}, y={self.offset_y}")
        print(f"SoundButton {self.position + 1} - Offset: x={self.offset_x}, y={self.offset_y}")
        
        # Widgets anzeigen
        self.show_all()
    
    def get_button_config(self):
        """Lädt die Button-spezifische Konfiguration"""
        # Für neue Buttons immer eine neue Konfiguration erstellen
        if self.position >= len(self.config.get('buttons', [])):
            return {
                'position': self.position,
                'scale_value': self.config['scale']['default'],
                'text': f"Button {self.position + 1}"
            }
        
        # Für existierende Buttons die gespeicherte Konfiguration laden
        buttons = self.config.get('buttons', [])
        for button in buttons:
            if button['position'] == self.position:
                return button.copy()  # Erstelle eine Kopie der Konfiguration
        
        # Fallback: Neue Konfiguration
        return {
            'position': self.position,
            'scale_value': self.config['scale']['default'],
            'text': f"Button {self.position + 1}"
        }
    
    def hex_to_rgb(self, hex_color):
        """Konvertiert einen Hex-Farbcode (#RRGGBB) in RGB-Werte (0-1)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return [r, g, b]
    
    def load_config(self):
        """Lädt die Konfigurationsdatei"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warnung: config.json nicht gefunden, verwende Standardwerte")
            return {
                'soundbutton': {
                    'width': 300,
                    'height': 200,
                    'button_height': 150,
                    'scale_height': 30,
                    'scale_width': 200,
                    'margin': 10,
                    'spacing': 5
                },
                'button': {
                    'radius': 15,
                    'delete_button_size': 30,
                    'text_size': 20,
                    'background_color': '#CCCCCC',
                    'delete_button_color': '#CC3333',
                    'text_color': '#000000'
                },
                'scale': {
                    'min': 0,
                    'max': 100,
                    'default': 50
                }
            }
    
    def set_offset(self, offset_x, offset_y):
        """Setzt den Offset des Buttons"""
        self.offset_x = offset_x
        self.offset_y = offset_y
        print(f"SoundButton {self.position + 1} - Offset aktualisiert: x={self.offset_x}, y={self.offset_y}")
        self.drawing_area.queue_draw()  # Neu zeichnen bei Änderung
    
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
        button_config = self.config['button']
        button_size = self.config['soundbutton']
        
        # Abgerundetes Rechteck als Hintergrund zeichnen
        bg_color = self.hex_to_rgb(button_config['background_color'])
        cr.set_source_rgb(*bg_color)
        self.rounded_rectangle(cr, 0, 0, button_size['width'], button_size['button_height'], button_config['radius'])
        cr.fill()
        
        # Lösch-Button (rotes X) zeichnen
        delete_size = button_config['delete_button_size']
        delete_x = button_size['width'] - delete_size - 10
        delete_y = 10
        
        # Roter Hintergrund für den Lösch-Button
        delete_color = self.hex_to_rgb(button_config['delete_button_color'])
        cr.set_source_rgb(*delete_color)
        self.rounded_rectangle(cr, delete_x, delete_y, delete_size, delete_size, delete_size/2)
        cr.fill()
        
        # Weißes X zeichnen
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_line_width(3)
        padding = 5
        cr.move_to(delete_x + padding, delete_y + padding)
        cr.line_to(delete_x + delete_size - padding, delete_y + delete_size - padding)
        cr.move_to(delete_x + delete_size - padding, delete_y + padding)
        cr.line_to(delete_x + padding, delete_y + delete_size - padding)
        cr.stroke()
        
        # Text auf dem Button
        text_color = self.hex_to_rgb(button_config['text_color'])
        cr.set_source_rgb(*text_color)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(button_config['text_size'])
        text_x = 20
        text_y = button_size['button_height'] / 2 + 10
        cr.move_to(text_x, text_y)
        cr.show_text(self.button_config['text'])
        
        return False
    
    def on_button_press(self, widget, event):
        button_config = self.config['button']
        button_size = self.config['soundbutton']
        
        # Prüfe, ob der Lösch-Button geklickt wurde
        delete_size = button_config['delete_button_size']
        delete_x = button_size['width'] - delete_size - 10
        delete_y = 10
        
        if (delete_x <= event.x <= delete_x + delete_size and 
            delete_y <= event.y <= delete_y + delete_size):
            print(f"Lösch-Button von Button {self.position + 1} wurde geklickt!")
            if self.on_delete:
                self.on_delete(self)
            return True
        
        # Wenn der Klick außerhalb des Lösch-Buttons war
        print(f"Außerhalb des Lösch-Buttons von Button {self.position + 1} geklickt: x={event.x}, y={event.y}")
        return True
    
    def on_scale_changed(self, scale):
        """Callback für Änderungen am Schieberegler"""
        value = scale.get_value()
        self.button_config['scale_value'] = value
        print(f"Button {self.position + 1} - Schieberegler auf {value} gesetzt")
    
    def save_config(self):
        """Speichert die aktuelle Button-Konfiguration"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = self.config
        
        # Aktualisiere oder füge die Button-Konfiguration hinzu
        buttons = config.get('buttons', [])
        found = False
        for button in buttons:
            if button['position'] == self.position:
                button.update(self.button_config)
                found = True
                break
        if not found:
            buttons.append(self.button_config)
        
        config['buttons'] = buttons
        
        # Speichere die aktualisierte Konfiguration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4) 