#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import json
from soundbutton import SoundButton
import pygame
import os
from global_settings_dialog import GlobalSettingsDialog

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
        
        # Variablen für die Langklick-Erkennung
        self.press_timeout_id = None
        self.LONG_PRESS_TIME = 500  # 500ms = 0.5 Sekunden
        self.press_start_time = 0
        
        # Dialog-Status, um mehrfaches Öffnen zu verhindern
        self.global_settings_dialog_open = False
        
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
        
        # FlowBox konfigurieren für automatische Anordnung
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
        
        # Event für Klicks auf den Hintergrund der FlowBox
        event_box = Gtk.EventBox()
        event_box.add(self.flowbox)
        event_box.connect("button-press-event", self.on_background_click)
        
        main_box.pack_start(event_box, True, True, 0)
        
        # Add-Button wird erst später in _load_buttons hinzugefügt
        self.add_button = None
    
    def _connect_signals(self):
        """Verbindet die Signal-Handler"""
        self.connect("destroy", self.on_destroy)
        self.connect("configure-event", self.on_window_configure)
        self.connect("key-press-event", self.on_key_press)
        self.connect("delete-event", self.on_window_delete)
        self.connect("button-press-event", self.on_background_click)  # Für Klicks auf Fensterhintergrund
    
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
            button = SoundButton(position=position, 
                               offset_x=0, 
                               offset_y=0, 
                               config=self.config, 
                               on_delete=self.delete_button)
            
            # Füge den Button zur FlowBox hinzu (normale Anordnung)
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
        """Fügt einen neuen Button hinzu, indem der Add-Button in einen regulären Button umgewandelt wird"""
        # Position des neuen Buttons bestimmen
        new_position = len(self.buttons)
        
        # Stelle sicher, dass es sich um einen Add-Button handelt
        if not add_button.is_add_button:
            print("Warnung: Der geklickte Button ist kein Add-Button")
            return
        
        # Konvertiere den Add-Button in einen regulären Button
        # Entferne ihn aus der FlowBox, damit wir ihn ändern können
        add_button_parent = add_button.get_parent()
        if add_button_parent:
            self.flowbox.remove(add_button_parent)
        
        # Erstelle einen neuen regulären Button an der gleichen Position
        new_button = SoundButton(position=new_position, offset_x=0, offset_y=0, 
                              config=self.config, on_delete=self.delete_button)
        
        # Füge den neuen Button zur FlowBox und zur Button-Liste hinzu
        self.flowbox.add(new_button)
        self.buttons.append(new_button)
        
        # Erstelle einen neuen Add-Button
        self.add_button = SoundButton(position=len(self.buttons), config=self.config, is_add_button=True)
        self.add_button.set_add_click_handler(self.add_new_button)
        self.flowbox.add(self.add_button)
        
        # Sortierung aktualisieren
        self.flowbox.invalidate_sort()
        self.flowbox.show_all()
        
        # Config speichern - diese Aktion sollte gespeichert werden, 
        # da sonst der neue Button beim Neustart verloren geht
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
            
            # Config speichern - diese Aktion sollte gespeichert werden,
            # da sonst der gelöschte Button beim Neustart wieder erscheint
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
        
        # Prüft, ob die Strg-Taste gedrückt ist
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        
        # Escape-Taste: Fenster schließen
        if keyname == 'Escape':
            self.save_config()
            self.destroy()
            return True
        
        # Strg+S: Konfiguration speichern
        if ctrl and keyname == 's':
            self.save_config()
            print("Konfiguration manuell gespeichert!")
            return True
            
        return False
    
    def on_window_delete(self, widget, event):
        """Handler für das Schließen des Fensters per Kreuz"""
        self.save_config()
        return False  # False, damit das Fenster zerstört wird
    
    def on_window_configure(self, widget, event):
        """Handler für Größenänderungen des Fensters"""
        # Prüfe, ob sich die Größe tatsächlich geändert hat
        if (self.config['window']['width'] != event.width or
            self.config['window']['height'] != event.height):
            self.config['window']['width'] = event.width
            self.config['window']['height'] = event.height
            # Speichere die Konfiguration NICHT mehr bei jeder Größenänderung
            # self.save_config()
        return False  # Weitergabe an andere Handler
    
    def on_background_click(self, widget, event):
        """Handler für Klicks auf den Hintergrund des Fensters"""
        # Für Rechtsklicks sofort reagieren
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # Rechtsklick auf den Hintergrund - nur wenn kein Dialog bereits offen ist
            if not self.global_settings_dialog_open:
                self.show_global_settings()
            return True
        
        # Für Langklicks mit der linken Maustaste (button 1)
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            # Speichere Startzeit und starte Timer
            self.press_start_time = event.time  # Verwende die Eventzeit
            
            # Timer für Langklick starten, nur wenn kein Dialog bereits offen ist
            if not self.global_settings_dialog_open and not self.press_timeout_id:
                self.press_timeout_id = GLib.timeout_add(self.LONG_PRESS_TIME, 
                                                     self.check_long_press)
            
            # Hier nicht True zurückgeben, damit normale Klicks weiterhin funktionieren
        
        # Button-Release-Event abfangen
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 1:
            # Timer löschen, wenn Button losgelassen wird bevor Langklick erkannt wurde
            if self.press_timeout_id:
                GLib.source_remove(self.press_timeout_id)
                self.press_timeout_id = None
        
        return False  # Event weitergeben
    
    def check_long_press(self):
        """Prüft, ob ein Langklick erkannt wurde"""
        # Verwende die aktuelle Zeit aus dem Gtk-System
        current_time = Gtk.get_current_event_time()
        
        if current_time == 0:  # Kein aktuelles Event verfügbar
            # Benutze die monotonische Uhr, aber konvertiert zu Millisekunden
            current_time = GLib.get_monotonic_time() // 1000
        
        # Berechne die vergangene Zeit in Millisekunden
        elapsed = current_time - self.press_start_time
        
        print(f"Langklick-Prüfung: {elapsed}ms vergangen (Ziel: {self.LONG_PRESS_TIME}ms)")
        
        if elapsed >= self.LONG_PRESS_TIME:
            # Langklick erkannt, Einstellungsdialog anzeigen
            print("Langklick erkannt!")
            if not self.global_settings_dialog_open:
                self.show_global_settings()
            
            self.press_timeout_id = None
            return False  # Timer nicht wiederholen
        
        # Timer fortsetzen
        return True
    
    def show_global_settings(self):
        """Zeigt den globalen Einstellungs-Dialog an"""
        if self.global_settings_dialog_open:
            print("Global-Settings-Dialog ist bereits geöffnet!")
            return
            
        print("Öffne Global-Settings-Dialog...")
        self.global_settings_dialog_open = True
        
        dialog = GlobalSettingsDialog(self, self.config)
        response = dialog.show()
        
        # Dialog ist jetzt geschlossen
        self.global_settings_dialog_open = False
        
        if response == Gtk.ResponseType.OK:
            print("Globale Einstellungen wurden geändert - wende Änderungen an...")
            
            # Speichern Sie die Konfiguration
            self.save_config()
            
            # Stellen Sie sicher, dass die Standardwerte für die Farbeinstellungen vorhanden sind
            if 'use_global_bg_color' not in self.config['soundbutton']:
                self.config['soundbutton']['use_global_bg_color'] = True
            if 'use_global_text_color' not in self.config['soundbutton']:
                self.config['soundbutton']['use_global_text_color'] = True
            
            # Aktualisieren Sie die FlowBox-Abstände
            sb_config = self.config['soundbutton']
            self.flowbox.set_row_spacing(sb_config['spacing'])
            self.flowbox.set_column_spacing(sb_config['spacing'])
            self.flowbox.set_margin_start(sb_config['spacing'])
            self.flowbox.set_margin_end(sb_config['spacing'])
            self.flowbox.set_margin_top(sb_config['spacing'])
            self.flowbox.set_margin_bottom(sb_config['spacing'])
            
            # Aktualisieren Sie alle Buttons, um die neuen globalen Einstellungen anzuwenden
            self.update_all_buttons()
            
            # Aktualisiere die gesamte UI, um sicherzustellen, dass alle Änderungen sichtbar sind
            self.queue_draw()
            self.flowbox.queue_draw()
            
            print("Globale Einstellungen wurden erfolgreich angewendet!")
    
    def update_all_buttons(self):
        """Aktualisiert alle Buttons mit den globalen Einstellungen durch vollständige Neuinstanziierung"""
        print("Aktualisiere alle Buttons mit globalen Einstellungen durch vollständige Neuinstanziierung...")
        
        # Zuerst die Buttons-Liste speichern und leeren
        old_buttons = self.buttons.copy()
        self.buttons = []
        
        # Alle bestehenden Buttons aus der FlowBox entfernen
        for child in list(self.flowbox.get_children()):
            self.flowbox.remove(child)
        
        # Alle Buttons neu erstellen, aber nicht den Add-Button
        for old_button in old_buttons:
            # Position und Konfiguration des alten Buttons übernehmen
            position = old_button.position
            config = old_button.button_config
            
            # Neuen Button mit gleicher Position und Konfiguration erstellen
            new_button = SoundButton(
                position=position,
                offset_x=0,
                offset_y=0,
                config=self.config,
                on_delete=self.delete_button
            )
            
            # Individuelle Konfiguration übernehmen
            new_button.button_config = config
            
            # Zur FlowBox hinzufügen
            self.flowbox.add(new_button)
            self.buttons.append(new_button)
            new_button.show_all()
            
            print(f"Button {position} neu erstellt")
        
        # Add-Button neu erstellen
        self.add_button = SoundButton(position=len(self.buttons), config=self.config, is_add_button=True)
        self.add_button.set_add_click_handler(self.add_new_button)
        self.flowbox.add(self.add_button)
        self.add_button.show_all()
        
        # Aktualisiere die FlowBox
        self.flowbox.invalidate_sort()
        self.flowbox.queue_resize()
        self.flowbox.queue_draw()
        self.flowbox.show_all()
        
        # Das gesamte Fenster aktualisieren
        self.queue_draw()
        
        print("Button-Neuinstanziierung abgeschlossen")

def main():
    """Main-Funktion"""
    win = SoundboardWindow()
    Gtk.main()

if __name__ == "__main__":
    main()