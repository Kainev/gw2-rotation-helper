from PySide6.QtCore import QObject, Signal

import keyboard


class ControlsHandler(QObject):
    on_control_pressed = Signal(str)

    def __init__(self, controls, parent=None):
        super().__init__(parent=parent)
        self.controls = controls

        self.modifiers = set()
        self.last_key = None
        self.current_key = None

        self.setup_listeners()

    def setup_listeners(self):
        keyboard.hook(self.on_event)

    def on_event(self, event):
        key = event.name
        scan_code = event.scan_code

        if event.event_type == keyboard.KEY_DOWN:
            if key in {'ctrl', 'alt', 'shift', 'cmd'}:
                self.modifiers.add(key)
            else:
                self.last_key = self.current_key
                self.current_key = scan_code

                if self.last_key != self.current_key:
                    self.check_input()
        elif event.event_type == keyboard.KEY_UP:
            if key in {'ctrl', 'alt', 'shift', 'cmd'}:
                self.modifiers.discard(key)
            else:
                self.current_key = None

    def check_input(self):
        for control in self.controls:
            if self.modifiers == control.modifiers and self.current_key in control.scan_codes:
                self.on_control_pressed.emit(control.name)
                break
