# pySoundboard

Ein modernes, benutzerfreundliches Soundboard für Linux, entwickelt mit Python und GTK3.

![pySoundboard Screenshot](images/screenshot.png)

## Features

- 🎵 Einfaches Abspielen von Soundeffekten per Mausklick
- 🎚️ Individuelle Lautstärkeregelung für jeden Sound
- 🎨 Anpassbare Button-Gestaltung
- ⚙️ Umfangreiche Konfigurationsmöglichkeiten
- ⌨️ Tastaturkürzel-Unterstützung
- 🖱️ Drag & Drop für Sound-Dateien
- 💾 Automatisches Speichern der Konfiguration

## Voraussetzungen

- Python 3.x
- GTK3
- PyGObject
- Pygame

### Installation der Abhängigkeiten

```bash
# Für Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pygame

# Für Fedora
sudo dnf install python3-gobject python3-gobject-gtk python3-pygame
```

## Installation

1. Klonen Sie das Repository:
```bash
git clone https://github.com/IhrUsername/pySoundboard.git
cd pySoundboard
```

2. Starten Sie das Programm:
```bash
python3 pySoundboard.py
```

## Verwendung

- Klicken Sie auf einen Sound-Button, um den Sound abzuspielen
- Um die Buttons umzusortieren kann eine neue gewünschte Position im einstellungsmenü jedes Buttons eingestellt werden.
- (noch fehlendes Feature) --Ziehen Sie Sound-Dateien per Drag & Drop auf das Fenster, um neue Buttons zu erstellen--
- Nutzen Sie die Lautstärkeregler an den Buttons für individuelle Lautstärkeeinstellungen
- Rechtsklick auf einen Button öffnet die Einstellungen für diesen Button
- Die globalen Einstellungen erreichen Sie über einen rechtsklick auf den Fensterhintergrung.

## Konfiguration

Die Konfiguration wird in der `config.json` Datei gespeichert. Sie enthält:
- Fenstereinstellungen
- Button-Layout und -Design
- Sound-Button-Konfigurationen

## Lizenz

Dieses Projekt ist unter der GPL3-Lizenz lizenziert. Siehe die [LICENSE](LICENSE) Datei für Details.

## Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Fork des Repositories und senden Sie einen Pull Request.

## Noch fehlende Features:
- Dateipfade in der Konfig rellativ zum aktuellen Ordner oder einem Global eingesteltem Pfad.
- Verschiedene Konfigs laden durch Aufruf mittels Parameter.

## Support

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im GitHub-Repository. 