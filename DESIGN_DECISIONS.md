# Designentscheidungen für pySoundboard

Dieses Dokument enthält wichtige Designentscheidungen, die während der Entwicklung getroffen wurden, um sicherzustellen, dass diese nicht in Vergessenheit geraten und bei zukünftigen Änderungen berücksichtigt werden.

## Allgemeine Architektur

- Das Programm verwendet GTK3 für die Benutzeroberfläche und pygame für die Audiowiedergabe
- Die Konfiguration wird in einer JSON-Datei gespeichert (config.json)
- Die Hauptklassen sind:
  - `SoundboardWindow`: Das Hauptfenster mit der FlowBox zur Anordnung der Buttons
  - `SoundButton`: Die einzelnen Buttons mit Audiowiedergabe-Funktionen
  - `SettingsDialog`: Dialog für Button-spezifische Einstellungen
  - `GlobalSettingsDialog`: Dialog für globale Einstellungen

## Button-Management

1. **Button-Erstellung und -Aktualisierung**:
   - Buttons werden nicht unnötig entfernt und neu erstellt, sondern ihre Eigenschaften werden aktualisiert
   - Bei Änderung der Button-Anzahl werden Buttons entfernt und neu erstellt
   - Der Add-Button wird immer neu erstellt, um Probleme zu vermeiden

2. **Button-Positionierung**:
   - Buttons werden anhand ihrer `position`-Eigenschaft sortiert
   - Beim Verschieben eines Buttons werden alle betroffenen Buttons entsprechend angepasst
   - Nach jeder Position-Änderung wird die Button-Liste sortiert und alle Buttons werden aktualisiert

3. **Add-Button**:
   - Der Add-Button ist ein spezieller Button mit `is_add_button=True`
   - Er wird immer als letzter Button angezeigt
   - Nach dem Klick wird er in einen normalen Button umgewandelt und ein neuer Add-Button wird erstellt

## Audio-Wiedergabe

1. **Ein- und Ausblenden**:
   - Die Audio-Wiedergabe hat eine Fade-In- und Fade-Out-Funktionalität
   - Timer werden verwendet, um die Lautstärke schrittweise zu erhöhen/verringern
   - Timer-Verwaltung erfolgt über GLib.timeout_source_new() und active_timers

2. **Lautstärkeregelung**:
   - Jeder Button hat einen eigenen Lautstärkeregler
   - Die Lautstärke wird in der Konfiguration gespeichert
   - Lautstärkeänderungen werden sofort angewendet

## Text und Darstellung

1. **Textausrichtung**:
   - Buttons unterstützen drei Ausrichtungen: links, zentriert, rechts
   - Die Ausrichtung wird in der Konfiguration gespeichert und beim Neuzeichnen angewendet

2. **Zeilenumbrüche**:
   - Zeilenumbrüche sind immer aktiviert (keine Einstellung mehr)
   - Dadurch wird die Benutzeroberfläche vereinfacht und das Erscheinungsbild verbessert

3. **Textpositionierung**:
   - Buttons können eine individuelle Textposition verwenden
   - Es werden Abstände von oben und links angegeben

4. **Farben**:
   - Buttons können individuelle Hintergrund- und Textfarben haben
   - Es gibt globale Standardfarben für alle Buttons

## Dialog-Anordnung

1. **Button-Einstellungsdialog**:
   - Die Reihenfolge der Einträge ist:
     1. Positionierung 
     2. Soundeinstellungen
     3. Buttontext/Textausrichtung/Textfarbe
     4. Buttonfarbe und Bild
     5. Button-Steuerelemente (Löschen, Abbrechen, OK)
   - Zwischen den Abschnitten befinden sich Trennstriche

2. **Globale Einstellungen**:
   - Enthält allgemeine Einstellungen für alle Buttons
   - Änderungen werden sofort auf alle Buttons angewendet

## Performance-Optimierungen

1. **Ereignisbehandlung**:
   - Langklicks werden mit einem Timer erkannt
   - Bei Verschieben von Buttons werden Widgets wiederverwendet, anstatt neu erstellt

2. **Speichern der Konfiguration**:
   - Die Konfiguration wird nur bei wichtigen Änderungen oder beim Beenden gespeichert
   - Dadurch wird die Anzahl der Schreibzugriffe auf die Festplatte reduziert 