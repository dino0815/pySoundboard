#!/usr/bin/env python3
from global_settings_dialog import GlobalSettingsDialog
from gi.repository import Gtk, Gdk, GLib
from soundbutton import SoundButton
import argparse
import pygame
import json
import os
import gi
gi.require_version('Gtk', '3.0')

class SoundboardWindow(Gtk.Window):
    # Konstanten für die Konfiguration
    DEFAULT_CONFIG = {
        "window": {
            "width": 163,
            "height": 95,
            "title": "Soundboard"
            "rootpfad: ."
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
    
    def __init__(self, config_file='config.json'):
        super().__init__(title="Soundboard")
        self.config_file = config_file
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
        """Lädt die Buttons aus der Konfiguration oder aktualisiert bestehende Buttons"""
        try:
            # Sortiere die Button-Konfigurationen nach Position
            sorted_buttons = sorted(self.config['buttons'], key=lambda x: x.get('position', 0))
            
            # Erstelle eine Kopie der Button-Liste, ohne Add-Button
            normal_buttons = [b for b in self.buttons if not hasattr(b, 'is_add_button') or not b.is_add_button]
            
            # Prüfe, ob wir Buttons aktualisieren oder neu erstellen müssen
            if len(normal_buttons) == len(sorted_buttons):
                # Buttons existieren bereits, aktualisiere nur ihre Eigenschaften
                for i, button_config in enumerate(sorted_buttons):
                    if i < len(normal_buttons):  # Sicherheitscheck
                        button = normal_buttons[i]
                        button.position = button_config.get('position', i)
                        button.offset_x = button_config.get('offset_x', 0)
                        button.offset_y = button_config.get('offset_y', 0)
                        button.button_config = button_config
                        if hasattr(button, '_update_button_after_settings'):
                            button._update_button_after_settings()
            else:
                # Anzahl der Buttons hat sich geändert, entferne alle und erstelle sie neu
                # Sichere das Entfernen aller vorhandenen Buttons
                for button in list(self.buttons):  # Kopie der Liste verwenden
                    if button and hasattr(button, 'get_parent'):
                        button_parent = button.get_parent()
                        if button_parent:
                            try:
                                self.flowbox.remove(button_parent)
                            except Exception as e:
                                print(f"Fehler beim Entfernen des Buttons: {e}")
                
                # Leere die Button-Liste
                self.buttons = []
                
                # Erstelle die Buttons neu
                for button_config in sorted_buttons:
                    try:
                        button = SoundButton(
                            position=button_config.get('position', 0),
                            offset_x=button_config.get('offset_x', 0),
                            offset_y=button_config.get('offset_y', 0),
                            config=self.config,
                            on_delete=self.delete_button
                        )
                        self.buttons.append(button)
                        self.flowbox.add(button)
                    except Exception as e:
                        print(f"Fehler beim Erstellen des Buttons: {e}")
            
            # Sichere Verarbeitung des Add-Buttons
            # Entferne alle existierenden Add-Buttons
            add_buttons = [b for b in self.buttons if hasattr(b, 'is_add_button') and b.is_add_button]
            for add_button in add_buttons:
                if add_button in self.buttons:
                    self.buttons.remove(add_button)
                if hasattr(add_button, 'get_parent'):
                    add_button_parent = add_button.get_parent()
                    if add_button_parent:
                        try:
                            self.flowbox.remove(add_button_parent)
                        except Exception as e:
                            print(f"Fehler beim Entfernen des Add-Buttons: {e}")
            
            # Erstelle einen neuen Add-Button
            try:
                self.add_button = SoundButton(
                    position=len(self.buttons),
                    offset_x=0,
                    offset_y=0,
                    config=self.config,
                    is_add_button=True
                )
                self.add_button.button.connect("button-press-event", self.on_add_button_clicked)
                self.add_button.set_add_click_handler(self.add_new_button)
                self.buttons.append(self.add_button)
                self.flowbox.add(self.add_button)
            except Exception as e:
                print(f"Fehler beim Erstellen des Add-Buttons: {e}")
            
            # Zeige alle Buttons an
            self.flowbox.show_all()
            
        except Exception as e:
            print(f"Fehler in _load_buttons: {e}")
            import traceback
            traceback.print_exc()
    
    def _reorder_buttons(self):
        """Ordnet die Buttons neu, indem die Konfiguration umsortiert und die Buttons aktualisiert werden"""
        try:
            # Sortiere die Button-Konfigurationen nach Position
            self.config['buttons'].sort(key=lambda x: x.get('position', 0))
            
            # Die Positionen in der Konfiguration bereinigen - falls doppelte oder lückenhafte Positionen existieren
            for i, button_config in enumerate(self.config['buttons']):
                # Sicherstellen, dass jede Position nur einmal vorkommt
                if button_config.get('position') != i:
                    print(f"Korrigiere Position von Button {button_config.get('text', 'Unbenannt')}: {button_config.get('position')} -> {i}")
                    button_config['position'] = i
            
            # Lade alle Buttons neu, aber NICHT die Positionen neu zuweisen
            self._load_buttons()
        except Exception as e:
            print(f"Fehler in _reorder_buttons: {e}")
            import traceback
            traceback.print_exc()
    
    def update_all_buttons(self):
        """Aktualisiert alle Buttons mit den neuen globalen Einstellungen"""
        for button in self.buttons:
            if not button.is_add_button:
                button._update_button_after_settings()
        
        # Ordne die Buttons neu
        self._reorder_buttons()
    
    def save_config(self, config_file):
        """Speichert die Konfiguration in eine Datei"""
        # Aktualisiere die Button-Konfigurationen im Config-Dictionary
        saved_buttons = []
        
        for button in self.buttons:
            if not button.is_add_button:
                saved_buttons.append(button.button_config)
        
        self.config['buttons'] = saved_buttons
        
        # Speichern
        with open(config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)
        
        print("Konfiguration gespeichert!")
    
    def load_config(self):
        """Lädt die Konfiguration aus einer Datei oder verwendet die Standard-Konfiguration"""
        try:
            with open(self.config_file, 'r') as config_file:
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
        try:
            # Stelle sicher, dass es sich um einen Add-Button handelt
            if not hasattr(add_button, 'is_add_button') or not add_button.is_add_button:
                print("Warnung: Der geklickte Button ist kein Add-Button")
                return
            
            # Position des neuen Buttons bestimmen
            new_position = len(self.config['buttons'])
            
            # Erstelle eine neue Button-Konfiguration
            new_button_config = {
                'position': new_position,
                'text': f"Button {new_position + 1}",
                'audio_file': "",
                'image_file': "",
                'loop': False
            }
            
            # Füge die neue Konfiguration zur Config hinzu
            self.config['buttons'].append(new_button_config)
            
            # Erstelle einen neuen regulären Button
            new_button = SoundButton(
                position=new_position, 
                offset_x=0, 
                offset_y=0, 
                config=self.config, 
                on_delete=self.delete_button
            )
            
            # Füge den neuen Button zur FlowBox und zur Button-Liste hinzu, bevor der Add-Button
            self.flowbox.add(new_button)
            self.buttons.insert(-1, new_button)  # Einfügen vor dem letzten Element (Add-Button)
            
            # Zeige den neuen Button an
            new_button.show_all()
            
            # Config speichern - diese Aktion sollte gespeichert werden, 
            # da sonst der neue Button beim Neustart verloren geht
            self.save_config(self.config_file)
            
            # Neu ordnen, um sicherzustellen, dass alles aktualisiert wird
            self._reorder_buttons()
        except Exception as e:
            print(f"Fehler beim Hinzufügen eines neuen Buttons: {e}")
            import traceback
            traceback.print_exc()
    
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
            self.save_config(self.config_file)
            
            print(f"Button an Position {position} gelöscht")
    
    def _update_button_positions(self):
        """Aktualisiert die Positionsangaben aller Buttons"""
        for i, button in enumerate(self.buttons):
            button.position = i
            button.button_config['position'] = i
    
    def on_destroy(self, widget):
        """Handler für das Schließen des Fensters"""
        self.save_config(self.config_file)
        Gtk.main_quit()
    
    def on_key_press(self, widget, event):
        """Handler für Tastatureingaben"""
        keyval = event.keyval
        keyname = Gdk.keyval_name(keyval)
        
        # Prüft, ob die Strg-Taste gedrückt ist
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        
        # Escape-Taste: Fenster schließen
        if keyname == 'Escape':
            self.save_config(self.config_file)
            self.destroy()
            return True
        
        # Strg+S: Konfiguration speichern
        if ctrl and keyname == 's':
            self.save_config(self.config_file)
            print("Konfiguration manuell gespeichert!")
            return True
            
        return False
    
    def on_window_delete(self, widget, event):
        """Handler für das Schließen des Fensters per Kreuz"""
        self.save_config(self.config_file)
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
            # Langklick erkannt, Einstellungsdialog anzeigenhallo, können wir beim abspielen der audiofiles ein kurzes ein- und ausblenden einbauen
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
            self.save_config(self.config_file)
            
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
    
    def on_add_button_clicked(self, button, event):
        """Handler für das Klicken des Add-Buttons"""
        try:
            if event.button == 1:  # Nur auf linke Maustaste reagieren
                # Finde den SoundButton-Objekt in der Buttons-Liste
                for sound_button in self.buttons:
                    if sound_button.is_add_button and sound_button.button == button:
                        self.add_new_button(sound_button)
                        return
                print("Warnung: Add-Button konnte nicht gefunden werden")
        except Exception as e:
            print(f"Fehler im Add-Button-Handler: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main-Funktion"""
    # Argument-Parser erstellen
    parser = argparse.ArgumentParser(description='pySoundboard - Ein Soundboard für eine GTK3 Umgebung')
    parser.add_argument('--config', '-c', 
                       help='Pfad zur Konfigurationsdatei (Standard: config.json)',
                       default='config.json')
    
    # Argumente parsen
    args = parser.parse_args()
    
    # Soundboard mit der angegebenen Konfigurationsdatei starten
    win = SoundboardWindow(config_file=args.config)
    Gtk.main()

if __name__ == "__main__":
    main()