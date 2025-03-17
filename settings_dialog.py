#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SettingsDialog:
    def __init__(self, parent_window, button_config, position):
        self.button_config = button_config
        self.position = position
        self.parent_window = parent_window
    
    def show(self):
        """Zeigt einen Dialog zum Ändern des Button-Texts, der Audiodatei und des Bildes"""
        dialog = Gtk.Dialog(title="Button-Einstellungen", transient_for=self.parent_window, flags=0)
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
        
        dialog.destroy()
    
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