import sys
from functools import partial
from threading import Thread

from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtWidgets import QApplication

import qdarktheme

from core import (
    config,
    FocusHook, get_screen_by_window_title,
    Rotation
)

from core.constants import (
    GW2_WINDOW_TITLE,
    GW2RH_WINDOW_TITLE,
)

from ui import (
    ActionHighlighter,
    ControlsHandler, RotationEditor
)
from ui.style import global_style_sheet


class RotationHelper(QObject):
    focus_changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        self._screen = get_screen_by_window_title(GW2_WINDOW_TITLE)

        try:
            self._state_machine = Rotation.load_from_file(config.rotation_file_path)
        except FileNotFoundError:
            self._state_machine = Rotation()

        self._controls_handler = ControlsHandler(config.controls, self)
        self._controls_handler.on_control_pressed.connect(self._handle_control_pressed)

        initial_sequence_name = self._state_machine.current_sequence.name if self._state_machine.current_sequence else "No Rotation"
        self._highlighter = ActionHighlighter(
            action=self._state_machine.action,
            screen=self._screen,
            label=initial_sequence_name
        )

        self._rotation_editor = None

        self._last_focused_window = ""

        self._focus_hook: FocusHook = FocusHook(partial(RotationHelper._on_focus_callback, self))
        self._start_focus_hook()

        self._hotkey_actions = {
            'toggle_rotation_editor': self._toggle_rotation_editor,
            'reset_rotation': self._reset_rotation,
            'reset_sequence': self._reset_sequence,
            'next_sequence': self._next_sequence
        }

        self.focus_changed.connect(self._on_focus_changed)

    def _start_focus_hook(self):
        focus_hook_thread = Thread(target=self._focus_hook.start)
        focus_hook_thread.daemon = True
        focus_hook_thread.start()

    def _on_focus_callback(self, window):
        self.focus_changed.emit(window)

    @Slot(str)
    def _on_focus_changed(self, window):
        if window == GW2RH_WINDOW_TITLE and self._last_focused_window != GW2_WINDOW_TITLE:
            self._highlighter.hide()
        elif window in [GW2_WINDOW_TITLE, GW2RH_WINDOW_TITLE]:
            self._highlighter.show()
        else:
            self._highlighter.hide()

        self._last_focused_window = window

    @Slot(str)
    def _handle_control_pressed(self, control):
        if not self._state_machine:
            return

        state_changed = self._state_machine.on_control_pressed(control)

        if state_changed:
            self._highlighter.highlight = self._state_machine.action
            self._highlighter.label = self._state_machine.current_sequence.name
        else:
            try:
                self._hotkey_actions[control]()
            except KeyError:
                pass

        if self._rotation_editor:
            self._rotation_editor.handle_control_press(control)

    def _next_sequence(self):
        self._state_machine.next()
        self._highlighter.highlight = self._state_machine.action
        self._highlighter.label = self._state_machine.current_sequence.name

    def _reset_rotation(self):
        self._state_machine.reset()
        self._highlighter.highlight = self._state_machine.action
        self._highlighter.label = self._state_machine.current_sequence.name

    def _reset_sequence(self):
        self._state_machine.reset_sequence()
        self._highlighter.highlight = self._state_machine.action
        self._highlighter.label = self._state_machine.current_sequence.name

    def _toggle_rotation_editor(self):
        if not self._rotation_editor:
            self._rotation_editor = RotationEditor()

            self._rotation_editor.show()
            self._rotation_editor.raise_()
            self._rotation_editor.activateWindow()

            self._rotation_editor.destroyed.connect(self._on_rotation_editor_closed)
            self._rotation_editor.rotation_changed.connect(self._on_rotation_modified)
        else:
            self._rotation_editor.close()
            self._rotation_editor = None

    @Slot()
    def _on_rotation_editor_closed(self):
        self._rotation_editor = None

    def _on_rotation_modified(self):
        self._highlighter.close()

        self._state_machine = Rotation.load_from_file(config.rotation_file_path)
        self._highlighter = ActionHighlighter(
            action=self._state_machine.action,
            screen=self._screen,
            label=self._state_machine.current_sequence.name
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Guild Wars 2 Rotation Helper')

    qdarktheme.setup_theme(additional_qss=global_style_sheet)

    config.load()

    _main = RotationHelper(app)

    app.exec()
