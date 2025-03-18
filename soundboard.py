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
    "window": {
        "width": 163,
        "height": 95,
        "title": "Soundboard"
    },
    "soundbutton": {
        "width": 100,
        "height": 75,
        "volume_height": 100,
        "volume_width": 15,
        "margin": 10,
        "spacing": 5,
        "initial_count": 3
    },
    "button": {
        "radius": 15,
        "delete_button_size": 20,
        "text_size": 13,
        "background_color": "#CCCCCC",
        "delete_button_color": "#CC3333",
        "text_color": "#000000",
        "text_x": 17,
        "text_y": 20,
        "control_buttons": {
            "size": 25,
            "spacing": 5,
            "y_offset": 110,
            "background_color": "#FFFFFF",
            "border_color": "#000000",
            "symbol_color": "#000000",
            "border_width": 1
        }
    },
    "volume": {
        "min": 0,
        "max": 100,
        "default": 50
    },
    "buttons": []
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
        self.add_button = None  # Referenz für den Add-Button
    
    def _setup_window(self):
        """Initialisiert die Fenster-Eigenschaften"""
        pygame.mixer.init()
        window_config = self.config['window']
        self.set_default_size(window_config['width'], window_config['height'])
        sb_config = self.config['soundbutton']
        # Nur die Mindestbreite setzen, nicht die Höhe
        self.set_size_request(sb_config['button_width'], -1)
    
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche mithilfe einer FlowBox für automatische Umbrechung"""
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_homogeneous(False)
        # Entferne den Aufruf von set_max_children_per_line(0)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.add(self.flowbox)
        self.add_button = Gtk.Button(label="+")
        self.add_button.connect("clicked", self.add_new_button)
        self.flowbox.add(self.add_button)
    
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
        """Lädt die gespeicherten Buttons in die FlowBox"""
        for saved_button in saved_buttons:
            position = saved_button['position']
            button = SoundButton(position=position, offset_x=0, offset_y=0, 
                               config=self.config, on_delete=self.delete_button)
            self.flowbox.add(button)
            self.buttons.append(button)
    
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
        # Diese Methode wird nicht mehr benötigt, da Gtk.FlowBox die Anordnung automatisch übernimmt.
        pass
    
    def add_new_button(self, widget):
        """Fügt einen neuen SoundButton hinzu und fügt ihn der FlowBox hinzu"""
        position = len(self.buttons)
        button = SoundButton(position=position, offset_x=0, offset_y=0, config=self.config, on_delete=self.delete_button)
        self.buttons.append(button)
        self.flowbox.add(button)
        print(f"Neuer SoundButton hinzugefügt. Position: {position + 1}, Gesamtanzahl: {len(self.buttons)}")
    
    def delete_button(self, button):
        """Löscht einen Button und aktualisiert die Positionen"""
        print(f"Lösche Button {button.position + 1}")
        
        # Zuerst das Entfernen aus der internen Liste
        if button in self.buttons:
            self.buttons.remove(button)
        
        # Stoppe alle laufenden Sounds des Buttons
        if hasattr(button, 'stop_sound'):
            button.stop_sound()
        
        # Aktualisiere die Positionen der verbleibenden Buttons
        for i, b in enumerate(self.buttons):
            b.position = i
            b.button_config['position'] = i
        
        # Dann das Widget aus der FlowBox entfernen, wenn es noch einen Parent hat
        if button.get_parent() is not None:
            parent = button.get_parent()
            if isinstance(parent, Gtk.FlowBoxChild):
                self.flowbox.remove(parent)
            else:
                self.flowbox.remove(button)
        
        # Stelle sicher, dass das Widget zerstört wird
        button.destroy()

    def _delete_button_idle(self, button):
        # Diese Methode wird nicht mehr benötigt, da wir die Löschung direkt durchführen
        pass
    
    def save_all_configs(self):
        """Speichert die Konfigurationen aller Buttons und die Fenstergröße"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = self.config

        # Fenstergröße aktualisieren
        width, height = self.get_size()
        config['window']['width'] = width
        config['window']['height'] = height

        # Buttons-Konfiguration speichern
        buttons = [button.button_config for button in self.buttons]
        config['buttons'] = buttons

        # Konfiguration in die Datei schreiben
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
    
    def on_destroy(self, *args):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        pygame.mixer.quit()
        Gtk.main_quit()
        return True
    
    def on_window_configure(self, widget, event):
        """Reagiert auf Fenstergrößenänderungen"""
        # Entferne die feste Mindesthöhe, damit sich das Fenster dynamisch anpasst.
        # sb_config = self.config['soundbutton']
        # min_height = sb_config['button_height'] + 2 * sb_config['margin']
        # self.set_size_request(-1, min_height)
        return False  # Weitergabe des Events
    
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