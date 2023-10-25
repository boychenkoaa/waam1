import sys

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QApplication
from PyQt6.QtWidgets import QMenu, QMenuBar, QFileDialog
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem

from viewport.panels.TransformPanel import ModelTransformPanel


class ProjectPanel(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self.parent = parent

        self.gui_layout = QVBoxLayout()
        self.setLayout(self.gui_layout)

        self.table = QTableWidget(0, 2)

        self.gui_layout.addWidget(self.table)

        # Наполним таблицу хоть чем-т0
        self.table.setRowCount(2)
        self.table.setItem(0, 0, QTableWidgetItem("Hello world"))

    def execute_command(self, input_command):
        # сюда обработку поступающих команд
        pass


class ControlPanel(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self.parent = parent

        self.gui_layout = QVBoxLayout()
        self.setLayout(self.gui_layout)

        self.transform_panel_model_widget = ModelTransformPanel(self)
        self.gui_layout.addWidget(self.transform_panel_model_widget)


class LeftPanel(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self.parent = parent

        self.gui_layout = QVBoxLayout()
        self.setLayout(self.gui_layout)

        self.project_panel_widget = ProjectPanel(self)
        self.control_panel_widget = ControlPanel(self)
        self.gui_layout.addWidget(self.project_panel_widget)
        self.gui_layout.addWidget(self.control_panel_widget)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self._createMenuBar()
        self._initUI()

    def _createMenuBar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)

        fileMenu = QMenu("File", self)
        menuBar.addMenu(fileMenu)

        fileMenu.addSeparator()
        importAction = fileMenu.addAction("Import model")
        importAction.triggered.connect(self.import_model)

    def _initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.gui_layout = QVBoxLayout()
        self.central_widget.setLayout(self.gui_layout)

        self.left_panel = LeftPanel(self)

        self.gui_layout.addWidget(self.left_panel)

    def import_model(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "../3D models",
            "STL Files (*.stl)",
        )

        if file_name[0] != '':
            print("File name", file_name[0])
            # Сюда вставить отправку реквеста при импорте модели
            # request = {"type": "add_model", "params": {"file_name": file_name[0]}}
            # self.project_mediator.execute_command(request)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
