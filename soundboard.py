#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from soundbutton import SoundButton

class SoundboardWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Soundboard")
        self.set_default_size(1000, 300)  # Breiteres Fenster für horizontale Anordnung
        
        # Hauptcontainer
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.box)
        
        # Header mit Plus-Button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.box.pack_start(header_box, False, False, 0)
        
        plus_button = Gtk.Button(label="+")
        plus_button.connect("clicked", self.on_plus_clicked)
        header_box.pack_start(plus_button, False, False, 0)
        
        # Scrolled Window für die Buttons
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)  # Horizontales Scrollen
        self.scrolled.set_vexpand(True)
        self.scrolled.set_hexpand(True)
        self.box.pack_start(self.scrolled, True, True, 0)
        
        # Container für die Buttons (horizontal)
        self.areas_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.areas_container.set_margin_start(10)
        self.areas_container.set_margin_end(10)
        self.areas_container.set_margin_top(10)
        self.areas_container.set_margin_bottom(10)
        self.areas_container.set_hexpand(True)  # Container soll horizontal expandieren
        self.scrolled.add(self.areas_container)
        
        # Initial drei Buttons erstellen
        for i in range(3):
            self.add_new_button()
        
        # Fenster anzeigen
        self.show_all()
    
    def update_button_positions(self):
        """Aktualisiert die Positionen aller Buttons"""
        for i, button in enumerate(self.areas_container.get_children()):
            # Horizontale Anordnung: x-Offset basierend auf Position
            offset_x = i * 320  # 300px Breite + 20px Abstand
            offset_y = 0
            button.set_offset(offset_x, offset_y)
            print(f"Button {i + 1} Position aktualisiert - x={offset_x}, y={offset_y}")
    
    def add_new_button(self):
        """Fügt einen neuen SoundButton hinzu"""
        position = len(self.areas_container.get_children())
        # Horizontale Anordnung: x-Offset basierend auf Position
        offset_x = position * 320  # 300px Breite + 20px Abstand
        offset_y = 0
        
        button = SoundButton(position=position, offset_x=offset_x, offset_y=offset_y)
        self.areas_container.pack_start(button, False, False, 0)
        
        print(f"Neuer SoundButton hinzugefügt. Position: {position + 1}, Gesamtanzahl: {position + 1}")
        print(f"Button {position + 1} Offset: x={offset_x}, y={offset_y}")
        
        # Positionen aller Buttons aktualisieren
        self.update_button_positions()
        
        # ScrolledWindow anpassen
        total_width = (300 + 20) * (position + 1) + 20  # (Breite + Abstand) * Anzahl + Margins
        self.scrolled.set_min_content_width(total_width)
        
        # Container neu anzeigen
        self.areas_container.show_all()
    
    def on_plus_clicked(self, button):
        """Callback für den Plus-Button"""
        print("Plus-Button wurde geklickt!")
        self.add_new_button()

win = SoundboardWindow()
win.connect("destroy", Gtk.main_quit)
Gtk.main() 