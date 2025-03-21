#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk
import os
import time
import argparse

class CounterWindow(Gtk.Window):
    def __init__(self, image_path=None):
        Gtk.Window.__init__(self, title="Counter App")
        self.set_default_size(300, 250)
        self.set_border_width(20)
        self.counter = 0
        
        # Variablen für die Langklick-Erkennung
        self.press_timeout_id = None
        self.LONG_PRESS_TIME = 500  # 500ms = 0.5 Sekunden
        self.press_start_time = 0
        self.is_pressed = False
        
        # CSS-Button-Status
        self.css_button_pressed = False
        
        # Pfad zum Bild
        if image_path and os.path.exists(image_path):
            self.image_path = image_path
        else:
            # Standard-Bildpfad, falls keiner angegeben wurde oder der angegebene ungültig ist
            self.image_path = os.path.join("images", "StevesGalaxy.png")
            if image_path and not os.path.exists(image_path):
                print(f"WARNUNG: Bild nicht gefunden: {image_path}")
                print(f"Verwende Standard-Bild: {self.image_path}")
        
        self.theme_colors = self.get_theme_colors()  # Theme-Farben
        self._setup_css()  # CSS-Provider erstellen
        self.setup_ui() # UI aufbauen   
    
    def get_theme_colors(self):
        """Extrahiert Farben aus dem aktuellen Theme"""
        # Widget erstellen, um auf das Theme zuzugreifen
        temp_widget = Gtk.Button()
        style = temp_widget.get_style_context()
        
        # Farben extrahieren
        normal_color = style.get_color(Gtk.StateFlags.NORMAL)
        
        # Hintergrundfarbe auslesen
        success, normal_bg = style.lookup_color("theme_bg_color")
        if not success:
            # Fallback
            normal_bg = Gdk.RGBA(0.9, 0.9, 0.9, 1.0)
        
        # Gedrückte Button-Farbe auslesen
        temp_button = Gtk.Button()
        button_style = temp_button.get_style_context()
        button_style.set_state(Gtk.StateFlags.ACTIVE)
        
        pressed_bg = Gdk.RGBA(0.8, 0.8, 0.8, 1.0)
        
        # Versuchen, die Farbe direkt aus dem Button-Style zu bekommen
        success = False
        try:
            success, pressed_bg = button_style.lookup_color("button_active_bg_color")
            if not success:
                success, pressed_bg = button_style.lookup_color("theme_button_active_bg")
        except:
            pass
        
        if not success:
            # Fallback: Dunklere Version der normalen Hintergrundfarbe
            pressed_bg = Gdk.RGBA(
                normal_bg.red * 0.9,
                normal_bg.green * 0.9,
                normal_bg.blue * 0.9,
                normal_bg.alpha
            )
        
        # 3D-Effekt-Farben berechnen
        light_factor = 1.3
        dark_factor = 0.7
        
        # Highlight-Farbe (heller)
        highlight = Gdk.RGBA(
            min(1.0, normal_bg.red * light_factor),
            min(1.0, normal_bg.green * light_factor),
            min(1.0, normal_bg.blue * light_factor),
            normal_bg.alpha
        )
        
        # Schatten-Farbe (dunkler)
        shadow = Gdk.RGBA(
            normal_bg.red * dark_factor,
            normal_bg.green * dark_factor,
            normal_bg.blue * dark_factor,
            normal_bg.alpha
        )
        
        return {
            'normal_text': normal_color,
            'normal_bg': normal_bg,
            'pressed_bg': pressed_bg,
            'highlight': highlight,
            'shadow': shadow
        }
    
    def _rgba_to_hex(self, rgba):
        """Konvertiert ein RGBA-Objekt in einen Hex-Farbcode für CSS"""
        r = int(rgba.red * 255)
        g = int(rgba.green * 255)
        b = int(rgba.blue * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _setup_css(self):
        """Erstellt und lädt das CSS für den Button"""
        # Theme-Farben für CSS
        normal_bg_hex = self._rgba_to_hex(self.theme_colors['normal_bg'])
        normal_text_hex = self._rgba_to_hex(self.theme_colors['normal_text'])
        highlight_hex = self._rgba_to_hex(self.theme_colors['highlight'])
        shadow_hex = self._rgba_to_hex(self.theme_colors['shadow'])
        pressed_bg_hex = self._rgba_to_hex(self.theme_colors['pressed_bg'])
        
        # CSS definieren
        css = f"""
        .custom-button {{
            background-color: {normal_bg_hex};
            color: {normal_text_hex};
            border-radius: 10px;
            padding: 10px;
            min-width: 120px;
            min-height: 60px;
            font-weight: bold;
            border-style: solid;
            border-width: 2px;
            border-color: {highlight_hex} {shadow_hex} {shadow_hex} {highlight_hex}; /* oben rechts unten links */
            transition: all 0.1s ease;
        }}
        
        .custom-button-toggled {{
            background-color: {pressed_bg_hex};
            color: {normal_text_hex};
            border-radius: 10px;
            padding: 12px 8px 8px 12px; /* oben rechts unten links */
            min-width: 120px;
            min-height: 60px;
            font-weight: bold;
            border-style: solid;
            border-width: 2px;
            border-color: {shadow_hex} {highlight_hex} {highlight_hex} {shadow_hex}; /* oben rechts unten links */
            transition: all 0.1s ease;
        }}
        """
        
        # CSS-Provider erstellen und laden
        self.provider = Gtk.CssProvider()
        self.provider.load_from_data(css.encode())
        
        # Das CSS global hinzufügen
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def setup_ui(self):
        """Hauptmethode zum Aufbau der Benutzeroberfläche"""
        # Vertikale Box für die Anordnung
        self.main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.main_vbox)
        
        # Label für den Zähler
        self.counter_label = Gtk.Label()
        self.update_counter_display()
        self.main_vbox.pack_start(self.counter_label, True, True, 0)
        
        # Button erstellen
        self.create_toggle_button()
    
    def update_counter_display(self):
        """Aktualisiert das Zähler-Label mit dem aktuellen Wert"""
        self.counter_label.set_markup(f"<span size='xx-large'>{self.counter}</span>")
    
    def create_toggle_button(self):
        """Erstellt den CSS-gestylten Toggle-Button"""
        # Button erstellen
        button = Gtk.Button()
        button.set_size_request(150, 120)
        
        # CSS-Klasse hinzufügen
        style_context = button.get_style_context()
        style_context.add_class("custom-button")
        
        # Inhalt des Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Bild laden
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=self.image_path,
            width=64, 
            height=64, 
            preserve_aspect_ratio=True
        )
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        
        # Text-Label
        label = Gtk.Label()
        label.set_markup("<span weight='bold' size='large'>Klick mich</span>")
        
        # Komponenten speichern für späteren Zugriff
        self.button = button
        self.button_image = image
        self.button_label = label
        self.button_box = button_box
        
        # Inhalt zum Layout hinzufügen
        button_box.pack_start(image, False, False, 2)
        button_box.pack_start(label, False, False, 2)
        button.add(button_box)
        
        # Events verbinden
        button.connect("clicked", self.on_button_clicked)
        button.connect("button-press-event", self.on_button_press)
        button.connect("button-release-event", self.on_button_release)
        
        # Button zum Hauptcontainer hinzufügen
        self.main_vbox.pack_start(button, True, False, 10)
    
    def on_button_press(self, widget, event):
        """Handler für Button-Druck-Event"""
        self.press_start_time = time.time()
        self.is_pressed = True
        
        # Timer für Langklick starten
        self.press_timeout_id = GLib.timeout_add(self.LONG_PRESS_TIME, 
                                               self.check_long_press)
        return False
    
    def on_button_release(self, widget, event):
        """Handler für Button-Loslassen-Event"""
        self.is_pressed = False
        
        # Timer löschen wenn Button losgelassen wird bevor Langklick erkannt wurde
        if self.press_timeout_id:
            GLib.source_remove(self.press_timeout_id)
            self.press_timeout_id = None
        return False
    
    def check_long_press(self):
        """Prüft, ob ein Langklick erkannt wurde"""
        elapsed = time.time() - self.press_start_time
        
        if self.is_pressed and elapsed >= self.LONG_PRESS_TIME / 1000.0:
            self.show_dialog()
            self.press_timeout_id = None
            return False  # Timer nicht wiederholen
        
        if not self.is_pressed:
            self.press_timeout_id = None
            return False  # Button wurde losgelassen, Timer stoppen
        
        return True  # Timer fortsetzen
    
    def show_dialog(self):
        """Zeigt einen Dialog mit dem aktuellen Zählerstand an"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Langer Klick erkannt!"
        )
        dialog.format_secondary_text(
            f"Aktueller Zählerstand: {self.counter}"
        )
        dialog.run()
        dialog.destroy()
    
    def on_button_clicked(self, button):
        """Handler für Klick auf den Button"""
        style_context = button.get_style_context()
        
        if not self.css_button_pressed:
            # Zum gedrückten Zustand wechseln
            style_context.remove_class("custom-button")
            style_context.add_class("custom-button-toggled")
            self.button_label.set_markup("<span weight='bold' size='large'>Gedrückt</span>")
            
            # Bild und Text leicht verschieben
            margin = self.button_box.get_margin_top()
            self.button_box.set_margin_top(margin + 2)
            self.button_box.set_margin_start(2)
            
            self.css_button_pressed = True
        else:
            # Zurück zum normalen Zustand
            style_context.remove_class("custom-button-toggled")
            style_context.add_class("custom-button")
            self.button_label.set_markup("<span weight='bold' size='large'>Klick mich</span>")
            
            # Bild und Text zurücksetzen
            self.button_box.set_margin_top(0)
            self.button_box.set_margin_start(0)
            
            # Zähler erhöhen (nur beim Zurückwechseln vom gedrückten Zustand)
            self.counter += 1
            self.update_counter_display()
            
            self.css_button_pressed = Fnalse

def main():
    # Kommandozeilenargumente verarbeiten
    parser = argparse.ArgumentParser(description='GTK Counter App')
    parser.add_argument('--image', '-i', dest='image_path', 
                        help='Pfad zum anzuzeigenden Bild')
    args = parser.parse_args()
    
    # Fenster erstellen und Bildpfad übergeben
    win = CounterWindow(args.image_path)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main() 