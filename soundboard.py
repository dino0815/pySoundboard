#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import json
from soundbutton import SoundButton

class SoundboardWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Soundboard")
        self.config = self.load_config()
        self.buttons = []
        
        # Fenster-Eigenschaften aus der Konfiguration
        window_config = self.config['window']
        self.set_default_size(window_config['width'], window_config['height'])
        
        # Hauptcontainer
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)
        
        # Header-Box mit Plus-Button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        plus_button = Gtk.Button(label="+")
        plus_button.connect("clicked", self.add_new_button)
        header_box.pack_start(plus_button, False, False, 0)
        self.box.pack_start(header_box, False, False, 0)
        
        # ScrolledWindow für die Buttons
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled.set_hexpand(True)
        self.scrolled.set_vexpand(True)
        
        # Container für die Buttons
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_config = self.config['soundbutton']
        self.button_box.set_spacing(button_config['spacing'])
        self.button_box.set_margin_start(button_config['margin'])
        self.button_box.set_margin_end(button_config['margin'])
        self.button_box.set_margin_top(button_config['margin'])
        self.button_box.set_margin_bottom(button_config['margin'])
        
        self.scrolled.add(self.button_box)
        self.box.pack_start(self.scrolled, True, True, 0)
        
        # Initiale Buttons erstellen
        saved_buttons = self.config.get('buttons', [])
        if saved_buttons:
            # Wenn gespeicherte Buttons existieren, diese verwenden
            for saved_button in saved_buttons:
                position = saved_button['position']
                offset_x = position * (button_config['width'] + button_config['spacing'])
                offset_y = 0
                button = SoundButton(position=position, offset_x=offset_x, offset_y=offset_y, config=self.config, on_delete=self.delete_button)
                self.buttons.append(button)
                self.button_box.pack_start(button, False, False, 0)
        else:
            # Wenn keine gespeicherten Buttons existieren, initial_count verwenden
            for i in range(self.config['soundbutton']['initial_count']):
                self.add_new_button(None)
        
        # Event-Handler für das Schließen des Fensters
        self.connect("destroy", self.on_destroy)
        
        # Initiale ScrolledWindow-Größe setzen
        self.update_scrolled_window_size()
        
        # Alle Widgets anzeigen
        self.show_all()
    
    def load_config(self):
        """Lädt die Konfigurationsdatei"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warnung: config.json nicht gefunden, verwende Standardwerte")
            return {
                'window': {
                    'width': 1000,
                    'height': 300,
                    'title': "Soundboard"
                },
                'soundbutton': {
                    'width': 300,
                    'height': 200,
                    'button_height': 150,
                    'scale_height': 30,
                    'scale_width': 200,
                    'margin': 10,
                    'spacing': 5,
                    'initial_count': 3
                }
            }
    
    def update_button_positions(self):
        """Aktualisiert die Positionen aller Buttons"""
        button_config = self.config['soundbutton']
        for i, button in enumerate(self.buttons):
            button.position = i  # Aktualisiere die Position
            offset_x = i * (button_config['width'] + button_config['spacing'])
            offset_y = 0
            button.set_offset(offset_x, offset_y)
        self.update_scrolled_window_size()
    
    def update_scrolled_window_size(self):
        """Aktualisiert die Größe der ScrolledWindow basierend auf der Anzahl der Buttons"""
        button_config = self.config['soundbutton']
        total_width = len(self.buttons) * (button_config['width'] + button_config['spacing']) + 2 * button_config['margin']
        self.scrolled.set_min_content_width(total_width)
    
    def add_new_button(self, widget):
        """Fügt einen neuen SoundButton hinzu"""
        position = len(self.buttons)
        button_config = self.config['soundbutton']
        offset_x = position * (button_config['width'] + button_config['spacing'])
        offset_y = 0
        
        button = SoundButton(position=position, offset_x=offset_x, offset_y=offset_y, config=self.config, on_delete=self.delete_button)
        self.buttons.append(button)
        self.button_box.pack_start(button, False, False, 0)
        
        print(f"Neuer SoundButton hinzugefügt. Position: {position + 1}, Gesamtanzahl: {len(self.buttons)}")
        self.update_button_positions()
    
    def delete_button(self, button):
        """Löscht einen Button und aktualisiert die Positionen der verbleibenden Buttons"""
        print(f"Lösche Button {button.position + 1}")
        
        # Button aus der Liste und GUI entfernen
        self.buttons.remove(button)
        self.button_box.remove(button)
        
        # Konfiguration aktualisieren
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            # Entferne den Button aus der gespeicherten Konfiguration
            if 'buttons' in config:
                # Entferne den gelöschten Button
                config['buttons'] = [b for b in config['buttons'] if b['position'] != button.position]
                
                # Aktualisiere die Positionen der verbleibenden Buttons
                for i, b in enumerate(config['buttons']):
                    b['position'] = i
                
                print(f"Konfiguration aktualisiert. Verbleibende Buttons: {len(config['buttons'])}")
            
            # Speichere die aktualisierte Konfiguration
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Konfiguration: {e}")
        
        # Positionen der verbleibenden Buttons aktualisieren
        for i, b in enumerate(self.buttons):
            b.position = i
            b.button_config['position'] = i
        self.update_button_positions()
    
    def on_destroy(self, widget):
        """Speichert die Konfiguration beim Schließen"""
        print("Speichere Button-Konfigurationen...")
        for button in self.buttons:
            button.save_config()
        Gtk.main_quit()

def main():
    win = SoundboardWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main() 