# Designentscheidungen für pySoundboard

Dieses Dokument enthält wichtige Designentscheidungen, die während der Entwicklung getroffen wurden, um sicherzustellen, dass diese nicht in Vergessenheit geraten und bei zukünftigen Änderungen berücksichtigt werden.

## Allgemeine Architektur

- Das Programm verwendet GTK3 für die Benutzeroberfläche und pygame für die Audiowiedergabe
- Die Konfiguration wird in einer JSON-Datei gespeichert 
- Die Hauptklassen sind:
  - `SoundboardWindow`: Das Hauptfenster mit der FlowBox zur Anordnung der Buttons
  - `SoundButton`: Die einzelnen Buttons mit Audiowiedergabe-Funktionen
  - `ButtonSettingsDialog`: Dialog für Button-spezifische Einstellungen
  - `GlobalSettingsDialog`: Dialog für globale Einstellungen
  - `ConfigManager`: Verwaltet die Datenstrucktur mit allen Einstellungen und der Button-Zusammenstellung

## Konfigurations-Management

- der KonfigurationsManager bekommt die beim Programmaufruf übergebenen Konfigurations-Datei übergeben
- Wenn keine Übergeben wurde wird "config.json" verwendet. 
- Die Konfiguration wird aus Konfigurations-Datei geladen. 
- Wenn die Konfig-Datei nicht existiert wird nur die Default-Konfig geladen.
- Wenn aus einer Datei geladen wird überprüft, ob alle wichtigen einstellungen vorhanden sind und wenn nicht mit den defaultwerten hinzugefügt.
- Die Konfiguration wird dem restlichen Programm so bereit gestellt, dass direckt drauf zugegriffen werden kann.
- Die Konfiguration wird nur durch "Strg+S" oder beim Beenden gespeichert
- Es gibt einen Parameter(read_only) in der Konfiguration, der besagt, ob die Konfigurationsdatei überschrieben werden darf (default:false) 
- Wenn dieser auf true gesetzt ist, wird beim versuch zu Speichern gefragt unter welchem neuen Dateinamen/Pfad gespeichert werden soll.
- Die Tastenkombination "Strg-Shift+S" erzeugt diese nachfrage und Speicherung auch wenn das Konfigfile nicht geschützt ist.

## Button-Management

1. **Button-Erstellung und -Aktualisierung**:
   - Buttons werden nicht unnötig entfernt und neu erstellt, sondern ihre Eigenschaften werden aktualisiert
   - Nur bei Änderung der Button-Anzahl werden Buttons entfernt und neu erstellt
   - Der Add-Button bleibt immer als letzter Butten in der Reihe

2. **Button-Positionierung**:
   - Buttons werden anhand ihrer `position`-Eigenschaft sortiert
   - Beim Verschieben eines Buttons werden die `position`-Eigenschaften alle betroffenen Buttons entsprechend angepasst
   - Nach jeder Position-Änderung werden allen Buttons die Eigenschafften neu zugewiesen. 

3. **Add-Button**:
   - Der Add-Button ist ein spezieller Button mit `is_add_button=True`
   - Er wird immer als letzter Button angezeigt
   - Nach dem Klick wird er in einen normalen Button umgewandelt und ein neuer Add-Button wird am ende der Liste erstellt

## Audio-Wiedergabe

1. **Lautstärkeregelung**:
   - Jeder Button hat einen eigenen Lautstärkeregler
   - Die Lautstärke wird in der Konfiguration gespeichert
   - Lautstärkeänderungen werden sofort angewendet

2. **Abspielen**:
   - Jeder Button Verhällt sich wie ein Toggle-Button.
   - Beim aktivieren des Buttons wird der Sound von vorne abgespielt. 
   - Beim deaktivieren wird der Sound gestopt.
   - Sobald der Sound zuende abgespielt ist deaktiviert sich der Button automatisch.

3. **Ein- und Ausblenden**:
   - Die Audio-Wiedergabe hat eine Fade-In- und Fade-Out-Funktionalität
   - Timer werden verwendet, um die Lautstärke schrittweise zu erhöhen/verringern
   - Timer-Verwaltung erfolgt über GLib.timeout_source_new() und active_timers

## Text und Darstellung

1. **Textausrichtung**:
   - Buttons unterstützen drei Ausrichtungen: links, zentriert, rechts
   - Die Ausrichtung wird in der Konfiguration gespeichert und beim Neuzeichnen angewendet

2. **Zeilenumbrüche**:
   - Zeilenumbrüche werden durch "\n" im ButtonText erzeugt.

3. **Textpositionierung**:
   - Buttons können eine individuelle Textposition verwenden.
   - Es werden Abstände von oben und links angegeben.

4. **Farben**:
   - Wenn nicht anderes Angegeben, werden die Farben des System-Themes verwendet.
   - Es können andere Standardfarben festgelegt werden.
   - Buttons können individuelle Hintergrund- und Textfarben haben

## Dialog-Anordnung

1. **Button-Einstellungsdialog**:
   - Die Reihenfolge der Einträge ist:
     1. Positionierung 
     2. Soundeinstellungen
     3. Buttontext/Textausrichtung/Textfarbe
     4. Buttonfarbe und Bild
     5. Button-Steuerelemente (Löschen, Abbrechen, OK)
   - Zwischen den Abschnitten befinden sich Trennstriche
   - Änderungen werden sofort angewendet und der Button neu gezeichnet

2. **Globale Einstellungen**:
   - Enthält allgemeine Einstellungen für alle Buttons
   - Änderungen werden sofort auf alle Buttons angewendet

## Performance-Optimierungen

1. **Ereignisbehandlung**:
   - Langklicks werden mit einem Timer erkannt
   - Bei Verschieben von Buttons werden Widgets wiederverwendet, anstatt neu erstellt


