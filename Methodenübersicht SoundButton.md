Methodenübersicht SoundButton:

class SoundButton(Gtk.Box):
    def __init__(self, position=0, config=None, on_delete=None, is_add_button=False):
    def _setup_ui(self):
    def _create_volume_slider(self, sb_config):
    def get_button_config(self):
    def hex_to_rgb(self, hex_color):
    def _rgba_to_hex(self, rgba):
    def get_theme_colors(self):
    def _apply_css_style(self):
    def _get_image_css(self, class_name, image_path):
    def update_image(self, image_path):
    def toggle_button_state(self):
    def _reset_button_state(self):
    def _remove_timer(self):
    def play_sound(self):
    def _start_fade_in(self):
    def _check_sound_finished(self, channel):
    def stop_sound(self):
    def _start_fade_out(self):
        def fade_step(user_data=None):
    def on_button_press(self, widget, event):
    def on_button_release(self, widget, event):
    def check_long_press(self):
    def show_settings_dialog(self):
    def _update_button_after_settings(self):
    def on_volume_changed(self, volume_slider):
    def set_add_click_handler(self, handler):
    def _hex_to_rgba(self, hex_color):