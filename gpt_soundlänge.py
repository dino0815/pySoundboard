import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

import pygame
import os
from urllib.parse import unquote, urlparse

class SoundLengthApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Soundlänge anzeigen")
        self.set_default_size(400, 200)
        self.set_border_width(20)

        self.label = Gtk.Label(label="Ziehe eine Sounddatei hierher")
        self.add(self.label)

        # Drag-and-Drop aktivieren
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        target = Gtk.TargetEntry.new("text/uri-list", 0, 0)
        self.drag_dest_set_target_list(Gtk.TargetList.new([target]))
        self.connect("drag-data-received", self.on_drag_data_received)

        # Pygame initialisieren
        pygame.mixer.init()

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        uris = data.get_uris()
        if not uris:
            self.label.set_text("Keine Datei erkannt.")
            return

        # URI in Pfad umwandeln und dekodieren (für Leerzeichen etc.)
        raw_uri = uris[0]
        path = urlparse(raw_uri).path
        filepath = unquote(path)

        if not os.path.isfile(filepath):
            self.label.set_text("Ungültiger Pfad.")
            return

        try:
            pygame.mixer.music.load(filepath)
            sound = pygame.mixer.Sound(filepath)
            length = sound.get_length()
            self.label.set_text(f"Länge: {length:.2f} Sekunden")
        except Exception as e:
            self.label.set_text(f"Fehler beim Laden: {e}")

def main():
    app = SoundLengthApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
