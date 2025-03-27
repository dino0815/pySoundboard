import json
import os

class ConfigManager:
    ###################################################################################################################################
    # Konstanten für die Konfiguration
    DEFAULT_CONFIG = {
        "window": {
            "title": "Soundboard",
            "width":  200,
            "height": 100,
            "soundpfad_prefix": "",
            "imagepfad_prefix": ""
        },
        "soundbutton": {
            "button_width":  100,
            "button_height":  75,
            "spacing":         5,
            "radius":         15,
            "text_x":          5,
            "text_y":          5,
            "text_size":      13,
            "text_color":       "#000000",
            "background_color": "#CCCCCC",
            "volume_min":      0,
            "volume_max":    100,
            "volume_width":   15,
            "volume_default": 90,
        },
        "buttons": []
    }

    ###################################################################################################################################
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
    ###################################################################################################################################
    def load_config(self):
        """Lädt die Konfiguration aus der Datei und ergänzt fehlende Werte mit Standardwerten"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Keine gültige Konfigurationsdatei gefunden, verwende Standardkonfiguration!")
            config = self.DEFAULT_CONFIG.copy()
            
        # Ergänze fehlende Werte mit Standardwerten
        self._validate_config(config)
        
        return config
        
    ###################################################################################################################################
    def _validate_config(self, config):
        """Überprüft und ergänzt die Konfiguration mit Standardwerten"""
        # Für jede Sektion in der Standardkonfiguration
        for section, settings in self.DEFAULT_CONFIG.items():
            if section not in config:
                config[section] = settings.copy()
            elif isinstance(settings, dict):
                # Für jede Einstellung in der Sektion
                for key, value in settings.items():
                    if key not in config[section]:
                        config[section][key] = value
                        
    ###################################################################################################################################
    def save_config(self):
        """Speichert die aktuelle Konfiguration in die Datei"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    ###################################################################################################################################
    def resolve_path(self, relative_path, prefix_type='sound'):
        """Löst einen relativen Pfad unter Berücksichtigung des konfigurierten Prefixes auf"""
        if not relative_path:
            return ""
            
        # Hole den entsprechenden Prefix aus der Konfiguration
        prefix_key = f"{prefix_type}pfad_prefix"
        prefix = self.config['window'].get(prefix_key, "")
        
        # Wenn kein Prefix gesetzt ist, verwende das aktuelle Verzeichnis
        if not prefix:
            return os.path.join(os.getcwd(), relative_path)
            
        # Verwende den konfigurierten Prefix
        return os.path.join(prefix, relative_path) 