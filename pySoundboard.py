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
    ###################################################################################################################################
    # Konstanten für die Konfiguration
    DEFAULT_CONFIG = {
        "window": {
            "title": "Soundboard",
            "width":  200,
            "height": 100,
            "soundpfad_prefix": ".",
            "imagepfad_prefix": "."
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
    

    ###################################################################################################################################
    def _show_config_dialog(self, config_file):
        """Zeigt einen Dialog an, wenn die Konfigurationsdatei nicht gefunden wurde"""
        dialog = Gtk.Dialog(
            title="Konfigurationsdatei nicht gefunden",
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL
        )
        
        # Dialog-Inhalt
        content_area = dialog.get_content_area()
        message = Gtk.Label( label=f"Die Konfigurationsdatei: {config_file} konnte nicht gefunden werden.\nSoll die Datei erstellt werden?" )
        message.set_line_wrap(True)
        message.set_margin_start(20)
        message.set_margin_end(20)
        message.set_margin_top(20)
        message.set_margin_bottom(20)
        content_area.pack_start(message, True, True, 0)
        
        # Buttons
        dialog.add_buttons(
            "Programm Beenden", Gtk.ResponseType.CLOSE,
            "Datei Erstellen", Gtk.ResponseType.ACCEPT
        )

        # Dialog anzeigen und auf Antwort warten
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()        
        return response == Gtk.ResponseType.ACCEPT
        
    ###################################################################################################################################
    def __init__(self, config_file='config.json'):
        super().__init__(title="Soundboard")       # Titel des Fensters

        self.config_file = config_file             # Pfad zur Konfigurationsdatei
        self.buttons = []                          # Liste der SoundButtons
        self.config = self.load_config()           # Konfiguration aus der Datei laden
        self._setup_window()                       # Fenster-Eigenschaften initialisieren
        self._setup_ui()                           # UI-Elemente erstellen
        self._load_buttons()                       # Buttons aus der Konfiguration laden
        self._connect_signals()                    # Signale verbinden
        
        # Variablen für die Langklick-Erkennung
        self.press_timeout_id = None               # ID des Timers für Langklick-Erkennung
        self.LONG_PRESS_TIME = 500                 # 500ms = 0.5 Sekunden
        self.press_start_time = 0                  # Zeitpunkt des Langklick-Starts
        
        # Dialog-Status, um mehrfaches Öffnen zu verhindern
        self.global_settings_dialog_open = False   # Status des Global-Settings-Dialogs        
        self.show_all()                            # Zeige alle Widgets an
        self.add_button = None                     # Referenz für den Add-Button
    
    ###################################################################################################################################
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
                    
    ###################################################################################################################################
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
                
        # Feste Abstände zwischen den Buttons
        button_config = self.config['soundbutton']

        # FlowBox konfigurieren für automatische Anordnung
        self.flowbox = Gtk.FlowBox()                            # FlowBox erstellen
        self.flowbox.set_valign(Gtk.Align.START)                # Vertikale Ausrichtung am Anfang
        self.flowbox.set_halign(Gtk.Align.START)                # Horizontale Ausrichtung am Anfang
        self.flowbox.set_hexpand(True)                          # Ausdehnung in horizontaler Richtung
        self.flowbox.set_homogeneous(True)                      # Gleichmäßige Größe der Buttons
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE) # Keine Auswahl möglich
        self.flowbox.set_min_children_per_line(1)               # Mindestens 1 Button pro Zeile
        self.flowbox.set_max_children_per_line(20)              # Höchstens 20 Buttons pro Zeile
        self.flowbox.set_row_spacing(button_config['spacing'])      # Abstand zwischen den Zeilen
        self.flowbox.set_column_spacing(button_config['spacing'])   # Abstand zwischen den Spalten
        self.flowbox.set_margin_start(button_config['spacing'])     # Abstand zum linken Rand
        self.flowbox.set_margin_end(button_config['spacing'])       # Abstand zum rechten Rand
        self.flowbox.set_margin_top(button_config['spacing'])       # Abstand zum oberen Rand
        self.flowbox.set_margin_bottom(button_config['spacing'])    # Abstand zum unteren Rand
        
        # Event für Klicks auf den Hintergrund der FlowBox
        event_box = Gtk.EventBox()                              # EventBox erstellen
        event_box.add(self.flowbox)                             # FlowBox zum EventBox hinzufügen
        event_box.connect("button-press-event", self.on_background_click) # Signalhandler für Klicks auf den Hintergrund        
        main_box.pack_start(event_box, True, True, 0)           # EventBox in die Hauptbox packen
        
        # Add-Button wird erst später in _load_buttons hinzugefügt
        self.add_button = None                                  # Referenz für den Add-Button
    
    ###################################################################################################################################
    def _connect_signals(self):
        """Verbindet die Signal-Handler"""
        self.connect("destroy", self.on_destroy)                     # Signalhandler für das Schließen des Fensters
        self.connect("configure-event", self.on_window_configure)    # Signalhandler für Größenänderungen des Fensters
        self.connect("key-press-event", self.on_key_press)           # Signalhandler für Tastatureingaben
        self.connect("delete-event", self.on_window_delete)          # Signalhandler für das Schließen des Fensters per Kreuz
        self.connect("button-press-event", self.on_background_click) # Für Klicks auf Fensterhintergrund
    
    ###################################################################################################################################
    def _load_buttons(self):
        """Lädt die Buttons aus der Konfiguration oder aktualisiert bestehende Buttons"""
        try:
            # Sortiere die Button-Konfigurationen nach Position
            sorted_buttons = sorted(self.config['buttons'], key=lambda x: x.get('position', 0))
            
            # Erstelle eine Kopie der Button-Liste, ohne Add-Button
            normal_buttons = [b for b in self.buttons if not hasattr(b, 'is_add_button') or not b.is_add_button]
            
            # Prüfe, ob wir Buttons aktualisieren oder neu erstellen müssen
            if  len(normal_buttons) == len(sorted_buttons):
                # Buttons existieren bereits, aktualisiere nur ihre Eigenschaften
                for i, button_config in enumerate(sorted_buttons):
                    if i < len(normal_buttons):     # Sicherheitscheck
                        button = normal_buttons[i]  # Button aus der Liste nehmen
                        button.position = button_config.get('position', i)    # Position setzen
                        button.button_config = button_config                  # Button-Konfiguration setzen
                        if  hasattr(button, '_update_button_after_settings'): # Wenn der Button eine Update-Methode hat, dann aufrufen
                            button._update_button_after_settings() 
            else:
                # Anzahl der Buttons hat sich geändert, entferne alle und erstelle sie neu
                # Sichere das Entfernen aller vorhandenen Buttons
                for button in list(self.buttons):  # Kopie der Liste verwenden
                    if  button and hasattr(button, 'get_parent'):
                        button_parent = button.get_parent()  # Elternelement des Buttons nehmen
                        if  button_parent:
                            try:
                                self.flowbox.remove(button_parent)  # Elternelement aus der FlowBox entfernen
                            except Exception as e:
                                print(f"Fehler beim Entfernen des Buttons: {e}")  # Fehler ausgeben
                
                # Leere die Button-Liste
                self.buttons = []  # Liste der Buttons leeren
                
                # Erstelle die Buttons neu
                for button_config in sorted_buttons:  # Für jede Button-Konfiguration
                    try:
                        button = SoundButton(
                            position=button_config.get('position', 0),  # Position setzen
                            config=self.config,                         # Konfiguration setzen
                            on_delete=self.delete_button                # Lösch-Handler setzen
                        )
                        self.buttons.append(button)                     # Button zur Liste hinzufügen
                        self.flowbox.add(button)                        # Button zur FlowBox hinzufügen
                    except Exception as e:
                        print(f"Fehler beim Erstellen des Buttons: {e}")# Fehler ausgeben
            
            # Sichere Verarbeitung des Add-Buttons
            # Entferne alle existierenden Add-Buttons
            add_buttons = [b for b in self.buttons if hasattr(b, 'is_add_button') and b.is_add_button]  # Add-Buttons aus der Liste nehmen
            for add_button in add_buttons:
                if add_button in self.buttons:
                    self.buttons.remove(add_button)                # Button aus der Liste entfernen
                if hasattr(add_button, 'get_parent'): 
                    add_button_parent = add_button.get_parent()    # Elternelement des Add-Buttons nehmen
                    if add_button_parent:
                        try:
                            self.flowbox.remove(add_button_parent) # Elternelement aus der FlowBox entfernen
                        except Exception as e:
                            print(f"Fehler beim Entfernen des Add-Buttons: {e}")  # Fehler ausgeben
            
            # Erstelle einen neuen Add-Button
            try:
                self.add_button = SoundButton( 
                    position=len(self.buttons),       # Position setzen
                    config=self.config,               # Konfiguration setzen
                    is_add_button=True                # Add-Button-Status setzen
                )
                self.add_button.button.connect("button-press-event", self.on_add_button_clicked)  # Signalhandler für Klicks auf den Add-Button
                self.add_button.set_add_click_handler(self.add_new_button)  # Add-Button-Handler setzen
                self.buttons.append(self.add_button)  # Add-Button zur Liste hinzufügen
                self.flowbox.add(self.add_button)     # Add-Button zur FlowBox hinzufügen
            except Exception as e:
                print(f"Fehler beim Erstellen des Add-Buttons: {e}")  # Fehler ausgeben
            
            # Zeige alle Buttons an
            self.flowbox.show_all()
            
        except Exception as e:
            print(f"Fehler in _load_buttons: {e}")    # Fehler ausgeben
            import traceback
            traceback.print_exc()                     # Traceback ausgeben
    
    ###################################################################################################################################
    def _reorder_buttons(self):
        """Ordnet die Buttons neu, indem die Konfiguration umsortiert und die Buttons aktualisiert werden"""
        try:
            # Sortiere die Button-Konfigurationen nach Position
            self.config['buttons'].sort(key=lambda x: x.get('position', 0))
            
            # Die Positionen in der Konfiguration bereinigen - falls doppelte oder lückenhafte Positionen existieren
            for i, button_config in enumerate(self.config['buttons']):
                # Sicherstellen, dass jede Position nur einmal vorkommt
                if  button_config.get('position') != i: 
                    print(f"Korrigiere Position von Button {button_config.get('text', 'Unbenannt')}: {button_config.get('position')} -> {i}")
                    button_config['position'] = i     # Position setzen
            
            # Lade alle Buttons neu, aber NICHT die Positionen neu zuweisen
            self._load_buttons()                      # Buttons neu laden
        except Exception as e:
            print(f"Fehler in _reorder_buttons: {e}") # Fehler ausgeben
            import traceback
            traceback.print_exc()                     # Traceback ausgeben
    
    ###################################################################################################################################
    def update_all_buttons(self):
        """Aktualisiert alle Buttons mit den neuen globalen Einstellungen"""
        for button in self.buttons:
            if not button.is_add_button:
                button._update_button_after_settings()  # Button aktualisieren
        
        # Ordne die Buttons neu
        self._reorder_buttons()
    
    ###################################################################################################################################
    def save_config(self, config_file):
        """Speichert die Konfiguration in eine Datei"""
        # Aktualisiere die Button-Konfigurationen im Config-Dictionary
        saved_buttons = []                           # Liste der gespeicherten Buttons
        
        for button in self.buttons:
            if not button.is_add_button:
                saved_buttons.append(button.button_config)  # Button-Konfiguration zur Liste hinzufügen
        
        self.config['buttons'] = saved_buttons       # Button-Konfigurationen im Config-Dictionary speichern
        
        # Speichern
        with open(config_file, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)  # Konfiguration in die Datei speichern
        
        print("Konfiguration gespeichert!")          # Nachricht ausgeben
    
    ###################################################################################################################################
    def load_config(self):
        """Lädt die Konfiguration aus einer Datei oder verwendet die Standard-Konfiguration"""
        try:
            with open(self.config_file, 'r') as config_file:
                config = json.load(config_file)      # Konfiguration aus der Datei laden
                print("Konfiguration geladen!")      # Nachricht ausgeben
                
                # Überprüfe, ob alle erforderlichen Schlüssel vorhanden sind
                self.validate_config(config)         # Konfiguration überprüfen
                
                return config  # Konfiguration zurückgeben
        except (FileNotFoundError, json.JSONDecodeError):
            print("Keine gültige Konfigurationsdatei gefunden, verwende Standardkonfiguration!")  # Nachricht ausgeben
            return self.DEFAULT_CONFIG.copy()        # Standardkonfiguration zurückgeben
    
    ###################################################################################################################################
    def validate_config(self, config):
        """Überprüft, ob alle erforderlichen Schlüssel vorhanden sind, und fügt fehlende hinzu"""
        for section, settings in self.DEFAULT_CONFIG.items():  # Für jede Sektion in der Standardkonfiguration
            if section not in config:
                config[section] = settings           # Sektion hinzufügen
            elif isinstance(settings, dict):         # Wenn die Sektion ein Dictionary ist
                for key, value in settings.items():  # Für jeden Schlüssel und Wert in der Sektion
                    if key not in config[section]:   # Wenn der Schlüssel nicht in der Sektion vorhanden ist
                        config[section][key] = value # Schlüssel und Wert hinzufügen
    
    ###################################################################################################################################
    def add_new_button(self, add_button):
        """Fügt einen neuen Button hinzu, indem der Add-Button in einen regulären Button umgewandelt wird"""
        try:
            # Stelle sicher, dass es sich um einen Add-Button handelt
            if not hasattr(add_button, 'is_add_button') or not add_button.is_add_button:
                print("Warnung: Der geklickte Button ist kein Add-Button")  # Nachricht ausgeben
                return  # Rückgabe, um unnötige weitere Verarbeitung zu vermeiden
            
            # Position des neuen Buttons bestimmen
            new_position = len(self.config['buttons']) # Position setzen
            
            # Erstelle eine neue Button-Konfiguration
            new_button_config = {
                'position': new_position,              # Position setzen
                'text': f"Button {new_position + 1}",  # Text setzen
                'audio_file': "",                      # Audio-Datei setzen
                'image_file': "",                      # Bild-Datei setzen
                'loop': False                          # Schleife setzen
            }
            
            # Füge die neue Konfiguration zur Config hinzu
            self.config['buttons'].append(new_button_config) # Neue Konfiguration zur Liste hinzufügen
            
            # Erstelle einen neuen regulären Button
            new_button = SoundButton(
                position=new_position,                       # Position setzen
                config=self.config,                          # Konfiguration setzen
                on_delete=self.delete_button                 # Lösch-Handler setzen
            )
            
            # Füge den neuen Button zur FlowBox und zur Button-Liste hinzu, bevor der Add-Button
            self.flowbox.add(new_button)                     # Neuer Button zur FlowBox hinzufügen
            self.buttons.insert(-1, new_button)              # Neuer Button zur Button-Liste hinzufügen
            new_button.show_all()                            # Neuer Button anzeigen
            
            # Config speichern - diese Aktion sollte gespeichert werden, 
            # da sonst der neue Button beim Neustart verloren geht
            self.save_config(self.config_file)               # Konfiguration speichern
            
            # Neu ordnen, um sicherzustellen, dass alles aktualisiert wird
            self._reorder_buttons()                          # Buttons neu ordnen
        except Exception as e:
            print(f"Fehler beim Hinzufügen eines neuen Buttons: {e}")  # Fehler ausgeben
            import traceback
            traceback.print_exc()                            # Traceback ausgeben 
    
    ###################################################################################################################################
    def delete_button(self, position):
        """Löscht einen Button"""
        # Finde den Button anhand der Position
        button_to_remove = None                              # Button-Referenz initialisieren
        for button in self.buttons:
            if button.position == position:                  # Wenn die Position des Buttons mit der angegebenen Position übereinstimmt
                button_to_remove = button                    # Button-Referenz setzen
                break
        
        if button_to_remove:
            # Aus der FlowBox entfernen
            flowbox_child = button_to_remove.get_parent()    # Elternelement des Buttons nehmen
            self.flowbox.remove(flowbox_child)               # Elternelement aus der FlowBox entfernen
            
            # Aus der Button-Liste entfernen
            self.buttons.remove(button_to_remove)            # Button aus der Liste entfernen
            self._update_button_positions()                  # Positionen aktualisieren
            self.flowbox.invalidate_sort()                   # FlowBox aktualisieren
            self.flowbox.show_all()                          # Alle Elemente anzeigen
            
            # Config speichern - diese Aktion sollte gespeichert werden,
            # da sonst der gelöschte Button beim Neustart wieder erscheint
            self.save_config(self.config_file)               # Konfiguration speichern
            
            print(f"Button an Position {position} gelöscht") # Nachricht ausgeben
    
    ###################################################################################################################################
    def _update_button_positions(self):
        """Aktualisiert die Positionsangaben aller Buttons"""
        for i, button in enumerate(self.buttons):
            button.position = i                              # Position setzen
            button.button_config['position'] = i             # Position setzen
    
    ###################################################################################################################################
    def on_destroy(self, widget):
        """Handler für das Schließen des Fensters"""
        self.save_config(self.config_file)                   # Konfiguration speichern
        Gtk.main_quit()                                      # Programm beenden
    
    ###################################################################################################################################
    def on_key_press(self, widget, event):
        """Handler für Tastatureingaben"""
        keyval = event.keyval                                # Tastaturwert nehmen
        keyname = Gdk.keyval_name(keyval)                    # Tastaturname nehmen
        
        # Prüft, ob die Strg-Taste gedrückt ist
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK) # Strg-Taste prüfen
        
        # Escape-Taste: Fenster schließen
        if keyname == 'Escape':
            self.save_config(self.config_file)               # Konfiguration speichern
            self.destroy()                                   # Fenster schließen
            return True                                      # True zurückgeben
        
        # Strg+S: Konfiguration speichern
        if ctrl and keyname == 's':
            self.save_config(self.config_file)               # Konfiguration speichern
            print("Konfiguration manuell gespeichert!")      # Nachricht ausgeben
            return True                                      # True zurückgeben            
        return False                                         # False zurückgeben
    
    ###################################################################################################################################
    def on_window_delete(self, widget, event):
        """Handler für das Schließen des Fensters per Kreuz"""
        self.save_config(self.config_file)                   # Konfiguration speichern
        return False                                         # False, damit das Fenster zerstört wird  
    
    ###################################################################################################################################
    def on_window_configure(self, widget, event):
        """Handler für Größenänderungen des Fensters"""
        # Prüfe, ob sich die Größe tatsächlich geändert hat
        if (self.config['window']['width'] != event.width or
            self.config['window']['height'] != event.height):
            self.config['window']['width'] = event.width          # Breite setzen
            self.config['window']['height'] = event.height        # Höhe setzen
        return False  # Weitergabe an andere Handler
    
    ###################################################################################################################################
    def on_background_click(self, widget, event):
        """Handler für Klicks auf den Hintergrund des Fensters"""
        # Für Rechtsklicks sofort reagieren
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3: 
            # Rechtsklick auf den Hintergrund - nur wenn kein Dialog bereits offen ist
            if not self.global_settings_dialog_open: 
                self.show_global_settings()                       # Dialog anzeigen
            return True                                           # True zurückgeben
        
        # Für Langklicks mit der linken Maustaste (button 1)
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            # Speichere Startzeit und starte Timer
            self.press_start_time = event.time                    # Verwende die Eventzeit
            
            # Timer für Langklick starten, nur wenn kein Dialog bereits offen ist
            if not self.global_settings_dialog_open and not self.press_timeout_id:
                self.press_timeout_id = GLib.timeout_add(self.LONG_PRESS_TIME, 
                                                     self.check_long_press)  # Timer starten
            
            # Hier nicht True zurückgeben, damit normale Klicks weiterhin funktionieren
        
        # Button-Release-Event abfangen
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 1:
            # Timer löschen, wenn Button losgelassen wird bevor Langklick erkannt wurde
            if self.press_timeout_id: 
                GLib.source_remove(self.press_timeout_id)         # Timer löschen
                self.press_timeout_id = None                      # Timer-ID löschen
        
        return False  # Event weitergeben
    
    ###################################################################################################################################
    def check_long_press(self):
        """Prüft, ob ein Langklick erkannt wurde"""
        # Verwende die aktuelle Zeit aus dem Gtk-System
        current_time = Gtk.get_current_event_time()               # aktuelle Zeit nehmen 
        
        if current_time == 0:                                     # Kein aktuelles Event verfügbar
            # Benutze die monotonische Uhr, aber konvertiert zu Millisekunden
            current_time = GLib.get_monotonic_time() // 1000      # Monotonische Uhr verwenden
        
        # Berechne die vergangene Zeit in Millisekunden
        elapsed = current_time - self.press_start_time            # vergangene Zeit berechnen
        
        print(f"Langklick-Prüfung: {elapsed}ms vergangen (Ziel: {self.LONG_PRESS_TIME}ms)" )  # Nachricht ausgeben
        
        if elapsed >= self.LONG_PRESS_TIME:
            # Langklick erkannt, Einstellungsdialog anzeigenhallo, können wir beim abspielen der audiofiles ein kurzes ein- und ausblenden einbauen
            print("Langklick erkannt!")                           # Nachricht ausgeben
            if not self.global_settings_dialog_open: 
                self.show_global_settings()                       # Dialog anzeigen
            
            self.press_timeout_id = None                          # Timer nicht wiederholen        
            return False                                          # Timer nicht wiederholen        
        # Timer fortsetzen  
        return True                                               # True zurückgeben
    
    ###################################################################################################################################
    def show_global_settings(self):
        """Zeigt den globalen Einstellungs-Dialog an"""
        if self.global_settings_dialog_open:                      # Wenn der Dialog bereits geöffnet ist
            print("Global-Settings-Dialog ist bereits geöffnet!") # Nachricht ausgeben
            return  # Rückgabe, um unnötige weitere Verarbeitung zu vermeiden
            
        print("Öffne Global-Settings-Dialog...")                  # Nachricht ausgeben
        self.global_settings_dialog_open = True                   # Dialog öffnen
        
        dialog = GlobalSettingsDialog(self, self.config)          # Dialog erstellen
        response = dialog.show()                                  # Dialog anzeigen
        
        # Dialog ist jetzt geschlossen
        self.global_settings_dialog_open = False                  # Dialog schließen
        
        if response == Gtk.ResponseType.OK:                       # Wenn der Dialog mit OK geschlossen wurde
            print("Globale Einstellungen wurden geändert - wende Änderungen an...")  # Nachricht ausgeben
            
            # Speichern Sie die Konfiguration
            self.save_config(self.config_file)                    # Konfiguration speichern
            
            # Stellen Sie sicher, dass die Standardwerte für die Farbeinstellungen vorhanden sind
            if 'use_global_bg_color' not in self.config['soundbutton']: 
                self.config['soundbutton']['use_global_bg_color'] = True   # Standardwert setzen
            if 'use_global_text_color' not in self.config['soundbutton']:
                self.config['soundbutton']['use_global_text_color'] = True # Standardwert setzen
            
            # Aktualisieren Sie die FlowBox-Abstände
            button_config = self.config['soundbutton']                # Konfiguration nehmen
            self.flowbox.set_row_spacing(button_config['spacing'])    # Abstand zwischen den Zeilen setzen
            self.flowbox.set_column_spacing(button_config['spacing']) # Abstand zwischen den Spalten setzen
            self.flowbox.set_margin_start(button_config['spacing'])   # Abstand zum linken Rand setzen
            self.flowbox.set_margin_end(button_config['spacing'])     # Abstand zum rechten Rand setzen
            self.flowbox.set_margin_top(button_config['spacing'])     # Abstand zum oberen Rand setzen
            self.flowbox.set_margin_bottom(button_config['spacing'])  # Abstand zum unteren Rand setzen
            
            # Aktualisieren Sie alle Buttons, um die neuen globalen Einstellungen anzuwenden
            self.update_all_buttons()                             # Buttons aktualisieren
            
            # Aktualisiere die gesamte UI, um sicherzustellen, dass alle Änderungen sichtbar sind
            self.queue_draw()                                     # UI aktualisieren
            self.flowbox.queue_draw()                             # FlowBox aktualisieren
            
            print("Globale Einstellungen wurden erfolgreich angewendet!")  # Nachricht ausgeben
    
    ###################################################################################################################################
    def on_add_button_clicked(self, button, event):
        """Handler für das Klicken des Add-Buttons"""
        try:
            if event.button == 1:                                 # Nur auf linke Maustaste reagieren
                # Finde den SoundButton-Objekt in der Buttons-Liste
                for sound_button in self.buttons:
                    if sound_button.is_add_button and sound_button.button == button:
                        self.add_new_button(sound_button)         # Neuer Button hinzufügen
                        return                                    # Rückgabe, um unnötige weitere Verarbeitung zu vermeiden
                print("Warnung: Add-Button konnte nicht gefunden werden")  # Nachricht ausgeben
        except Exception as e:
            print(f"Fehler im Add-Button-Handler: {e}")           # Fehler ausgeben
            import traceback
            traceback.print_exc()                                 # Traceback ausgeben 

###################################################################################################################################
def main():
    """Main-Funktion"""
    # Argument-Parser erstellen
    parser = argparse.ArgumentParser(description='pySoundboard - Ein Soundboard für eine GTK3 Umgebung')  # Argument-Parser erstellen
    parser.add_argument('--config', '-c', 
                       help='Pfad zur Konfigurationsdatei (Standard: config.json)',  # Hilfe für die Konfigurationsdatei
                       default='config.json')  # Standardkonfigurationsdatei        
    args = parser.parse_args()                                    # Argumente parsen
    # Soundboard mit der angegebenen Konfigurationsdatei starten
    win = SoundboardWindow(config_file=args.config)               # Soundboard-Fenster erstellen
    Gtk.main()                                                    # GTK-Hauptschleife starten

if __name__ == "__main__":
    main()  # Hauptfunktion ausführen