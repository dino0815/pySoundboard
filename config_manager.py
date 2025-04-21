import json
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

###################################################################################################################################
class ConfigManager:
    def __init__(self, parent=None, config_file='config.json'):
        self.parent = parent
        self.config_file = config_file
        self.data = self.load_config()
        self.buttonlist = self.load_buttonlist()
        self.is_new_config = config_file == '' or config_file is None
        self.has_changes = False  # Statusvariable für Änderungen
        
    ###################################################################################################################################
    # Konstanten für die Konfiguration
    DEFAULT_CONFIG = {
        "Window": {
            "title_prefix":             "Soundboard: ",
            "window_width":               400,
            "window_height":              200,
            "read_only":                False
        },
        "buttons": [
            {
                "position":                       0,
                "soundpfad_prefix":       "sounds/",
                "imagepfad_prefix":       "images/",
                "button_width":                 100,
                "button_height":                 75,
                "button_spacing":                 5,
                "button_radius":                 10,
                "audio_file":                    "",
                "volume":                        50,
                "fade_time_ms":                1000,
                "loop":                       False,
                "text":                    "Button",
                "use_custom_text_position":    True,
                "text_x":                        10,
                "text_y":                        10,
                "text_size":                     13,
                "text_align":                "left",
                "use_custom_text_color":      False,
                "text_color":             "#000000",
                "use_custom_bg_color":        False,
                "background_color":       "#4e9a06",
                "use_custom_image":           False,
                "image_file":                    "",
                "image_x":                       10,
                "image_y":                       10,
                "image_scale":                    0
            },
            {
                "position":                       1,
                "text":           "Minimal\nButton",
            }
        ]
    }

    ###################################################################################################################################
    def load_config(self):
        """Lädt die Konfiguration aus der Datei und ergänzt fehlende Werte mit Standardwerten"""
        # Wenn kein Dateiname angegeben ist, verwende die Standardkonfiguration
        if self.config_file == '' or self.config_file is None:
            print("Keine Konfigurationsdatei angegeben, verwende Standardkonfiguration!")
            return self.DEFAULT_CONFIG.copy()
            
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Keine gültige Konfigurationsdatei gefunden, erstelle neue Konfiguration!")
            data = self.DEFAULT_CONFIG.copy()
            
        # Ergänze fehlende Werte mit Standardwerten
        """Überprüft und ergänzt die Konfiguration mit Standardwerten"""
        # Für jede Sektion in der Standardkonfiguration
        for section, settings in self.DEFAULT_CONFIG.items():
            if section not in data:
                data[section] = settings.copy()
            elif isinstance(settings, dict):
                # Für jede Einstellung in der Sektion
                for key, value in settings.items():
                    if key not in data[section]:
                        data[section][key] = value
        return data

    ###################################################################################################################################
    def get_default_button(self):
        """Holt den Default-Button (Button0) aus der Konfiguration"""
        if self.data['buttons'] and self.data['buttons'][0].get('position') == 0:
            return self.data['buttons'][0]
        return None

    ###################################################################################################################################
    def load_buttonlist(self):
        """Lade die Buttons sortiert nach ihrer Position"""
        # Behalte alle Buttons in der Liste, einschließlich des Default-Buttons
        buttonlist = sorted(self.data['buttons'], key=lambda x: x.get('position', 0))
        
        # Hole den Default-Button (Position 0)
        default_button = None
        for button in buttonlist:
            if button.get('position', 0) == 0:
                default_button = button
                break
        
        # Wenn kein Default-Button gefunden wurde, erstelle einen
        if default_button is None:
            default_button = self.DEFAULT_CONFIG['buttons'][0]
            buttonlist.insert(0, default_button)
        
        # Durchnummeriere die Buttons neu und und verändere sie nicht
        for i, button in enumerate(buttonlist):
            #if button.get('position', 0) != 0:  # Nicht den Default-Button ändern
                button['position'] = i
                
        # Aktualisiere die Buttonliste in der Konfiguration
        self.data['buttons'] = buttonlist
        
        return buttonlist
    
    ###################################################################################################################################
    def save_config(self, parent_window=None):
        """Speichert die aktuelle Konfiguration in die Datei"""
        # Wenn keine Datei angegeben ist oder es sich um eine neue Konfiguration handelt,
        # öffne den "Speichern unter"-Dialog
        if self.config_file == '' or self.config_file is None or self.is_new_config:
            if parent_window:
                return self.save_config_as_dialog(parent_window)
            else:
                print("Fehler: Kein übergeordnetes Fenster für den Dialog angegeben!")
                return False
        elif self.data['Window']['read_only']:
            print("Konfiguration ist schreibgeschützt!")
            if parent_window:
                # Zeige einen Dialog, der erklärt, dass die Konfiguration schreibgeschützt ist
                dialog = Gtk.MessageDialog(
                    transient_for=parent_window,
                    flags=0,
                    message_type=Gtk.MessageType.WARNING,
                    buttons=Gtk.ButtonsType.OK_CANCEL,
                    text="Die Konfiguration ist schreibgeschützt und kann nicht direkt gespeichert werden."
                )
                dialog.format_secondary_text("Möchten Sie die Konfiguration unter einem neuen Namen speichern?")
                
                response = dialog.run()
                dialog.destroy()
                
                if response == Gtk.ResponseType.OK:
                    return self.save_config_as_dialog(parent_window)

                else:
                    return False
            else:
                print("Fehler: Kein übergeordnetes Fenster für den Dialog angegeben!")
                return False
        else:
            # Speichere die Konfiguration in die angegebene Datei
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            self.mark_saved()  # Markiere, dass alle Änderungen gespeichert wurden
        return True

    ###################################################################################################################################
    def save_config_as(self, new_config_file):
        """Speichert die aktuelle Konfiguration unter einem neuen Dateinamen"""
        # Speichere die Konfiguration direkt in die neue Datei
        try:
            with open(new_config_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            self.config_file = new_config_file
            self.is_new_config = False  # Markiere, dass es keine neue Konfiguration mehr ist
            self.mark_saved()  # Markiere, dass alle Änderungen gespeichert wurden
            print(f"Konfiguration wurde unter '{new_config_file}' gespeichert")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Konfiguration unter '{new_config_file}': {e}")
            return False

    ###################################################################################################################################
    def save_config_as_dialog(self, parent_window):
        """Öffnet einen Dateiauswahldialog zum Speichern der Konfiguration unter einem neuen Namen"""
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        
        print("Öffne Dateiauswahldialog...")
        
        try:
            dialog = Gtk.FileChooserDialog(
                title="Konfiguration speichern unter",
                parent=parent_window,
                action=Gtk.FileChooserAction.SAVE
            )
            
            # Filter für JSON-Dateien
            filter_json = Gtk.FileFilter()
            filter_json.set_name("JSON-Dateien")
            filter_json.add_mime_type("application/json")
            filter_json.add_pattern("*.json")
            dialog.add_filter(filter_json)
            
            # Aktuelle Konfigurationsdatei als Vorschlag setzen
            if self.config_file:
                dialog.set_filename(self.config_file)
            
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK
            )
            dialog.set_modal(True)             # Stelle sicher, dass der Dialog modal ist
            dialog.show_all()                   # Zeige den Dialog an
            #print("Dialog wird angezeigt...")
            response = dialog.run()
            #print(f"Dialog-Antwort: {response}")
            if response == Gtk.ResponseType.OK:
                new_config_file = dialog.get_filename()
                #print(f"Ausgewählte Datei: {new_config_file}")
                
                # Stelle sicher, dass die Datei die Endung .json hat
                if not new_config_file.endswith('.json'):
                    new_config_file += '.json'
                    #print(f"Dateiendung hinzugefügt: {new_config_file}")
                
                # Prüfe, ob die Datei bereits existiert
                if os.path.exists(new_config_file):
                    # Versuche, die existierende Konfiguration zu laden
                    try:
                        with open(new_config_file, 'r') as f:
                            existing_config = json.load(f)
                        
                        # Prüfe, ob die Konfiguration schreibgeschützt ist
                        if 'Window' in existing_config and 'read_only' in existing_config['Window'] and existing_config['Window']['read_only']:
                            # Konfiguration ist schreibgeschützt, zeige Fehlermeldung
                            error_dialog = Gtk.MessageDialog(
                                transient_for=parent_window,
                                flags=0,
                                message_type=Gtk.MessageType.ERROR,
                                buttons=Gtk.ButtonsType.OK,
                                text="Die ausgewählte Konfiguration ist schreibgeschützt und kann nicht überschrieben werden."
                            )
                            error_dialog.run()
                            error_dialog.destroy()
                            
                            # Schließe den aktuellen Dialog und öffne einen neuen
                            dialog.destroy()
                            return self.save_config_as_dialog(parent_window)
                        else:
                            # Konfiguration ist nicht schreibgeschützt, frage nach Überschreiben
                            confirm_dialog = Gtk.MessageDialog(
                                transient_for=parent_window,
                                flags=0,
                                message_type=Gtk.MessageType.QUESTION,
                                buttons=Gtk.ButtonsType.YES_NO,
                                text=f"Die Datei '{new_config_file}' existiert bereits. Möchten Sie sie überschreiben?"
                            )
                            confirm_response = confirm_dialog.run()
                            confirm_dialog.destroy()
                            
                            if confirm_response != Gtk.ResponseType.YES:
                                # Benutzer möchte nicht überschreiben, schließe den Dialog
                                dialog.destroy()
                                return False
                    except (json.JSONDecodeError, FileNotFoundError):
                        # Datei existiert, ist aber keine gültige JSON-Datei
                        confirm_dialog = Gtk.MessageDialog(
                            transient_for=parent_window,
                            flags=0,
                            message_type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.YES_NO,
                            text=f"Die Datei '{new_config_file}' existiert bereits, ist aber keine gültige Konfigurationsdatei. Möchten Sie sie überschreiben?"
                        )
                        confirm_response = confirm_dialog.run()
                        confirm_dialog.destroy()
                        
                        if confirm_response != Gtk.ResponseType.YES:
                            # Benutzer möchte nicht überschreiben, schließe den Dialog
                            dialog.destroy()
                            return False
                
                # Speichere die Konfiguration unter dem neuen Namen
                if self.save_config_as(new_config_file):
                    print(f"Konfiguration wurde unter '{new_config_file}' gespeichert")
                    dialog.destroy()
                    return True
                else:
                    print(f"Fehler beim Speichern der Konfiguration unter '{new_config_file}'")
                    dialog.destroy()
                    return False
            
            dialog.destroy()
            return False
        except Exception as e:
            print(f"Fehler im save_config_as_dialog: {e}")
            import traceback
            traceback.print_exc()
            return False

    ###################################################################################################################################
    def add_minimal_button(self):
        """Fügt einen minimalen Button zur Konfiguration hinzu"""
        new_position = len(self.data['buttons'])              # Bestimme die neue Position basierend auf der Länge der Liste
        print(f"Add new minimal button at position: {new_position}")
        new_button = self.DEFAULT_CONFIG['buttons'][1].copy() # Kopiere den minimalen Button aus der Standardkonfiguration
        new_button['position'] = new_position                 # Setze die neue Position
        self.data['buttons'].append(new_button)               # Füge den neuen Button zur Konfiguration hinzu
        self.buttonlist = self.load_buttonlist()              # Aktualisiere die Buttonliste
        #self.mark_changed()                                   # Markiere, dass es Änderungen am Soundboard gegeben hat
        return new_button

    ###################################################################################################################################
    def delete_button(self, position):
        """Entfernt einen Button anhand seiner Position aus der Konfiguration"""
        for i, button in enumerate(self.data['buttons']):             # Finde den Button in der Konfiguration
            if button.get('position') == position:
                del self.data['buttons'][i]                           # Entferne den Button aus der Konfiguration
                self.buttonlist = self.load_buttonlist()              # Aktualisiere die Buttonliste
                return True        
        return False                                                  # Button nicht gefunden

    ###################################################################################################################################
    def mark_changed(self):
        """Markiert, dass es Änderungen am Soundboard gegeben hat"""
        self.has_changes = True
        self.parent.update_window_title()  # Aktualisiere den Fenstertitel
        return True
        
    ###################################################################################################################################
    def mark_saved(self):
        """Markiert, dass alle Änderungen gespeichert wurden"""
        self.has_changes = False
        self.parent.update_window_title()  # Aktualisiere den Fenstertitel

        return True
        
    ###################################################################################################################################
    def has_unsaved_changes(self):
        """Gibt zurück, ob es ungespeicherte Änderungen gibt"""
        print(f"has_changes: {self.has_changes}")
        return self.has_changes

    ###################################################################################################################################
    def create_portable_config(self, button_config):
        """Erstellt eine portable Version der Button-Konfiguration für Drag & Drop zwischen Soundboards"""
        import os
        
        # Erstelle eine Kopie der Button-Konfiguration
        portable_config = button_config.copy()
        
        # Konvertiere relative Pfade zu absoluten Pfaden
        if 'audio_file' in portable_config and portable_config['audio_file']:
            if not os.path.isabs(portable_config['audio_file']):
                # Wenn ein soundpfad_prefix vorhanden ist, verwende es
                if 'soundpfad_prefix' in portable_config:
                    base_path = os.path.dirname(self.config_file) if self.config_file else os.getcwd()
                    portable_config['audio_file'] = os.path.join(base_path, portable_config['soundpfad_prefix'], portable_config['audio_file'])
                else:
                    base_path = os.path.dirname(self.config_file) if self.config_file else os.getcwd()
                    portable_config['audio_file'] = os.path.join(base_path, portable_config['audio_file'])
        
        if 'image_file' in portable_config and portable_config['image_file']:
            if not os.path.isabs(portable_config['image_file']):
                # Wenn ein imagepfad_prefix vorhanden ist, verwende es
                if 'imagepfad_prefix' in portable_config:
                    base_path = os.path.dirname(self.config_file) if self.config_file else os.getcwd()
                    portable_config['image_file'] = os.path.join(base_path, portable_config['imagepfad_prefix'], portable_config['image_file'])
                else:
                    base_path = os.path.dirname(self.config_file) if self.config_file else os.getcwd()
                    portable_config['image_file'] = os.path.join(base_path, portable_config['image_file'])
        
        # Füge Informationen über das Quell-Soundboard hinzu
        if self.config_file:
            portable_config['CopyOf'] = os.path.splitext(os.path.basename(self.config_file))[0]
        else:
            portable_config['CopyOf'] = "unnamed_soundboard"
        
        return portable_config

    ###################################################################################################################################
    def import_portable_config(self, portable_config, target_position=None):
        """Importiert eine portable Konfiguration und konvertiert sie in eine lokale Konfiguration"""
        try:
            # Erstelle eine Kopie der Konfiguration
            local_config = portable_config.copy()

            if 'audio_file' in local_config and local_config['audio_file']:
                if os.path.isabs(local_config['audio_file']):
                    # Hole den imagepfad_prefix aus der Konfiguration oder verwende den Standard
                    soundpfad_prefix = self.data['Window'].get('soundpfad_prefix', 'sounds/')
                    # Versuche, den Pfad relativ zum Konfigurationsverzeichnis zu machen
                    if self.config_file:
                        base_path = os.path.dirname(self.config_file)
                        try:
                            local_config['audio_file'] = os.path.relpath(local_config['audio_file'], base_path)
                        except ValueError:
                            # Wenn der Pfad nicht relativ gemacht werden kann, behalte den absoluten Pfad
                            pass

            if 'image_file' in local_config and local_config['image_file']:
                if os.path.isabs(local_config['image_file']):
                    # Hole den imagepfad_prefix aus der Konfiguration oder verwende den Standard
                    imagepfad_prefix = self.data['Window'].get('imagepfad_prefix', 'images/')
                    # Versuche, den Pfad relativ zum Konfigurationsverzeichnis zu machen
                    if self.config_file:
                        base_path = os.path.dirname(self.config_file)
                        try:
                            local_config['image_file'] = os.path.relpath(local_config['image_file'], base_path)
                        except ValueError:
                            # Wenn der Pfad nicht relativ gemacht werden kann, behalte den absoluten Pfad
                            pass
            
            # Setze die gewünschte Position, falls angegeben
            if target_position is not None:
                local_config['position'] = target_position
            
            return local_config
        except Exception as e:
            print(f"Fehler beim Importieren der portablen Konfiguration: {e}")
            return None

    ###################################################################################################################################
    def add_portable_button(self, portable_config, target_position=None):
        """Fügt einen Button aus einer portablen Konfiguration hinzu"""
        try:
            # Importiere die portable Konfiguration
            local_config = self.import_portable_config(portable_config, target_position)
            if not local_config:
                return False
            
            # Wenn keine Position angegeben wurde, füge den Button am Ende hinzu
            if target_position is None:
                target_position = len(self.buttonlist) + 1
                local_config['position'] = target_position
            
            # Verschiebe existierende Buttons, um Platz zu machen
            for button in self.buttonlist:
                if button['position'] >= target_position:
                    button['position'] += 1
            
            # Füge den neuen Button zur Liste hinzu
            self.buttonlist.append(local_config)
            
            # Sortiere die Buttonliste nach Position
            self.buttonlist.sort(key=lambda x: x.get('position', 0))
            
            # Aktualisiere die Konfiguration
            self.data['buttons'] = self.buttonlist
            
            # Markiere Änderungen
            self.mark_changed()
            
            return True
        except Exception as e:
            print(f"Fehler beim Hinzufügen des portablen Buttons: {e}")
            return False