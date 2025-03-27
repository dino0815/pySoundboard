#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk
import os
import time
import argparse

class Window(Gtk.Window):
    def __init__(self, image_path=None):
        Gtk.Window.__init__(self, title="Test Button App")
        self.set_default_size(300, 250)
        self.set_border_width(5)

        self.is_pressed       = False        

        # Pfad zum Bild
        if image_path: 
            if os.path.exists(image_path):
                self.image_path = image_path
            else:
                print(f"WARNUNG: Bild nicht gefunden: {image_path}")
                self.image_path = None 
        else:
            self.image_path = None 

        self.theme_colors = self.get_theme_colors()  # Theme-Farben
        self._setup_css()                            # CSS-Provider erstellen
        self.setup_ui()                              # UI aufbauen   
    
    ##########################################################################################
    def get_theme_colors(self):
        """Extrahiert Farben aus dem aktuellen Theme"""
        # Widget erstellen, um auf das Theme zuzugreifen
        temp_button = Gtk.Button()
        style       = temp_button.get_style_context()
        
        # Farben extrahieren
        success, text_color      = style.lookup_color("theme_text_color")
        success, normal_bg_color = style.lookup_color("theme_bg_color")

        # 3D-Effekt-Farben berechnen
        dark_factor    = 0.7
        pressed_factor = 0.9
        light_factor   = 1.3
        
        #PressedColor als Dunklere Version der normalen Hintergrundfarbe
        pressed_bg_color = Gdk.RGBA(
            normal_bg_color.red   * pressed_factor,
            normal_bg_color.green * pressed_factor,
            normal_bg_color.blue  * pressed_factor,
            normal_bg_color.alpha
        )

        # Highlight-Farbe (heller)
        highlight_color = Gdk.RGBA(
            min(1.0, normal_bg_color.red   * light_factor),
            min(1.0, normal_bg_color.green * light_factor),
            min(1.0, normal_bg_color.blue  * light_factor),
            normal_bg_color.alpha
        )
        
        # Schatten-Farbe (dunkler)
        shadow_color = Gdk.RGBA(
            normal_bg_color.red   * dark_factor,
            normal_bg_color.green * dark_factor,
            normal_bg_color.blue  * dark_factor,
            normal_bg_color.alpha
        )
        
        #print(f"text_color:       {text_color}")
        #print(f"normal_bg_color:  {normal_bg_color}")
        #print(f"pressed_bg_color: {pressed_bg_color}")
        #print(f"highlight_color:  {highlight_color}")
        #print(f"shadow_color:     {shadow_color}")

        return {
            'normal_text': text_color,
            'normal_bg':   normal_bg_color,
            'pressed_bg':  pressed_bg_color,
            'highlight':   highlight_color,
            'shadow':      shadow_color
        }
    
    ##########################################################################################
    def _rgba_to_hex(self, rgba):
        """Konvertiert ein RGBA-Objekt in einen Hex-Farbcode für CSS"""
        r = int(rgba.red * 255)
        g = int(rgba.green * 255)
        b = int(rgba.blue * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    ##########################################################################################
    def _setup_css(self):
        """Erstellt und lädt das CSS für den Button"""
        # Theme-Farben für CSS
        normal_bg_hex   = self._rgba_to_hex(self.theme_colors['normal_bg'])
        normal_text_hex = self._rgba_to_hex(self.theme_colors['normal_text'])
        highlight_hex   = self._rgba_to_hex(self.theme_colors['highlight'])
        shadow_hex      = self._rgba_to_hex(self.theme_colors['shadow'])
        pressed_bg_hex  = self._rgba_to_hex(self.theme_colors['pressed_bg'])
        
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
            border-color: {highlight_hex} {shadow_hex} {shadow_hex} {highlight_hex}; /*oben rechts unten links*/
            transition: all 0.1s ease;
        }}
        
        .custom-button-toggled {{
            background-color: {pressed_bg_hex};
            color: {normal_text_hex};
            border-radius: 10px;
            padding: 12px 8px 8px 12px; /*oben rechts unten links*/
            min-width: 120px;
            min-height: 60px;
            font-weight: bold;
            border-style: solid;
            border-width: 2px;
            border-color: {shadow_hex} {highlight_hex} {highlight_hex} {shadow_hex};/*oben rechts unten links*/
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
    
    ##########################################################################################
    def setup_ui(self):
        """Hauptmethode zum Aufbau der Benutzeroberfläche"""
        # Vertikale Box für die Anordnung #
        self.main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.main_vbox)
        
        # Button erstellen #
        self.create_toggle_button()
    
    ##########################################################################################
    def create_toggle_button(self):
        """Erstellt den CSS-gestylten Toggle-Button"""
        # Button erstellen #
        button = Gtk.Button()
        button.set_size_request(150, 120)

        # CSS-Klasse hinzufügen #
        style_context = button.get_style_context()
        style_context.add_class("custom-button")
        
        # Inhalt des Buttons #
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Bild laden #
        if self.image_path:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=self.image_path,
                width=64, 
                height=64, 
                preserve_aspect_ratio=True
            )
            image = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            image=None
        
        ### Text-Label ###
        label = Gtk.Label()
        label.set_markup("<span weight='bold' size='large'>Klick mich</span>")
        
        # Komponenten speichern für späteren Zugriff #
        self.button = button
        self.button_image = image
        self.button_label = label
        self.button_box = button_box

        # Label sollte den gesamten Button-Bereich nutzen können #
        self.button_box.set_hexpand(False)
        self.button_box.set_vexpand(False)
                
        # Inhalt zum Layout hinzufügen #
        if image:
            button_box.pack_start(image, False, False, 2)
        button_box.pack_start(label, False, False, 2)
        button.add(button_box)
        
        # Events verbinden #
        button.connect("clicked", self.on_button_clicked)
        
        # Button zum Hauptcontainer hinzufügen #
        self.main_vbox.pack_start(button, True, False, 10)
    
    ##########################################################################################
    def on_button_clicked(self, button):
        """Handler für Klick auf den Button"""
        style_context = button.get_style_context()
        
        if not self.is_pressed:
            # Zum gedrückten Zustand wechseln
            style_context.remove_class("custom-button")
            style_context.add_class("custom-button-toggled")
            self.button_label.set_markup("<span weight='bold' size='large'>Gedrückt</span>")
            
            ### Bild und Text leicht verschieben
            # margin = self.button_box.get_margin_top()
            # self.button_box.set_margin_top(margin + 2)
            # self.button_box.set_margin_start(2)
            self.is_pressed = True

        else: # is_pressed = true
            # Zurück zum normalen Zustand
            style_context.remove_class("custom-button-toggled")
            style_context.add_class("custom-button")
            self.button_label.set_markup("<span weight='bold' size='large'>Klick mich</span>")
            
            ### Bild und Text zurücksetzen
            # self.button_box.set_margin_top(0)
            # self.button_box.set_margin_start(0)            
            self.is_pressed = False

##########################################################################################
def main():
    # Kommandozeilenargumente verarbeiten
    parser = argparse.ArgumentParser(description='GTK Counter App')
    parser.add_argument('--image', '-i', dest='image_path', 
                        help='Pfad zum anzuzeigenden Bild')
    args = parser.parse_args()
    
    # Fenster erstellen und Bildpfad übergeben
    win = Window(args.image_path)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

##########################################################################################
if __name__ == "__main__":
    main() 
