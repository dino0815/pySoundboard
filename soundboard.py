#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import json
from soundbutton import SoundButton
import pygame

class SoundboardWindow(Gtk.Window):
    # Konstanten für die Konfiguration
    DEFAULT_CONFIG = {
        'window': {
            'width': 1000,
            'height': 200,
            'title': "Soundboard"
        },
        'soundbutton': {
            'width': 300,
            'height': 150,
            'volume_height': 30,
            'volume_width': 200,
            'margin': 10,
            'spacing': 5,
            'initial_count': 3
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
    
    def __init__(self):
        super().__init__(title="Soundboard")
        self.buttons = []
        self.config = self.load_config()
        self._setup_window()
        self._setup_ui()
        self._load_buttons()
        self._connect_signals()
        self.show_all()
    
    def _setup_window(self):
        """Initialisiert die Fenster-Eigenschaften"""
        pygame.mixer.init()
        window_config = self.config['window']
        self.set_default_size(window_config['width'], window_config['height'])
        
        # Minimale Fenstergröße setzen
        button_config = self.config['soundbutton']
        min_height = button_config['height'] + button_config['volume_height'] + button_config['spacing'] + 20
        self.set_size_request(button_config['width'], min_height)
    
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Hauptcontainer
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)
        
        # Header mit Plus-Button
        self._create_header()
        
        # ScrolledWindow für die Buttons
        self._create_scrolled_window()
    
    def _create_header(self):
        """Erstellt die Header-Leiste mit dem Plus-Button"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Leerer Platzhalter links
        header_box.pack_start(Gtk.Label(), True, True, 0)
        # Plus-Button rechts
        plus_button = Gtk.Button(label="+")
        plus_button.connect("clicked", self.add_new_button)
        header_box.pack_end(plus_button, False, False, 0)
        self.box.pack_start(header_box, False, False, 0)
    
    def _create_scrolled_window(self):
        """Erstellt den scrollbaren Bereich für die Buttons"""
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
    
    def _connect_signals(self):
        """Verbindet die Signal-Handler"""
        self.connect("destroy", self.on_destroy)
        self.connect("configure-event", self.on_window_configure)
        self.connect("key-press-event", self.on_key_press)
        self.connect("delete-event", self.on_window_delete)
    
    def _load_buttons(self):
        """Lädt die gespeicherten Buttons oder erstellt neue"""
        saved_buttons = self.config.get('buttons', [])
        if saved_buttons:
            self._load_saved_buttons(saved_buttons)
        else:
            self._create_initial_buttons()
    
    def _load_saved_buttons(self, saved_buttons):
        """Lädt die gespeicherten Buttons"""
        button_config = self.config['soundbutton']
        for saved_button in saved_buttons:
            position = saved_button['position']
            offset_x = position * (button_config['width'] + button_config['volume_height'] + button_config['spacing'])
            button = SoundButton(position=position, offset_x=offset_x, offset_y=0, 
                               config=self.config, on_delete=self.delete_button)
            self.buttons.append(button)
            self.button_box.pack_start(button, False, False, 0)
    
    def _create_initial_buttons(self):
        """Erstellt die initialen Buttons"""
        for _ in range(self.config['soundbutton']['initial_count']):
            self.add_new_button(None)
    
    def load_config(self):
        """Lädt die Konfigurationsdatei"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warnung: config.json nicht gefunden, verwende Standardwerte")
            return self.DEFAULT_CONFIG.copy()
    
    def update_button_positions(self):
        """Aktualisiert die Positionen aller Buttons"""
        button_config = self.config['soundbutton']
        for i, button in enumerate(self.buttons):
            offset_x = i * (button_config['width'] + button_config['volume_height'] + button_config['spacing'])
            button.set_offset(offset_x, 0)
        self.update_scrolled_window_size()
    
    def update_scrolled_window_size(self):
        """Aktualisiert die Größe des ScrolledWindow"""
        button_config = self.config['soundbutton']
        total_width = len(self.buttons) * (button_config['width'] + button_config['volume_height'] + button_config['spacing']) + 2 * button_config['margin']
        self.scrolled.set_min_content_width(total_width)
    
    def add_new_button(self, widget):
        """Fügt einen neuen SoundButton hinzu"""
        position = len(self.buttons)
        button_config = self.config['soundbutton']
        offset_x = position * (button_config['width'] + button_config['volume_height'] + button_config['spacing'])
        
        button = SoundButton(position=position, offset_x=offset_x, offset_y=0, 
                           config=self.config, on_delete=self.delete_button)
        self.buttons.append(button)
        self.button_box.pack_start(button, False, False, 0)
        
        print(f"Neuer SoundButton hinzugefügt. Position: {position + 1}, Gesamtanzahl: {len(self.buttons)}")
        self.update_button_positions()
    
    def delete_button(self, button):
        """Löscht einen Button und aktualisiert die Positionen"""
        print(f"Lösche Button {button.position + 1}")
        
        # Button aus der Liste und GUI entfernen
        self.buttons.remove(button)
        self.button_box.remove(button)
        
        # Positionen der verbleibenden Buttons aktualisieren
        for i, b in enumerate(self.buttons):
            b.position = i
            b.button_config['position'] = i
        self.update_button_positions()
    
    def save_all_configs(self):
        """Speichert die Konfigurationen aller Buttons"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = self.config
        
        buttons = [button.button_config for button in self.buttons]
        config['buttons'] = buttons
        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
    
    def on_destroy(self, *args):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        pygame.mixer.quit()
        Gtk.main_quit()
        return True
    
    def on_window_configure(self, widget, event):
        """Reagiert auf Fenstergrößenänderungen"""
        height = self.get_allocated_height()
        button_config = self.config['soundbutton']
        min_height = button_config['height'] + button_config['volume_height'] + button_config['spacing'] + 20
        if height < min_height:
            self.set_size_request(-1, min_height)
    
    def on_key_press(self, widget, event):
        """Handler für Tastatureingaben"""
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_s:
            self.save_all_configs()
            return True
        return False
    
    def on_window_delete(self, widget, event):
        """Handler für das Schließen des Fensters"""
        self.save_all_configs()
        return False

def main():
    win = SoundboardWindow()
    Gtk.main()

if __name__ == "__main__":
    main() 