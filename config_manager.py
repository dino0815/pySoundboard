import json
#import os

###################################################################################################################################
class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.data = self.load_config()
        self.buttonlist = self.load_buttonlist()
        
    ###################################################################################################################################
    # Konstanten für die Konfiguration
    DEFAULT_CONFIG = {
        "Window": {
            "title":             "Soundboard",
            "window_width":               200,
            "window_height":              100,
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
    def save_config(self):
        """Speichert die aktuelle Konfiguration in die Datei"""
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    ###################################################################################################################################
    def add_minimal_button(self):
        """Fügt einen minimalen Button zur Konfiguration hinzu"""
        new_position = len(self.data['buttons'])              # Bestimme die neue Position basierend auf der Länge der Liste
        new_button = self.DEFAULT_CONFIG['buttons'][1].copy() # Kopiere den minimalen Button aus der Standardkonfiguration
        new_button['position'] = new_position                 # Setze die neue Position
        self.data['buttons'].append(new_button)               # Füge den neuen Button zur Konfiguration hinzu
        self.buttonlist = self.load_buttonlist()              # Aktualisiere die Buttonliste
        #self.save_config()                                    # Speichere die Konfiguration        
        return new_position

    ###################################################################################################################################
    def delete_button(self, position):
        """Entfernt einen Button anhand seiner Position aus der Konfiguration"""
        # Finde den Button in der Konfiguration
        for i, button in enumerate(self.data['buttons']):
            if button.get('position') == position:
                # Entferne den Button aus der Konfiguration
                del self.data['buttons'][i]
                # Speichere die Konfiguration
                #self.save_config()
                # Aktualisiere die Buttonliste
                self.buttonlist = self.load_buttonlist()
                return True
        
        # Button nicht gefunden
        return False