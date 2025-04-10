import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

class SoundButton(Gtk.EventBox):
    def __init__(self, label_text, click_callback=None):
        super().__init__()
        self.set_visible_window(False)

        self.label = Gtk.Label(label=label_text)
        self.label.set_name("sound-button")
        self.add(self.label)

        self.click_callback = click_callback
        self.drag_started = False
        self.click_position = None

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)

        self.connect("button-press-event", self.on_button_press)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("button-release-event", self.on_button_release)
        self.connect("drag-begin", self.on_drag_begin)

        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE)
        self.drag_source_add_text_targets()
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.MOVE)
        self.drag_dest_add_text_targets()

        self.connect("drag-data-get", self.on_drag_data_get)
        self.connect("drag-data-received", self.on_drag_data_received)

        self.apply_css()

    def apply_css(self):
        css = """
        .sound-button {
            background-color: #3a7ca5;
            color: #ffffff;
            border-radius: 8px;
            padding: 10px;
            min-width: 100px;
            min-height: 40px;
            font-weight: bold;
            font-size: 14px;
            border-style: solid;
            border-width: 2px;
            border-color: #ffffff #1c4e80 #1c4e80 #ffffff;
        }

        .sound-button-active {
            background-color: #2a5d84;
            border-color: #1c4e80 #ffffff #ffffff #1c4e80;
        }
        """

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.label.get_style_context().add_class("sound-button")

    def on_button_press(self, widget, event):
        if event.button == 1:
            self.click_position = (event.x_root, event.y_root)
            self.drag_started = False
            self.label.get_style_context().add_class("sound-button-active")

    def on_motion_notify(self, widget, event):
        if event.state & Gdk.ModifierType.BUTTON1_MASK and self.click_position:
            dx = abs(event.x_root - self.click_position[0])
            dy = abs(event.y_root - self.click_position[1])
            if dx > 8 or dy > 8 and not self.drag_started:
                self.drag_started = True
                # Erstelle eine TargetList für Text
                targets = Gtk.TargetList.new([])
                targets.add_text_targets(0)
                # Starte den Drag-Vorgang mit einem gültigen Objekt
                self.drag_begin_with_coordinates(targets, Gdk.DragAction.MOVE, 1, event, event.x_root, event.y_root)

    def on_button_release(self, widget, event):
        self.label.get_style_context().remove_class("sound-button-active")
        if not self.drag_started and event.button == 1:
            if self.click_callback:
                self.click_callback(self.label.get_text())

    def on_drag_begin(self, widget, drag_context):
        # Erstelle ein Pixbuf für die Vorschau
        alloc = self.get_allocation()
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, alloc.width, alloc.height)
        
        # Hole den Stilkontext und zeichne den Button
        style_context = self.get_style_context()
        style_context.save()
        style_context.add_class("sound-button")
        
        # Erstelle einen Cairo-Kontext für das Pixbuf
        window = self.get_window()
        if window:
            cr = window.cairo_create()
            
            # Zeichne den Button
            Gtk.render_background(style_context, cr, 0, 0, alloc.width, alloc.height)
            Gtk.render_frame(style_context, cr, 0, 0, alloc.width, alloc.height)
            
            # Zeichne den Text
            layout = self.label.get_layout()
            layout.set_text(self.label.get_text(), -1)
            text_width, text_height = layout.get_pixel_size()
            text_x = (alloc.width - text_width) / 2
            text_y = (alloc.height - text_height) / 2
            
            Gtk.render_layout(style_context, cr, text_x, text_y, layout)
            
            # Konvertiere den Cairo-Kontext in ein Pixbuf
            surface = cr.get_target()
            pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, alloc.width, alloc.height)
            
            # Setze das Pixbuf als Drag-Icon
            Gtk.drag_set_icon_pixbuf(drag_context, pixbuf, 0, 0)
        
        # Stelle den Stilkontext wieder her
        style_context.restore()

    def on_drag_data_get(self, widget, drag_context, data, info, time):
        data.set_text(self.label.get_text(), -1)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        source_text = data.get_text()
        target_text = self.label.get_text()
        self.label.set_text(source_text)

        for child in self.get_toplevel().get_children()[0].get_children():
            if isinstance(child, SoundButton) and child != self:
                if child.label.get_text() == source_text:
                    child.label.set_text(target_text)
                    break

        Gtk.drag_finish(drag_context, True, False, time)

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Drag-and-Drop Buttons mit Screenshot")
        self.set_default_size(600, 400)

        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_max_children_per_line(4)

        def on_click(label_text):
            print(f"Geklickt: {label_text}")

        for i in range(12):
            btn = SoundButton(f"Button {i+1}", on_click)
            flow.add(btn)

        scroll = Gtk.ScrolledWindow()
        scroll.add(flow)
        self.add(scroll)
        self.show_all()

win = MainWindow()
win.connect("destroy", Gtk.main_quit)
Gtk.main()
