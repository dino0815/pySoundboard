import sys   # Importiere sys, um das Kommandozeilenargument zu verarbeiten
import pygame
import signal
import gi    # Importiere gi, um die GTK-Bibliothek zu verwenden
import json
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from config_manager import ConfigManager
from Soundbutton import Soundbutton

############################################################################################################
class Soundboard(Gtk.Window):
    def __init__(self, config_file=None):
        Gtk.Window.__init__(self, title="Soundboard")
        pygame.mixer.init()                  # Pygame für Audio initialisieren
        
        # Wenn keine Konfigurationsdatei angegeben wurde, verwende einen leeren String
        if config_file is None:
            config_file = ""
        self.config = ConfigManager(config_file)
        self.set_default_size(self.config.data['Window']['window_width'], self.config.data['Window']['window_height'])
        self.set_size_request(-1, -1)        # Keine Mindestgröße setzen
        self.default_button = None           # Default-Button
        # Erstelle ScrolledWindow mit optimierter Konfiguration
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.add(self.scrolled_window)       # Füge ScrolledWindow zum Hauptfenster hinzu
        
        # Erstelle FlowBox mit optimierter Konfiguration
        self.flowbox = Gtk.FlowBox()         # FlowBox konfigurieren für automatische Anordnung
        self.flowbox.set_valign(Gtk.Align.START)                # Vertikale Ausrichtung am Anfang
        self.flowbox.set_halign(Gtk.Align.START)                # Horizontale Ausrichtung am Anfang
        self.flowbox.set_hexpand(True)                          # Ausdehnung in horizontaler Richtung
        self.flowbox.set_vexpand(True)                          # Ausdehnung in vertikaler Richtung
        self.flowbox.set_homogeneous(True)                      # Gleichmäßige Größe der Buttons
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE) # Keine Auswahl möglich
        self.flowbox.set_min_children_per_line(1)               # Mindestens 1 Button pro Zeile
        self.flowbox.set_max_children_per_line(20)              # Höchstens 20 Buttons pro Zeile
        self.flowbox.set_row_spacing(5)                         # Abstand zwischen den Zeilen
        self.flowbox.set_column_spacing(5)                      # Abstand zwischen den Spalten
        self.flowbox.set_margin_start(5)                        # Abstand zum linken Rand
        self.flowbox.set_margin_end(5)                          # Abstand zum rechten Rand
        self.flowbox.set_margin_top(5)                          # Abstand zum oberen Rand
        self.flowbox.set_margin_bottom(5)                       # Abstand zum unteren Rand
        self.flowbox.set_activate_on_single_click(False)        # Deaktiviere automatische Aktivierung
        self.flowbox.set_filter_func(None)                      # Keine Filterfunktion
        self.flowbox.set_sort_func(None)                        # Keine Sortierfunktion
        self.scrolled_window.add(self.flowbox)

        # Erstelle Buttons aus der gefilterten Buttonliste (ohne Default-Button)
        for button in self.config.buttonlist:
            if button.get('position') != 0:  # solange es nicht der Default-Button ist
                button = Soundbutton(parent=self, default_button=self.config.data['buttons'][0], button_config=button)
                self.flowbox.add(button)                                 # FlowBox kümmert sich um die Positionierung
            else:
                self.default_button = button

        self.connect("key-press-event",    self.on_key_press)        # Signalhandler für Tastatureingaben
        self.connect("button-press-event", self.on_background_click) # Für Klicks auf Fensterhintergrund
        self.connect("configure-event",    self.on_window_configure) # Signalhandler für Größenänderungen des Fensters
        self.connect("destroy",            self.on_destroy)          # Signalhandler für Fenster-Schließen
        
        # Signal-Handler für SIGINT (Strg+C) registrieren
        signal.signal(signal.SIGINT, self.on_sigint)

        # Abonniere das Signal für Änderungen des Themas
        self.connect("realize", self.on_realize)
        self.show_all()

    ########################################################################################################
    def on_realize(self, widget):
        settings = Gtk.Settings.get_default()
        settings.connect("notify::gtk-theme-name", self.on_theme_changed)

    ########################################################################################################
    def on_background_click(self, window, event):
        """ Diese Funktion wird nur bei Rechtsklick auf den Hintergrund ausgeführt """
        if event.button == 3:  # Nur bei Rechtsklick
            #print("--- Hintergrund Rechtsklick ---")
            self.open_kontextmenu(event)  # Öffne das Kontextmenü
            return True  # Event wurde behandelt
        return False  # Bei Linksklick: Event ignorieren

    ########################################################################################################
    def open_kontextmenu(self, event):
        """Öffnet das Kontextmenü für den Hintergrund"""
        menu = Gtk.Menu()
        
        # Menüeintrag "Button hinzufügen"
        item1 = Gtk.MenuItem(label="Button hinzufügen")
        item1.connect("activate", self.on_add_button)
        menu.append(item1)
        
        # Event-Handler für Klicks außerhalb des Menüs
        menu.connect("deactivate", self.on_menu_deactivate)
        
        menu.show_all()
        menu.popup_at_pointer(event)
        return True  # Event wurde behandelt
        
    ########################################################################################################
    def on_menu_deactivate(self, menu):
        """Wird aufgerufen, wenn das Menü geschlossen wird"""
        menu.popdown()
        
    ########################################################################################################
    def on_add_button(self, widget=None):
        """Fügt einen neuen Button am Ende der Liste hinzu"""
        new_position = self.config.add_minimal_button() # Füge einen minimalen Button zur Konfiguration hinzu      
        # Erstelle den neuen Button und füge ihn zur FlowBox hinzu
        new_button = Soundbutton(parent=self, default_button=self.config.data['buttons'][0], button_config=self.config.data['buttons'][new_position])
        self.flowbox.add(new_button) 
        self.flowbox.show_all()                         # Aktualisiere die Anzeige
        if widget:                                      # Nur wenn ein Widget übergeben wurde (Menüpunkt)
            widget.get_parent().popdown()               # Menü schließen
        self.config.mark_changed()  # Markiere Änderungen

    ########################################################################################################
    def on_key_press(self, widget, event):
        """Handler für Tastatureingaben"""
        keyval = event.keyval                                # Tastaturwert nehmen
        keyname = Gdk.keyval_name(keyval)                    # Tastaturname nehmen
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK) # Strg-Taste prüfen
        shift = (event.state & Gdk.ModifierType.SHIFT_MASK)  # Shift-Taste prüfen
        alt = (event.state & Gdk.ModifierType.MOD1_MASK)     # Alt-Taste prüfen
        """ # Debug-Ausgabe für alle Tastenkombinationen
        print(f"Taste gedrückt: {keyname}", end="")
        if alt: print("+Alt", end="")
        if ctrl: print("+Strg", end="")
        if shift: print("+Shift", end="")
        if super: print("+Super", end="")
        if lock: print("+Lock", end="")
        if hyper: print("Hyper gedrückt", end="")
        if meta: print("+Meta", end="")
        if num: print("+Num", end="")
        print(" ")
        """
        if ctrl and keyname == 'n':                            # Strg+N: Button hinzufügen
            self.on_add_button(None)                           # Button hinzufügen (None als Widget-Parameter)
            return True                                        # keine Weitergabe an andere Handler
        
        if ctrl and keyname == 'q':                            # Strg+Q: Fenster schließen
            self.config.save_config(self)                      # Konfiguration speichern
            self.destroy()                                     # Fenster schließen
            return True                                        # keine Weitergabe an andere Handler
        
        if ctrl and shift and keyname == 'S':                  # Strg+Shift+S: Konfiguration unter neuem Namen speichern
            print("Konfiguration unter neuem Namen speichern")
            self.config.save_config_as_dialog(self)            # Öffne den Dialog zum Speichern unter einem neuen Namen
            return True                                        # keine Weitergabe an andere Handler

        if ctrl and keyname == 's':                            # Strg+S: Konfiguration speichern
            print("Konfiguration gespeichert")
            self.config.save_config(self)                      # Konfiguration speichern
            return True                                        # keine Weitergabe an andere Handler
        
        return False                                           # Weitergabe an andere Handler
    
    ########################################################################################################
    def on_window_configure(self, widget, event):
        """Handler für Größenänderungen des Fensters"""
        self.config.data['Window']['window_width'] = event.width    # Breite setzen
        self.config.data['Window']['window_height'] = event.height  # Höhe setzen
        self.flowbox.queue_resize()                          # FlowBox neu anpassen
        self.flowbox.queue_draw()                            # FlowBox neu zeichnen        
        return True  # keine Weitergabe an andere Handler
    
    #########################################################################################################
    def on_theme_changed(self, settings, gparam):
        # Dies wird aufgerufen, wenn sich das GTK-Theme ändert
        theme_name = Gtk.Settings.get_default().get_property("gtk-theme-name")
        print(f"Thema wurde geändert zu: {theme_name}")
        
        for child in self.flowbox.get_children():
            if isinstance(child.get_child(), Soundbutton):  # Sicherstellen, dass es sich um einen Button handelt
                child.get_child().apply_colors_and_css()
                child.get_child().queue_draw()
        self.flowbox.show_all()

    ########################################################################################################
    def stop_all_sounds(self):
        """Stoppt alle Sounds"""
        for child in self.flowbox.get_children():
            if isinstance(child.get_child(), Soundbutton):  # Sicherstellen, dass es sich um einen Button handelt
                child.get_child().deactivate_button()

    #########################################################################################################
    def move_button(self, current_position, new_position):
        """Verschiebt den Button die neue Position"""
        button_to_move = self.flowbox.get_children()[current_position-1]        # Hole das Button-Widget
        self.flowbox.remove(button_to_move)         # Entferne den Button von der FlowBox
        self.flowbox.insert(button_to_move, new_position-1)  # Füge den Button an der neuen Position ein

        for i, child in enumerate(self.flowbox.get_children()):
            if isinstance(child.get_child(), Soundbutton):  # Sicherstellen, dass es sich um einen Button handelt
                child.get_child().button_config['position'] = i+1
        buttonlist = sorted(self.config.data['buttons'], key=lambda x: x.get('position', 0))
        self.config.data['buttons'] = buttonlist
        self.flowbox.show_all()
        self.config.mark_changed()  # Markiere Änderungen

    #########################################################################################################
    def remove_button(self, button):
        """Entfernt einen Button aus der FlowBox"""
        if hasattr(self, 'flowbox'):
            self.flowbox.remove(button)
            self.flowbox.show_all()
            button.delete_button()       
            self.config.mark_changed()  # Markiere Änderungen
            return True
        return False

    ########################################################################################################
    def on_save_config_as(self):
        """Öffnet einen Dateiauswahldialog zum Speichern der Konfiguration unter einem neuen Namen"""
        self.config.save_config_as_dialog(self)

    ########################################################################################################
    def on_destroy(self, widget, data=None):
        """Behandelt das Schließen des Fensters"""
        # Prüfen, ob es ungespeicherte Änderungen gibt
        if self.config.has_unsaved_changes():
            # Prüfen, ob die Konfiguration schreibgeschützt ist oder eine neue Konfiguration ist
            if self.config.data['Window'].get('read_only', False) or self.config.is_new_config:
                # Wenn schreibgeschützt oder neue Konfiguration, nur "Speichern unter" anbieten
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.NONE,
                    text="Es gibt ungespeicherte Änderungen."
                )
                if self.config.data['Window'].get('read_only', False):
                    dialog.format_secondary_text("Die aktuelle Konfiguration ist schreibgeschützt.")
                else:
                    dialog.format_secondary_text("Es handelt sich um eine neue Konfiguration.")
                dialog.add_buttons(
                    "Speichern unter", Gtk.ResponseType.YES,
                    "Verwerfen", Gtk.ResponseType.NO
                )
                response = dialog.run()
                dialog.destroy()
                
                if response == Gtk.ResponseType.YES:
                    # Speichern unter neuem Namen
                    self.config.save_config_as_dialog(self)
                    self.cleanup_resources()
                    Gtk.main_quit()
                else:  # NO
                    # Änderungen verwerfen
                    self.cleanup_resources()
                    Gtk.main_quit()
            else:
                # Wenn nicht schreibgeschützt und keine neue Konfiguration, alle Optionen anbieten
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.NONE,
                    text="Es gibt ungespeicherte Änderungen."
                )
                dialog.format_secondary_text("Was möchten Sie mit den Änderungen tun?")
                dialog.add_buttons(
                    "Speichern", Gtk.ResponseType.YES,
                    "Speichern unter", Gtk.ResponseType.ACCEPT,
                    "Verwerfen", Gtk.ResponseType.NO
                )
                response = dialog.run()
                dialog.destroy()
                
                if response == Gtk.ResponseType.YES:
                    # Speichern in der aktuellen Datei
                    self.config.save_config(self)
                    self.cleanup_resources()
                    Gtk.main_quit()
                elif response == Gtk.ResponseType.ACCEPT:
                    # Speichern unter neuem Namen
                    self.config.save_config_as_dialog(self)
                    self.cleanup_resources()
                    Gtk.main_quit()
                else:  # NO
                    # Änderungen verwerfen
                    self.cleanup_resources()
                    Gtk.main_quit()
        else:
            # Keine Änderungen, direkt beenden
            self.cleanup_resources()
            Gtk.main_quit()

    ########################################################################################################
    def cleanup_resources(self):
        """Gibt alle Ressourcen frei"""
        for button in self.flowbox.get_children():
            if isinstance(button.get_child(), Soundbutton):    # Sicherstellen, dass es sich um einen Button handelt
                button.get_child().delete_button()             # Löscht den Button
        pygame.mixer.quit()

    ########################################################################################################
    def on_sigint(self, signum, frame):
        """Handler für SIGINT (Strg+C)"""
        print("Strg+C gedrückt, beende Programm...")
        
        # Prüfe, ob es ungespeicherte Änderungen gibt
        if self.config.has_unsaved_changes():
            print("Ungespeicherte Änderungen gefunden, erstelle Autosave...")
            self.create_autosave()
        
        # Ressourcen freigeben und Programm beenden
        self.cleanup_resources()
        Gtk.main_quit()  # Beende die GTK-Hauptschleife
        sys.exit(0)  # Stelle sicher, dass das Programm beendet wird

    ########################################################################################################    
    def create_autosave(self):
        """Erstellt eine automatische Sicherungskopie der Konfiguration"""
        import os
        import glob
        
        # Bestimme den Basisnamen für die Autosave-Datei
        if self.config.config_file and self.config.config_file != "":
            # Wenn eine Konfigurationsdatei existiert, verwende ihren Namen als Basis
            base_name = os.path.splitext(os.path.basename(self.config.config_file))[0]
            base_dir = os.path.dirname(self.config.config_file)
        else:
            # Wenn keine Konfigurationsdatei existiert, verwende "unnamed_soundboard"
            base_name = "unnamed_soundboard"
            base_dir = os.getcwd()  # Aktuelles Verzeichnis
        
        # Suche nach existierenden Autosave-Dateien
        pattern = os.path.join(base_dir, f"{base_name}_autosave_*.json")
        existing_autosaves = glob.glob(pattern)
        
        # Bestimme die höchste Nummer
        max_num = 0
        for autosave in existing_autosaves:
            try:
                # Extrahiere die Nummer aus dem Dateinamen
                num_str = os.path.basename(autosave).split("_autosave_")[1].split(".json")[0]
                num = int(num_str)
                if num > max_num:
                    max_num = num
            except (ValueError, IndexError):
                # Ignoriere Dateien, die nicht dem erwarteten Format entsprechen
                pass
        
        # Erstelle den neuen Dateinamen mit der nächsthöheren Nummer
        new_num = max_num + 1
        autosave_file = os.path.join(base_dir, f"{base_name}_autosave_{new_num}.json")
        
        # Speichere die Konfiguration
        with open(autosave_file, 'w') as f:
            json.dump(self.config.data, f, indent=4)
        
        print(f"Autosave erstellt: {autosave_file}")

############################################################################################################
if len(sys.argv) > 1:
    app = Soundboard(config_file=sys.argv[1])
else:
    app = Soundboard()
app.show_all()
Gtk.main() # Starte die GTK-Hauptschleife
sys.exit(0) # Stelle sicher, dass das Programm beendet wird