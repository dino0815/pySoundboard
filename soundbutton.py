#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
import json
import pygame
import os
from settings_dialog import SettingsDialog

class SoundButton(Gtk.Box):
    # Konstanten für die Konfiguration
    DEFAULT_CONFIG = {
        'soundbutton': {
            'width': 300,
            'height': 150,
            'volume_height': 30,
            'volume_width': 200,
            'margin': 10,
            'spacing': 5
        },
        'button': {
            'radius': 15,
            'delete_button_size': 30,
            'text_size': 20,
            'background_color': '#CCCCCC',
            'delete_button_color': '#CC3333',
            'text_color': '#000000',
            'text_x': 17,
            'text_y': 20
        },
        'volume': {
            'min': 0,
            'max': 100,
            'default': 50
        }
    }
    
    def __init__(self, position=0, offset_x=0, offset_y=0, config=None, on_delete=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.position = position
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.config = config or self.load_config()
        self.on_delete = on_delete
        
        # Sound-Status
        self.sound = None
        self.is_playing = False
        self.is_looping = False
        
        # Button-spezifische Konfiguration laden
        self.button_config = self.get_button_config()
        
        # UI erstellen
        self._setup_ui()
        
        # Debug-Ausgabe
        print(f"SoundButton {self.position + 1} erstellt - Position: x={self.offset_x}, y={self.offset_y}")
        print(f"SoundButton {self.position + 1} - Offset: x={self.offset_x}, y={self.offset_y}")
        
        # Widgets anzeigen
        self.show_all()
    
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        button_config = self.config['soundbutton']
        
        # Container für Button und Regler
        self.button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.button_container.set_size_request(button_config['width'], button_config['height'])
        self.button_container.set_vexpand(False)
        self.button_container.set_hexpand(False)
        
        # DrawingArea für den Button
        self._create_drawing_area(button_config)
        
        # Lautstärkeregler
        self._create_volume_slider(button_config)
        
        # Widgets zum Button-Container hinzufügen
        self.button_container.pack_start(self.drawing_area, False, False, 0)
        self.button_container.pack_start(self.volume_container, False, False, button_config['spacing'])
        
        # Widgets zum Hauptcontainer hinzufügen
        self.pack_start(self.button_container, False, False, 0)
    
    def _create_drawing_area(self, button_config):
        """Erstellt die DrawingArea für den Button"""
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(button_config['width'], button_config['height'])
        self.drawing_area.set_vexpand(False)
        self.drawing_area.set_hexpand(False)
        
        # Event-Handler
        self.drawing_area.connect("draw", self.on_draw)
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button-press-event", self.on_button_press)
    
    def _create_volume_slider(self, button_config):
        """Erstellt den Lautstärkeregler"""
        self.volume_slider = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL)
        volume_config = self.config['volume']
        self.volume_slider.set_range(volume_config['min'], volume_config['max'])
        self.volume_slider.set_value(self.button_config['volume'])
        self.volume_slider.set_draw_value(False)
        self.volume_slider.set_vexpand(False)
        self.volume_slider.set_hexpand(False)
        self.volume_slider.set_size_request(button_config['volume_width'], button_config['height'])
        self.volume_slider.set_inverted(True)
        self.volume_slider.connect("value-changed", self.on_volume_changed)
        
        # Container für den Lautstärkeregler
        self.volume_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.volume_container.set_vexpand(False)
        self.volume_container.set_hexpand(False)
        self.volume_container.set_size_request(button_config['volume_width'], button_config['height'])
        self.volume_container.pack_start(self.volume_slider, False, False, 0)
    
    def get_button_config(self):
        """Lädt die Button-spezifische Konfiguration"""
        if self.position >= len(self.config.get('buttons', [])):
            return {
                'position': self.position,
                'volume': self.config['volume']['default'],
                'text': f"Button {self.position + 1}"
            }
        
        buttons = self.config.get('buttons', [])
        for button in buttons:
            if button['position'] == self.position:
                return button.copy()
        
        return {
            'position': self.position,
            'volume': self.config['volume']['default'],
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
            return self.DEFAULT_CONFIG.copy()
    
    def set_offset(self, offset_x, offset_y):
        """Setzt den Offset des Buttons"""
        self.offset_x = offset_x
        self.offset_y = offset_y
        print(f"SoundButton {self.position + 1} - Offset aktualisiert: x={self.offset_x}, y={self.offset_y}")
        self.drawing_area.queue_draw()
    
    def rounded_rectangle(self, cr, x, y, width, height, radius):
        """Zeichnet ein abgerundetes Rechteck"""
        degrees = 3.14159 / 180.0
        
        cr.new_sub_path()
        cr.arc(x + width - radius, y + radius, radius, -90 * degrees, 0)
        cr.arc(x + width - radius, y + height - radius, radius, 0, 90 * degrees)
        cr.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
        cr.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
        cr.close_path()
    
    def draw_control_button(self, cr, x, y, size, bg_color, border_color, symbol_color, border_width, symbol_type):
        """Zeichnet einen Steuerungsbutton mit Symbol"""
        # Hintergrund
        cr.set_source_rgb(*bg_color)
        self.rounded_rectangle(cr, x, y, size, size, size/4)
        cr.fill()
        
        # Rahmen
        cr.set_source_rgb(*border_color)
        cr.set_line_width(border_width)
        self.rounded_rectangle(cr, x, y, size, size, size/4)
        cr.stroke()
        
        # Symbol
        cr.set_source_rgb(*symbol_color)
        cr.set_line_width(2)
        
        if symbol_type == "play":
            # Dreieck für Play
            cr.move_to(x + size/3, y + size/4)
            cr.line_to(x + size/3, y + 3*size/4)
            cr.line_to(x + 2*size/3, y + size/2)
            cr.close_path()
            cr.fill()
        elif symbol_type == "stop":
            # Quadrat für Stop
            margin = size/4
            cr.rectangle(x + margin, y + margin, size - 2*margin, size - 2*margin)
            cr.fill()
        elif symbol_type == "loop":
            # Unendlichkeitssymbol (∞)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(size * 0.9)
            extents = cr.text_extents("∞")
            text_x = x + (size - extents.width) / 2 -2
            text_y = y + (size + extents.height) / 2 + 1
            cr.move_to(text_x, text_y)
            cr.show_text("∞")
        elif symbol_type == "delete":
            # Schwarzes Kreuz
            padding = 5
            cr.move_to(x + padding, y + padding)
            cr.line_to(x + size - padding, y + size - padding)
            cr.move_to(x + size - padding, y + padding)
            cr.line_to(x + padding, y + size - padding)
            cr.stroke()
    
    def on_draw(self, widget, cr):
        """Zeichnet den Button"""
        button_config = self.config['button']
        button_size = self.config['soundbutton']
        
        # Hintergrund
        bg_color = self.hex_to_rgb(button_config['background_color'])
        cr.set_source_rgb(*bg_color)
        self.rounded_rectangle(cr, 0, 0, button_size['width'], button_size['height'], button_config['radius'])
        cr.fill()
        
        # Bild zeichnen, falls vorhanden
        if 'image_file' in self.button_config and self.button_config['image_file']:
            self._draw_image(cr, button_size)
        
        # Lösch-Button
        self._draw_delete_button(cr, button_config, button_size)
        
        # Text
        self._draw_text(cr, button_config)
        
        # Steuerungsbuttons
        self._draw_control_buttons(cr, button_config, button_size)
        
        return False
    
    def _draw_image(self, cr, button_size):
        """Zeichnet das Button-Bild"""
        try:
            image = cairo.ImageSurface.create_from_png(self.button_config['image_file'])
            cr.save()
            
            # Bild skalieren und zentrieren
            image_width = image.get_width()
            image_height = image.get_height()
            scale_x = button_size['width'] / image_width
            scale_y = button_size['height'] / image_height
            scale = min(scale_x, scale_y) * 0.8
            
            x = (button_size['width'] - image_width * scale) / 2
            y = (button_size['height'] - image_height * scale) / 2
            
            cr.translate(x, y)
            cr.scale(scale, scale)
            cr.set_source_surface(image, 0, 0)
            cr.paint()
            cr.restore()
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
    
    def _draw_delete_button(self, cr, button_config, button_size):
        """Zeichnet den Lösch-Button"""
        delete_size = button_config['delete_button_size']
        delete_x = button_size['width'] - delete_size - 10
        delete_y = 10
        
        control_config = button_config['control_buttons']
        self.draw_control_button(
            cr,
            delete_x,
            delete_y,
            delete_size,
            self.hex_to_rgb(control_config['background_color']),
            self.hex_to_rgb(control_config['border_color']),
            self.hex_to_rgb(control_config['symbol_color']),
            control_config['border_width'],
            "delete"
        )
    
    def _draw_text(self, cr, button_config):
        """Zeichnet den Button-Text"""
        text_color = self.hex_to_rgb(button_config['text_color'])
        cr.set_source_rgb(*text_color)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(button_config['text_size'])
        cr.move_to(button_config['text_x'], button_config['text_y'])
        cr.show_text(self.button_config['text'])
    
    def _draw_control_buttons(self, cr, button_config, button_size):
        """Zeichnet die Steuerungsbuttons"""
        control_config = button_config['control_buttons']
        control_size = control_config['size']
        spacing = control_config['spacing']
        
        y_offset = button_size['height'] - control_size - spacing
        total_control_width = 3 * control_size + 2 * spacing
        start_x = (button_size['width'] - total_control_width) / 2
        
        # Play-Button
        self.draw_control_button(
            cr,
            start_x,
            y_offset,
            control_size,
            self.hex_to_rgb(control_config['background_color']),
            self.hex_to_rgb(control_config['border_color']),
            self.hex_to_rgb(control_config['symbol_color']),
            control_config['border_width'],
            "play"
        )
        
        # Stop-Button
        self.draw_control_button(
            cr,
            start_x + control_size + spacing,
            y_offset,
            control_size,
            self.hex_to_rgb(control_config['background_color']),
            self.hex_to_rgb(control_config['border_color']),
            self.hex_to_rgb(control_config['symbol_color']),
            control_config['border_width'],
            "stop"
        )
        
        # Loop-Button
        self.draw_control_button(
            cr,
            start_x + 2 * (control_size + spacing),
            y_offset,
            control_size,
            self.hex_to_rgb(control_config['background_color']),
            self.hex_to_rgb(control_config['border_color']),
            self.hex_to_rgb(control_config['symbol_color']),
            control_config['border_width'],
            "loop"
        )
    
    def play_sound(self):
        """Spielt den Sound ab"""
        if 'audio_file' in self.button_config and self.button_config['audio_file']:
            try:
                if self.sound and self.is_playing:
                    self.stop_sound()
                
                self.sound = pygame.mixer.Sound(self.button_config['audio_file'])
                self.sound.set_volume(self.button_config['volume'] / 100.0)
                
                self.sound.play()
                self.is_playing = True
                
                print(f"Button {self.position + 1} - Sound wird abgespielt")
            except Exception as e:
                print(f"Fehler beim Abspielen des Sounds: {e}")
                self.stop_sound()
    
    def stop_sound(self):
        """Stoppt den Sound"""
        if self.sound and self.is_playing:
            try:
                self.sound.stop()
                self.is_playing = False
                print(f"Button {self.position + 1} - Sound gestoppt")
            except Exception as e:
                print(f"Fehler beim Stoppen des Sounds: {e}")
    
    def toggle_loop(self):
        """Schaltet die Schleifenwiedergabe ein/aus"""
        if self.sound:
            try:
                self.is_looping = not self.is_looping
                if self.is_looping:
                    self.sound.play(-1)
                    print(f"Button {self.position + 1} - Schleifenwiedergabe aktiviert")
                else:
                    self.stop_sound()
                    print(f"Button {self.position + 1} - Schleifenwiedergabe deaktiviert")
            except Exception as e:
                print(f"Fehler beim Umschalten der Schleifenwiedergabe: {e}")
                self.stop_sound()
    
    def on_button_press(self, widget, event):
        """Handler für Mausklicks"""
        button_config = self.config['button']
        button_size = self.config['soundbutton']
        
        # Lösch-Button
        if self._is_delete_button_clicked(event, button_config, button_size):
            if self.on_delete:
                self.on_delete(self)
            return True
        
        # Control-Buttons
        if self._is_control_button_clicked(event, button_config, button_size):
            return True
        
        # Rechtsklick
        if event.button == 3:
            self.show_text_dialog()
            return True
        
        print(f"Außerhalb aller Buttons von Button {self.position + 1} geklickt: x={event.x}, y={event.y}")
        return True
    
    def _is_delete_button_clicked(self, event, button_config, button_size):
        """Prüft, ob der Lösch-Button geklickt wurde"""
        delete_size = button_config['delete_button_size']
        delete_x = button_size['width'] - delete_size - 10
        delete_y = 10
        
        if (delete_x <= event.x <= delete_x + delete_size and 
            delete_y <= event.y <= delete_y + delete_size):
            print(f"Lösch-Button von Button {self.position + 1} wurde geklickt!")
            return True
        return False
    
    def _is_control_button_clicked(self, event, button_config, button_size):
        """Prüft, ob ein Control-Button geklickt wurde"""
        control_config = button_config['control_buttons']
        control_size = control_config['size']
        spacing = control_config['spacing']
        
        y_offset = button_size['height'] - control_size - spacing
        total_control_width = 3 * control_size + 2 * spacing
        start_x = (button_size['width'] - total_control_width) / 2
        
        if y_offset <= event.y <= y_offset + control_size:
            # Play-Button
            if start_x <= event.x <= start_x + control_size:
                print(f"Play-Button von Button {self.position + 1} wurde geklickt!")
                self.play_sound()
                return True
            
            # Stop-Button
            if start_x + control_size + spacing <= event.x <= start_x + 2 * control_size + spacing:
                print(f"Stop-Button von Button {self.position + 1} wurde geklickt!")
                self.stop_sound()
                return True
            
            # Loop-Button
            if start_x + 2 * (control_size + spacing) <= event.x <= start_x + 3 * control_size + 2 * spacing:
                print(f"Loop-Button von Button {self.position + 1} wurde geklickt!")
                self.toggle_loop()
                return True
        return False
    
    def show_text_dialog(self):
        """Zeigt den Einstellungsdialog"""
        dialog = SettingsDialog(self.get_toplevel(), self.button_config, self.position)
        dialog.show()
        self.drawing_area.queue_draw()
    
    def on_volume_changed(self, volume_slider):
        """Handler für Änderungen am Lautstärkeregler"""
        value = volume_slider.get_value()
        self.button_config['volume'] = value
        if self.sound:
            self.sound.set_volume(value / 100.0)
        print(f"Button {self.position + 1} - Lautstärke auf {value} gesetzt") 