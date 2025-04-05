# Was noch zu erledigen ist:
[x] Neuzeichnen bei F5, inklusive erneutem Theme-Auslesen
[x] Relative Pfade
[ ] Dialog Globale-Einstellingen
[ ] Neuen Button erstellen zum Global-Dialog hinzufügen
[x] Dialog Buttom-Einstellungen
[ ] Neuzeichnen nach schließen der Dialoge
[ ] Verschieben implementieren
[ ] Button vorschau im Button-Dialog, der sofort aktualisiert wird

# #############################################################################################################
# Funktioniert nicht, da die Soundbox-Elemente in Flowbox-Child-containern stecken
        for child in self.flowbox.get_children():
            if isinstance(child, Soundbutton):  # Sicherstellen, dass es sich um einen Button handelt
                child.apply_colors_and_css()
                child.queue_draw()

# #############################################################################################################
# Das geht, ist aber noch sperrig
        for child in children:
            print(f"Kind-Typ: {type(child)}")
            # Hole das eigentliche Widget aus dem FlowBoxChild
            if isinstance(child, Gtk.FlowBoxChild):
                widget = child.get_child()
                print(f"Widget im FlowBoxChild: {type(widget)}")
                if isinstance(widget, Soundbutton):
                    print(f"Soundbutton gefunden: Position {widget.button_config['position']}")
                    widget.apply_colors_and_css()
                    widget.queue_draw()
                else:
                    print(f"Kein Soundbutton im FlowBoxChild: {widget}")
            else:
                print(f"Kein FlowBoxChild: {child}")

# #############################################################################################################
# Das geht und ist schön kompakt
        for child in self.flowbox.get_children():
            if isinstance(child.get_child(), Soundbutton):  # Sicherstellen, dass es sich um einen Button handelt
                child.get_child().apply_colors_and_css()
                child.get_child().queue_draw()
 