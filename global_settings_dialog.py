#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import pygame
import os

class GlobalSettingsDialog:
    def __init__(self, parent_window, config):
        """Initialisiert den Dialog für globale Einstellungen
        
        Args:
            parent_window: Das übergeordnete Fenster
            config: Die Konfiguration der gesamten Anwendung
        """
        if not config:
            raise ValueError("Keine Konfiguration übergeben")
            
        self.config = config
        self.parent_window = parent_window
        pygame.mixer.init()  # Initialisiere pygame.mixer für die Audio-Wiedergabe
        self.is_playing = False  # Zustand für die Wiedergabe
    
    def show(self):
        """Zeigt einen Dialog für globale Einstellungen an, die für alle Buttons gelten"""
        dialog = Gtk.Dialog(title="Globale Einstellungen", transient_for=self.parent_window, flags=0)
        
        # Buttons hinzufügen
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        # Container für den Inhalt
        content_area = dialog.get_content_area()
        content_area.set_border_width(10)
        
        # Titel für den Dialog
        title_label = Gtk.Label()
        title_label.set_markup("<b>Globale Einstellungen für alle Buttons</b>")
        title_label.set_margin_bottom(10)
        content_area.pack_start(title_label, False, False, 0)
        
        # Beschreibung
        description_label = Gtk.Label(
            label="Diese Einstellungen gelten für alle Buttons, außer wenn individuelle Einstellungen festgelegt sind."
        )
        description_label.set_line_wrap(True)
        description_label.set_margin_bottom(10)
        content_area.pack_start(description_label, False, False, 0)
        
        # Trennlinie
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(5)
        separator.set_margin_bottom(15)
        content_area.pack_start(separator, False, False, 0)
        
        # ================ AUDIO- UND BUTTONEINSTELLUNGEN ==============================================
        button_settings_label = Gtk.Label()
        button_settings_label.set_markup("<b>Button-Einstellungen</b>")
        button_settings_label.set_halign(Gtk.Align.START)
        content_area.pack_start(button_settings_label, False, False, 5)
        
        # Standard-Lautstärke
        volume_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        volume_label = Gtk.Label(label="Standard-Lautstärke:")
        volume_box.pack_start(volume_label, False, False, 0)
        
        volume_adjustment = Gtk.Adjustment(
            value=self.config['soundbutton'].get('volume_default', 50),
            lower=0,
            upper=100,
            step_increment=1,
            page_increment=10
        )
        volume_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=volume_adjustment)
        volume_scale.set_digits(0)
        volume_scale.set_draw_value(True)
        volume_scale.set_value_pos(Gtk.PositionType.RIGHT)
        volume_box.pack_start(volume_scale, True, True, 5)
        
        content_area.pack_start(volume_box, True, True, 5)
        
        # Knopfgröße
        size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        size_label = Gtk.Label(label="Buttongröße:")
        size_box.pack_start(size_label, False, False, 0)
        
        # Horizontale Box für die Spinbuttons
        size_spinbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        size_spinbox.set_spacing(5)
        
        # Breite
        width_label = Gtk.Label(label="Breite:")
        size_spinbox.pack_start(width_label, False, False, 0)
        
        width_adjustment = Gtk.Adjustment(
            value=self.config['soundbutton'].get('button_width', 100),
            lower=50,
            upper=300,
            step_increment=5,
            page_increment=20
        )
        width_spinbutton = Gtk.SpinButton()
        width_spinbutton.set_adjustment(width_adjustment)
        size_spinbox.pack_start(width_spinbutton, False, False, 5)
        
        # Höhe
        height_label = Gtk.Label(label="Höhe:")
        size_spinbox.pack_start(height_label, False, False, 0)
        
        height_adjustment = Gtk.Adjustment(
            value=self.config['soundbutton'].get('button_height', 75),
            lower=50,
            upper=200,
            step_increment=5,
            page_increment=20
        )
        height_spinbutton = Gtk.SpinButton()
        height_spinbutton.set_adjustment(height_adjustment)
        size_spinbox.pack_start(height_spinbutton, False, False, 0)
        
        size_box.pack_start(size_spinbox, True, True, 5)
        content_area.pack_start(size_box, True, True, 5)
        
        # Spacing
        spacing_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        spacing_label = Gtk.Label(label="Abstand zwischen Buttons:")
        spacing_box.pack_start(spacing_label, False, False, 0)
        
        spacing_adjustment = Gtk.Adjustment(
            value=self.config['soundbutton'].get('spacing', 5),
            lower=0,
            upper=20,
            step_increment=1,
            page_increment=5
        )
        spacing_spinbutton = Gtk.SpinButton()
        spacing_spinbutton.set_adjustment(spacing_adjustment)
        spacing_box.pack_start(spacing_spinbutton, True, True, 5)
        
        content_area.pack_start(spacing_box, True, True, 5)

        # Trennlinie für die nächste Sektion
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(15)
        separator.set_margin_bottom(15)
        content_area.pack_start(separator, False, False, 0)
        
        # ================ TEXTEINSTELLUNGEN ===========================================================
        text_settings_label = Gtk.Label()
        text_settings_label.set_markup("<b>Texteinstellungen</b>")
        text_settings_label.set_halign(Gtk.Align.START)
        content_area.pack_start(text_settings_label, False, False, 5)
        
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
        current_align = self.config['soundbutton'].get('text_align', 'center')
        for i, row in enumerate(text_align_store):
            if row[0] == current_align:
                text_align_combo.set_active(i)
                break
        if text_align_combo.get_active() == -1:
            text_align_combo.set_active(0)  # Fallback auf Zentriert
        
        text_align_box.pack_start(text_align_combo, True, True, 5)
        content_area.pack_start(text_align_box, True, True, 0)
        
        # Individuelle Textposition
        text_pos_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        text_pos_check = Gtk.CheckButton(label="Individuelle Textposition verwenden")
        text_pos_check.set_active(self.config['soundbutton'].get('use_custom_text_position', False))
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
            value=self.config['soundbutton'].get('text_margin_top', 0),
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
            value=self.config['soundbutton'].get('text_margin_left', 0),
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
        
        # ================ FARBEINSTELLUNGEN ==========================================================
        # Trennlinie für die nächste Sektion
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(15)
        separator.set_margin_bottom(15)
        content_area.pack_start(separator, False, False, 0)
        
        color_settings_label = Gtk.Label()
        color_settings_label.set_markup("<b>Farbeinstellungen</b>")
        color_settings_label.set_halign(Gtk.Align.START)
        content_area.pack_start(color_settings_label, False, False, 5)
        
        # Buttonfarbe
        color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        color_label = Gtk.Label(label="Button-Hintergrundfarbe:")
        color_box.pack_start(color_label, True, True, 0)
        
        button_color_button = Gtk.ColorButton()
        bg_color = self.config['soundbutton'].get('background_color', '#cccccc')
        rgba = self.hex_to_rgba(bg_color)
        button_color_button.set_rgba(rgba)
        color_box.pack_start(button_color_button, False, False, 5)
        
        content_area.pack_start(color_box, True, True, 0)
        
        # Textfarbe
        text_color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        text_color_label = Gtk.Label(label="Button-Textfarbe:")
        text_color_box.pack_start(text_color_label, True, True, 0)
        
        text_color_button = Gtk.ColorButton()
        text_color = self.config['soundbutton'].get('text_color', '#000000')
        text_rgba = self.hex_to_rgba(text_color)
        text_color_button.set_rgba(text_rgba)
        text_color_box.pack_start(text_color_button, False, False, 5)
        
        content_area.pack_start(text_color_box, True, True, 5)
        
        # Checkbox für die Verwendung der globalen Textfarbe (anstelle von Systemfarben)
        use_global_text_color_check = Gtk.CheckButton(label="Globale Textfarbe verwenden (statt Systemfarben)")
        use_global_text_color_check.set_active(self.config['soundbutton'].get('use_global_text_color', True))
        content_area.pack_start(use_global_text_color_check, True, True, 5)
        
        # Checkbox für die Verwendung der globalen Hintergrundfarbe (anstelle von Systemfarben)
        use_global_bg_color_check = Gtk.CheckButton(label="Globale Hintergrundfarbe verwenden (statt Systemfarben)")
        use_global_bg_color_check.set_active(self.config['soundbutton'].get('use_global_bg_color', True))
        content_area.pack_start(use_global_bg_color_check, True, True, 5)
        
        # ================ BUTTON-GRAFIK ===============================================================
        # Trennlinie für die nächste Sektion
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(15)
        separator.set_margin_bottom(15)
        content_area.pack_start(separator, False, False, 0)
        
        image_settings_label = Gtk.Label()
        image_settings_label.set_markup("<b>Standard Button-Grafik</b>")
        image_settings_label.set_halign(Gtk.Align.START)
        content_area.pack_start(image_settings_label, False, False, 5)
        
        # Beschreibung
        image_desc_label = Gtk.Label(
            label="Wenn gesetzt, wird diese Grafik für alle Buttons verwendet, die keine eigene Grafik haben."
        )
        image_desc_label.set_line_wrap(True)
        image_desc_label.set_margin_bottom(10)
        content_area.pack_start(image_desc_label, False, False, 0)
        
        # Eingabefeld mit Durchsuchen-Button für Bilddatei
        image_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        image_box.set_spacing(5)
        
        # Textfeld für den Dateipfad
        image_path_entry = Gtk.Entry()
        image_path = self.config['soundbutton'].get('default_image_file', "")
        image_path_entry.set_text(image_path)
        image_path_entry.set_hexpand(True)
        image_box.pack_start(image_path_entry, True, True, 0)
        
        # Durchsuchen-Button
        browse_button = Gtk.Button(label="Durchsuchen...")
        image_box.pack_start(browse_button, False, False, 0)
        
        # Dateiwähler-Dialog
        def on_browse_clicked(widget):
            dialog = Gtk.FileChooserDialog(
                title="Bilddatei auswählen",
                parent=self.parent_window,
                action=Gtk.FileChooserAction.OPEN
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
            
            # Filterung auf Bilddateien
            filter_images = Gtk.FileFilter()
            filter_images.set_name("Bilder")
            filter_images.add_mime_type("image/png")
            filter_images.add_mime_type("image/jpeg")
            filter_images.add_mime_type("image/gif")
            filter_images.add_pattern("*.png")
            filter_images.add_pattern("*.jpg")
            filter_images.add_pattern("*.jpeg")
            filter_images.add_pattern("*.gif")
            dialog.add_filter(filter_images)
            
            # Alle Dateien
            filter_any = Gtk.FileFilter()
            filter_any.set_name("Alle Dateien")
            filter_any.add_pattern("*")
            dialog.add_filter(filter_any)
            
            # Wenn ein Pfad bereits gesetzt ist, diesen als Startpunkt verwenden
            if os.path.exists(image_path_entry.get_text()):
                dialog.set_filename(image_path_entry.get_text())
            
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                image_path_entry.set_text(dialog.get_filename())
            
            dialog.destroy()
        
        browse_button.connect("clicked", on_browse_clicked)
        
        # Vorschau-Button
        preview_button = Gtk.Button(label="Vorschau")
        image_box.pack_start(preview_button, False, False, 0)
        
        def on_preview_clicked(widget):
            # Prüfe, ob die Datei existiert
            image_path = image_path_entry.get_text()
            if not image_path or not os.path.exists(image_path):
                preview_dialog = Gtk.MessageDialog(
                    transient_for=self.parent_window,
                    modal=True,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Bilddatei nicht gefunden!"
                )
                preview_dialog.format_secondary_text(
                    "Die angegebene Datei existiert nicht oder ist nicht lesbar."
                )
                preview_dialog.run()
                preview_dialog.destroy()
                return
            
            # Erstelle einen Dialog mit der Bildvorschau
            preview_dialog = Gtk.Dialog(
                title="Bildvorschau",
                transient_for=self.parent_window,
                flags=0
            )
            preview_dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
            
            # Erstelle ein Bild-Widget mit der ausgewählten Datei
            image = Gtk.Image()
            image.set_from_file(image_path)
            
            # Scrollbare Ansicht
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll.add(image)
            
            # Setze eine angemessene Größe
            preview_dialog.get_content_area().add(scroll)
            preview_dialog.set_default_size(400, 300)
            
            preview_dialog.show_all()
            preview_dialog.run()
            preview_dialog.destroy()
        
        preview_button.connect("clicked", on_preview_clicked)
        
        # Checkbox für die Nutzung der globalen Grafik
        use_default_image_check = Gtk.CheckButton(label="Globale Grafik für Buttons ohne eigene Grafik verwenden")
        use_default_image_check.set_active(self.config['soundbutton'].get('use_default_image', False))
        content_area.pack_start(image_box, True, True, 5)
        content_area.pack_start(use_default_image_check, True, True, 5)
                
        # Dialog anzeigen #############################################################################
        dialog.show_all()
        
        # Dialog ausführen
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            # Textausrichtung speichern
            active_iter = text_align_combo.get_active_iter()
            if active_iter:
                text_align = text_align_store[active_iter][0]
                self.config['soundbutton']['text_align'] = text_align
            
            # Zeilenumbrüche sind immer aktiviert
            self.config['soundbutton']['line_breaks'] = True
            
            # Textpositionierung speichern
            use_custom_position = text_pos_check.get_active()
            self.config['soundbutton']['use_custom_text_position'] = use_custom_position
            self.config['soundbutton']['text_margin_top'] = int(top_spinbutton.get_value())
            self.config['soundbutton']['text_margin_left'] = int(left_spinbutton.get_value())
            
            # Farben aus Farbauswahl in Hex-Format umwandeln
            bg_rgba = button_color_button.get_rgba()
            bg_hex = self.rgba_to_hex(bg_rgba)
            
            text_rgba = text_color_button.get_rgba()
            text_hex = self.rgba_to_hex(text_rgba)
            
            # Speichere Farbeinstellungen
            self.config['soundbutton']['background_color'] = bg_hex
            self.config['soundbutton']['text_color'] = text_hex
            
            # Speichere Einstellungen für die Verwendung globaler vs. Systemfarben
            self.config['soundbutton']['use_global_text_color'] = use_global_text_color_check.get_active()
            self.config['soundbutton']['use_global_bg_color'] = use_global_bg_color_check.get_active()
            
            # Speichere Button-Grafik-Einstellungen
            image_path = image_path_entry.get_text()
            if image_path and os.path.exists(image_path):
                self.config['soundbutton']['default_image_file'] = image_path
            else:
                # Wenn die Datei nicht existiert, entferne den Eintrag
                self.config['soundbutton']['default_image_file'] = ""
            
            self.config['soundbutton']['use_default_image'] = use_default_image_check.get_active()
            
            # Speichere Lautstärke und Größeneinstellungen
            self.config['soundbutton']['volume_default'] = int(volume_scale.get_value())
            self.config['soundbutton']['button_width'] = int(width_spinbutton.get_value())
            self.config['soundbutton']['button_height'] = int(height_spinbutton.get_value())
            self.config['soundbutton']['spacing'] = int(spacing_spinbutton.get_value())
            
            print("Globale Einstellungen gespeichert")
        
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