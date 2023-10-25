from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt6.QtWidgets import QLabel, QTabWidget, QDial, QSpinBox, QDoubleSpinBox, QMenu, QCheckBox


class OperationPanel(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.gui_layout = QHBoxLayout()
        self.setLayout(self.gui_layout)
        self.gui_layout.setSpacing(1)

        button_test1 = QPushButton("A")
        self.gui_layout.addWidget(button_test1)
        button_test2 = QPushButton("B")
        self.gui_layout.addWidget(button_test2)
        button_test3 = QPushButton("C")
        self.gui_layout.addWidget(button_test3)
        button_test4 = QPushButton("D")
        self.gui_layout.addWidget(button_test4)
