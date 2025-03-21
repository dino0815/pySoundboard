#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import json
from soundbutton import SoundButton
import pygame
import os

class SoundboardWindow(Gtk.Window):
    # Konstanten für die Konfiguration
    DEFAULT_CONFIG = {
        "window": {
            "width": 163,
            "height": 95,
            "title": "Soundboard"
        },
        "soundbutton": {
            "button_width": 100,
            "button_height": 75,
            "volume_height": 100,
            "volume_width": 15,
            "spacing": 5,
            "radius": 15,
            "delete_button_size": 20,
            "text_size": 13,
            "background_color": "#CCCCCC",
            "text_color": "#000000",
            "text_x": 17,
            "text_y": 20,
            "volume_min": 0,
            "volume_max": 100,
            "volume_default": 50,
            "control_buttons": {
                "size": 25,
                "spacing": 5,
                "background_color": "#FFFFFF",
                "border_color": "#000000",
                "symbol_color": "#000000",
                "border_width": 1
            }
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
        # Initialisiere pygame.mixer mit Fehlerbehandlung
        try:
            if not pygame.mixer.get_init():
                print("Initialisiere pygame.mixer in SoundboardWindow")
                pygame.mixer.init()
        except Exception as e:
            print(f"Fehler bei der Initialisierung von pygame.mixer: {e}")
            # Versuche es mit einigen Standardparametern erneut
            try:
                pygame.mixer.init(44100, -16, 2, 2048)
                print("pygame.mixer mit Standardparametern initialisiert")
            except Exception as e:
                print(f"Kritischer Fehler: Konnte pygame.mixer nicht initialisieren: {e}")
        
        window_config = self.config['window']
        self.set_default_size(window_config['width'], window_config['height'])
        # Keine Mindestgröße setzen
        self.set_size_request(-1, -1)
    
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche mithilfe einer FlowBox für automatische Umbrechung"""
        # Scrolled Window für vertikales Scrollen
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scrolled)
        
        # Haupt-Box für vertikales Layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_vexpand(True)
        scrolled.add(main_box)
        
        # FlowBox konfigurieren
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_halign(Gtk.Align.START)
        self.flowbox.set_hexpand(True)
        self.flowbox.set_homogeneous(True)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_min_children_per_line(1)
        self.flowbox.set_max_children_per_line(20)
        
        # Feste Abstände zwischen den Buttons
        sb_config = self.config['soundbutton']
        self.flowbox.set_row_spacing(sb_config['spacing'])
        self.flowbox.set_column_spacing(sb_config['spacing'])
        
        # Äußere Abstände der FlowBox (auch spacing verwenden)
        self.flowbox.set_margin_start(sb_config['spacing'])
        self.flowbox.set_margin_end(sb_config['spacing'])
        self.flowbox.set_margin_top(sb_config['spacing'])
        self.flowbox.set_margin_bottom(sb_config['spacing'])
        
        main_box.pack_start(self.flowbox, True, True, 0)
        
        # Add-Button wird erst später in _load_buttons hinzugefügt
        self.add_button = None
    
    def _connect_signals(self):
        """Verbindet die Signal-Handler"""
        self.connect("destroy", self.on_destroy)
        #self.connect("configure-event", self.on_window_configure)
        self.connect("key-press-event", self.on_key_press)
        self.connect("delete-event", self.on_window_delete)
    
    def _load_buttons(self):
        """Lädt die gespeicherten Buttons oder erstellt neue"""
        saved_buttons = self.config.get('buttons', [])
        
        # Lade die gespeicherten Buttons
        if saved_buttons:
            self._load_saved_buttons(saved_buttons)
        
        # Erstelle und füge den Add-Button am Ende hinzu
        self.add_button = SoundButton(position=len(self.buttons), config=self.config, is_add_button=True)
        self.add_button.set_add_click_handler(self.add_new_button)
        self.flowbox.add(self.add_button)
        self.flowbox.show_all()
    
    def _load_saved_buttons(self, saved_buttons):
        """Lädt die gespeicherten Buttons in die FlowBox"""
        # Sortiere die gespeicherten Buttons nach Position
        sorted_buttons = sorted(saved_buttons, key=lambda x: x['position'])
        
        for saved_button in sorted_buttons:
            position = saved_button['position']
            button = SoundButton(position=position, offset_x=0, offset_y=0, 
                               config=self.config, on_delete=self.delete_button)
            self.flowbox.add(button)
            self.buttons.append(button)
            button.show_all()
        
        # Invalidiere die Sortierung nach dem Laden aller Buttons
        self.flowbox.invalidate_sort()
    
    def save_config(self):
        """Speichert die Konfiguration in eine Datei"""
        # Aktualisiere die Button-Konfigurationen im Config-Dictionary
        saved_buttons = []
        
        for button in self.buttons:
            if not button.is_add_button:
                saved_buttons.append(button.button_config)
        
        self.config['buttons'] = saved_buttons
        
        # Speichern
        with open('config.json', 'w') as config_file:
            json.dump(self.config, config_file, indent=4)
        
        print("Konfiguration gespeichert!")
    
    def load_config(self):
        """Lädt die Konfiguration aus einer Datei oder verwendet die Standard-Konfiguration"""
        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                print("Konfiguration geladen!")
                
                # Überprüfe, ob alle erforderlichen Schlüssel vorhanden sind
                self.validate_config(config)
                
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            print("Keine gültige Konfigurationsdatei gefunden, verwende Standardkonfiguration!")
            return self.DEFAULT_CONFIG.copy()
    
    def validate_config(self, config):
        """Überprüft, ob alle erforderlichen Schlüssel vorhanden sind, und fügt fehlende hinzu"""
        for section, settings in self.DEFAULT_CONFIG.items():
            if section not in config:
                config[section] = settings
            elif isinstance(settings, dict):
                for key, value in settings.items():
                    if key not in config[section]:
                        config[section][key] = value
    
    def add_new_button(self, add_button):
        """Fügt einen neuen Button hinzu"""
        # Position des neuen Buttons bestimmen
        new_position = len(self.buttons)
        
        # Neuen Button erstellen
        new_button = SoundButton(position=new_position, offset_x=0, offset_y=0, 
                              config=self.config, on_delete=self.delete_button)
        
        # Button zur Flowbox und zur Button-Liste hinzufügen
        self.flowbox.add(new_button)
        self.buttons.append(new_button)
        
        # Sortierung aktualisieren
        self.flowbox.invalidate_sort()
        self.flowbox.show_all()
        
        # Config speichern
        self.save_config()
    
    def delete_button(self, position):
        """Löscht einen Button"""
        # Finde den Button anhand der Position
        button_to_remove = None
        for button in self.buttons:
            if button.position == position:
                button_to_remove = button
                break
        
        if button_to_remove:
            # Aus der FlowBox entfernen
            flowbox_child = button_to_remove.get_parent()
            self.flowbox.remove(flowbox_child)
            
            # Aus der Button-Liste entfernen
            self.buttons.remove(button_to_remove)
            
            # Positionen aktualisieren
            self._update_button_positions()
            
            # FlowBox aktualisieren
            self.flowbox.invalidate_sort()
            self.flowbox.show_all()
            
            # Config speichern
            self.save_config()
            
            print(f"Button an Position {position} gelöscht")
    
    def _update_button_positions(self):
        """Aktualisiert die Positionsangaben aller Buttons"""
        for i, button in enumerate(self.buttons):
            button.position = i
            button.button_config['position'] = i
    
    def on_destroy(self, widget):
        """Handler für das Schließen des Fensters"""
        self.save_config()
        Gtk.main_quit()
    
    def on_key_press(self, widget, event):
        """Handler für Tastatureingaben"""
        keyval = event.keyval
        keyname = Gdk.keyval_name(keyval)
        
        # Escape-Taste: Fenster schließen
        if keyname == 'Escape':
            self.save_config()
            self.destroy()
            return True
        
        return False
    
    def on_window_delete(self, widget, event):
        """Handler für das Schließen des Fensters per Kreuz"""
        self.save_config()
        return False  # False, damit das Fenster zerstört wird
    
    def on_window_configure(self, widget, event):
        """Handler für Größenänderungen des Fensters"""
        self.config['window']['width'] = event.width
        self.config['window']['height'] = event.height
        return False  # Weitergabe an andere Handler

def main():
    """Main-Funktion"""
    win = SoundboardWindow()
    Gtk.main()

if __name__ == "__main__":
    main()