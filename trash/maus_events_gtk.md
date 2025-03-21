# GTK Maus-Events Übersicht

Diese Dokumentation bietet einen umfassenden Überblick über die verschiedenen Maus-Events, die vom GTK-System bereitgestellt und in Python-GTK-Anwendungen verwendet werden können.

## Haupt-Maus-Events

### 1. BUTTON_PRESS_MASK
- **Beschreibung**: Wird ausgelöst, wenn eine Maustaste gedrückt wird
- **Event-Objekt-Eigenschaften**:
  - `event.button`: Nummer der gedrückten Taste (1 = links, 2 = Mitte, 3 = rechts)
  - `event.x`, `event.y`: Position des Mauszeigers relativ zum Widget
  - `event.state`: Modifikatoren wie gedrückte Tasten (z.B. Control, Shift)
- **Typischer Callback**: `on_button_press`
- **Verwendung**:
  ```python
  widget.connect("button-press-event", self.on_button_press)
  ```

### 2. BUTTON_RELEASE_MASK
- **Beschreibung**: Wird ausgelöst, wenn eine Maustaste losgelassen wird
- **Event-Objekt-Eigenschaften**: Gleich wie bei BUTTON_PRESS_MASK
- **Typischer Callback**: `on_button_release`
- **Verwendung**:
  ```python
  widget.connect("button-release-event", self.on_button_release)
  ```

### 3. POINTER_MOTION_MASK
- **Beschreibung**: Wird ausgelöst, wenn die Maus bewegt wird, unabhängig vom Status der Maustasten
- **Event-Objekt-Eigenschaften**:
  - `event.x`, `event.y`: Aktuelle Position des Mauszeigers
  - `event.state`: Zustand der Modifikatoren und Maustasten während der Bewegung
- **Typischer Callback**: `on_motion_notify`
- **Verwendung**:
  ```python
  widget.connect("motion-notify-event", self.on_motion_notify)
  ```

### 4. SCROLL_MASK
- **Beschreibung**: Erfasst Mausrad-Scrolling-Events (vertikal und horizontal)
- **Event-Objekt-Eigenschaften**:
  - `event.direction`: Scrollrichtung (GDK_SCROLL_UP, GDK_SCROLL_DOWN, GDK_SCROLL_LEFT, GDK_SCROLL_RIGHT)
  - `event.x`, `event.y`: Position des Mauszeigers während des Scrollens
- **Typischer Callback**: `on_scroll`
- **Verwendung**:
  ```python
  widget.connect("scroll-event", self.on_scroll)
  ```

### 5. SMOOTH_SCROLL_MASK
- **Beschreibung**: Erfasst präzisere Scrolling-Events, besonders nützlich für Touchpads
- **Event-Objekt-Eigenschaften**:
  - `event.delta_x`, `event.delta_y`: Präzise Scroll-Deltas
- **Typischer Callback**: `on_scroll`
- **Verwendung**: Wie bei SCROLL_MASK, aber mit präziseren Werten

## Spezifische Bewegungs-Events

### 6. BUTTON1_MOTION_MASK
- **Beschreibung**: Wird ausgelöst, wenn die Maus bewegt wird, während die linke Maustaste gedrückt ist
- **Besonderheit**: Besonders nützlich für Drag-Operationen
- **Prüfung in POINTER_MOTION_MASK-Handler**:
  ```python
  if event.state & Gdk.ModifierType.BUTTON1_MASK:
      # Linke Maustaste ist gedrückt während der Bewegung
  ```

### 7. BUTTON2_MOTION_MASK
- **Beschreibung**: Wird ausgelöst, wenn die Maus bewegt wird, während die mittlere Maustaste gedrückt ist
- **Prüfung in POINTER_MOTION_MASK-Handler**:
  ```python
  if event.state & Gdk.ModifierType.BUTTON2_MASK:
      # Mittlere Maustaste ist gedrückt während der Bewegung
  ```

### 8. BUTTON3_MOTION_MASK
- **Beschreibung**: Wird ausgelöst, wenn die Maus bewegt wird, während die rechte Maustaste gedrückt ist
- **Prüfung in POINTER_MOTION_MASK-Handler**:
  ```python
  if event.state & Gdk.ModifierType.BUTTON3_MASK:
      # Rechte Maustaste ist gedrückt während der Bewegung
  ```

### 9. BUTTON_MOTION_MASK
- **Beschreibung**: Wird ausgelöst, wenn die Maus bewegt wird, während irgendeine Maustaste gedrückt ist
- **Hinweis**: Eine Kombination aus BUTTON1_MOTION_MASK, BUTTON2_MOTION_MASK und BUTTON3_MOTION_MASK

## Widget-Betreten/Verlassen-Events

### 10. ENTER_NOTIFY_MASK
- **Beschreibung**: Wird ausgelöst, wenn der Mauszeiger ein Widget betritt
- **Typischer Callback**: `on_enter_notify`
- **Verwendung**:
  ```python
  widget.connect("enter-notify-event", self.on_enter_notify)
  ```
- **Anwendungsbeispiel**: Hover-Effekte, Tooltip-Anzeige

### 11. LEAVE_NOTIFY_MASK
- **Beschreibung**: Wird ausgelöst, wenn der Mauszeiger ein Widget verlässt
- **Typischer Callback**: `on_leave_notify`
- **Verwendung**:
  ```python
  widget.connect("leave-notify-event", self.on_leave_notify)
  ```
- **Anwendungsbeispiel**: Zurücksetzen von Hover-Effekten

## Leistungsoptimierung

### 12. POINTER_MOTION_HINT_MASK
- **Beschreibung**: Reduziert die Anzahl der Bewegungsereignisse für eine bessere Leistung
- **Funktionsweise**: Das System sendet nur ein Ereignis und wartet dann, bis die Anwendung explizit nach der aktuellen Mausposition fragt
- **Nutzung**: Kombinieren mit POINTER_MOTION_MASK für effizientere Bewegungsverarbeitung in leistungsintensiven Anwendungen

## Touch-Events

### 13. TOUCH_MASK
- **Beschreibung**: Erfasst Touch-Events von Touchscreens
- **Event-Objekt-Eigenschaften**:
  - `event.touch.sequence`: Touch-Sequenz (für Multi-Touch)
  - `event.x`, `event.y`: Berührungsposition
- **Typische Callbacks**: `on_touch_begin`, `on_touch_update`, `on_touch_end`
- **Unterstützung**: Multi-Touch-Gesten

### 14. TOUCHPAD_GESTURE_MASK
- **Beschreibung**: Erfasst Touchpad-Gesten wie Pinch-to-Zoom oder Zwei-Finger-Scrollen
- **Event-Objekt-Eigenschaften**: Abhängig von der Geste (Pinch, Swipe, etc.)
- **Typische Callbacks**: `on_gesture_pinch`, `on_gesture_swipe`

## Tablet-Events

### 15. PROXIMITY_IN_MASK
- **Beschreibung**: Wird ausgelöst, wenn ein Stift in die Nähe eines Grafiktabletts kommt
- **Typischer Callback**: `on_proximity_in`

### 16. PROXIMITY_OUT_MASK
- **Beschreibung**: Wird ausgelöst, wenn ein Stift sich vom Grafiktablett entfernt
- **Typischer Callback**: `on_proximity_out`

### 17. TABLET_PAD_MASK
- **Beschreibung**: Erfasst Events von Tablet-Pad-Tasten und -Reglern
- **Verwendung**: Nützlich für professionelle Grafiksoftware

## Allgemeine Events

### 18. ALL_EVENTS_MASK
- **Beschreibung**: Eine Kombination aller Event-Masken
- **Warnung**: Kann die Leistung beeinträchtigen, da sehr viele Events generiert werden
- **Empfehlung**: In der Regel besser, nur die tatsächlich benötigten Events zu aktivieren

## Praktische Anwendung

### Aktivieren von Events für ein Widget

```python
widget.add_events(
    Gdk.EventMask.BUTTON_PRESS_MASK |
    Gdk.EventMask.BUTTON_RELEASE_MASK |
    Gdk.EventMask.POINTER_MOTION_MASK |
    Gdk.EventMask.SCROLL_MASK
)
```

### Typische Kombination für Drag & Drop

```python
widget.add_events(
    Gdk.EventMask.BUTTON_PRESS_MASK |
    Gdk.EventMask.BUTTON_RELEASE_MASK |
    Gdk.EventMask.POINTER_MOTION_MASK
)

# Event-Handler
widget.connect("button-press-event", self.on_button_press)
widget.connect("button-release-event", self.on_button_release)
widget.connect("motion-notify-event", self.on_motion_notify)
```

### Beispiel für einen einfachen Drag & Drop-Handler

```python
def on_button_press(self, widget, event):
    if event.button == 1:  # Linke Maustaste
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    return True

def on_motion_notify(self, widget, event):
    if self.dragging:
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        # Bewege das Widget oder andere Aktion
    return True

def on_button_release(self, widget, event):
    if event.button == 1:  # Linke Maustaste
        self.dragging = False
        # Abschließende Aktionen
    return True
```

## Ereignis-Propagierung

GTK-Ereignisse werden von den äußersten Containern zu den innersten Widgets propagiert. Der Rückgabewert des Event-Handlers bestimmt, ob das Event weiter propagieren soll:

- `return True`: Stoppt die Propagierung (Event wurde verarbeitet)
- `return False`: Event propagiert weiter zu anderen Widgets

## Tastatur-Modifikatoren in Maus-Events

Häufig verwendete Modifikatoren in `event.state`:

```python
if event.state & Gdk.ModifierType.CONTROL_MASK:
    # Control-Taste ist gedrückt
    
if event.state & Gdk.ModifierType.SHIFT_MASK:
    # Shift-Taste ist gedrückt
    
if event.state & Gdk.ModifierType.MOD1_MASK:
    # Alt-Taste ist gedrückt
```

Diese können mit Maus-Events kombiniert werden, um erweiterte Interaktionen zu ermöglichen. 