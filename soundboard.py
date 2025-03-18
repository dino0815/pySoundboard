#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import json
from soundbutton import SoundButton, AddButton
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
        # Rahmen für äußere Abstände
        self.flowbox.set_margin_start(sb_config['margin'])
        self.flowbox.set_margin_end(sb_config['margin'])
        self.flowbox.set_margin_top(sb_config['margin'])
        self.flowbox.set_margin_bottom(sb_config['margin'])
        
        main_box.pack_start(self.flowbox, True, True, 0)
        
        # Add-Button wird später in _load_buttons hinzugefügt
        self.add_button = None

    def _connect_signals(self):
        """Verbindet die Signal-Handler"""
        self.connect("destroy", self.on_destroy)
        self.connect("configure-event", self.on_window_configure)
        self.connect("key-press-event", self.on_key_press)
        self.connect("delete-event", self.on_window_delete)
    
    def _load_buttons(self):
        """Lädt die gespeicherten Buttons oder erstellt neue"""
        # Erstelle zuerst den Add-Button
        self.add_button = AddButton(self.add_new_button, config=self.config)
        
        saved_buttons = self.config.get('buttons', [])
        if saved_buttons:
            self._load_saved_buttons(saved_buttons)
        else:
            self._create_initial_buttons()
        
        # Add-Button am Ende hinzufügen
        self.flowbox.add(self.add_button)
        self.flowbox.show_all()
    
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
        # Erstelle den neuen Button
        position = len(self.buttons)
        button = SoundButton(position=position, offset_x=0, offset_y=0, config=self.config, on_delete=self.delete_button)
        self.buttons.append(button)
        
        # Entferne alle Kinder aus der FlowBox und speichere sie temporär
        children_widgets = []
        for child in self.flowbox.get_children():
            widget = child.get_child()  # Hole das eigentliche Widget aus dem FlowBoxChild
            if widget:
                # Entferne die Referenz vom Parent
                child.remove(widget)
                if widget != self.add_button:  # Speichere nur die normalen Buttons
                    children_widgets.append(widget)
            self.flowbox.remove(child)
        
        # Füge alle normalen Buttons wieder hinzu
        for btn in children_widgets:
            btn.show_all()
            self.flowbox.add(btn)
        
        # Füge den neuen Button hinzu
        button.show_all()
        self.flowbox.add(button)
        
        # Füge den Add-Button am Ende hinzu
        if self.add_button:
            self.add_button.show_all()
            self.flowbox.add(self.add_button)
        
        # Zeige die FlowBox und alle ihre Kinder
        self.flowbox.show_all()
        
        print(f"Neuer SoundButton hinzugefügt. Position: {position + 1}, Gesamtanzahl: {len(self.buttons)}")
        
        # Stelle sicher, dass das Layout aktualisiert wird
        self.flowbox.queue_resize()
    
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
        
        # Entferne alle Kinder aus der FlowBox und speichere sie temporär
        children_widgets = []
        for child in self.flowbox.get_children():
            widget = child.get_child()  # Hole das eigentliche Widget aus dem FlowBoxChild
            if widget and widget != button:  # Ignoriere den zu löschenden Button
                # Entferne die Referenz vom Parent
                child.remove(widget)
                if widget != self.add_button:  # Speichere nur die normalen Buttons
                    children_widgets.append(widget)
            self.flowbox.remove(child)
        
        # Füge alle normalen Buttons wieder hinzu
        for btn in children_widgets:
            btn.show_all()
            self.flowbox.add(btn)
        
        # Füge den Add-Button am Ende hinzu
        if self.add_button:
            self.add_button.show_all()
            self.flowbox.add(self.add_button)
        
        # Stelle sicher, dass das Widget zerstört wird
        button.destroy()
        
        # Zeige die FlowBox und alle ihre Kinder
        self.flowbox.show_all()
        
        # Stelle sicher, dass das Layout aktualisiert wird
        self.flowbox.queue_resize()

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
        # Lasse das Fenster sich natürlich an den Inhalt anpassen
        return False
    
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