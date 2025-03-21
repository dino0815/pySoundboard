#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
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
        
        # Abspielen-Button für die Audiodatei
        play_button = Gtk.ToggleButton(label="Abspielen")
        play_button.connect("toggled", self.on_play_toggled, file_entry)
        file_box.pack_start(play_button, False, False, 5)
        
        content_area.pack_start(file_box, True, True, 0)
        
        # Checkbox für Endlosschleife (Loop-Funktion)
        loop_check = Gtk.CheckButton(label="In Endlosschleife abspielen")
        loop_check.set_active(self.button_config.get('loop', False))
        content_area.pack_start(loop_check, True, True, 5)
        
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
        
        # Trennlinie hinzufügen
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(15)
        separator.set_margin_bottom(15)
        content_area.pack_start(separator, True, True, 0)
        
        # Button zum Löschen des Buttons
        delete_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        delete_button_box.set_halign(Gtk.Align.CENTER)
        
        delete_button = Gtk.Button(label="Diesen Button löschen")
        delete_button.set_margin_top(5)
        delete_button.set_margin_bottom(10)
        delete_button.connect("clicked", self.on_delete_button_clicked, dialog)
        
        # Roten Hintergrund für den Löschen-Button
        delete_button_style = delete_button.get_style_context()
        provider = Gtk.CssProvider()
        provider.load_from_data(b".delete-button { background-color: #CC0000; color: white; }")
        delete_button_style.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        delete_button_style.add_class("delete-button")
        
        delete_button_box.pack_start(delete_button, False, False, 0)
        content_area.pack_start(delete_button_box, True, True, 0)
        
        # Dialog anzeigen
        dialog.show_all()
        
        # Dialog ausführen
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            new_text = text_entry.get_text()
            new_file = file_entry.get_text()
            new_image = image_entry.get_text()
            loop_enabled = loop_check.get_active()
            
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
        
        # Falls Musik noch läuft, stoppe sie
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
        
        dialog.destroy()
    
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