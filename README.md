# Soundboard
Ein einfaches Soundboard für Linux, mit dem du Sounds per Klick abspielen kannst, entwickelt mit Python und GTK3.

## Funktionen
- Erstelle und verwalte Soundbuttons mit benutzerdefinierten Sounds
- Passe das Aussehen der Buttons an (Farbe, Text, Bilder)
- Steuere die Lautstärke jedes Sounds individuell
- Aktiviere Endlosschleifen für Sounds
- Verschiebe Buttons per Drag & Drop oder Kontextmenü
- Drag & Drop von Bild- und Sounddateien auf Buttons oder Hintergrund
- Kontextmenü für schnelle Anpassungen
- Speichere deine Konfiguration für spätere Verwendung
- Status-Anzeige für Sound-Zuordnung und Loop-Funktion
- Verbesserte Pfadbehandlung für portable Konfigurationen
- Jedem Button kann einzeln eine Zeit für FadeIn und FadeOut gesetzt werden

## Installation

### Voraussetzungen
- Python 3.6 oder höher
- GTK3
- PyGame

### Installationsschritte

1. **Installiere die erforderlichen Pakete:**
   Für Ubuntu/Debian:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pygame
   ```

   Für Fedora:
   ```bash
   sudo dnf install python3 python3-gobject python3-gobject-gtk python3-pygame
   ```

   Für Arch Linux:
   ```bash
   sudo pacman -S python python-gobject python-pygame
   ```

2. **Klonen oder herunterladen des Repositories:**
   ```bash
   git clone https://github.com/dein-username/Soundboard.git
   cd Soundboard
   ```
   Oder lade die ZIP-Datei herunter und entpacke sie.

3. **Erstelle Verzeichnisse, wenn du nicht andere verwenden möchtest:**
   ```bash
   mkdir -p sounds images
   ```
   PS: Momentan müssen die Pfad-Prefixe für Sound- / und Bild-Dateien noch per Hand in der gespeicherten Config-Datei angepasst werden.

## Verwendung

1. **Starte das Soundboard:**
   ```bash
   python3 Soundboard.py
   ```
   #oder

   ```bash
   python3 Soundboard.py config.json # Vorbereitete Soundboards im json-Format öffnen, Name beliebig 
   ```

2. **Füge Sounds hinzu:**
   - Rechtsklick auf einen Button und wähle "Sounddatei auswählen"
   - Wähle eine Audiodatei aus (unterstützt werden MP3, WAV, OGG, etc.)
   - oder ziehe einfach eine Sounddatei aus dem dateimanager auf den Button. (Drag&Drop)

3. **Passe die Buttons an:**
   - Rechtsklick auf einen Button für das Kontextmenü
   - Ändere Text, Farbe, Bild und andere Eigenschaften
   - oder ziehe einfach eine Bilddatei aus dem dateimanager auf den Button. (Drag&Drop)

4. **Speichere deine Konfiguration:**
   - "Strg-S"

## Verzeichnisstruktur
- `Soundboard.py` - Hauptprogramm
- `Sounbutton.py` - die Button-Klasse
- `config_manager.py` - Verwaltet die Konfiguration
- `sounds/` - Verzeichnis für Sounddateien (Optional)
- `images/` - Verzeichnis für Bilder(Optional)
- `config.json` - Speichert die Konfiguration (Optional, Name beliebig)

## Tastenkombinationen
- **Strg+N**:       Fügt einen neuen Button hinzu 
- **Strg+S**:       Speichern der Konfiguration / des Soundboards
- **Strg+Shift+S**: Speichern der Konfiguration / des Soundboards unter neuem Namen
- **Strg+Q**:       Beendet das Programm 
- Auch mit **Strg+C** in der Konsole kann das Programm sauber beendet werden.

## Drag & Drop Funktionen
- **Bilder und Sounds**: Ziehe Dateien per Drag & Drop auf einen Button um diese Datei hinzu zufügen
- **Bilder und Sounds**: Ziehe Dateien per Drag & Drop auf den Hintergrund um damit neue Buttons zu erzeugen.
- **Button-Verschiebung**: Verschiebe Buttons per Drag & Drop an neue Positionen
- **Board-Übertragung**: Verschiebe Buttons zwischen verschiedenen Soundboards

## Fehlerbehebung / FAQ
- **Problem**: "ModuleNotFoundError: No module named 'gi'"
  **Lösung**: Installiere die GTK-Bindings für Python: `sudo apt-get install python3-gi`

- **Problem**: "ModuleNotFoundError: No module named 'pygame'"
  **Lösung**: Installiere PyGame: `sudo apt-get install python3-pygame`

- **Problem**: Sounds werden nicht abgespielt
  **Lösung**: Überprüfe, ob die Sounddateien im richtigen Verzeichnis liegen und die Berechtigungen korrekt sind

## Noch fehlende Features:
- Vorkonfugurierte Button-Datenbank mit Schlagwort Filterung

## Lizenz
Dieses Projekt ist unter der GPL3-Lizenz lizenziert. Siehe die [LICENSE](LICENSE) Datei für Details.

## Beitragen
Beiträge sind willkommen! Bitte erstellen Sie einen Fork des Repositories und senden Sie einen Pull Request.

## Support
Bei Fragen oder Problemen erstellen Sie bitte ein Issue im GitHub-Repository. 

## Autor
Sebastian Löser