import sys

import qdarktheme
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                               QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
                               QLabel, QListWidgetItem, QSplitter, QSizePolicy, QStyledItemDelegate, QHeaderView,
                               QFrame, QGraphicsDropShadowEffect, QMenu, QFileDialog)
from PySide6.QtCore import Qt, QEvent, Signal, Slot

from core import Transition, Sequence, Rotation, config
from core.constants import ACTION_NAMES


# class Sequence:
#     def __init__(self, name, actions, transitions=None):
#         self.name = name
#         self.actions = actions
#         self.transitions = transitions or []
#
#
# class Transition:
#     def __init__(self, to, on, to_position=0):
#         self.to = to
#         self.on = on
#         self.to_position = to_position
#
#
# class StateMachine:
#     def __init__(self):
#         self.sequences = []
from ui.style import global_style_sheet


class CustomItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(40)  # Set the height of the list item
        return size


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(self.items)
        combo.currentIndexChanged.connect(lambda: self.commitData.emit(combo))
        return combo

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        if value:
            editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.DisplayRole)


class EditableComboBoxItem(QWidget):
    valueChanged = Signal(str)

    def __init__(self, actions, initial_text, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel(initial_text)
        self.combo = QComboBox()
        self.combo.addItems(actions)
        self.combo.setVisible(False)
        self.combo.setStyleSheet("""
            QComboBox {
                background-color: #444444;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #555555;
                color: white;
            }
        """)
        self.combo.setMinimumHeight(40)  # Set the height to match the list item height

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.label.mouseDoubleClickEvent = self.edit_item
        self.combo.activated.connect(self.finish_edit)
        self.combo.installEventFilter(self)

    def edit_item(self, event):
        self.label.setVisible(False)
        self.combo.setVisible(True)
        self.combo.setCurrentText(self.label.text())
        self.combo.setFocus()

    def finish_edit(self):
        self.label.setText(self.combo.currentText())
        self.label.setVisible(True)
        self.combo.setVisible(False)
        self.valueChanged.emit(self.combo.currentText())

    def eventFilter(self, obj, event):
        if obj == self.combo:
            if event.type() == QEvent.FocusOut and not self.combo.view().hasFocus():
                self.finish_edit()
        return super().eventFilter(obj, event)


class SequenceListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            # Ignore F2 key to prevent entering edit mode
            event.ignore()
        else:
            # Call the base class implementation for other keys
            super().keyPressEvent(event)


class RotationEditor(QWidget):
    rotation_changed = Signal()

    def __init__(self):
        super().__init__()

        # Properties
        self.setWindowTitle("Rotation Editor")
        self.setFixedSize(1024, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet(global_style_sheet)

        # Widgets
        self.record_button = None
        self.transition_table = None
        self.action_combo = None
        self.action_list = None
        self._sequence_list = None
        self.sequence_name_le = None

        self.to_delegate = None
        self.on_delegate = None

        #
        self.file_path = None
        self.record_actions = False

        self.state_machine = Rotation()

        self.init_ui()

    def init_ui(self):
        # Layouts
        main_layout = QHBoxLayout()
        sequence_layout = QVBoxLayout()
        sequence_button_layout = QHBoxLayout()
        action_layout = QVBoxLayout()
        action_button_layout = QHBoxLayout()
        transition_layout = QVBoxLayout()
        transition_button_layout = QHBoxLayout()

        # Layout Settings
        main_layout.setContentsMargins(0, 0, 5, 0)
        action_layout.setContentsMargins(10, 10, 10, 10)
        action_layout.setSpacing(10)
        transition_layout.setSpacing(10)
        transition_button_layout.addStretch()

        # Sequence Widgets
        menu_button = QPushButton("Menu")
        menu_button.setObjectName("Menu")

        menu_button.setContentsMargins(20, 0, 0, 0)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                border: 1px solid #444444;  /* Set border color and thickness */
                margin-top:2px;
                width: 150px;  /* Adjust width to ensure full display */
                border-radius: 5px;
            }
            QMenu::item {
                padding-right: 50px;  /* Add padding to accommodate shortcut text */
            }
        """)

        # Actions
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new)

        open_action = QAction("Open", self, triggered=self.on_open)
        open_action.setShortcut("Ctrl+O")

        save_action = QAction("Save", self, triggered=self.on_save)
        save_action.setShortcut("Ctrl+S")

        save_as_action = QAction("Save As", self, triggered=self.on_save_as)

        close_action = QAction("Close", self, triggered=self.on_close)
        close_action.setShortcut("Ctrl+W")

        menu.addAction(new_action)
        menu.addSeparator()
        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(save_action)
        menu.addAction(save_as_action)
        menu.addSeparator()
        menu.addAction(close_action)
        menu_button.setMenu(menu)

        self._sequence_list = SequenceListWidget()
        self._sequence_list.setObjectName("sequence_list")
        self._sequence_list.setItemDelegate(CustomItemDelegate(self._sequence_list))
        self._sequence_list.itemClicked.connect(self.on_sequence_selected)
        self._sequence_list.itemChanged.connect(self.on_sequence_name_edited)

        self.sequence_name_le = QLineEdit()
        self.sequence_name_le.setMinimumHeight(100)  # Set the desired height
        self.sequence_name_le.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sequence_name_le.setPlaceholderText("Sequence Name")
        self.sequence_name_le.returnPressed.connect(self.add_sequence)

        add_sequence_button = QPushButton("Add")
        add_sequence_button.clicked.connect(self.add_sequence)
        add_sequence_button.setProperty("flat", True)  # Set custom property

        # Populate Sequence Layout
        sequence_button_layout.addWidget(self.sequence_name_le)
        sequence_button_layout.addWidget(add_sequence_button)

        sequence_layout.addWidget(menu_button)
        sequence_layout.addWidget(self._sequence_list)
        sequence_layout.addLayout(sequence_button_layout)

        # Create Sequence Widget
        sequence_widget = QWidget()
        sequence_widget.setObjectName("sequence_widget")  # Set object name for styling
        sequence_widget.setLayout(sequence_layout)
        sequence_widget.setFixedSize(200, 600)  # Fixed size for the entire sequence section

        # Action Widgets
        action_title_lb = QLabel("Actions")
        action_title_lb.setStyleSheet("font-size: 14px; font-weight: bold; color: #aaaaaa;")

        self.record_button = QPushButton("Record")
        self.record_button.setProperty("flat", True)
        self.record_button.clicked.connect(self.toggle_recording)

        self.action_list = QListWidget()
        self.action_list.setObjectName("action_list")
        self.action_list.setItemDelegate(CustomItemDelegate(self.action_list))

        self.action_combo = QComboBox()
        self.action_combo.addItems(ACTION_NAMES)  # Add your predefined actions here

        add_action_button = QPushButton("Add")
        add_action_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_action_button.clicked.connect(self.add_action)
        add_action_button.setProperty("flat", True)  # Set custom property

        # Populate Action layout
        action_button_layout.addWidget(self.action_combo)
        action_button_layout.addWidget(add_action_button)

        action_title_layout = QHBoxLayout()
        action_title_layout.addWidget(action_title_lb)
        action_title_layout.addWidget(self.record_button)

        action_layout.addLayout(action_title_layout)
        action_layout.addWidget(self.action_list)
        action_layout.addLayout(action_button_layout)

        # Create Action Widget
        action_card = QFrame()
        action_card.setLayout(action_layout)
        action_card.setFixedWidth(280)

        # Transition Widgets
        transition_title_lb = QLabel("Transitions")
        transition_title_lb.setStyleSheet("font-size: 14px; font-weight: bold; color: #aaaaaa; padding: 10px")

        self.transition_table = QTableWidget(0, 3)
        self.transition_table.setHorizontalHeaderLabels(["To", "On", "To Position"])
        self.transition_table.horizontalHeader().setStretchLastSection(True)
        self.transition_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Create and set delegates for "To" and "On" columns
        self.to_delegate = ComboBoxDelegate(self.sequence_names())
        self.on_delegate = ComboBoxDelegate(["complete"] + ACTION_NAMES)

        self.transition_table.setItemDelegateForColumn(0, self.to_delegate)
        self.transition_table.setItemDelegateForColumn(1, self.on_delegate)
        self.transition_table.cellChanged.connect(self.on_transition_table_cell_changed)

        add_transition_button = QPushButton("Add")
        add_transition_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_transition_button.clicked.connect(self.add_transition)
        add_transition_button.setProperty("flat", True)  # Set custom property

        # Populate transition layout
        transition_button_layout.addWidget(add_transition_button)
        transition_layout.addWidget(transition_title_lb)
        transition_layout.addWidget(self.transition_table)
        transition_layout.addLayout(transition_button_layout)

        # Create Transition widget
        transition_widget = QWidget()
        transition_widget.setLayout(transition_layout)

        # Main Layout
        main_layout.addWidget(sequence_widget)
        main_layout.addWidget(action_card)
        main_layout.addWidget(transition_widget)

        self.setLayout(main_layout)

        self.load_rotation_from_config()

    def update_ui(self):
        self._sequence_list.clear()
        for sequence in self.state_machine._sequences:
            item = QListWidgetItem(sequence.name)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setData(Qt.UserRole, sequence.name)
            self._sequence_list.addItem(item)
        self.action_list.clear()
        self.transition_table.setRowCount(0)

    def toggle_recording(self):
        self.record_actions = not self.record_actions
        self.record_button.setText('Stop Recording' if self.record_actions else 'Record')

    def update_window_title(self):
        if self.file_path:
            self.setWindowTitle(f"Rotation Editor  -  {self.file_path}")
        else:
            self.setWindowTitle(f"Rotation Editor  -  Untitled")

    def load_rotation_from_config(self):
        if config.rotation_file_path:
            self.state_machine = Rotation.load_from_file(config.rotation_file_path)
            self.file_path = config.rotation_file_path
            self.to_delegate.items = self.sequence_names()
            self.update_window_title()
            self.update_ui()

            if self._sequence_list.count() > 0:
                first_item = self._sequence_list.item(0)
                self._sequence_list.setCurrentItem(first_item)
                self.on_sequence_selected(first_item)

    def on_new(self):
        self.state_machine = Rotation()
        self._sequence_list.clear()
        self.action_list.clear()
        self.transition_table.setRowCount(0)
        self.file_path = None
        self.update_window_title()

    def on_save(self):
        if self.file_path:
            self.state_machine.save_to_file(self.file_path)
            config.rotation_file_path = self.file_path
            config.save()
            self.rotation_changed.emit()
            print(f"State machine saved to {self.file_path}")
        else:
            self.on_save_as()

    def on_save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Rotation", "", "JSON Files (*.json)")
        if file_path:
            self.state_machine.save_to_file(file_path)
            self.file_path = file_path
            self.update_window_title()
            config.rotation_file_path = self.file_path
            config.save()
            self.rotation_changed.emit()
            print(f"State machine saved to {file_path}")

    def on_open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Rotation", "", "JSON Files (*.json)")
        if file_path:
            self.state_machine = Rotation.load_from_file(file_path)
            self.file_path = file_path
            config.rotation_file_path = self.file_path
            config.save()
            self.to_delegate.items = self.sequence_names()
            self.rotation_changed.emit()
            self.update_window_title()
            self.update_ui()
            print(f"State machine loaded from {file_path}")

            if self._sequence_list.count() > 0:
                first_item = self._sequence_list.item(0)
                self._sequence_list.setCurrentItem(first_item)
                self.on_sequence_selected(first_item)

    def on_close(self):
        self.close()

    def sequence_names(self):
        return [seq.name for seq in self.state_machine._sequences]

    def add_sequence(self):
        sequence_name = self.sequence_name_le.text()
        if sequence_name:
            new_sequence = Sequence(sequence_name, [])
            self.state_machine.add_sequence(new_sequence)

            item = QListWidgetItem(sequence_name)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setData(Qt.UserRole, sequence_name)

            self._sequence_list.addItem(item)
            self._sequence_list.setCurrentItem(item)

            self.sequence_name_le.clear()

            self.to_delegate.items = self.sequence_names()

    def on_sequence_selected(self, item):
        selected_sequence_name = item.text()
        selected_sequence = next(seq for seq in self.state_machine._sequences if seq.name == selected_sequence_name)
        self.update_action_list(selected_sequence)
        self.update_transition_table(selected_sequence)

    def on_sequence_name_edited(self, item):
        old_name = item.data(Qt.UserRole)
        new_name = item.text()
        sequence = next(seq for seq in self.state_machine._sequences if seq.name == old_name)
        sequence.name = new_name
        item.setData(Qt.UserRole, new_name)
        self.to_delegate.items = self.sequence_names()

    def update_action_list(self, sequence):
        self.action_list.clear()
        for idx, action in enumerate(sequence.actions):
            item_widget = EditableComboBoxItem(["action1", "action2", "action3"], action)  # TODO: Add actions
            item_widget.valueChanged.connect(lambda value, i=idx: self.update_action(sequence, i, value))
            item = QListWidgetItem(self.action_list)
            item.setSizeHint(item_widget.sizeHint())
            self.action_list.setItemWidget(item, item_widget)

    def update_action(self, sequence, index, value):
        sequence.actions[index] = value

    def update_transition_table(self, sequence):
        self.transition_table.setRowCount(0)
        for transition in sequence.transitions:
            row_position = self.transition_table.rowCount()
            self.transition_table.insertRow(row_position)
            self.transition_table.setItem(row_position, 0, QTableWidgetItem(transition.to))
            self.transition_table.setItem(row_position, 1, QTableWidgetItem(transition.on))
            self.transition_table.setItem(row_position, 2, QTableWidgetItem(str(transition.to_position)))

    def add_action(self):
        selected_action = self.action_combo.currentText()
        if selected_action:
            current_item = self._sequence_list.currentItem()
            if current_item:
                selected_sequence_name = current_item.text()
                selected_sequence = next(seq for seq in self.state_machine._sequences if seq.name == selected_sequence_name)
                selected_sequence.actions.append(selected_action)
                self.update_action_list(selected_sequence)

    def handle_control_press(self, control):
        if not self.record_actions:
            return

        if control in ACTION_NAMES:
            current_item = self._sequence_list.currentItem()
            if current_item:
                selected_sequence_name = current_item.text()
                selected_sequence = next(
                    seq for seq in self.state_machine._sequences if seq.name == selected_sequence_name)
                selected_sequence.actions.append(control)
                self.update_action_list(selected_sequence)

    def add_transition(self):
        current_item = self._sequence_list.currentItem()
        if current_item:
            selected_sequence_name = current_item.text()
            selected_sequence = next(seq for seq in self.state_machine._sequences if seq.name == selected_sequence_name)
            new_transition = Transition(self.sequence_names()[0], "complete", 0)
            selected_sequence.transitions.append(new_transition)
            self.update_transition_table(selected_sequence)

    @Slot(int, int)
    def on_transition_table_cell_changed(self, row, column):
        current_item = self._sequence_list.currentItem()
        if not current_item:
            return

        selected_sequence_name = current_item.text()
        selected_sequence = next(seq for seq in self.state_machine._sequences if seq.name == selected_sequence_name)
        if column == 0:
            selected_sequence.transitions[row].to = self.transition_table.item(row, column).text()
        elif column == 1:
            selected_sequence.transitions[row].on = self.transition_table.item(row, column).text()
        elif column == 2:
            selected_sequence.transitions[row].to_position = int(self.transition_table.item(row, column).text())


if __name__ == "__main__":

    app = QApplication(sys.argv)
    qdarktheme.setup_theme(additional_qss=global_style_sheet)
    _editor = RotationEditor()
    _editor.setStyleSheet(global_style_sheet)
    _editor.show()
    sys.exit(app.exec())
