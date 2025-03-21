#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import pygame  # Hinzufügen von pygame für die Audio-Wiedergabe

class SettingsDialog:
    def __init__(self, parent_window, button_config, position, on_delete=None):
        if not button_config:
            raise ValueError("Keine Button-Konfiguration übergeben")
            
        self.button_config = button_config
        self.position = position
        self.parent_window = parent_window
        self.on_delete = on_delete  # Callback-Funktion für das Löschen
        pygame.mixer.init()  # Initialisiere pygame.mixer für die Audio-Wiedergabe
        self.is_playing = False  # Zustand für die Wiedergabe
    
    def show(self):
        """Zeigt einen Dialog zum Ändern des Button-Texts, der Audiodatei und des Bildes"""
        dialog = Gtk.Dialog(title="Button-Einstellungen", transient_for=self.parent_window, flags=0)
        
        # Änderung: Buttons hinzufügen mit Löschen-Button links
        delete_button = Gtk.Button(label="Diesen Button löschen")
        dialog.add_action_widget(delete_button, Gtk.ResponseType.REJECT)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        # Roten Hintergrund für den Löschen-Button
        delete_button_style = delete_button.get_style_context()
        provider = Gtk.CssProvider()
        provider.load_from_data(b".delete-button { background-color: #CC0000; color: white; }")
        delete_button_style.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        delete_button_style.add_class("delete-button")
        
        # Container für den Inhalt
        content_area = dialog.get_content_area()
        
        # Label und Textfeld für den Button-Text
        text_label = Gtk.Label(label="Button-Text:")
        content_area.pack_start(text_label, True, True, 0)
        
        text_entry = Gtk.Entry()
        text_entry.set_text(self.button_config.get('text', f"Button {self.position + 1}"))
        content_area.pack_start(text_entry, True, True, 0)
        
        # Alle Textbezogenen Einstellungen zusammenfassen
        # Trennlinie für die Texteinstellungen
        text_settings_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        text_settings_separator.set_margin_top(5)
        text_settings_separator.set_margin_bottom(5)
        content_area.pack_start(text_settings_separator, True, True, 0)
        
        # Textausrichtung-Optionen
        text_align_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        text_align_label = Gtk.Label(label="Textausrichtung:")
        text_align_box.pack_start(text_align_label, False, False, 0)
        
        # Combobox für die Textausrichtung
        text_align_store = Gtk.ListStore(str, str)
        text_align_store.append(["center", "Zentriert"])
        text_align_store.append(["left", "Linksbündig"])
        text_align_store.append(["right", "Rechtsbündig"])
        
        text_align_combo = Gtk.ComboBox.new_with_model(text_align_store)
        renderer_text = Gtk.CellRendererText()
        text_align_combo.pack_start(renderer_text, True)
        text_align_combo.add_attribute(renderer_text, "text", 1)
        
        # Aktuelle Ausrichtung auswählen
        current_align = self.button_config.get('text_align', 'center')
        active_iter = None
        for i, row in enumerate(text_align_store):
            if row[0] == current_align:
                text_align_combo.set_active(i)
                break
        if text_align_combo.get_active() == -1:
            text_align_combo.set_active(0)  # Fallback auf Zentriert
        
        text_align_box.pack_start(text_align_combo, True, True, 5)
        content_area.pack_start(text_align_box, True, True, 0)
        
        # Option für Zeilenumbrüche
        line_break_check = Gtk.CheckButton(label="Zeilenumbrüche aktivieren")
        line_break_check.set_active(self.button_config.get('line_breaks', True))
        content_area.pack_start(line_break_check, True, True, 5)
        
        # Textpositionierung - direkt nach der Texteingabe
        # Checkbox für individuelle Textpositionierung
        text_pos_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        text_pos_check = Gtk.CheckButton(label="Individuelle Textposition verwenden")
        text_pos_check.set_active(self.button_config.get('use_custom_text_position', False))
        text_pos_box.pack_start(text_pos_check, True, True, 0)
        content_area.pack_start(text_pos_box, True, True, 5)
        
        # Container für die Eingabefelder (nur oben und links)
        margins_grid = Gtk.Grid()
        margins_grid.set_column_spacing(10)
        margins_grid.set_row_spacing(5)
        
        # Oben
        top_label = Gtk.Label(label="Abstand oben:")
        top_label.set_halign(Gtk.Align.START)
        margins_grid.attach(top_label, 0, 0, 1, 1)
        
        top_adjustment = Gtk.Adjustment(
            value=self.button_config.get('text_margin_top', 0),
            lower=0,
            upper=50,
            step_increment=1,
            page_increment=5
        )
        top_spinbutton = Gtk.SpinButton()
        top_spinbutton.set_adjustment(top_adjustment)
        margins_grid.attach(top_spinbutton, 1, 0, 1, 1)
        
        # Links
        left_label = Gtk.Label(label="Abstand links:")
        left_label.set_halign(Gtk.Align.START)
        margins_grid.attach(left_label, 0, 1, 1, 1)
        
        left_adjustment = Gtk.Adjustment(
            value=self.button_config.get('text_margin_left', 0),
            lower=0,
            upper=50,
            step_increment=1,
            page_increment=5
        )
        left_spinbutton = Gtk.SpinButton()
        left_spinbutton.set_adjustment(left_adjustment)
        margins_grid.attach(left_spinbutton, 1, 1, 1, 1)
        
        # Aktiviere/Deaktiviere die Eingabefelder basierend auf dem Status der Checkbox
        def on_text_pos_check_toggled(widget):
            margins_grid.set_sensitive(widget.get_active())
        
        text_pos_check.connect("toggled", on_text_pos_check_toggled)
        on_text_pos_check_toggled(text_pos_check)  # Initial-Status setzen
        
        # Füge das Grid zum Dialog hinzu
        content_area.pack_start(margins_grid, True, True, 5)
        
        # Trennlinie für die nächste Sektion
        next_section_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        next_section_separator.set_margin_top(10)
        next_section_separator.set_margin_bottom(10)
        content_area.pack_start(next_section_separator, True, True, 0)
        
        # Änderung: Label und Container für das Bild VOR Audiodatei
        image_label = Gtk.Label(label="Button-Bild:")
        content_area.pack_start(image_label, True, True, 0)
        
        image_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        image_entry = Gtk.Entry()
        image_entry.set_text(self.button_config.get('image_file', ''))
        image_entry.set_hexpand(True)
        image_box.pack_start(image_entry, True, True, 0)
        
        image_browse_button = Gtk.Button(label="Durchsuchen")
        image_browse_button.connect("clicked", self.on_browse_clicked, image_entry, "image")
        image_box.pack_start(image_browse_button, False, False, 5)
        
        content_area.pack_start(image_box, True, True, 0)
        
        # Neue Farbauswahl-Optionen
        # Trennlinie für bessere Übersicht
        separator1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator1.set_margin_top(10)
        separator1.set_margin_bottom(10)
        content_area.pack_start(separator1, True, True, 0)
        
        # 1. Buttonfarbe
        color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Checkbox für eigene Buttonfarbe
        button_color_check = Gtk.CheckButton(label="Eigene Buttonfarbe verwenden")
        button_color_check.set_active(self.button_config.get('use_custom_bg_color', False))
        color_box.pack_start(button_color_check, True, True, 0)
        
        # Farbauswahl für Buttonfarbe
        button_color_button = Gtk.ColorButton()
        bg_color = self.button_config.get('background_color', '#cccccc')
        rgba = self.hex_to_rgba(bg_color)
        button_color_button.set_rgba(rgba)
        color_box.pack_start(button_color_button, False, False, 5)
        
        content_area.pack_start(color_box, True, True, 0)
        
        # 2. Textfarbe
        text_color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Checkbox für eigene Textfarbe
        text_color_check = Gtk.CheckButton(label="Eigene Textfarbe verwenden")
        text_color_check.set_active(self.button_config.get('use_custom_text_color', False))
        text_color_box.pack_start(text_color_check, True, True, 0)
        
        # Farbauswahl für Textfarbe
        text_color_button = Gtk.ColorButton()
        text_color = self.button_config.get('text_color', '#000000')
        text_rgba = self.hex_to_rgba(text_color)
        text_color_button.set_rgba(text_rgba)
        text_color_box.pack_start(text_color_button, False, False, 5)
        
        content_area.pack_start(text_color_box, True, True, 0)
        
        # Trennlinie für bessere Übersicht
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator2.set_margin_top(10)
        separator2.set_margin_bottom(10)
        content_area.pack_start(separator2, True, True, 0)
        
        # Label und Container für die Audiodatei
        file_label = Gtk.Label(label="Audiodatei:")
        content_area.pack_start(file_label, True, True, 0)
        
        file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        file_entry = Gtk.Entry()
        file_entry.set_text(self.button_config.get('audio_file', ''))
        file_entry.set_hexpand(True)
        file_box.pack_start(file_entry, True, True, 0)
        
        browse_button = Gtk.Button(label="Durchsuchen")
        browse_button.connect("clicked", self.on_browse_clicked, file_entry, "audio")
        file_box.pack_start(browse_button, False, False, 5)
        
        # Abspielen-Button für die Audiodatei
        play_button = Gtk.ToggleButton(label="Abspielen")
        play_button.connect("toggled", self.on_play_toggled, file_entry)
        file_box.pack_start(play_button, False, False, 5)
        
        content_area.pack_start(file_box, True, True, 0)
        
        # Checkbox für Endlosschleife (Loop-Funktion)
        loop_check = Gtk.CheckButton(label="In Endlosschleife abspielen")
        loop_check.set_active(self.button_config.get('loop', False))
        content_area.pack_start(loop_check, True, True, 5)
        
        # Trennlinie für bessere Übersicht
        separator3 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator3.set_margin_top(10)
        separator3.set_margin_bottom(10)
        content_area.pack_start(separator3, True, True, 0)
        
        # Änderung: Entferne den separaten Löschen-Button am Ende
        # Verbinde den Löschen-Button in der Action-Area mit dem Lösch-Handler
        delete_button.connect("clicked", self.on_delete_button_clicked, dialog)
        
        # Dialog anzeigen
        dialog.show_all()
        
        # Dialog ausführen
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            new_text = text_entry.get_text()
            new_file = file_entry.get_text()
            new_image = image_entry.get_text()
            loop_enabled = loop_check.get_active()
            
            # Textausrichtung und Zeilenumbruch-Optionen speichern
            active_iter = text_align_combo.get_active_iter()
            if active_iter:
                text_align = text_align_store[active_iter][0]
                self.button_config['text_align'] = text_align
            
            line_breaks = line_break_check.get_active()
            self.button_config['line_breaks'] = line_breaks
            
            # Textpositionierung speichern
            use_custom_position = text_pos_check.get_active()
            self.button_config['use_custom_text_position'] = use_custom_position
            self.button_config['text_margin_top'] = int(top_spinbutton.get_value())
            self.button_config['text_margin_left'] = int(left_spinbutton.get_value())
            # Zurücksetzen von unten und rechts, wenn nicht mehr verwendet
            if not use_custom_position:
                self.button_config['text_margin_top'] = 0
                self.button_config['text_margin_left'] = 0
            
            # Alte Werte für unten und rechts entfernen, da wir sie nicht mehr verwenden
            if 'text_margin_bottom' in self.button_config:
                del self.button_config['text_margin_bottom']
            if 'text_margin_right' in self.button_config:
                del self.button_config['text_margin_right']
            
            # Speichere Farbeinstellungen
            use_custom_bg = button_color_check.get_active()
            use_custom_text = text_color_check.get_active()
            
            # Farben aus Farbauswahl in Hex-Format umwandeln
            bg_rgba = button_color_button.get_rgba()
            bg_hex = self.rgba_to_hex(bg_rgba)
            
            text_rgba = text_color_button.get_rgba()
            text_hex = self.rgba_to_hex(text_rgba)
            
            # Speichere Farbeinstellungen
            self.button_config['use_custom_bg_color'] = use_custom_bg
            self.button_config['background_color'] = bg_hex
            self.button_config['use_custom_text_color'] = use_custom_text
            self.button_config['text_color'] = text_hex
            
            if new_text.strip():  # Nur wenn der Text nicht leer ist
                self.button_config['text'] = new_text
                # Button-Text aktualisieren
                if hasattr(self.parent_window, 'buttons'):
                    for button in self.parent_window.buttons:
                        if button.position == self.position:
                            button.button.set_label(new_text)
                            break
                print(f"Button {self.position + 1} - Text auf '{new_text}' geändert")
            
            if new_file.strip():  # Nur wenn eine Datei ausgewählt wurde
                self.button_config['audio_file'] = new_file
                print(f"Button {self.position + 1} - Audiodatei auf '{new_file}' gesetzt")
            
            if new_image.strip():  # Nur wenn ein Bild ausgewählt wurde
                self.button_config['image_file'] = new_image
                # Bild sofort aktualisieren
                if hasattr(self.parent_window, 'buttons'):
                    for button in self.parent_window.buttons:
                        if button.position == self.position:
                            if hasattr(button, 'update_image') and callable(button.update_image):
                                button.update_image(new_image)
                            break
                print(f"Button {self.position + 1} - Bild auf '{new_image}' gesetzt")
            
            # Speichere den Loop-Status
            self.button_config['loop'] = loop_enabled
            print(f"Button {self.position + 1} - Endlosschleife ist {'aktiviert' if loop_enabled else 'deaktiviert'}")
            
            # Button aktualisieren, damit die neuen Farben angewendet werden
            if hasattr(self.parent_window, 'buttons'):
                for button in self.parent_window.buttons:
                    if button.position == self.position:
                        if hasattr(button, '_apply_css_style') and callable(button._apply_css_style):
                            button._apply_css_style()
                        break
            
            print(f"Button {self.position + 1} - Farbeinstellungen aktualisiert")
        
        # Falls Musik noch läuft, stoppe sie
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
        
        dialog.destroy()
        
        # Gib den Response zurück, damit der Aufrufer weiß, ob Änderungen vorgenommen wurden
        return response
    
    def hex_to_rgba(self, hex_color):
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
    
    def rgba_to_hex(self, rgba):
        """Konvertiert ein RGBA-Objekt in einen Hex-Farbcode"""
        r = int(rgba.red * 255)
        g = int(rgba.green * 255)
        b = int(rgba.blue * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def on_delete_button_clicked(self, button, parent_dialog):
        """Zeigt einen Bestätigungsdialog zum Löschen des Buttons an"""
        # Bestätigungsdialog erstellen
        confirm_dialog = Gtk.MessageDialog(
            transient_for=parent_dialog,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Button wirklich löschen?"
        )
        confirm_dialog.format_secondary_text(
            f"Der Button '{self.button_config.get('text', '')}' wird unwiederbringlich gelöscht. Fortfahren?"
        )
        
        response = confirm_dialog.run()
        confirm_dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            print(f"Button {self.position + 1} - Löschen bestätigt")
            # Dialog schließen und den Lösch-Callback aufrufen
            parent_dialog.response(Gtk.ResponseType.CANCEL)  # Dialog beenden
            
            # Callback aufrufen, wenn vorhanden
            if self.on_delete:
                self.on_delete(self.position)
    
    def on_browse_clicked(self, button, entry, file_type):
        """Öffnet einen Dateiauswahl-Dialog"""
        dialog = Gtk.FileChooserDialog(
            title="Datei auswählen",
            transient_for=self.parent_window,
            action=Gtk.FileChooserAction.OPEN
        )
        
        if file_type == "audio":
            # Filter für Audiodateien
            audio_filter = Gtk.FileFilter()
            audio_filter.set_name("Audiodateien")
            audio_filter.add_mime_type("audio/*")
            dialog.add_filter(audio_filter)
        else:  # image
            # Filter für Bilddateien
            image_filter = Gtk.FileFilter()
            image_filter.set_name("Bilddateien")
            image_filter.add_mime_type("image/*")
            dialog.add_filter(image_filter)
        
        # Alle Dateien
        all_filter = Gtk.FileFilter()
        all_filter.set_name("Alle Dateien")
        all_filter.add_pattern("*")
        dialog.add_filter(all_filter)
        
        # Buttons
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        # Aktuelles Verzeichnis setzen
        dialog.set_current_folder(".")
        
        # Dialog anzeigen
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            entry.set_text(filename)
        
        dialog.destroy()
    
    def on_play_toggled(self, button, file_entry):
        """Startet oder stoppt die Wiedergabe der Audiodatei"""
        file_path = file_entry.get_text().strip()
        if button.get_active():  # Wenn der Button gedrückt ist
            if file_path:
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    self.is_playing = True
                    button.set_label("Stoppen")  # Ändere die Beschriftung
                except pygame.error as e:
                    print(f"Fehler beim Abspielen der Datei: {e}")
                    button.set_active(False)  # Setze den Button zurück
                except Exception as e:
                    print(f"Unerwarteter Fehler beim Abspielen: {e}")
                    button.set_active(False)  # Setze den Button zurück
            else:
                print("Keine Datei ausgewählt.")
                button.set_active(False)  # Setze den Button zurück
        else:  # Wenn der Button losgelassen wird
            if self.is_playing:
                try:
                    # Prüfe, ob Mixer noch initialisiert ist
                    if pygame.mixer.get_init():
                        pygame.mixer.music.stop()
                    self.is_playing = False
                    button.set_label("Abspielen")  # Ändere die Beschriftung zurück
                except pygame.error as e:
                    print(f"Fehler beim Stoppen der Audiowiedergabe: {e}")
                except Exception as e:
                    print(f"Unerwarteter Fehler beim Stoppen: {e}")
                    self.is_playing = False