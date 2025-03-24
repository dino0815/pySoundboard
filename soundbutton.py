#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import cairo
import json
import pygame
import os
from settings_dialog import SettingsDialog

class SoundButton(Gtk.Box):
    def __init__(self, position=0, offset_x=0, offset_y=0, config=None, on_delete=None, is_add_button=False):
        if config is None:
            raise ValueError("Keine Konfiguration übergeben. SoundButton benötigt eine gültige Konfiguration.")
        
        if 'soundbutton' not in config:
            raise ValueError("Ungültige Konfiguration: 'soundbutton' Sektion fehlt")
            
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        
        self.position = position
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.config = config
        self.on_delete = on_delete
        self.is_add_button = is_add_button
        
        # Stelle sicher, dass pygame.mixer initialisiert ist
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
                print("Pygame mixer wurde in SoundButton.__init__ initialisiert")
            except Exception as e:
                print(f"Fehler bei der Initialisierung von pygame.mixer: {e}")
        
        # Sound-Status
        self.sound = None
        self.is_playing = False
        self.is_looping = False
        self.is_toggled = False  # Status für Toggle-Funktionalität
        self.fade_timer = None  # Timer für Fade-Effekte
        self.fade_duration = 50  # Dauer des Fade-Effekts in Millisekunden
        self.fade_steps = 10  # Anzahl der Schritte für den Fade-Effekt
        self.fade_step_func = None  # Speichert die aktuelle Fade-Step-Funktion
        self.fade_source = None  # Speichert die aktuelle GLib.Source
        
        # Button-spezifische Konfiguration laden
        self.button_config = self.get_button_config()
        
        # Variablen für die Langklick-Erkennung
        self.press_timeout_id = None
        self.LONG_PRESS_TIME = 500  # 500ms = 0.5 Sekunden
        self.press_start_time = 0
        
        # Dialog-Status, um mehrfaches Öffnen zu verhindern
        self.settings_dialog_open = False
        
        # UI erstellen
        self._setup_ui()
        
        # CSS-Styling anwenden
        self._apply_css_style()
        
        if not is_add_button:
            print(f"SoundButton '{self.button_config['text']}'")
            print(f"SoundButton '{self.button_config['text']}'")
        
        # Widgets anzeigen
        self.show_all()
    
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche mit einem normalen Button statt DrawingArea"""
        sb_config = self.config['soundbutton']
        
        # Container für Button und Regler
        self.button_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.button_container.set_size_request(sb_config['button_width'], sb_config['button_height'])
        
        # Container für den Button
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.button_box.set_size_request(sb_config['button_width'], sb_config['button_height'])
        
        # Erstelle einen normalen Button
        button_width = sb_config['button_width']
        self.button = Gtk.Button()
        self.button.set_size_request(button_width, sb_config['button_height'])
        
        # Setze den Text auf dem Button
        if self.is_add_button:
            self.button.set_label("+")
        else:
            # Anstatt direkt das Label zu setzen, erstellen wir ein Label-Widget,
            # das Zeilenumbrüche unterstützt
            button_text = self.button_config['text']
            
            # Wir erstellen ein Label-Widget
            self.label = Gtk.Label()
            
            # Einfache Ersetzung von \n für bessere Zeilenumbrüche
            if '\\n' in button_text:
                button_text = button_text.replace('\\n', '\n')
            
            self.label.set_text(button_text)
            self.label.set_use_markup(True)  # Ermöglicht Markup (z.B. <b>, <i>, etc.)
            
            # Aktiviere Zeilenumbrüche im Label - verwende individuelle oder globale Einstellung
            line_breaks = self.button_config.get('line_breaks')
            if line_breaks is None:  # Wenn nicht gesetzt, verwende globale Einstellung
                line_breaks = sb_config.get('line_breaks', True)
                self.button_config['line_breaks'] = line_breaks
            
            self.label.set_line_wrap(line_breaks)
            self.label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            
            # Textausrichtung gemäß individueller oder globaler Konfiguration
            text_align = self.button_config.get('text_align')
            if text_align is None or text_align == "":  # Wenn nicht gesetzt, verwende globale Einstellung
                text_align = sb_config.get('text_align', 'center')
                self.button_config['text_align'] = text_align
            
            if text_align == 'left':
                self.label.set_justify(Gtk.Justification.LEFT)
                self.label.set_halign(Gtk.Align.START)
            elif text_align == 'right':
                self.label.set_justify(Gtk.Justification.RIGHT)
                self.label.set_halign(Gtk.Align.END)
            else:  # center (default)
                self.label.set_justify(Gtk.Justification.CENTER)
                self.label.set_halign(Gtk.Align.CENTER)
                
            # Zusätzliche Anpassungen für die Textposition im Button
            # Prüfen, ob individuelle Textposition verwendet werden soll
            use_custom_position = self.button_config.get('use_custom_text_position')
            if use_custom_position is None:  # Wenn nicht gesetzt, verwende globale Einstellung
                use_custom_position = sb_config.get('use_custom_text_position', False)
                self.button_config['use_custom_text_position'] = use_custom_position
            
            # Zurücksetzen aller Margins
            self.label.set_margin_top(0)
            self.label.set_margin_bottom(0)
            self.label.set_margin_start(0)
            self.label.set_margin_end(0)
            
            # Wenn individuelle Positionierung verwendet wird, immer linksbündig und von oben ausgerichtet
            if use_custom_position:
                # Position von der oberen linken Ecke - verwende individuelle oder globale Werte
                margin_top = self.button_config.get('text_margin_top')
                if margin_top is None:
                    margin_top = sb_config.get('text_margin_top', 0)
                    self.button_config['text_margin_top'] = margin_top
                
                margin_left = self.button_config.get('text_margin_left')
                if margin_left is None:
                    margin_left = sb_config.get('text_margin_left', 0)
                    self.button_config['text_margin_left'] = margin_left
                
                # Setze Margins für die Position
                self.label.set_margin_top(margin_top)
                self.label.set_margin_start(margin_left)
                
                # Absolute Positionierung für den Text
                self.label.set_valign(Gtk.Align.START)  # Immer von oben ausgerichtet
                self.label.set_halign(Gtk.Align.START)  # Immer von links ausgerichtet
                
                # Label sollte den gesamten Button-Bereich nutzen können
                self.label.set_hexpand(True)
                self.label.set_vexpand(True)
                
                print(f"Individuelle Textposition aktiviert: top={margin_top}, left={margin_left}")
            else:
                print("Keine individuelle Textposition verwendet")
            
            # Wichtig: Label muss sichtbar sein
            self.label.show()
            # Füge das Label zum Button hinzu
            self.button.add(self.label)
        
        # Event-Handler für Button
        self.button.connect("button-press-event", self.on_button_press)
        self.button.connect("button-release-event", self.on_button_release)
        
        # Button zum Container hinzufügen
        self.button_box.pack_start(self.button, True, True, 0)
        
        # Button-Box zum Hauptcontainer hinzufügen
        self.button_container.pack_start(self.button_box, True, True, 0)
        
        # Lautstärkeregler als Overlay erstellen, wenn es kein Add-Button ist
        if not self.is_add_button:
            # Overlay, um den Lautstärkeregler über den Button zu legen
            self.overlay = Gtk.Overlay()
            self.overlay.add(self.button_container)
            
            # Lautstärkeregler erstellen
            self._create_volume_slider(sb_config)
            
            # Lautstärkeregler rechts positionieren
            self.volume_container.set_halign(Gtk.Align.END)
            self.volume_container.set_valign(Gtk.Align.FILL)
            self.volume_container.set_margin_end(2)  # Abstand zum rechten Rand
            
            # Lautstärkeregler zum Overlay hinzufügen
            self.overlay.add_overlay(self.volume_container)
            
            # Overlay zum Hauptcontainer hinzufügen
            self.pack_start(self.overlay, True, True, 0)
        else:
            # Bei Add-Button nur den Button-Container hinzufügen
            self.pack_start(self.button_container, True, True, 0)
        
        # Widget-Eigenschaften setzen
        self.set_hexpand(True)
        self.set_vexpand(False)
    
    def _create_volume_slider(self, sb_config):
        """Erstellt den Lautstärkeregler"""
        self.volume_slider = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL)
        # Verwende nun volume_min und volume_max
        self.volume_slider.set_range(sb_config['volume_min'], sb_config['volume_max'])
        self.volume_slider.set_value(int(self.get_button_config().get('volume', sb_config['volume_default'])))
        self.volume_slider.set_draw_value(False)  # Zeige den Wert NICHT an
        self.volume_slider.set_digits(0)  # Keine Dezimalstellen
        self.volume_slider.set_vexpand(True)  # Nutze die gesamte verfügbare Höhe
        self.volume_slider.set_hexpand(False)
        self.volume_slider.set_size_request(sb_config['volume_width'], sb_config['button_height'] - 20)
        self.volume_slider.set_inverted(True)
        
        # Reduziere den Abstand zum Rand, damit mehr Höhe für den Schieberegler bleibt
        self.volume_slider.set_margin_top(5)
        self.volume_slider.set_margin_bottom(5)
        self.volume_slider.connect("value-changed", self.on_volume_changed)
        
        # Container für den Lautstärkeregler
        self.volume_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.volume_container.set_vexpand(True)  # Nutze die gesamte verfügbare Höhe
        self.volume_container.set_hexpand(False)
        self.volume_container.set_size_request(sb_config['volume_width'], sb_config['button_height'])
        self.volume_container.pack_start(self.volume_slider, True, True, 0)  # True für expand und fill
    
    def get_button_config(self):
        """Lädt die Button-spezifische Konfiguration"""
        sb_config = self.config['soundbutton']
        if self.position >= len(self.config.get('buttons', [])):
            return {
                'position': self.position,
                'volume': sb_config['volume_default'],
                'text': f"Button {self.position + 1}"
            }
        
        buttons = self.config.get('buttons', [])
        for button in buttons:
            if button['position'] == self.position:
                return button.copy()
        
        return {
            'position': self.position,
            'volume': sb_config['volume_default'],
            'text': f"Button {self.position + 1}"
        }
    
    def hex_to_rgb(self, hex_color):
        """Konvertiert einen Hex-Farbcode (#RRGGBB) in RGB-Werte (0-1)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return [r, g, b]
    
    def set_offset(self, offset_x, offset_y):
        """Setzt den Offset des Buttons"""
        self.offset_x = offset_x
        self.offset_y = offset_y
        print(f"SoundButton '{self.button_config['text']}' - Offset aktualisiert: x={self.offset_x}, y={self.offset_y}")
    
    def _rgba_to_hex(self, rgba):
        """Konvertiert ein RGBA-Objekt in einen Hex-Farbcode für CSS"""
        r = int(rgba.red * 255)
        g = int(rgba.green * 255)
        b = int(rgba.blue * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def get_theme_colors(self):
        """Extrahiert Farben aus dem aktuellen Theme"""
        # Widget erstellen, um auf das Theme zuzugreifen
        temp_widget = Gtk.Button()
        style = temp_widget.get_style_context()
        
        # Farben extrahieren
        normal_color = style.get_color(Gtk.StateFlags.NORMAL)
        
        # Hintergrundfarbe auslesen
        success, normal_bg = style.lookup_color("theme_bg_color")
        if not success:
            # Fallback
            normal_bg = Gdk.RGBA(0.9, 0.9, 0.9, 1.0)
        
        # Gedrückte Button-Farbe auslesen
        temp_button = Gtk.Button()
        button_style = temp_button.get_style_context()
        button_style.set_state(Gtk.StateFlags.ACTIVE)
        
        pressed_bg = Gdk.RGBA(0.8, 0.8, 0.8, 1.0)
        
        # Versuchen, die Farbe direkt aus dem Button-Style zu bekommen
        success = False
        try:
            # Zuerst versuchen, die Theme-Auswahlfarbe zu bekommen (oft bessere Kontraste)
            success, pressed_bg = button_style.lookup_color("theme_selected_bg_color")
            if not success:
                # Fallback auf spezifischen Button-Aktiv-Hintergrund
                success, pressed_bg = button_style.lookup_color("theme_button_active_bg")
        except:
            pass
        
        if not success:
            # Fallback: Dunklere Version der normalen Hintergrundfarbe
            pressed_bg = Gdk.RGBA(
                normal_bg.red * 0.9,
                normal_bg.green * 0.9,
                normal_bg.blue * 0.9,
                normal_bg.alpha
            )
        
        # 3D-Effekt-Farben berechnen mit optimierten Faktoren
        light_factor = 1.35  # Etwas erhöht für besseren Kontrast
        dark_factor = 0.65   # Etwas reduziert für dunkleren Schatten
        
        # Highlight-Farbe (heller)
        highlight = Gdk.RGBA(
            min(1.0, normal_bg.red * light_factor),
            min(1.0, normal_bg.green * light_factor),
            min(1.0, normal_bg.blue * light_factor),
            normal_bg.alpha
        )
        
        # Schatten-Farbe (dunkler)
        shadow = Gdk.RGBA(
            normal_bg.red * dark_factor,
            normal_bg.green * dark_factor,
            normal_bg.blue * dark_factor,
            normal_bg.alpha
        )
        
        return {
            'text': normal_color,
            'normal_bg': normal_bg,
            'pressed_bg': pressed_bg,
            'highlight': highlight,
            'shadow': shadow
        }
    
    def _apply_css_style(self):
        """Wendet CSS-Styling auf den Button an"""
        sb_config = self.config['soundbutton']
        button_style = self.button.get_style_context()
        
        # Theme-Farben extrahieren
        theme_colors = self.get_theme_colors()
        
        # Einstellungen für Farbe und Bild
        global_bg_color = sb_config.get('background_color', '#cccccc')
        global_text_color = sb_config.get('text_color', '#000000')
        use_global_bg_color = sb_config.get('use_global_bg_color', True)
        use_global_text_color = sb_config.get('use_global_text_color', True)
        use_default_image = sb_config.get('use_default_image', False)
        default_image_file = sb_config.get('default_image_file', "")
        
        # Prüfe, ob benutzerdefinierte Farben für diesen Button gesetzt sind
        use_custom_bg = self.button_config.get('use_custom_bg_color', False)
        use_custom_text = self.button_config.get('use_custom_text_color', False)
        
        # Hintergrundfarbe bestimmen:
        # 1. Individuelle Farbe hat immer Vorrang, wenn gesetzt
        # 2. Wenn keine individuelle Farbe: globale Farbe oder Theme-Farbe je nach Einstellung
        if use_custom_bg and 'background_color' in self.button_config:
            # Individuelle Farbe verwenden
            bg_color = self.button_config['background_color']
        elif use_global_bg_color:
            # Globale Farbe verwenden
            bg_color = global_bg_color
        else:
            # System-Theme-Farbe verwenden
            bg_color = self._rgba_to_hex(theme_colors['normal_bg'])
        
        # Erzeugt RGBA-Objekt für Farbe, um daraus die Effektfarben abzuleiten
        bg_rgba = self._hex_to_rgba(bg_color)
        
        # Gedrückte Farbe als dunklere Version der Hauptfarbe
        pressed_bg = Gdk.RGBA(
            bg_rgba.red * 0.8,
            bg_rgba.green * 0.8,
            bg_rgba.blue * 0.8,
            bg_rgba.alpha
        )
        pressed_bg_hex = self._rgba_to_hex(pressed_bg)
        
        # Highlight (heller) und Schatten (dunkler) aus der Farbe ableiten
        light_factor = 1.35
        dark_factor = 0.65
        
        # Highlight-Farbe (heller)
        highlight = Gdk.RGBA(
            min(1.0, bg_rgba.red * light_factor),
            min(1.0, bg_rgba.green * light_factor),
            min(1.0, bg_rgba.blue * light_factor),
            bg_rgba.alpha
        )
        highlight_hex = self._rgba_to_hex(highlight)
        
        # Schatten-Farbe (dunkler)
        shadow = Gdk.RGBA(
            bg_rgba.red * dark_factor,
            bg_rgba.green * dark_factor,
            bg_rgba.blue * dark_factor,
            bg_rgba.alpha
        )
        shadow_hex = self._rgba_to_hex(shadow)
        
        # Textfarbe bestimmen: 
        # 1. Individuelle Farbe hat immer Vorrang, wenn gesetzt
        # 2. Wenn keine individuelle Farbe: globale Farbe oder Theme-Farbe je nach Einstellung
        if use_custom_text and 'text_color' in self.button_config:
            # Individuelle Farbe verwenden
            text_color = self.button_config['text_color']
        elif use_global_text_color:
            # Globale Farbe verwenden
            text_color = global_text_color
        else:
            # System-Theme-Farbe verwenden
            text_color = self._rgba_to_hex(theme_colors['text'])
        
        # Einzigartige Klasse für diesen Button
        unique_class = f"button-{self.position}"
        
        # Basis-CSS neu erstellen mit verbessertem 3D-Effekt ohne 1px-Rahmen
        css = f"""
        .{unique_class}.sound-button {{
            background-color: {bg_color};
            color: {text_color};
            border-radius: 10px;
            padding: 10px;
            font-weight: bold;
            border-style: none;
            box-shadow: 2px 0px 0px {highlight_hex} inset, 
                       0px 2px 0px {highlight_hex} inset,
                       -2px 0px 0px {shadow_hex} inset,
                       0px -2px 0px {shadow_hex} inset;
            transition: all 0.15s ease;
        }}
        
        .{unique_class}.sound-button:active {{
            background-color: {pressed_bg_hex};
            padding: 12px 8px 8px 12px; /* oben rechts unten links - verschoben für Eindruckeffekt */
            box-shadow: -2px 0px 0px {highlight_hex} inset, 
                       0px -2px 0px {highlight_hex} inset,
                       2px 0px 0px {shadow_hex} inset,
                       0px 2px 0px {shadow_hex} inset;
        }}
        
        .{unique_class}.sound-button-toggled {{
            background-color: {pressed_bg_hex};
            color: {text_color};
            border-radius: 10px;
            padding: 12px 8px 8px 12px; /* oben rechts unten links - verschoben für Eindruckeffekt */
            font-weight: bold;
            border-style: none;
            box-shadow: -2px 0px 0px {highlight_hex} inset, 
                       0px -2px 0px {highlight_hex} inset,
                       2px 0px 0px {shadow_hex} inset,
                       0px 2px 0px {shadow_hex} inset;
            transition: all 0.15s ease;
        }}
        """
        
        if self.is_add_button:
            css += f"""
            .{unique_class}.add-button {{
                font-size: 24px;
                font-weight: bold;
            }}
            """
        else:
            # Hintergrundbild verwenden - priorisiere individuelles Bild, verwende globales als Fallback
            use_image = False
            image_path = None
            
            # Prüfe auf individuelles Bild
            if 'image_file' in self.button_config and self.button_config['image_file']:
                image_path = self.button_config['image_file']
                if os.path.exists(image_path):
                    use_image = True
            
            # Wenn kein individuelles Bild oder es existiert nicht und globales Bild ist aktiviert
            if (not use_image) and use_default_image and default_image_file and os.path.exists(default_image_file):
                image_path = default_image_file
                use_image = True
            
            # Füge CSS für Hintergrundbild hinzu, wenn vorhanden
            if use_image and image_path:
                css += self._get_image_css(unique_class, image_path)
                print(f"Verwende Bild für Button '{self.button_config.get('text', 'Unbekannt')}': {image_path}")
        
        # Füge dem Button die CSS-Klassen hinzu
        button_style.add_class(unique_class)
        button_style.add_class("sound-button")
        
        if self.is_add_button:
            button_style.add_class("add-button")
        
        # Erstelle und lade CSS-Provider nur für diesen spezifischen Button
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        
        # Entferne den alten Provider, falls vorhanden
        if hasattr(self, 'css_provider'):
            button_style.remove_provider(self.css_provider)
        
        # Füge den neuen Provider NUR zum Button-Style-Context hinzu, nicht zum Screen
        button_style.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        # Speichere den Provider für spätere Updates
        self.css_provider = provider
    
    def _get_image_css(self, class_name, image_path):
        """Generiert CSS für ein Hintergrundbild"""
        return f"""
        .{class_name}.sound-button {{
            background-image: url('{image_path}');
            background-position: center;
            background-repeat: no-repeat;
            background-size: contain;
        }}
        
        .{class_name}.sound-button-toggled {{
            background-image: url('{image_path}');
            background-position: center;
            background-repeat: no-repeat;
            background-size: contain;
        }}
        """
    
    def update_image(self, image_path):
        """Aktualisiert das Bild des Buttons sofort"""
        if not image_path or not os.path.exists(image_path):
            return False
            
        # Aktualisiere die Button-Konfiguration
        self.button_config['image_file'] = image_path
        
        # CSS neu anwenden
        self._apply_css_style()
        
        return True
    
    def toggle_button_state(self):
        """Wechselt den Zustand des Buttons (gedrückt/nicht gedrückt)"""
        style_context = self.button.get_style_context()
        
        if not self.is_toggled:
            # Prüfe, ob eine Sounddatei zugeordnet ist
            has_audio = 'audio_file' in self.button_config and self.button_config['audio_file'] and os.path.exists(self.button_config['audio_file'])
            
            # Zum gedrückten Zustand wechseln
            style_context.remove_class("sound-button")
            style_context.add_class("sound-button-toggled")
            self.is_toggled = True
            
            # Sound abspielen, wenn der Button gedrückt wird
            if not self.is_playing and not self.is_add_button:
                if has_audio:
                    self.play_sound()
                else:
                    # Keine Sounddatei vorhanden - sofort wieder deaktivieren
                    print(f"SoundButton '{self.button_config['text']}' - Keine Sounddatei zugeordnet, deaktiviere Button")
                    # Verzögerte Ausführung, damit der Button-Zustand sichtbar ist
                    GLib.timeout_add(150, self._reset_button_state)
        else:
            # Zurück zum normalen Zustand
            style_context.remove_class("sound-button-toggled")
            style_context.add_class("sound-button")
            self.is_toggled = False
            
            # Sound stoppen, wenn der Button losgelassen wird
            if self.is_playing:
                self.stop_sound()
    
    def _reset_button_state(self):
        """Setzt den Button-Zustand zurück (für Buttons ohne Sounddatei)"""
        if self.is_toggled:
            style_context = self.button.get_style_context()
            style_context.remove_class("sound-button-toggled")
            style_context.add_class("sound-button")
            self.is_toggled = False
        return False  # Einmalige Ausführung
    
    def _remove_timer(self):
        """Entfernt einen Timer sicher"""
        if self.fade_source:
            try:
                self.fade_source.destroy()
            except:
                pass  # Ignoriere Fehler beim Entfernen des Timers
            finally:
                self.fade_source = None
                self.fade_timer = None
                self.fade_step_func = None
    
    def play_sound(self):
        """Spielt den Sound ab"""
        if 'audio_file' in self.button_config and self.button_config['audio_file']:
            try:
                # Stelle sicher, dass pygame.mixer initialisiert ist
                if not pygame.mixer.get_init():
                    print("Initialisiere pygame.mixer in SoundButton")
                    pygame.mixer.init()
                    
                if self.sound and self.is_playing:
                    self.stop_sound()
                
                # Stelle sicher, dass der alte Timer gestoppt ist
                self._remove_timer()
                
                self.sound = pygame.mixer.Sound(self.button_config['audio_file'])
                self.sound.set_volume(0.0)  # Starte mit 0 Lautstärke
                
                # Überprüfe ob Endlosschleife aktiviert ist
                if self.button_config.get('loop', False):
                    self.sound.play(-1)  # -1 bedeutet Endlosschleife
                    self.is_looping = True
                else:
                    channel = self.sound.play()
                    self.is_looping = False
                    
                    # Ereignisbehandlung für das Ende des Sounds hinzufügen, wenn verfügbar
                    if channel and hasattr(pygame.mixer, 'Channel'):
                        # Überprüfe periodisch, ob der Sound fertig ist
                        GLib.timeout_add(100, self._check_sound_finished, channel)
                
                self.is_playing = True
                
                # Starte Fade-in
                self._start_fade_in()
                
                print(f"SoundButton '{self.button_config['text']}' - Sound wird abgespielt")
            except Exception as e:
                print(f"Fehler beim Abspielen des Sounds: {e}")
                self.stop_sound()
    
    def _start_fade_in(self):
        """Startet den Fade-in Effekt"""
        if not self.sound or not self.is_playing:
            return
            
        target_volume = self.button_config['volume'] / 100.0
        step_size = target_volume / self.fade_steps
        current_step = 0
        
        def fade_step(user_data=None):
            nonlocal current_step
            if not self.sound or not self.is_playing:
                return False
                
            current_step += 1
            current_volume = min(step_size * current_step, target_volume)
            self.sound.set_volume(current_volume)
            
            if current_step < self.fade_steps:
                return True
            return False
        
        # Stelle sicher, dass der alte Timer gestoppt ist
        self._remove_timer()
        
        # Speichere die Fade-Step-Funktion
        self.fade_step_func = fade_step
        
        # Starte den Fade-in Timer
        self.fade_source = GLib.timeout_source_new(self.fade_duration // self.fade_steps)
        self.fade_source.set_callback(self.fade_step_func)
        self.fade_source.attach()
        self.fade_timer = self.fade_source.get_id()
    
    def _check_sound_finished(self, channel):
        """Überprüft, ob der Sound fertig ist"""
        try:
            if not self.sound or not self.is_playing:
                return False
                
            if not channel.get_busy() and self.is_playing and not self.is_looping:
                # Sound ist fertig, Button deaktivieren
                self.stop_sound()
                # Stelle sicher, dass der Button-Zustand korrekt ist
                if self.is_toggled:
                    style_context = self.button.get_style_context()
                    style_context.remove_class("sound-button-toggled")
                    style_context.add_class("sound-button")
                    self.is_toggled = False
                return False  # Timer stoppen
            
            # Sound läuft noch, Timer weiterlaufen lassen
            return True
        except pygame.error as e:
            print(f"Fehler bei Soundüberprüfung: {e}")
            return False # Bei Fehlern Timer beenden
        except Exception as e:
            print(f"Unerwarteter Fehler bei Soundüberprüfung: {e}")
            return False
    
    def stop_sound(self):
        """Stoppt den Sound"""
        if self.sound and self.is_playing:
            try:
                # Stelle sicher, dass pygame.mixer initialisiert ist
                if not pygame.mixer.get_init():
                    print("Initialisiere pygame.mixer in SoundButton (stop_sound)")
                    pygame.mixer.init()
                
                # Stelle sicher, dass der alte Timer gestoppt ist
                self._remove_timer()
                
                # Starte Fade-out
                self._start_fade_out()
                
                # Stelle sicher, dass der Button-Zustand korrekt ist
                if self.is_toggled:
                    style_context = self.button.get_style_context()
                    style_context.remove_class("sound-button-toggled")
                    style_context.add_class("sound-button")
                    self.is_toggled = False
                
            except Exception as e:
                print(f"Fehler beim Stoppen des Sounds: {e}")
    
    def _start_fade_out(self):
        """Startet den Fade-out Effekt"""
        if not self.sound or not self.is_playing:
            return
            
        start_volume = self.sound.get_volume()
        step_size = start_volume / self.fade_steps
        current_step = 0
        
        def fade_step(user_data=None):
            nonlocal current_step, start_volume
            if not self.sound or not self.is_playing:
                return False
                
            current_step += 1
            current_volume = max(start_volume - (step_size * current_step), 0.0)
            self.sound.set_volume(current_volume)
            
            if current_step < self.fade_steps:
                return True
                
            # Nach Fade-out den Sound stoppen
            self.sound.stop()
            self.is_playing = False
            self.is_looping = False
            
            # Button-Status zurücksetzen, wenn er gedrückt ist
            if self.is_toggled:
                style_context = self.button.get_style_context()
                style_context.remove_class("sound-button-toggled")
                style_context.add_class("sound-button")
                self.is_toggled = False
            
            print(f"SoundButton '{self.button_config['text']}' - Sound gestoppt")
            return False
        
        # Stelle sicher, dass der alte Timer gestoppt ist
        self._remove_timer()
        
        # Speichere die Fade-Step-Funktion
        self.fade_step_func = fade_step
        
        # Starte den Fade-out Timer
        self.fade_source = GLib.timeout_source_new(self.fade_duration // self.fade_steps)
        self.fade_source.set_callback(self.fade_step_func)
        self.fade_source.attach()
        self.fade_timer = self.fade_source.get_id()
    
    def on_button_press(self, widget, event):
        """Handler für Mausklicks"""
        # Rechtsklick auf Button für Einstellungsdialog
        if event.button == 3 and not self.is_add_button:  # Rechtsklick (3) und kein Add-Button
            if not self.settings_dialog_open:
                self.show_settings_dialog()
            return True
            
        # Langklick-Erkennung nur für Linksklick starten
        if event.button == 1:  # Linksklick
            self.press_start_time = event.time
            
            # Timer für Langklick starten, nur wenn kein Dialog bereits geöffnet ist
            if not self.settings_dialog_open and not self.press_timeout_id:
                self.press_timeout_id = GLib.timeout_add(self.LONG_PRESS_TIME, 
                                                       self.check_long_press)
            
            if self.is_add_button:  # Linksklick auf Add-Button
                if hasattr(self, 'on_add_click'):
                    self.on_add_click(self)
                return True
            
        return False
    
    def on_button_release(self, widget, event):
        """Handler für Maus-Loslassen-Event"""
        # Timer löschen wenn Button losgelassen wird bevor Langklick erkannt wurde
        if self.press_timeout_id:
            GLib.source_remove(self.press_timeout_id)
            self.press_timeout_id = None
        
        # Normale Button-Aktion (Toggle Sound abspielen/stoppen) ausführen
        if event.button == 1 and not self.is_add_button:
            self.toggle_button_state()
        
        return False
    
    def check_long_press(self):
        """Prüft, ob ein Langklick erkannt wurde"""
        # Verwende die aktuelle Zeit in Millisekunden
        elapsed = GLib.get_monotonic_time() / 1000 - self.press_start_time
        
        if elapsed >= self.LONG_PRESS_TIME:
            # Langklick erkannt, Einstellungsdialog anzeigen
            if not self.is_add_button and not self.settings_dialog_open:
                self.show_settings_dialog()
            self.press_timeout_id = None
            return False  # Timer nicht wiederholen
        
        # Timer fortsetzen
        return True
    
    def show_settings_dialog(self):
        """Zeigt den Einstellungsdialog"""
        if self.settings_dialog_open:
            print(f"Button {self.position}: Settings-Dialog ist bereits geöffnet!")
            return
            
        print(f"Button {self.position}: Öffne Settings-Dialog...")
        self.settings_dialog_open = True
        
        dialog = SettingsDialog(self.get_toplevel(), self.button_config, self.position, self.on_delete)
        response = dialog.show()
        
        # Dialog ist jetzt geschlossen
        self.settings_dialog_open = False
        
        # Aktualisiere den Button, wenn sich Einstellungen geändert haben
        if response == Gtk.ResponseType.OK:
            self._update_button_after_settings()
    
    def _update_button_after_settings(self):
        """Aktualisiert den Button nach dem Ändern der Einstellungen"""
        # Nur für normale Buttons, nicht für Add-Buttons
        if not self.is_add_button:
            print(f"Aktualisiere Button {self.position} nach Einstellungsänderung (vollständige Neuzeichnung)")
            
            # Komplette Neuinitialisierung des Buttons
            sb_config = self.config['soundbutton']
            
            # 1. Entferne alle Widgets vom Button-Container
            for child in self.get_children():
                self.remove(child)
                
            # 2. Erstelle den Button komplett neu
            # Container für Button und Regler
            self.button_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.button_container.set_size_request(sb_config['button_width'], sb_config['button_height'])
            
            # Container für den Button
            self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            self.button_box.set_size_request(sb_config['button_width'], sb_config['button_height'])
            
            # Erstelle einen normalen Button
            button_width = sb_config['button_width']
            self.button = Gtk.Button()
            self.button.set_size_request(button_width, sb_config['button_height'])
            
            # Anstatt direkt das Label zu setzen, erstellen wir ein Label-Widget,
            # das Zeilenumbrüche unterstützt
            button_text = self.button_config['text']
            
            # Wir erstellen ein Label-Widget
            self.label = Gtk.Label()
            
            # Einfache Ersetzung von \n für bessere Zeilenumbrüche
            if '\\n' in button_text:
                button_text = button_text.replace('\\n', '\n')
                print(f"Verarbeite Zeilenumbrüche in Text: '{button_text}'")
            
            self.label.set_text(button_text)
            self.label.set_use_markup(True)  # Ermöglicht Markup (z.B. <b>, <i>, etc.)
            
            # Aktiviere Zeilenumbrüche im Label - verwende individuelle oder globale Einstellung
            line_breaks = self.button_config.get('line_breaks')
            if line_breaks is None:  # Wenn nicht gesetzt, verwende globale Einstellung
                line_breaks = sb_config.get('line_breaks', True)
                self.button_config['line_breaks'] = line_breaks
            
            self.label.set_line_wrap(line_breaks)
            self.label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            print(f"Zeilenumbrüche sind {'aktiviert' if line_breaks else 'deaktiviert'}")
            
            # Textausrichtung gemäß individueller oder globaler Konfiguration
            text_align = self.button_config.get('text_align')
            if text_align is None or text_align == "":  # Wenn nicht gesetzt, verwende globale Einstellung
                text_align = sb_config.get('text_align', 'center')
                self.button_config['text_align'] = text_align
            
            if text_align == 'left':
                self.label.set_justify(Gtk.Justification.LEFT)
                self.label.set_halign(Gtk.Align.START)
            elif text_align == 'right':
                self.label.set_justify(Gtk.Justification.RIGHT)
                self.label.set_halign(Gtk.Align.END)
            else:  # center (default)
                self.label.set_justify(Gtk.Justification.CENTER)
                self.label.set_halign(Gtk.Align.CENTER)
            print(f"Textausrichtung ist '{text_align}'")
            
            # Zusätzliche Anpassungen für die Textposition im Button
            # Prüfen, ob individuelle Textposition verwendet werden soll
            use_custom_position = self.button_config.get('use_custom_text_position')
            if use_custom_position is None:  # Wenn nicht gesetzt, verwende globale Einstellung
                use_custom_position = sb_config.get('use_custom_text_position', False)
                self.button_config['use_custom_text_position'] = use_custom_position
            
            # Zurücksetzen aller Margins
            self.label.set_margin_top(0)
            self.label.set_margin_bottom(0)
            self.label.set_margin_start(0)
            self.label.set_margin_end(0)
            
            # Wenn individuelle Positionierung verwendet wird, immer linksbündig und von oben ausgerichtet
            if use_custom_position:
                # Position von der oberen linken Ecke - verwende individuelle oder globale Werte
                margin_top = self.button_config.get('text_margin_top')
                if margin_top is None:
                    margin_top = sb_config.get('text_margin_top', 0)
                    self.button_config['text_margin_top'] = margin_top
                
                margin_left = self.button_config.get('text_margin_left')
                if margin_left is None:
                    margin_left = sb_config.get('text_margin_left', 0)
                    self.button_config['text_margin_left'] = margin_left
                
                # Setze Margins für die Position
                self.label.set_margin_top(margin_top)
                self.label.set_margin_start(margin_left)
                
                # Absolute Positionierung für den Text
                self.label.set_valign(Gtk.Align.START)  # Immer von oben ausgerichtet
                self.label.set_halign(Gtk.Align.START)  # Immer von links ausgerichtet
                
                # Label sollte den gesamten Button-Bereich nutzen können
                self.label.set_hexpand(True)
                self.label.set_vexpand(True)
                
                print(f"Individuelle Textposition aktiviert: top={margin_top}, left={margin_left}")
            else:
                print("Keine individuelle Textposition verwendet")
            
            # Wichtig: Label muss sichtbar sein
            self.label.show()
            # Füge das Label zum Button hinzu
            self.button.add(self.label)
            
            # Event-Handler für Button
            self.button.connect("button-press-event", self.on_button_press)
            self.button.connect("button-release-event", self.on_button_release)
            
            # Button zum Container hinzufügen
            self.button_box.pack_start(self.button, True, True, 0)
            
            # Button-Box zum Hauptcontainer hinzufügen
            self.button_container.pack_start(self.button_box, True, True, 0)
            
            # Lautstärkeregler als Overlay erstellen
            # Overlay, um den Lautstärkeregler über den Button zu legen
            self.overlay = Gtk.Overlay()
            self.overlay.add(self.button_container)
            
            # Lautstärkeregler erstellen
            self._create_volume_slider(sb_config)
            
            # Lautstärkeregler rechts positionieren
            self.volume_container.set_halign(Gtk.Align.END)
            self.volume_container.set_valign(Gtk.Align.FILL)
            self.volume_container.set_margin_end(5)  # Abstand zum rechten Rand
            
            # Lautstärkeregler zum Overlay hinzufügen
            self.overlay.add_overlay(self.volume_container)
            
            # Overlay zum Hauptcontainer hinzufügen
            self.pack_start(self.overlay, True, True, 0)
            
            # 3. Gestalte das neu erstellte Widget mit CSS
            self._apply_css_style()
            
            # 4. Alles anzeigen
            self.show_all()
            
            # 5. Nochmals erzwingen, dass der Button neu gezeichnet wird
            self.button.queue_resize()
            self.button.queue_draw()
            self.button_container.queue_resize()
            self.button_container.queue_draw()
            self.button_box.queue_resize()
            self.button_box.queue_draw()
            self.overlay.queue_resize()
            self.overlay.queue_draw()
            self.queue_resize()
            self.queue_draw()
            
            print(f"Button {self.position} vollständig neu gezeichnet!")
    
    def on_volume_changed(self, volume_slider):
        """Handler für Änderungen am Lautstärkeregler"""
        try:
            value = int(volume_slider.get_value())  # Konvertiere zu Ganzzahl
            self.button_config['volume'] = value
            
            # Stelle sicher, dass pygame.mixer initialisiert ist, bevor Lautstärke gesetzt wird
            if self.sound:
                if not pygame.mixer.get_init():
                    print("Initialisiere pygame.mixer in on_volume_changed")
                    pygame.mixer.init()
                    # Rekonstruiere den Sound, da er nach Mixer-Neuinitialisierung verlorengegangen ist
                    if 'audio_file' in self.button_config and self.button_config['audio_file']:
                        self.sound = pygame.mixer.Sound(self.button_config['audio_file'])
                
                self.sound.set_volume(value / 100.0)
            
            print(f"'{self.button_config['text']}' - Lautstärke auf {value} gesetzt")
        except pygame.error as e:
            print(f"Pygame-Fehler beim Setzen der Lautstärke: {e}")
        except Exception as e:
            print(f"Fehler beim Setzen der Lautstärke: {e}")
    
    def set_add_click_handler(self, handler):
        """Setzt den Handler für Klicks auf den Add-Button"""
        self.on_add_click = handler
    
    def _hex_to_rgba(self, hex_color):
        """Konvertiert einen Hex-Farbcode in ein RGBA-Objekt"""
        if not hex_color or not hex_color.startswith('#'):
            hex_color = '#cccccc'  # Standard-Grau als Fallback
            
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:  # Kurze Hex-Notation (#RGB)
            hex_color = ''.join([c*2 for c in hex_color])
            
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        rgba = Gdk.RGBA()
        rgba.red = r
        rgba.green = g
        rgba.blue = b
        rgba.alpha = 1.0
        return rgba