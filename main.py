import sys
import os.path

from PyQt6.QtGui import QMatrix4x4, QSurfaceFormat
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, QApplication
from PyQt6.QtWidgets import QSplitter, QTabWidget, QMenuBar, QMenu, QFileDialog
from PyQt6.QtCore import Qt

from viewport.panels.ScenePanel import ScenePanel
from viewport.panels.OperationPanel import OperationPanel
from viewport.viewport2d.glwindow2d import Scene2D
from viewport.viewport3d.glwindow3d import Scene3D
from viewport.panels.ProjectPanel import ProjectPanel

from viewport.libs.SceneStorage import FrontendMediator
from viewport.libs.ProjectMediator import ProjectMediator
from viewport.libs.UltraGlobalMediator import UltraGlobalMediator

from config.configmanager import ConfigManager, ConfigParameters


class LeftPanel(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self.parent = parent

        self.gui_layout = QVBoxLayout()
        self.setLayout(self.gui_layout)

        self.project_panel_widget = ProjectPanel(self, self.parent.project_mediator)
        self.gui_layout.addWidget(self.project_panel_widget)

        button_upload_model = QPushButton("Upload model")
        self.gui_layout.addWidget(button_upload_model)
        button_upload_model.clicked.connect(self.button_upload_model_function)

    def button_upload_model_function(self):
        request = {"type": "add_model", "params": {"file_name": "3D models/cube.stl"}}
        self.parent.project_mediator.execute_command(request)


class RightPanel(QWidget):
    def __init__(self, parent=None, storage=None, *args, **kwargs):
        super().__init__()

        self.parent = parent
        self.storage = storage

        self.gui_layout = QVBoxLayout()
        self.setLayout(self.gui_layout)
        self.gui_layout.setSpacing(0)

        icons_vertical_layout = QHBoxLayout()
        self.gui_layout.addLayout(icons_vertical_layout)

        self.tab_bar_left = QTabWidget()
        self.tab_bar_left.setTabPosition(QTabWidget.TabPosition.East)
        self.gui_layout.addWidget(self.tab_bar_left)

        self.scene_panel_widget \
            = ScenePanel(self)
        self.tab_bar_left.addTab(self.scene_panel_widget, "Scene")

        self.operation_panel = OperationPanel(self)
        icons_vertical_layout.addWidget(self.operation_panel)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.ultra_global_mediator = UltraGlobalMediator()
        self.frontend_mediator = FrontendMediator()
        self.project_mediator = ProjectMediator()

        self.ultra_global_mediator.connect_objects([self.frontend_mediator,
                                                    self.project_mediator])

        self._createMenuBar()

        self.window3d = Scene3D(self)
        self.window2d = Scene2D(self)

        self.initUI()

        self.frontend_mediator.connect_objects([self.right_panel.scene_panel_widget,
                                                self.window2d.graphics_scene.scene_storage])

        self.project_mediator.connect_objects([self.left_panel.project_panel_widget,
                                               self.window3d.graphics_scene.scene_storage])

    def _createMenuBar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)

        fileMenu = QMenu("File", self)
        menuBar.addMenu(fileMenu)

        open_prj_action = fileMenu.addAction("Open project", self.open_prj_action_function)
        save_prj_action = fileMenu.addAction("Save project")
        save_prj_as_action = fileMenu.addAction("Save project as...")
        fileMenu.addSeparator()
        importAction = fileMenu.addAction("Import model")
        importAction.triggered.connect(self.import_model)

        infoMenu = menuBar.addMenu("Info")

    def initUI(self):
        self.central_widget = QWidget()
        self.gui_layout = QVBoxLayout()
        self.windows = QHBoxLayout()
        buttons_view = QHBoxLayout()
        self.central_widget.setLayout(self.gui_layout)
        self.setCentralWidget(self.central_widget)
        self.gui_layout.addLayout(self.windows)
        self.gui_layout.addLayout(buttons_view)

        button_view_model = QPushButton("M")
        buttons_view.addWidget(button_view_model)
        button_view_model.clicked.connect(self.button_view_model_function)

        button_view_model_slice = QPushButton("MS")
        buttons_view.addWidget(button_view_model_slice)
        button_view_model_slice.clicked.connect(self.button_view_model_slice_function)

        button_view_mix = QPushButton("X")
        buttons_view.addWidget(button_view_mix)
        button_view_mix.clicked.connect(self.button_view_mix_function)

        button_view_slice_model = QPushButton("SM")
        buttons_view.addWidget(button_view_slice_model)
        button_view_slice_model.clicked.connect(self.button_view_slice_model_function)

        button_view_slice = QPushButton("S")
        buttons_view.addWidget(button_view_slice)
        button_view_slice.clicked.connect(self.button_view_slice_function)

        button_view_model.setMaximumWidth(50)
        button_view_model_slice.setMaximumWidth(50)
        button_view_mix.setMaximumWidth(50)
        button_view_slice_model.setMaximumWidth(50)
        button_view_slice.setMaximumWidth(50)
        buttons_view.addStretch(1)  # move buttons to left

        self.left_panel = LeftPanel(self)
        self.right_panel = RightPanel(self)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.windows.addWidget(self.splitter)
        self.windows.setContentsMargins(0, 0, 0, 0)

        self.splitter.addWidget(self.left_panel)
        self.left_panel.setMinimumWidth(240)
        self.left_panel.setMaximumWidth(240)

        self.splitter.addWidget(self.window3d)
        self.window3d.setMinimumSize(400, 600)

        self.splitter.addWidget(self.window2d)
        self.window2d.setMinimumSize(400, 600)

        self.splitter.addWidget(self.right_panel)
        self.right_panel.setMinimumWidth(260)
        self.right_panel.setMaximumWidth(260)

        # splitter.setSizes([240, 1000, 1000, 240])  # Hide right panel
        self.splitter.setSizes([100, 1000, 1000, 100])

    def open_prj_action_function(self):
        print("Open project function")

    def import_model(self):
        prev_dir = ConfigManager.read_workspace_property(ConfigParameters.working_dir)
        if prev_dir == "" or not os.path.exists(prev_dir):
            prev_dir = "${HOME}"

        file_name = QFileDialog.getOpenFileName(
            self,
            "Open File",
            prev_dir,
            "STL Files (*.stl)",
        )
        if file_name[0] != '':
            ConfigManager.write_workspace_property(ConfigParameters.working_dir, file_name[0])
            print(file_name[0])
            # self.upload_3d_model(file_name[0])
            request = {"type": "add_model", "params": {"file_name": file_name[0]}}
            self.project_mediator.execute_command(request)

    def button_view_model_function(self):
        self.splitter.setSizes([100, 1000, 0, 0])

    def button_view_model_slice_function(self):
        self.splitter.setSizes([100, 1000, 500, 0])

    def button_view_mix_function(self):
        self.splitter.setSizes([100, 1000, 1000, 100])

    def button_view_slice_model_function(self):
        self.splitter.setSizes([0, 500, 1000, 100])

    def button_view_slice_function(self):
        self.splitter.setSizes([0, 0, 1000, 100])


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fmt = QSurfaceFormat()
    fmt.setVersion(4, 4)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    fmt.setSamples(4)
    fmt.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    fmt.setSwapInterval(1)
    QSurfaceFormat.setDefaultFormat(fmt)

    ex = MainWindow()
    ex.setWindowTitle("WAAM trajectory planner")
    # ex.setMinimumSize(200, 200)
    ex.show()
    sys.exit(app.exec())
