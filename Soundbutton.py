import gi    # Importiere gi, um die GTK-Bibliothek zu verwenden
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf
import pygame
import os
import json
from urllib.parse import unquote

#############################################################################################################
class Soundbutton(Gtk.EventBox):
    def __init__(self, parent=None, default_button=None, button_config=None, position=None):
        super().__init__()
        self.parent = parent # kann None sein, da wir dann das Kontextmenu abschalten

        if default_button is not None:
            self.default_button   = default_button
        else:
            self.default_button   = self.create_default_button()
        
        if button_config is not None:
            self.button_config    = button_config
        else:
            self.button_config    = self.create_minimal_button(position)
        
        self.sound                = None
        self.channel              = None
        self.timer_id             = None
        self.is_pressed           = False
        self.last_click_time      = 0       # Für Cooldown
        self.drag_started         = False   # Für Drag-and-Drop
        self.click_position       = None    # Für Drag-and-Drop
        self.changed_volume       = False   # Für Slider-Klick

        self.set_size_request(150, 75)
        self.set_hexpand(False)             # EventBox horizontal NICHT ausdehnen
        self.set_vexpand(False)             # EventBox vertikal NICHT ausdehnen	
        self.connect("button-press-event", self.on_eventbox_click)
        
        # Drag-and-Drop-Funktionalität hinzufügen
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)
        
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("button-release-event", self.on_button_release)
        self.connect("drag-begin", self.on_drag_begin)
        
        # Drag-and-Drop-Quelle und Ziel konfigurieren
        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE)
        self.drag_source_add_text_targets()
        target_entries = Gtk.TargetEntry.new("text/uri-list", 0, 0)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [target_entries], Gdk.DragAction.COPY | Gdk.DragAction.MOVE)
        self.drag_dest_add_text_targets()
        
        self.connect("drag-data-get", self.on_drag_data_get)
        self.connect("drag-data-received", self.on_drag_data_received)
        
        # Füge die sound-button-Klasse zum EventBox hinzu
        self.get_style_context().add_class("sound-button")
        
        # Erstelle eine horizontale Box für Text und Slider
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_hexpand(True)
        hbox.set_vexpand(True)
        self.add(hbox)

        # Füge Text hinzu
        self.text_label = Gtk.Label(label=button_config['text'])
        self.text_label.set_hexpand(True)
        self.text_label.set_halign(Gtk.Align.START)  # Box-Ausrichtung: links
        self.text_label.set_valign(Gtk.Align.START)  # Box-Ausrichtung: oben
        self.text_label.set_line_wrap(True)          # Zeilenumbruch aktivieren
        self.text_label.set_justify(Gtk.Justification.CENTER)  # Text in sich zentrieren
                   
        # Setze Text-Position basierend auf Konfiguration
        if 'use_custom_text_position' in button_config and button_config['use_custom_text_position']:
            self.text_label.set_margin_start(button_config['text_x'])
            self.text_label.set_margin_top(button_config['text_y'])
        else:
            self.text_label.set_margin_start(self.default_button['text_x'])
            self.text_label.set_margin_top(self.default_button['text_y'])

        # Setze Text-Ausrichtung
        align_map = {
            "left":   Gtk.Justification.LEFT,
            "center": Gtk.Justification.CENTER,
            "fill":   Gtk.Justification.FILL,
            "right":  Gtk.Justification.RIGHT
        }
        
        if 'text_align' in button_config:
            self.text_label.set_justify(align_map.get(button_config['text_align'], Gtk.Justification.CENTER))
        else:
            self.text_label.set_justify(align_map.get(self.default_button['text_align'], Gtk.Justification.CENTER))

        hbox.pack_start(self.text_label, True, True, 0)

        self.status_icon = Gtk.Label(label="🔇")
        self.status_icon.set_halign(Gtk.Align.END)  # Box-Ausrichtung: rechts
        self.status_icon.set_valign(Gtk.Align.START)  # Box-Ausrichtung: oben
        hbox.pack_start(self.status_icon, False, False, 0)  # Füge den Slider zur horizontalen Box hinzu
        self.status_icon.set_margin_top(5)
        #self.status_icon.get_style_context().add_class("status-icon")
        #self.status_icon.set_margin_top(self.default_button['text_y'])
        #self.status_icon.set_margin_end(5)
        #self.status_icon.set_text("∞")
        #self.status_icon.set_text("🔊")
        #self.status_icon.set_text("")

       # Initialisiere das Status-Icon basierend auf den Button-Eigenschaften
        self.update_status_icon()

        # Erstelle einen Slider (Gtk.Scale)
        self.volume = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL, 0, 100, 1)
        self.volume.set_hexpand(False)       # Slider horizontal NICHT ausdehnen
        self.volume.set_vexpand(True)        # Slider vertikal ausdehnen	
        self.volume.set_draw_value(False)    # Zeige den Wert NICHT an
        self.volume.set_digits(0)            # Keine Dezimalstellen
        self.volume.set_inverted(True)       # Invertiere die Skala
        self.volume.set_margin_top(3) 
        self.volume.set_margin_bottom(3)
        self.volume.set_margin_end(3)        # Rechter Rand
        self.volume.set_halign(Gtk.Align.END)# Am rechten Rand ausrichten
        
        # Setze den initialen Lautstärkewert
        if 'volume' in button_config:
            self.volume.set_value(button_config['volume'])
        else:
            self.volume.set_value(self.default_button['volume'])
            self.button_config['volume'] = self.default_button['volume'] # Speichere den neuen Wert in der Konfiguration

        # Verbinde den Slider mit der Lautstärkeregelung
        self.volume.connect("value-changed", self.on_volume_changed)

        # Lade den Sound beim Initialisieren
        if 'audio_file' in button_config and button_config['audio_file']:
            try:
                # Konstruiere den vollständigen Pfad mit Prefix
                full_sound_path = os.path.join(self.default_button['soundpfad_prefix'], button_config['audio_file'])
                self.sound = pygame.mixer.Sound(full_sound_path)        # Lade den Sound
                self.sound.set_volume(button_config['volume'] / 100.0)  # Setze die Lautstärke
            except Exception as e:
                print(f"Fehler beim Laden des Sounds: {e}")

        hbox.pack_start(self.volume, False, False, 0)  # Füge den Slider zur horizontalen Box hinzu

        # EventBox CSS-Klasse setzen
        self.get_style_context().add_class("sound-button")
        
        # Basis-CSS für alle Buttons
        self.apply_colors_and_css()
        
        # Individuelle Farben setzen, wenn konfiguriert
        if button_config.get('use_custom_bg_color', False) or button_config.get('use_custom_text_color', False):
            self.apply_colors_and_css()
        
        # Setze Hintergrundbild basierend auf Konfiguration
        #if 'image_file' in button_config and button_config['image_file']:
        #    self.apply_custom_image()
        #elif self.default_button['use_custom_image'] and self.default_button['image_file']:
        #    self.apply_default_image()
        self.apply_image()

    #########################################################################################################
    def apply_colors_and_css(self):
        """Wendet die Farben und die Basis-CSS-Einstellungen auf den Button an"""
        # Hole die globalen Einstellungen
        button_width = self.default_button['button_width']
        button_height = self.default_button['button_height']
        button_radius = self.default_button['button_radius']
        button_spacing = self.default_button['button_spacing']
        text_size = self.default_button['text_size']
        
        # Bestimme die Text-Farbe
        if self.button_config.get('use_custom_text_color', False) and 'text_color' in self.button_config and self.button_config['text_color']:
            text_color = self.button_config['text_color']
        elif self.default_button['use_custom_text_color']:
            text_color = self.default_button['text_color']
        else: # Wenn keine individuelle Textfarbe eingestellt ist, wird die Theme-Textfarbe verwendet
            temp_button = Gtk.Button()
            style = temp_button.get_style_context()
            erg, tc = style.lookup_color("theme_text_color")
            text_color = f"#{int(tc.red * 255):02x}{int(tc.green * 255):02x}{int(tc.blue * 255):02x}"

        # Bestimme die Hintergrundfarbe
        if self.button_config.get('use_custom_bg_color', False) and 'background_color' in self.button_config and self.button_config['background_color']:
            bg_color = self.button_config['background_color']
            # Berechne die abgeleiteten Farben
            r = int(bg_color[1:3], 16)
            g = int(bg_color[3:5], 16)
            b = int(bg_color[5:7], 16)
            highlight_color = f"#{int(min(255, r*1.3)):02x}{int(min(255, g*1.3)):02x}{int(min(255, b*1.3)):02x}"
            pressed_color = f"#{int(r*0.9):02x}{int(g*0.9):02x}{int(b*0.9):02x}"
            shadow_color = f"#{int(r*0.7):02x}{int(g*0.7):02x}{int(b*0.7):02x}"
        elif self.default_button['use_custom_bg_color'] and 'background_color' in self.default_button and self.default_button['background_color']:
            bg_color = self.default_button['background_color']
            # Berechne die abgeleiteten Farben
            r = int(bg_color[1:3], 16)
            g = int(bg_color[3:5], 16)
            b = int(bg_color[5:7], 16)
            highlight_color = f"#{int(min(255, r*1.3)):02x}{int(min(255, g*1.3)):02x}{int(min(255, b*1.3)):02x}"
            pressed_color = f"#{int(r*0.9):02x}{int(g*0.9):02x}{int(b*0.9):02x}"
            shadow_color = f"#{int(r*0.7):02x}{int(g*0.7):02x}{int(b*0.7):02x}"
        else: # Wenn keine individuelle Hintergrundfarbe eingestellt ist, wird die Theme-Hintergrundfarbe verwendet
            temp_button = Gtk.Button()
            style = temp_button.get_style_context()
            erg, c = style.lookup_color("theme_bg_color")
            highlight_color = f"#{int(min(255, c.red*255*1.3)):02x}{int(min(255, c.green*255*1.3)):02x}{int(min(255, c.blue*255*1.3)):02x}"
            bg_color        = f"#{int(c.red*255*1.0):02x}{int(c.green*255*1.0):02x}{int(c.blue*255*1.0):02x}"
            pressed_color   = f"#{int(c.red*255*0.9):02x}{int(c.green*255*0.9):02x}{int(c.blue*255*0.9):02x}"
            shadow_color    = f"#{int(c.red*255*0.7):02x}{int(c.green*255*0.7):02x}{int(c.blue*255*0.7):02x}"
        
        # Basis-CSS für alle Buttons
        css = f"""
        .sound-button {{
            background-color: {bg_color};
            color: {text_color};
            border-radius: {button_radius}px;
            padding: {button_spacing}px;
            min-width: {button_width}px;
            min-height: {button_height}px;
            font-weight: bold;
            font-size: {text_size}px;
            border-style: solid;
            border-width: 2px;
            border-color: {highlight_color} {shadow_color} {shadow_color} {highlight_color};
            transition: all 0.05s ease;
        }}

        .sound-button-active {{
            background-color: {pressed_color};
            color: {text_color};
            border-radius: {button_radius}px;
            padding: {button_spacing+2}px {button_spacing-2}px {button_spacing-2}px {button_spacing+2}px;
            min-width: {button_width}px;
            min-height: {button_height}px;
            font-weight: bold;
            font-size: {text_size}px;
            border-style: solid;
            border-width: 2px;
            border-color: {shadow_color} {highlight_color} {highlight_color} {shadow_color};
            transition: all 0.05s ease;
        }}

        .status-icon {{
            font-weight: bold;
            font-size: 20px;
        }}
        """
        #    font-size: {text_size+10}px;
        
        # CSS Provider erstellen und anwenden
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode())
        self.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.status_icon.get_style_context().add_class("status-icon")
        
        # Füge die sound-button-Klasse zum EventBox hinzu
        self.get_style_context().add_class("sound-button")

    #########################################################################################################
    def apply_image(self):
        """Wendet ein Hintergrundbild auf den Button an wenn eines eingestellt ist."""
        if self.button_config.get('image_file', False): # Wenn ein individuelles Bild eingestellt ist            
            self.get_style_context().add_class("sound-button-with-image") 
            # Lade den X Positionierungswert    
            print(f"use button individual image")
            
            if 'image_x' in self.button_config:
                image_x = self.button_config['image_x']
            else:
                image_x = self.default_button['image_x']
            # Lade den Y Positionierungswert    
            if 'image_y' in self.button_config:
                image_y = self.button_config['image_y']
            else:
                image_y = self.default_button['image_y']
            # Lade den Skalierungsfaktor    
            if 'image_scale' in self.button_config:
                image_scale = self.button_config['image_scale']
            else:
                image_scale = self.default_button['image_scale']
            # Prüfe ob AUTO Skalierung gewünscht ist
            if image_scale == 0 or image_scale is None:
                background_size = "contain"
            else:
                background_size = f"{image_scale}% auto"
            # Hole den vollständigen Bildpfad
            if 'image_file' in self.button_config:
                full_image_path = os.path.join(self.default_button['imagepfad_prefix'], self.button_config['image_file'])
            else:
                #full_image_path = os.path.join(self.default_button['imagepfad_prefix'], self.default_button['image_file'])
                full_image_path = None
            #self.get_style_context().add_class("sound-button-with-image")
        
            print(f"full_image_path: {full_image_path}")
            print(f"image_x: {image_x}")
            print(f"image_y: {image_y}")
            print(f"image_scale: {image_scale}")

            provider = Gtk.CssProvider()
            provider.load_from_data(f"""
                .sound-button-with-image {{
                    background-image: url("{full_image_path}");
                    background-repeat: no-repeat;
                    background-position: calc(100% - {image_x}px) {image_y}px;
                    background-size: {background_size};
                }}
            """.encode())
            self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        elif self.default_button['use_custom_image'] and self.default_button['image_file']:
            self.get_style_context().add_class("sound-button-with-image") 
            print(f"use default button image")
            # Hole die Positionierungswerte
            image_x = self.default_button['image_x']
            image_y = self.default_button['image_y']
            image_scale = self.default_button['image_scale']
            # Prüfe ob AUTO Skalierung gewünscht ist
            if image_scale == 0 or image_scale is None:
                background_size = "contain"
            else:
                background_size = f"{image_scale}% auto"
            # Hole den vollständigen Bildpfad
            full_image_path = os.path.join(self.default_button['imagepfad_prefix'], self.default_button['image_file'])
        
            provider = Gtk.CssProvider()
            provider.load_from_data(f"""
                .sound-button-with-image {{
                    background-image: url("{full_image_path}");
                    background-repeat: no-repeat;
                    background-position: calc(100% - {image_x}px) {image_y}px;
                    background-size: {background_size};
                }}
            """.encode())
            self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        else:
            self.get_style_context().remove_class("sound-button-with-image")    

    #########################################################################################################
    def on_volume_changed(self, scale):
        """Handler für Lautstärkeänderungen"""
        self.changed_volume = True
        volume = scale.get_value()
        # Runde den Volumenwert auf eine Ganzzahl
        volume_int = int(round(volume))
        if self.sound:
            self.sound.set_volume(volume_int / 100.0)
        self.button_config['volume'] = volume_int # Speichere den gerundeten Wert in der Konfiguration
        if self.parent and self.parent.config:
            self.parent.config.mark_changed()  # Markiere Änderungen

    #########################################################################################################
    def activate_button(self):
        """Aktiviert den Button visuell und spielt den Sound ab"""
        # Wenn der Button bereits aktiv ist, nichts tun
        if self.is_pressed:
            self.deactivate_button()              # Deaktiviere den Button
            return True
            
        style_context = self.get_style_context()
        style_context.remove_class("sound-button")
        style_context.add_class("sound-button-active")
        self.is_pressed = True

        """Spielt den Sound ab"""
        if self.sound:
            try:
                if self.button_config.get('loop', False):   # Wenn Endlosschleife
                    self.channel = self.sound.play(-1)
                else:    
                    self.channel = self.sound.play(0)
                    self.timer_id = GLib.timeout_add(100, self.check_sound_end)
            except Exception as e:
                print(f"Fehler beim Abspielen des Sounds: {e}")

    #########################################################################################################
    def check_sound_end(self):
        """Prüft, ob der Sound zu Ende ist und deaktiviert den Button"""
        if not self.sound or not self.channel:
            if self.timer_id:
                GLib.source_remove(self.timer_id)
                self.timer_id = None
            return False
            
        if self.button_config.get('loop', False): # Im Endlosschleifen-Modus nicht prüfen
            return True
            
        if not self.channel.get_busy():           # Sound ist zu Ende
            self.deactivate_button()              # Deaktiviere den Button
            return False
            
        return True  # Timer weiterlaufen lassen

    #########################################################################################################
    def deactivate_button(self):
        """Deaktiviert den Button visuell und stoppt den Sound"""
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
        # Button Visuell zurücksetzen    
        style_context = self.get_style_context()
        style_context.remove_class("sound-button-active")
        style_context.add_class("sound-button")
        self.is_pressed = False
        # Stoppt den Sound
        if self.sound and self.channel:
            self.channel.stop()
            self.channel = None

    #########################################################################################################
    def on_motion_notify(self, widget, event):
        """Handler für Mausbewegungen, um Drag-and-Drop zu starten"""
        if event.state & Gdk.ModifierType.BUTTON1_MASK and self.click_position:
            dx = abs(event.x_root - self.click_position[0])
            dy = abs(event.y_root - self.click_position[1])
            if (dx > 8 or dy > 8) and not self.drag_started:
                self.drag_started = True
                # Erstelle eine TargetList für Text
                targets = Gtk.TargetList.new([])
                targets.add_text_targets(0)
                # Starte den Drag-Vorgang mit einem gültigen Objekt
                self.drag_begin_with_coordinates(targets, Gdk.DragAction.MOVE, 1, event, event.x_root, event.y_root)

    #########################################################################################################
    def on_button_release(self, widget, event):
        """Handler für das Loslassen der Maustaste"""
        if not self.drag_started and event.button == 1:
            # Prüfe, ob der Slider gerade bewegt wird
            #if self.volume.get_state_flags() & Gtk.StateFlags.ACTIVE:
            if self.changed_volume:
                self.changed_volume = False # Ende der Lautstärkeänderung
                return True  # Wenn der Slider aktiv ist, ignoriere den Klick
            
            # Wenn kein Drag-and-Drop gestartet wurde, normalen Klick behandeln
            if self.is_pressed:           # Zurück zum normalen Zustand
                self.deactivate_button()  # Komplette Deaktivierung des Buttons                
            else:                         # Zum gedrückten Zustand wechseln
                self.activate_button()    # Komplette Aktivierung des Buttons
        self.drag_started = False
        self.click_position = None

    #########################################################################################################
    def on_drag_begin(self, widget, drag_context):
        """Handler für den Beginn des Drag-and-Drop-Vorgangs"""
        # Erstelle ein Pixbuf für die Vorschau
        alloc = self.get_allocation()
        
        # Hole den Stilkontext und zeichne den Button
        style_context = self.get_style_context()
        style_context.save()
        style_context.add_class("sound-button")
        
        # Erstelle einen Cairo-Kontext für das Pixbuf
        window = self.get_window()
        if window:
            cr = window.cairo_create()
            
            # Zeichne den Button
            Gtk.render_background(style_context, cr, 0, 0, alloc.width, alloc.height)
            Gtk.render_frame(style_context, cr, 0, 0, alloc.width, alloc.height)
            
            # Zeichne den Text
            layout = self.text_label.get_layout()
            layout.set_text(self.text_label.get_text(), -1)
            text_width, text_height = layout.get_pixel_size()
            text_x = (alloc.width - text_width) / 2
            text_y = (alloc.height - text_height) / 2
            
            Gtk.render_layout(style_context, cr, text_x, text_y, layout)
            
            # Konvertiere den Cairo-Kontext in ein Pixbuf
            surface = cr.get_target()
            pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, alloc.width, alloc.height)
            
            # Setze das Pixbuf als Drag-Icon
            Gtk.drag_set_icon_pixbuf(drag_context, pixbuf, 0, 0)
        
        # Stelle den Stilkontext wieder her
        style_context.restore()

    #########################################################################################################
    def on_drag_data_get(self, widget, drag_context, data, info, time):
        """Handler für das Abrufen der Drag-and-Drop-Daten"""
        # Erstelle eine portable Version der Button-Konfiguration
        if self.parent and self.parent.config:
            portable_config = self.parent.config.create_portable_config(self.button_config)
            # Konvertiere die Konfiguration in einen JSON-String
            data.set_text(json.dumps(portable_config), -1)
        else:
            # Fallback: Nur die Position senden
            data.set_text(str(self.button_config['position']), -1)

    #########################################################################################################
    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        """Handler für das Empfangen der Drag-and-Drop-Daten"""
        uris = data.get_uris()
        if uris:
            print("Elementanzahl: ", len(uris))
            print(f"uris: {uris}")
            for uri in uris:

                path = unquote(uri.replace("file://", "").strip())                 # Datei-URI -> Pfad dekodieren
                path = os.path.abspath(path)                                       # Sicherheitshalber echte Pfade auflösen
                print("Dateipfad empfangen:", path)
                if path.endswith(('.jpg', '.png')):                                # Bilddatei erkannt
                    print("Bilddatei:", path)
                    if not self.button_config.get('image_file', False):
                        self.button_config['image_file'] = path
                        self.apply_image()
                elif path.endswith(('.mp3', '.wav')):                  # Audio-Datei erkannt
                    print("Audio-Datei:", path)
                    if not self.button_config.get('audio_file', False):
                        #self.button_config['audio_file'] = path
                        self.add_sound(path)
                        self.update_status_icon()
                else:
                    print("Nicht unterstützter Dateityp.")
        else:
            #print("Keine URIs empfangen")
            try:
                # Versuche, die Daten als JSON zu parsen
                portable_config = json.loads(data.get_text())
                
                # Prüfe, ob es sich um ein Drag & Drop innerhalb des gleichen Boards handelt
                if self.parent and self.parent.config:
                    if 'CopyOf' in portable_config:
                        source_board = portable_config['CopyOf']
                        current_board = os.path.splitext(os.path.basename(self.parent.config.config_file))[0] if self.parent.config.config_file else "unnamed_soundboard"
                        
                        if source_board == current_board:
                            # Internes Drag & Drop: Nur Position ändern
                            source_position = portable_config['position']
                            target_position = self.button_config['position']
                            
                            if source_position != target_position:
                                print(f"Button von Position {source_position} nach {target_position} verschoben")
                                self.parent.move_button(current_position=source_position, new_position=target_position)
                        else:
                            # Externes Drag & Drop: Button kopieren
                            print(f"Button von Board '{source_board}' nach '{current_board}' kopiert")
                            if self.parent.config.add_portable_button(portable_config, target_position=self.button_config['position']):
                                print("Button erfolgreich kopiert")
                                # Aktualisiere die Anzeige
                                self.parent.update_buttons()
                            else:
                                print("Fehler beim Kopieren des Buttons")
                                Gtk.drag_finish(drag_context, False, False, time)
                                return
                    else:
                        # Altes Format: Nur Position
                        source_position = int(portable_config)
                        target_position = self.button_config['position']
                        
                        if source_position != target_position:
                            print(f"Button von Position {source_position} nach {target_position} verschoben")
                            self.parent.move_button(current_position=source_position, new_position=target_position)
                
                Gtk.drag_finish(drag_context, True, False, time)
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                print(f"Fehler beim Verarbeiten der Drag & Drop-Daten: {e}")
                Gtk.drag_finish(drag_context, False, False, time)

    #########################################################################################################
    def on_eventbox_click(self, button, event):
        """Diese Funktion wird aufgerufen, wenn der Button geklickt wird"""
        # Cooldown von 100ms (0.1 Sekunden)
        current_time = GLib.get_monotonic_time() / 1000  # Konvertiere zu Millisekunden
        if current_time - self.last_click_time < 100:    # Wenn weniger als 100ms seit dem letzten Klick
            return True
        self.last_click_time = current_time

        # Speichere die Klickposition für Drag-and-Drop
        if event.button == 1:  # Linksklick
            self.click_position = (event.x_root, event.y_root)
            self.drag_started = False
            return True  # Beende die Funktion hier, um die Aktivierung zu verhindern

        if event.button == 3:             # Nur bei Rechtsklick
            print(f"--- Button Rechtsklick --- {self.button_config['text']}")
            if self.parent is not None:
                print(f"--- KontextMenu wird aufgerufen")
                self.open_kontextmenu(event)  # Öffne das Kontextmenü
            return True                   # Event wird nicht weitergegeben

        return False  # Weitergabe an andere Handler

    #########################################################################################################
    def open_kontextmenu(self, event):
        """Öffnet das Kontextmenü für den Button"""
        menu = Gtk.Menu()
        
        # Menüeintrag "Sounddatei auswählen"
        if self.button_config.get('audio_file', '') != '':
            item1 = Gtk.MenuItem(label="Sounddatei ändern")
        else:
            item1 = Gtk.MenuItem(label="Sounddatei auswählen")
        item1.connect("activate", self.on_select_sound)
        menu.append(item1)
        
        # Menüeintrag "Endlos wiederholen" nur anzeigen, wenn eine Sounddatei ausgewählt ist
        if 'audio_file' in self.button_config and self.button_config['audio_file']:
            item2 = Gtk.MenuItem(label="Endlos wiederholen: " + ("Ein" if not self.button_config.get('loop', False) else "Aus"))
            item2.connect("activate", self.on_toggle_loop)
            menu.append(item2)
        
        # Menüeintrag "Button-Text ändern"
        item3 = Gtk.MenuItem(label="Button-Text ändern")
        item3.connect("activate", self.on_change_text)
        menu.append(item3)
        
        # Menüeintrag "Text-Farbe ändern"
        item6 = Gtk.MenuItem(label="Text-Farbe ändern")
        item6.connect("activate", self.on_change_text_color)
        menu.append(item6)
        
        # Menüeintrag "Text-Farbe entfernen" nur anzeigen, wenn eine benutzerdefinierte Textfarbe aktiv ist
        if self.button_config.get('use_custom_text_color', False):
            item7 = Gtk.MenuItem(label="Text-Farbe entfernen")
            item7.connect("activate", self.on_remove_text_color)
            menu.append(item7)
            
        # Menüeintrag "Button-Farbe ändern"
        item4 = Gtk.MenuItem(label="Button-Farbe ändern")
        item4.connect("activate", self.on_change_color)
        menu.append(item4)
        
        # Menüeintrag "Button-Farbe entfernen" nur anzeigen, wenn eine benutzerdefinierte Farbe aktiv ist
        if self.button_config.get('use_custom_bg_color', False):
            item5 = Gtk.MenuItem(label="Button-Farbe entfernen")
            item5.connect("activate", self.on_remove_color)
            menu.append(item5)
            
        # Bildverwaltung
        if self.button_config.get('image_file', False):
            # Wenn ein Bild eingestellt ist: "Bild ändern" und "Bild entfernen" anzeigen
            item8 = Gtk.MenuItem(label="Bild ändern")
            item8.connect("activate", self.on_add_image)
            menu.append(item8)
            
            item9 = Gtk.MenuItem(label="Bild entfernen")
            item9.connect("activate", self.on_remove_image)
            menu.append(item9)
        else:
            # Wenn kein Bild eingestellt ist: "Bild hinzufügen" anzeigen
            item8 = Gtk.MenuItem(label="Bild hinzufügen")
            item8.connect("activate", self.on_add_image)
            menu.append(item8)
        
        # Menüeintrag "Button verschieben"
        item10 = Gtk.MenuItem(label="Button verschieben")
        item10.connect("activate", self.on_move_button)
        menu.append(item10)
        
        # Menüeintrag "Button entfernen"
        item11 = Gtk.MenuItem(label="Button entfernen")
        item11.connect("activate", self.on_delete_button)
        menu.append(item11)
        
        # Rote Textfarbe für den "Button entfernen"-Eintrag
        item11.get_child().get_style_context().add_class("delete-button-menu-item")
        
        # CSS für die rote Textfarbe
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
            .delete-button-menu-item {
                color: #a51d2d;
                font-weight: bold;
            }
        """.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Event-Handler für Klicks außerhalb des Menüs
        menu.connect("deactivate", self.on_menu_deactivate)
        
        menu.show_all()
        menu.popup_at_pointer(event)
        return True  # Event wurde behandelt

    #########################################################################################################
    def on_menu_deactivate(self, menu):
        """Wird aufgerufen, wenn das Menü geschlossen wird"""
        menu.popdown()

    #########################################################################################################
    def on_select_sound(self, widget):
        """Öffnet einen Dateiauswahldialog für Sounddateien"""
        dialog = Gtk.FileChooserDialog(
            title="Sounddatei auswählen",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.OPEN
        )
        
        # Filter für Audiodateien
        filter_audio = Gtk.FileFilter()
        filter_audio.set_name("Audiodateien")
        filter_audio.add_mime_type("audio/*")
        dialog.add_filter(filter_audio)
        
        # Vorherige Datei als Startverzeichnis setzen
        if 'audio_file' in self.button_config and self.button_config['audio_file']:
            full_path = os.path.join(self.default_button['soundpfad_prefix'], self.button_config['audio_file'])
            if os.path.exists(full_path):
                dialog.set_filename(full_path)
        
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Speichere den relativen Pfad zur Sounddatei
            full_path = dialog.get_filename()
            self.add_sound(full_path)
        dialog.destroy()
        widget.get_parent().popdown()

    #########################################################################################################
    def add_sound(self, full_path):
        """fügt eine Sounddatei hinzu"""
        rel_path = os.path.relpath(full_path, os.path.abspath(self.default_button['soundpfad_prefix']))
        self.button_config['audio_file'] = rel_path
        print(f"Sounddatei ausgewählt: {rel_path}")
        
        # Lade den neuen Sound
        try:
            self.sound = pygame.mixer.Sound(full_path)
            self.sound.set_volume(self.button_config['volume'] / 100.0)
            print(f"Neuer Sound geladen: {rel_path}")
            self.update_status_icon()                 # Aktualisiere das Status-Icon
            if self.parent and self.parent.config:
                self.parent.config.mark_changed()  # Markiere Änderungen
        except Exception as e:
            print(f"Fehler beim Laden des Sounds: {e}")
    
    #########################################################################################################
    def on_toggle_loop(self, widget):
        """Schaltet die Endlosschleife ein oder aus"""
        self.button_config['loop'] = not self.button_config.get('loop', False)
        print(f"Endlos wiederholen: {'Ein' if self.button_config['loop'] else 'Aus'}")
        self.update_status_icon()                 # Aktualisiere das Status-Icon
        # Menü explizit schließen
        menu = widget.get_parent()
        menu.popdown()
        if self.parent and self.parent.config:
            self.parent.config.mark_changed()  # Markiere Änderungen

    #########################################################################################################
    def on_change_text(self, widget):
        """Öffnet einen Dialog zum Ändern des Button-Texts"""
        dialog = Gtk.Dialog(title="Button-Text ändern", parent=self.get_toplevel(), flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        # Texteingabefeld
        entry = Gtk.Entry()
        entry.set_text(self.button_config['text'])
        entry.connect("activate", lambda e: dialog.response(Gtk.ResponseType.OK))  # Enter-Taste als OK behandeln
        dialog.get_content_area().pack_start(entry, True, True, 0)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            new_text = entry.get_text()
            formatted_text = new_text.replace("\\n", "\n")
            self.button_config['text'] = formatted_text
            self.text_label.set_text(formatted_text)                     # Zeige den Text mit echten Zeilenumbrüchen im Label
            print(f"Neuer Button-Text: {formatted_text}")
            if self.parent and self.parent.config:
                self.parent.config.mark_changed()  # Markiere Änderungen
        
        dialog.destroy()
        widget.get_parent().popdown()

    #########################################################################################################
    def on_change_color(self, widget):
        """Öffnet einen Farbauswahldialog"""
        dialog = Gtk.ColorChooserDialog(
            title="Button-Farbe auswählen",
            parent=self.get_toplevel()
        )
        
        # Vorherige Farbe setzen
        color = Gdk.RGBA()
        if self.button_config.get('use_custom_bg_color', False) and 'background_color' in self.button_config:
            color.parse(self.button_config['background_color'])
        else:
            color.parse(self.default_button['background_color'])
        dialog.set_rgba(color)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            color = dialog.get_rgba()
            self.button_config['background_color'] = f"#{int(color.red * 255):02x}{int(color.green * 255):02x}{int(color.blue * 255):02x}"
            self.button_config['use_custom_bg_color'] = True  # Benutzerdefinierte Farbe aktivieren
            print(f"Neue Button-Farbe: {self.button_config['background_color']}")
            
            # Wende die neue Farbe an
            self.apply_colors_and_css()
            if self.parent and self.parent.config:
                self.parent.config.mark_changed()  # Markiere Änderungen
        
        dialog.destroy()
        widget.get_parent().popdown()

    #########################################################################################################
    def on_remove_color(self, widget):
        """Entfernt die benutzerdefinierte Farbe"""
        self.button_config['use_custom_bg_color'] = False
        print("Button-Farbe entfernt")
        
        # Wende die Standardfarbe an
        self.apply_colors_and_css()
        
        widget.get_parent().popdown()

    #########################################################################################################
    def on_change_text_color(self, widget):
        """Öffnet einen Farbauswahldialog für die Textfarbe"""
        dialog = Gtk.ColorChooserDialog(
            title="Text-Farbe auswählen",
            parent=self.get_toplevel()
        )
        
        # Vorherige Farbe setzen
        color = Gdk.RGBA()
        if self.button_config.get('use_custom_text_color', False) and 'text_color' in self.button_config:
            color.parse(self.button_config['text_color'])
        else:
            color.parse(self.default_button['text_color'])
        dialog.set_rgba(color)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            color = dialog.get_rgba()
            self.button_config['text_color'] = f"#{int(color.red * 255):02x}{int(color.green * 255):02x}{int(color.blue * 255):02x}"
            self.button_config['use_custom_text_color'] = True  # Benutzerdefinierte Textfarbe aktivieren
            print(f"Neue Text-Farbe: {self.button_config['text_color']}")
            
            # Wende die neue Farbe an
            self.apply_colors_and_css()
            if self.parent and self.parent.config:
                self.parent.config.mark_changed()  # Markiere Änderungen
        
        dialog.destroy()
        widget.get_parent().popdown()

    #########################################################################################################
    def on_remove_text_color(self, widget):
        """Entfernt die benutzerdefinierte Textfarbe"""
        self.button_config['use_custom_text_color'] = False
        print("Text-Farbe entfernt")
        
        # Wende die Standardfarbe an
        self.apply_colors_and_css()
        
        widget.get_parent().popdown()

    #########################################################################################################
    def create_default_button(self):
        """Erstellt einen Standard-Button"""
        return {
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
            "text":                "New Button",
            "use_custom_text_position":    True,
            "text_x":                         5,
            "text_y":                         5,
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
            }
    
    #########################################################################################################
    def create_minimal_button(self, position):
        """Erstellt einen minimalen Button"""
        if position is None:
            position = 1
        return {
            "position":                position,
            "text":            "Minimal Button",
        }
    
    #########################################################################################################
    def on_add_image(self, widget):
        """Öffnet einen Dateiauswahldialog für Bilder"""
        dialog = Gtk.FileChooserDialog(
            title="Bild auswählen",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.OPEN
        )
        
        # Filter für Bilddateien
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Bilder")
        filter_images.add_mime_type("image/*")
        dialog.add_filter(filter_images)
        
        # Vorherige Datei als Startverzeichnis setzen
        if 'image_file' in self.button_config and self.button_config['image_file']:
            full_path = os.path.join(self.default_button['imagepfad_prefix'], self.button_config['image_file'])
            if os.path.exists(full_path):
                dialog.set_filename(full_path)
        
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Speichere den relativen Pfad zum Bild
            full_path = dialog.get_filename()
            rel_path = os.path.relpath(full_path, os.path.abspath(self.default_button['imagepfad_prefix']))
            self.button_config['image_file'] = rel_path
            print(f"Bild ausgewählt: {rel_path}")
            
            # Wende das neue Bild an
            self.apply_image()
            if self.parent and self.parent.config:
                self.parent.config.mark_changed()  # Markiere Änderungen
        
        dialog.destroy()
        widget.get_parent().popdown()

    #########################################################################################################
    def on_remove_image(self, widget):
        """Entfernt das eingestellte Bild"""
        self.button_config['use_custom_image'] = False
        self.button_config['image_file'] = ""
        print("Bild entfernt")
        
        # Entferne die Bildklasse und wende die Änderungen an
        self.get_style_context().remove_class("sound-button-with-image")
        self.apply_image()
        
        widget.get_parent().popdown()
    
    #########################################################################################################
    def on_move_button(self, widget):
        """Öffnet einen Dialog zum Verschieben des Buttons"""
        dialog = Gtk.Dialog(title="Button verschieben", parent=self.get_toplevel(), flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        # Aktuelle Position anzeigen
        current_pos_label = Gtk.Label(label=f"Aktuelle Position: {self.button_config['position']}")
        dialog.get_content_area().pack_start(current_pos_label, True, True, 0)
        
        # Eingabefeld für die neue Position
        entry = Gtk.Entry()
        entry.set_text(str(self.button_config['position']))
        entry.connect("activate", lambda e: dialog.response(Gtk.ResponseType.OK))  # Enter-Taste als OK behandeln
        dialog.get_content_area().pack_start(entry, True, True, 0)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            try:
                new_position = int(entry.get_text())
                if new_position < 1:
                    raise ValueError("Position muss größer als 0 sein")
                
                # Rufe die move_button-Methode im Soundboard auf
                if self.parent and hasattr(self.parent, 'move_button'):
                    print(f"Button von Position {self.button_config['position']} nach {new_position} verschoben")
                    self.parent.move_button(current_position=self.button_config['position'], new_position=new_position)
                    if self.parent and self.parent.config:
                        self.parent.config.mark_changed()  # Markiere Änderungen
                else:
                    print("Fehler: Soundboard-Referenz nicht verfügbar oder move_button-Methode nicht gefunden")
            except ValueError as e:
                print(f"Fehler: {e}")
        
        dialog.destroy()
        widget.get_parent().popdown()

    #########################################################################################################
    def update_status_icon(self):
        """Aktualisiert das Status-Icon basierend auf den Button-Eigenschaften"""
        if self.button_config.get('audio_file', '') == '':
            self.status_icon.set_text("🔇")
        elif self.button_config.get('loop', False):
            self.status_icon.set_text("∞")
        else:
            self.status_icon.set_text("") # oder 🔊  

    #########################################################################################################
    def on_delete_button(self, widget):
        """Öffnet einen Dialog zur Bestätigung der Button-Löschung"""
        # Erstelle einen Bestätigungsdialog
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Möchtest du den Button '{self.button_config['text']}' wirklich löschen?"
        )
        dialog.format_secondary_text("Diese Aktion kann nicht rückgängig gemacht werden.")
        
        # Zeige den Dialog und warte auf Antwort
        response = dialog.run()
        
        if response == Gtk.ResponseType.YES:
            # Button aus der Konfiguration entfernen
            if self.parent and hasattr(self.parent, 'config'):
                # Verwende die delete_button-Methode des ConfigManagers
                position = self.button_config.get('position')
                if self.parent.config.delete_button(position):
                    # Informiere das Soundboard, dass der Button entfernt werden soll
                    if hasattr(self.parent, 'remove_button'):
                        self.parent.remove_button(self)
                    else:
                        # Fallback, falls die Methode nicht existiert
                        if hasattr(self.parent, 'flowbox'):
                            self.parent.flowbox.remove(self)
                            self.parent.flowbox.show_all()
                        self.destroy()
                else:
                    print(f"Fehler: Button mit Position {position} konnte nicht gelöscht werden")
            else:
                print("Fehler: Soundboard-Referenz nicht verfügbar oder ConfigManager nicht gefunden")
        
        # Dialog in jedem Fall zerstören
        dialog.destroy()
        
        # Menü schließen
        widget.get_parent().popdown()

    #########################################################################################################
    def delete_button(self):
        """Löscht den Button"""
        self.deactivate_button()
        # Entferne die CSS-Klassen
        style_context = self.get_style_context()
        style_context.remove_class("sound-button")
        style_context.remove_class("sound-button-active")
        self.destroy()
