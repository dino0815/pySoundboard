import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import pygame
import os
import time
from urllib.parse import unquote, urlparse

class SoundPlayer(Gtk.Window):
    def __init__(self):
        super().__init__(title="Sound mit exakter Fortschrittsanzeige")
        self.set_default_size(400, 150)
        self.set_border_width(20)

        # UI-Elemente
        self.label = Gtk.Label(label="Ziehe eine Sounddatei hierher")
        self.progress = Gtk.ProgressBar()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.pack_start(self.label, False, False, 0)
        vbox.pack_start(self.progress, False, False, 0)
        self.add(vbox)

        # Drag-and-Drop
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        target = Gtk.TargetEntry.new("text/uri-list", 0, 0)
        self.drag_dest_set_target_list(Gtk.TargetList.new([target]))
        self.connect("drag-data-received", self.on_drag_data_received)

        # Pygame-Mixer
        pygame.mixer.init()
        self.current_channel = None
        self.current_length = 0
        self.start_time = None

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time_):
        uris = data.get_uris()
        if not uris:
            self.label.set_text("Keine Datei erkannt.")
            return

        filepath = unquote(urlparse(uris[0]).path)
        if not os.path.isfile(filepath):
            self.label.set_text("Ungültiger Pfad.")
            return

        try:
            sound = pygame.mixer.Sound(filepath)
            self.current_length = sound.get_length()
            self.label.set_text(f"Spiele ab: {os.path.basename(filepath)} ({self.current_length:.2f} Sekunden)")
            self.play_with_timed_fade(sound)
        except Exception as e:
            self.label.set_text(f"Fehler: {e}")

    def play_with_timed_fade(self, sound):
        self.start_time = time.time()
        self.current_channel = sound.play()
        self.progress.set_fraction(0)

        # Fade-Out 1 Sekunde vor Ende
        fade_delay_ms = max(0, int((self.current_length - 1) * 1000))
        GLib.timeout_add(fade_delay_ms, self.do_fade_out)

        # Fortschrittsanzeige alle 100ms
        GLib.timeout_add(100, self.update_progress)

    def do_fade_out(self):
        if self.current_channel and self.current_channel.get_busy():
            self.current_channel.fadeout(1000)
        return False

    def update_progress(self):
        if not self.current_channel or not self.current_channel.get_busy():
            self.progress.set_fraction(1.0)
            return False

        elapsed = time.time() - self.start_time
        progress = min(1.0, elapsed / self.current_length)
        self.progress.set_fraction(progress)
        return True

def main():
    app = SoundPlayer()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
