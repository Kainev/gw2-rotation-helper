global_style_sheet = """
    #sequence_widget {
        background-color: #1c1c1f;
    }

    #sequence_list {
        background-color: #1c1c1f;
    }

    QTableWidget {
        border: none;
    }

    QHeaderView::section {
        background-color: #1c1c1f;
        color: white;
        padding: 5px;
        border: none;
    }

    QTableCornerButton::section {
        background-color: #1c1c1f;
    }

    QListWidget {
        border: none;
        margin: 0;
        background-color: #101012
    }
    QListWidget::item {
        border-radius: 3px;
        color: #aaaaaa;    /* Slightly gray color */
        font-weight: bold; /* Greater font weight */

    }
    QListWidget::item:selected {
        color: #ffffff;  /* Ensure the selected item text color is white */
        background-color: #2b4774;
    }

    QComboBox {
        background-color: #202124;
        color: white;
        padding: 5px;
        border-radius: 5px;
    }

    QLineEdit {
        padding: 10px;
        background-color: #1c1c1f;
    }

    QPushButton[flat="true"] {
        height: 30px;
    }

    QPushButton#Menu {
        height: 24px;
        background-color: #2a2b2f;

    }

    QPushButton#Menu::menu-indicator { image: none; }
"""