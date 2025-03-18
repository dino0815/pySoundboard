#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
import json
import pygame
import os
from settings_dialog import SettingsDialog

# Diese globale Variable wird nicht mehr benötigt, bleibt aber zunächst als Kommentar erhalten
# DRAGGING_BUTTON = None  # Speichert den aktuell gezogenen Button

class SoundButton(Gtk.Box):
    def __init__(self, position=0, offset_x=0, offset_y=0, config=None, on_delete=None, is_add_button=False):
        if config is None:
            raise ValueError("Keine Konfiguration übergeben. SoundButton benötigt eine gültige Konfiguration.")
        
        if 'soundbutton' not in config:
            raise ValueError("Ungültige Konfiguration: 'soundbutton' Sektion fehlt")
            
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.position = position
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.config = config
        self.on_delete = on_delete
        self.is_add_button = is_add_button
        
        # Sound-Status
        self.sound = None
        self.is_playing = False
        self.is_looping = False
        
        # Button-spezifische Konfiguration laden
        self.button_config = self.get_button_config()
        
        # UI erstellen
        self._setup_ui()
        
        # Styling aktivieren (für alle Buttons)
        self._apply_style()
        
        if not is_add_button:
            print(f"SoundButton '{self.button_config['text']}' erstellt - Position: x={self.offset_x}, y={self.offset_y}")
            print(f"SoundButton '{self.button_config['text']}' - Offset: x={self.offset_x}, y={self.offset_y}")
        
        # Widgets anzeigen
        self.show_all()
    
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        sb_config = self.config['soundbutton']
        
        # Container für Button und Regler
        self.button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.button_container.set_size_request(sb_config['button_width'], sb_config['button_height'])
        
        # DrawingArea für den Button
        self._create_drawing_area(sb_config)
        
        # Widgets zum Button-Container hinzufügen
        self.button_container.pack_start(self.drawing_area, True, True, 0)
        
        if not self.is_add_button:
            # Lautstärkeregler nur für normale Buttons
            self._create_volume_slider(sb_config)
            self.button_container.pack_start(self.volume_container, False, False, 0)
        
        # Widget zum Hauptcontainer hinzufügen
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.pack_start(self.button_container, True, True, 0)
    
    def _create_drawing_area(self, sb_config):
        """Erstellt die DrawingArea für den Button"""
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(sb_config['button_width'], sb_config['button_height'])
        self.drawing_area.set_vexpand(False)
        self.drawing_area.set_hexpand(False)
        
        # Event-Handler
        self.drawing_area.connect("draw", self.on_draw)
        
        # Maus-Events aktivieren
        self.drawing_area.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK
        )
        
        # Event-Handler für Maus-Events
        self.drawing_area.connect("button-press-event", self.on_button_press)
        self.drawing_area.connect("button-release-event", self.on_button_release)
        self.drawing_area.connect("motion-notify-event", self.on_motion_notify)
    
    def _create_volume_slider(self, sb_config):
        """Erstellt den Lautstärkeregler"""
        self.volume_slider = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL)
        # Verwende nun volume_min und volume_max
        self.volume_slider.set_range(sb_config['volume_min'], sb_config['volume_max'])
        self.volume_slider.set_value(int(self.get_button_config().get('volume', sb_config['volume_default'])))
        self.volume_slider.set_draw_value(False)  # Zeige den Wert NICHT an
        self.volume_slider.set_digits(0)  # Keine Dezimalstellen
        self.volume_slider.set_vexpand(True)  # Nutze die gesamte verfügbare Höhe
        self.volume_slider.set_hexpand(False)
        self.volume_slider.set_size_request(sb_config['volume_width'], sb_config['button_height'])
        self.volume_slider.set_inverted(True)
        
        # Reduziere den Abstand zum Rand, damit mehr Höhe für den Schieberegler bleibt
        self.volume_slider.set_margin_top(0)
        self.volume_slider.set_margin_bottom(0)
        self.volume_slider.connect("value-changed", self.on_volume_changed)
        
        # Container für den Lautstärkeregler
        self.volume_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.volume_container.set_vexpand(True)  # Nutze die gesamte verfügbare Höhe
        self.volume_container.set_hexpand(False)
        self.volume_container.set_size_request(sb_config['volume_width'], sb_config['button_height'])
        self.volume_container.pack_start(self.volume_slider, True, True, 0)  # True für expand und fill
    
    def get_button_config(self):
        """Lädt die Button-spezifische Konfiguration"""
        sb_config = self.config['soundbutton']
        if self.position >= len(self.config.get('buttons', [])):
            return {
                'position': self.position,
                'volume': sb_config['volume_default'],
                'text': f"Button {self.position + 1}"
            }
        
        buttons = self.config.get('buttons', [])
        for button in buttons:
            if button['position'] == self.position:
                return button.copy()
        
        return {
            'position': self.position,
            'volume': sb_config['volume_default'],
            'text': f"Button {self.position + 1}"
        }
    
    def hex_to_rgb(self, hex_color):
        """Konvertiert einen Hex-Farbcode (#RRGGBB) in RGB-Werte (0-1)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return [r, g, b]
    
    
    def set_offset(self, offset_x, offset_y):
        """Setzt den Offset des Buttons"""
        self.offset_x = offset_x
        self.offset_y = offset_y
        print(f"SoundButton '{self.button_config['text']}' - Offset aktualisiert: x={self.offset_x}, y={self.offset_y}")
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
        sb_config = self.config['soundbutton']
        
        # Hintergrund
        bg_color = self.hex_to_rgb(sb_config['background_color'])
        cr.set_source_rgb(*bg_color)
        self.rounded_rectangle(cr, 0, 0, sb_config['button_width'], sb_config['button_height'], sb_config['radius'])
        cr.fill()
        
        if self.is_add_button:
            # Plus-Symbol für Add-Button
            cr.set_source_rgb(0, 0, 0)  # Schwarze Farbe für das Symbol
            cr.set_line_width(3)
            
            # Berechne die Größe und Position des Plus-Symbols
            size = min(sb_config['button_width'], sb_config['button_height']) * 0.4
            center_x = sb_config['button_width'] / 2
            center_y = sb_config['button_height'] / 2
            
            # Zeichne horizontale Linie
            cr.move_to(center_x - size/2, center_y)
            cr.line_to(center_x + size/2, center_y)
            
            # Zeichne vertikale Linie
            cr.move_to(center_x, center_y - size/2)
            cr.line_to(center_x, center_y + size/2)
            
            cr.stroke()
        else:
            # Normaler Button mit allen Details
            if 'image_file' in self.button_config and self.button_config['image_file']:
                self._draw_image(cr, {'button_width': sb_config['button_width'], 'button_height': sb_config['button_height']})
            
            self._draw_delete_button(cr, sb_config)
            self._draw_text(cr, sb_config)
            self._draw_control_buttons(cr, sb_config)
        
        return False
    
    def _draw_image(self, cr, button_size):
        """Zeichnet das Button-Bild"""
        try:
            image = cairo.ImageSurface.create_from_png(self.button_config['image_file'])
            cr.save()
            
            # Bild skalieren und zentrieren
            image_width = image.get_width()
            image_height = image.get_height()
            scale_x = button_size['button_width'] / image_width
            scale_y = button_size['button_height'] / image_height
            scale = min(scale_x, scale_y) * 0.8
            
            x = (button_size['button_width'] - image_width * scale) / 2
            y = (button_size['button_height'] - image_height * scale) / 2
            
            cr.translate(x, y)
            cr.scale(scale, scale)
            cr.set_source_surface(image, 0, 0)
            cr.paint()
            cr.restore()
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
    
    def _draw_delete_button(self, cr, sb_config):
        """Zeichnet den Lösch-Button"""
        delete_size = sb_config['delete_button_size']
        delete_x = sb_config['button_width'] - delete_size - 10
        delete_y = 10
        
        control_config = sb_config['control_buttons']
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
    
    def _draw_text(self, cr, sb_config):
        """Zeichnet den Button-Text"""
        text_color = self.hex_to_rgb(sb_config['text_color'])
        cr.set_source_rgb(*text_color)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(sb_config['text_size'])
        cr.move_to(sb_config['text_x'], sb_config['text_y'])
        cr.show_text(self.button_config['text'])
    
    def _draw_control_buttons(self, cr, sb_config):
        """Zeichnet die Steuerungsbuttons"""
        control_config = sb_config['control_buttons']
        control_size = control_config['size']
        spacing = control_config['spacing']
        
        y_offset = sb_config['button_height'] - control_size - spacing
        total_control_width = 3 * control_size + 2 * spacing
        start_x = (sb_config['button_width'] - total_control_width) / 2
        
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
                # Stelle sicher, dass pygame.mixer initialisiert ist
                if not pygame.mixer.get_init():
                    print("Initialisiere pygame.mixer in SoundButton")
                    pygame.mixer.init()
                    
                if self.sound and self.is_playing:  # Korrigiere && zu and
                    self.stop_sound()
                
                self.sound = pygame.mixer.Sound(self.button_config['audio_file'])
                self.sound.set_volume(self.button_config['volume'] / 100.0)
                
                self.sound.play()
                self.is_playing = True
                
                print(f"SoundButton '{self.button_config['text']}' - Sound wird abgespielt")
            except Exception as e:
                print(f"Fehler beim Abspielen des Sounds: {e}")
                self.stop_sound()
    
    def stop_sound(self):
        """Stoppt den Sound"""
        if self.sound and self.is_playing:
            try:
                # Stelle sicher, dass pygame.mixer initialisiert ist
                if not pygame.mixer.get_init():
                    print("Initialisiere pygame.mixer in SoundButton (stop_sound)")
                    pygame.mixer.init()
                    
                self.sound.stop()
                self.is_playing = False
                print(f"SoundButton '{self.button_config['text']}' - Sound gestoppt")
            except Exception as e:
                print(f"Fehler beim Stoppen des Sounds: {e}")
    
    def toggle_loop(self):
        """Schaltet die Schleifenwiedergabe ein/aus"""
        if self.sound:
            try:
                # Stelle sicher, dass pygame.mixer initialisiert ist
                if not pygame.mixer.get_init():
                    print("Initialisiere pygame.mixer in SoundButton (toggle_loop)")
                    pygame.mixer.init()
                    
                self.is_looping = not self.is_looping
                if self.is_looping:
                    self.sound.play(-1)
                    print(f"SoundButton '{self.button_config['text']}' - Schleifenwiedergabe aktiviert")
                else:
                    self.stop_sound()
                    print(f"SoundButton '{self.button_config['text']}' - Schleifenwiedergabe deaktiviert")
            except Exception as e:
                print(f"Fehler beim Umschalten der Schleifenwiedergabe: {e}")
                self.stop_sound()
    
    def on_button_press(self, widget, event):
        """Handler für Mausklicks"""
        if self.is_add_button and event.button == 1:  # Linksklick auf Add-Button
            if hasattr(self, 'on_add_click'):
                self.on_add_click(self)
            return True
            
        if not self.is_add_button:
            # Normale Button-Funktionalität
            sb_config = self.config['soundbutton']
            
            if self._is_delete_button_clicked(event, sb_config):
                if self.on_delete:
                    self.on_delete(self)
                return True
            
            if self._is_control_button_clicked(event, sb_config):
                return True
            
            if event.button == 3:  # Rechtsklick
                self.show_text_dialog()
                return True
        
        return False
    
    def on_motion_notify(self, widget, event):
        """Handler für Mausbewegung"""
        return False
    
    def on_button_release(self, widget, event):
        """Handler für Maus-Loslassen"""
        return False
    
    def _is_delete_button_clicked(self, event, sb_config):
        """Prüft, ob der Lösch-Button geklickt wurde"""
        delete_size = sb_config['delete_button_size']
        delete_x = sb_config['button_width'] - delete_size - 10
        delete_y = 10
        
        if (delete_x <= event.x <= delete_x + delete_size and 
            delete_y <= event.y <= delete_y + delete_size):
            print(f"Lösch-Button von '{self.button_config['text']}' wurde geklickt!")
            return True
        return False
    
    def _is_control_button_clicked(self, event, sb_config):
        """Prüft, ob ein Control-Button geklickt wurde"""
        control_config = sb_config['control_buttons']
        control_size = control_config['size']
        spacing = control_config['spacing']
        
        y_offset = sb_config['button_height'] - control_size - spacing
        total_control_width = 3 * control_size + 2 * spacing
        start_x = (sb_config['button_width'] - total_control_width) / 2
        
        if y_offset <= event.y <= y_offset + control_size:
            # Play-Button
            if start_x <= event.x <= start_x + control_size:
                print(f"Play-Button von '{self.button_config['text']}' wurde geklickt!")
                self.play_sound()
                return True
            
            # Stop-Button
            if start_x + control_size + spacing <= event.x <= start_x + 2 * control_size + spacing:
                print(f"Stop-Button von '{self.button_config['text']}' wurde geklickt!")
                self.stop_sound()
                return True
            
            # Loop-Button
            if start_x + 2 * (control_size + spacing) <= event.x <= start_x + 3 * control_size + 2 * spacing:
                print(f"Loop-Button von '{self.button_config['text']}' wurde geklickt!")
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
        value = int(volume_slider.get_value())  # Konvertiere zu Ganzzahl
        self.button_config['volume'] = value
        if self.sound:
            self.sound.set_volume(value / 100.0)
        print(f"'{self.button_config['text']}' - Lautstärke auf {value} gesetzt")
    
    def set_add_click_handler(self, handler):
        """Setzt den Handler für Klicks auf den Add-Button"""
        self.on_add_click = handler
    
    def _apply_style(self):
        """Wendet das Styling auf den Button an"""
        style_context = self.get_style_context()
        style_context.add_class("sound-button")
        
        css = """
        .sound-button {
            background-color: #CCCCCC;
            border-radius: 5px;
            padding: 5px;
        }
        .sound-button.dragging {
            background-color: rgba(100, 100, 255, 0.3);
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }
        """
        
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )