#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo
import json

class SoundButton(Gtk.Box):
    def __init__(self, position=0, offset_x=0, offset_y=0, config=None, on_delete=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.position = position  # Speichere die Position
        self.offset_x = offset_x  # X-Offset für die Position
        self.offset_y = offset_y  # Y-Offset für die Position
        self.config = config or self.load_config()
        self.on_delete = on_delete  # Callback für das Löschen
        
        # Button-spezifische Konfiguration laden
        self.button_config = self.get_button_config()
        
        # Größen aus der Konfiguration
        button_config = self.config['soundbutton']
        self.set_size_request(button_config['width'], button_config['height'] + button_config['scale_height'] + button_config['spacing'])
        self.set_vexpand(False)
        self.set_hexpand(False)
        
        # DrawingArea für den Button
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(button_config['width'], button_config['height'])
        self.drawing_area.set_vexpand(False)
        self.drawing_area.set_hexpand(False)
        
        # Event-Handler für Zeichnen
        self.drawing_area.connect("draw", self.on_draw)
        
        # Event-Handler für Mausklicks
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button-press-event", self.on_button_press)
        
        # Schieberegler erstellen
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        scale_config = self.config['scale']
        self.scale.set_range(scale_config['min'], scale_config['max'])
        self.scale.set_value(self.button_config['volume'])
        self.scale.set_draw_value(False)  # Keine numerische Anzeige
        self.scale.set_vexpand(False)
        self.scale.set_hexpand(False)
        self.scale.set_size_request(button_config['scale_width'], button_config['scale_height'])
        self.scale.connect("value-changed", self.on_scale_changed)
        
        # Widgets zum Container hinzufügen
        self.pack_start(self.drawing_area, False, False, 0)
        self.pack_start(self.scale, False, False, button_config['spacing'])
        
        # Debug-Ausgabe
        print(f"SoundButton {self.position + 1} erstellt - Position: x={self.offset_x}, y={self.offset_y}")
        print(f"SoundButton {self.position + 1} - Offset: x={self.offset_x}, y={self.offset_y}")
        
        # Widgets anzeigen
        self.show_all()
    
    def get_button_config(self):
        """Lädt die Button-spezifische Konfiguration"""
        # Für neue Buttons immer eine neue Konfiguration erstellen
        if self.position >= len(self.config.get('buttons', [])):
            return {
                'position': self.position,
                'volume': self.config['scale']['default'],
                'text': f"Button {self.position + 1}"
            }
        
        # Für existierende Buttons die gespeicherte Konfiguration laden
        buttons = self.config.get('buttons', [])
        for button in buttons:
            if button['position'] == self.position:
                return button.copy()  # Erstelle eine Kopie der Konfiguration
        
        # Fallback: Neue Konfiguration
        return {
            'position': self.position,
            'volume': self.config['scale']['default'],
            'text': f"Button {self.position + 1}"
        }
    
    def hex_to_rgb(self, hex_color):
        """Konvertiert einen Hex-Farbcode (#RRGGBB) in RGB-Werte (0-1)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return [r, g, b]
    
    def load_config(self):
        """Lädt die Konfigurationsdatei"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warnung: config.json nicht gefunden, verwende Standardwerte")
            return {
                'soundbutton': {
                    'width': 300,
                    'height': 150,
                    'scale_height': 30,
                    'scale_width': 200,
                    'margin': 10,
                    'spacing': 5
                },
                'button': {
                    'radius': 15,
                    'delete_button_size': 30,
                    'text_size': 20,
                    'background_color': '#CCCCCC',
                    'delete_button_color': '#CC3333',
                    'text_color': '#000000',
                    'text_x': 17,
                    'text_y': 20
                },
                'scale': {
                    'min': 0,
                    'max': 100,
                    'default': 50
                }
            }
    
    def set_offset(self, offset_x, offset_y):
        """Setzt den Offset des Buttons"""
        self.offset_x = offset_x
        self.offset_y = offset_y
        print(f"SoundButton {self.position + 1} - Offset aktualisiert: x={self.offset_x}, y={self.offset_y}")
        self.drawing_area.queue_draw()  # Neu zeichnen bei Änderung
    
    def rounded_rectangle(self, cr, x, y, width, height, radius):
        # Hilfsfunktion zum Zeichnen eines abgerundeten Rechtecks
        degrees = 3.14159 / 180.0
        
        cr.new_sub_path()
        cr.arc(x + width - radius, y + radius, radius, -90 * degrees, 0)
        cr.arc(x + width - radius, y + height - radius, radius, 0, 90 * degrees)
        cr.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
        cr.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
        cr.close_path()
    
    def draw_control_button(self, cr, x, y, size, bg_color, border_color, symbol_color, border_width, symbol_type):
        """Zeichnet einen Steuerungsbutton mit Symbol"""
        # Hintergrund
        cr.set_source_rgb(*bg_color)
        self.rounded_rectangle(cr, x, y, size, size, size/4)
        cr.fill()
        
        # Rahmen
        cr.set_source_rgb(*border_color)
        cr.set_line_width(border_width)
        self.rounded_rectangle(cr, x, y, size, size, size/4)
        cr.stroke()
        
        # Symbol
        cr.set_source_rgb(*symbol_color)
        cr.set_line_width(2)
        
        if symbol_type == "play":
            # Dreieck für Play
            cr.move_to(x + size/3, y + size/4)
            cr.line_to(x + size/3, y + 3*size/4)
            cr.line_to(x + 2*size/3, y + size/2)
            cr.close_path()
            cr.fill()
        elif symbol_type == "stop":
            # Quadrat für Stop
            margin = size/4
            cr.rectangle(x + margin, y + margin, size - 2*margin, size - 2*margin)
            cr.fill()
        elif symbol_type == "loop":
            # Unendlichkeitssymbol (∞)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(size * 0.9)
            extents = cr.text_extents("∞")
            text_x = x + (size - extents.width) / 2 -2
            text_y = y + (size + extents.height) / 2 + 1
            cr.move_to(text_x, text_y)
            cr.show_text("∞")
        elif symbol_type == "delete":
            # Schwarzes Kreuz
            padding = 5
            cr.move_to(x + padding, y + padding)
            cr.line_to(x + size - padding, y + size - padding)
            cr.move_to(x + size - padding, y + padding)
            cr.line_to(x + padding, y + size - padding)
            cr.stroke()
    
    def on_draw(self, widget, cr):
        button_config = self.config['button']
        button_size = self.config['soundbutton']
        
        # Abgerundetes Rechteck als Hintergrund zeichnen
        bg_color = self.hex_to_rgb(button_config['background_color'])
        cr.set_source_rgb(*bg_color)
        self.rounded_rectangle(cr, 0, 0, button_size['width'], button_size['height'], button_config['radius'])
        cr.fill()
        
        # Bild zeichnen, falls vorhanden
        if 'image_file' in self.button_config and self.button_config['image_file']:
            try:
                # Bild laden und skalieren
                image = cairo.ImageSurface.create_from_png(self.button_config['image_file'])
                # Bild auf Button-Größe skalieren
                cr.save()
                # Bild in der Mitte des Buttons platzieren
                image_width = image.get_width()
                image_height = image.get_height()
                scale_x = button_size['width'] / image_width
                scale_y = button_size['height'] / image_height
                scale = min(scale_x, scale_y) * 0.8  # 80% der maximalen Größe
                
                # Bild zentrieren
                x = (button_size['width'] - image_width * scale) / 2
                y = (button_size['height'] - image_height * scale) / 2
                
                cr.translate(x, y)
                cr.scale(scale, scale)
                cr.set_source_surface(image, 0, 0)
                cr.paint()
                cr.restore()
            except Exception as e:
                print(f"Fehler beim Laden des Bildes: {e}")
        
        # Lösch-Button (X) mit draw_control_button zeichnen
        delete_size = button_config['delete_button_size']
        delete_x = button_size['width'] - delete_size - 10
        delete_y = 10
        
        # Steuerungsbutton-Konfiguration für den Lösch-Button verwenden
        control_config = button_config['control_buttons']
        self.draw_control_button(
            cr,
            delete_x,
            delete_y,
            delete_size,
            self.hex_to_rgb(control_config['background_color']),
            self.hex_to_rgb(control_config['border_color']),
            self.hex_to_rgb(control_config['symbol_color']),
            control_config['border_width'],
            "delete"  # Neuer Symboltyp für den Lösch-Button
        )
        
        # Text auf dem Button
        text_color = self.hex_to_rgb(button_config['text_color'])
        cr.set_source_rgb(*text_color)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(button_config['text_size'])
        cr.move_to(button_config['text_x'], button_config['text_y'])
        cr.show_text(self.button_config['text'])
        
        # Steuerungsbuttons zeichnen
        control_config = button_config['control_buttons']
        control_size = control_config['size']
        spacing = control_config['spacing']
        
        # Berechne die Y-Position der Steuerungsbuttons
        # Position = Button-Höhe - Control-Button-Größe - Abstand zum unteren Rand
        y_offset = button_size['height'] - control_size - spacing
        
        # Berechne die Gesamtbreite der Steuerungsbuttons
        total_control_width = 3 * control_size + 2 * spacing
        
        # Berechne die Startposition, damit die Buttons zentriert sind
        start_x = (button_size['width'] - total_control_width) / 2
        
        # Play-Button
        self.draw_control_button(
            cr,
            start_x,
            y_offset,
            control_size,
            self.hex_to_rgb(control_config['background_color']),
            self.hex_to_rgb(control_config['border_color']),
            self.hex_to_rgb(control_config['symbol_color']),
            control_config['border_width'],
            "play"
        )
        
        # Stop-Button
        self.draw_control_button(
            cr,
            start_x + control_size + spacing,
            y_offset,
            control_size,
            self.hex_to_rgb(control_config['background_color']),
            self.hex_to_rgb(control_config['border_color']),
            self.hex_to_rgb(control_config['symbol_color']),
            control_config['border_width'],
            "stop"
        )
        
        # Loop-Button
        self.draw_control_button(
            cr,
            start_x + 2 * (control_size + spacing),
            y_offset,
            control_size,
            self.hex_to_rgb(control_config['background_color']),
            self.hex_to_rgb(control_config['border_color']),
            self.hex_to_rgb(control_config['symbol_color']),
            control_config['border_width'],
            "loop"
        )
        
        return False
    
    def on_button_press(self, widget, event):
        button_config = self.config['button']
        button_size = self.config['soundbutton']
        
        # Prüfe, ob der Lösch-Button geklickt wurde
        delete_size = button_config['delete_button_size']
        delete_x = button_size['width'] - delete_size - 10
        delete_y = 10
        
        if (delete_x <= event.x <= delete_x + delete_size and 
            delete_y <= event.y <= delete_y + delete_size):
            print(f"Lösch-Button von Button {self.position + 1} wurde geklickt!")
            if self.on_delete:
                self.on_delete(self)
            return True
        
        # Control-Buttons überprüfen
        control_config = button_config['control_buttons']
        control_size = control_config['size']
        spacing = control_config['spacing']
        
        # Berechne die Y-Position der Steuerungsbuttons
        y_offset = button_size['height'] - control_size - spacing
        
        # Berechne die Gesamtbreite der Steuerungsbuttons
        total_control_width = 3 * control_size + 2 * spacing
        
        # Berechne die Startposition, damit die Buttons zentriert sind
        start_x = (button_size['width'] - total_control_width) / 2
        
        # Prüfe, ob der Klick im Bereich der Control-Buttons ist
        if (y_offset <= event.y <= y_offset + control_size):
            # Play-Button
            if (start_x <= event.x <= start_x + control_size):
                print(f"Play-Button von Button {self.position + 1} wurde geklickt!")
                return True
            
            # Stop-Button
            if (start_x + control_size + spacing <= event.x <= start_x + 2 * control_size + spacing):
                print(f"Stop-Button von Button {self.position + 1} wurde geklickt!")
                return True
            
            # Loop-Button
            if (start_x + 2 * (control_size + spacing) <= event.x <= start_x + 3 * control_size + 2 * spacing):
                print(f"Loop-Button von Button {self.position + 1} wurde geklickt!")
                return True
        
        # Rechtsklick auf den Button-Hintergrund
        if event.button == 3:  # 3 ist der Rechtsklick
            self.show_text_dialog()
            return True
        
        # Wenn der Klick außerhalb aller Buttons war
        print(f"Außerhalb aller Buttons von Button {self.position + 1} geklickt: x={event.x}, y={event.y}")
        return True
    
    def show_text_dialog(self):
        """Zeigt einen Dialog zum Ändern des Button-Texts, der Audiodatei und des Bildes"""
        dialog = Gtk.Dialog(title="Button-Einstellungen", transient_for=self.get_toplevel(), flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        # Container für den Inhalt
        content_area = dialog.get_content_area()
        
        # Label und Textfeld für den Button-Text
        text_label = Gtk.Label(label="Button-Text:")
        content_area.pack_start(text_label, True, True, 0)
        
        text_entry = Gtk.Entry()
        text_entry.set_text(self.button_config.get('text', f"Button {self.position + 1}"))
        content_area.pack_start(text_entry, True, True, 0)
        
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
        
        content_area.pack_start(file_box, True, True, 0)
        
        # Label und Container für das Bild
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
        
        # Dialog anzeigen
        dialog.show_all()
        
        # Dialog ausführen
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            new_text = text_entry.get_text()
            new_file = file_entry.get_text()
            new_image = image_entry.get_text()
            
            if new_text.strip():  # Nur wenn der Text nicht leer ist
                self.button_config['text'] = new_text
                print(f"Button {self.position + 1} - Text auf '{new_text}' geändert")
            
            if new_file.strip():  # Nur wenn eine Datei ausgewählt wurde
                self.button_config['audio_file'] = new_file
                print(f"Button {self.position + 1} - Audiodatei auf '{new_file}' gesetzt")
            
            if new_image.strip():  # Nur wenn ein Bild ausgewählt wurde
                self.button_config['image_file'] = new_image
                print(f"Button {self.position + 1} - Bild auf '{new_image}' gesetzt")
            
            self.drawing_area.queue_draw()  # Neu zeichnen
            self.save_config()  # Speichern
        
        dialog.destroy()
    
    def on_browse_clicked(self, button, entry, file_type):
        """Öffnet einen Dateiauswahl-Dialog"""
        dialog = Gtk.FileChooserDialog(
            title="Datei auswählen",
            transient_for=self.get_toplevel(),
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
    
    def on_scale_changed(self, scale):
        """Callback für Änderungen am Schieberegler"""
        value = scale.get_value()
        self.button_config['volume'] = value
        print(f"Button {self.position + 1} - Lautstärke auf {value} gesetzt")
    
    def save_config(self):
        """Speichert die aktuelle Button-Konfiguration"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = self.config
        
        # Aktualisiere oder füge die Button-Konfiguration hinzu
        buttons = config.get('buttons', [])
        found = False
        for button in buttons:
            if button['position'] == self.position:
                button.update(self.button_config)
                found = True
                break
        if not found:
            buttons.append(self.button_config)
        
        config['buttons'] = buttons
        
        # Speichere die aktualisierte Konfiguration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4) 