from PyQt6.QtGui import QMatrix4x4
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTableWidget, QAbstractItemView, QTableWidgetItem
from viewport.panels.TransformPanel import ModelTransformPanel, CSTransformPanel

id_enumeration = 100


class SimpleIDGenerator:
    def __init__(self):
        self.__last_id = -1

    def new_id(self):
        self.__last_id = self.__last_id + 1
        return self.__last_id


class StorageObject:
    def __init__(self, path, _id):
        self._full_path = path

        filename = path.split("/")
        if len(filename) > 1:
            self._name = filename[-1]
        else:
            self._name = path

        self._id = _id

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id


class ProjectPanel(QWidget):
    def __init__(self, parent=None, project_mediator=None, *args, **kwargs):
        super().__init__()
        self.parent = parent
        self.project_mediator = project_mediator

        self.objects_list = []
        self.id_generator = SimpleIDGenerator()

        self.initUI()

    def initUI(self):
        self.gui_layout = QVBoxLayout()
        self.setLayout(self.gui_layout)

        # Init project table
        self.table = QTableWidget(0, 2)
        self.gui_layout.addWidget(self.table)
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable changing

        self.table.setColumnWidth(0, 84)
        self.table.setColumnWidth(1, 72)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.table.setMaximumHeight(100)

        self.tab_bar_left = QTabWidget()
        self.tab_bar_left.setTabPosition(QTabWidget.TabPosition.West)
        self.gui_layout.addWidget(self.tab_bar_left)
        self.transform_panel_model_widget = ModelTransformPanel(self, self.project_mediator)
        self.tab_bar_left.addTab(self.transform_panel_model_widget, "&Model set")

        self.transform_panel_cross_section_widget = CSTransformPanel(self, self.project_mediator)
        self.tab_bar_left.addTab(self.transform_panel_cross_section_widget, "&CS set")

    def clear(self):
        self.table.clear()
        self.table.setRowCount(0)
        # self.table_id_list.clear()

    def add_object(self, model_object):
        self.objects_list.append(StorageObject(str(model_object.filename), self.id_generator.new_id()))
        self.table.setRowCount(len(self.objects_list))

        self.table.setItem(len(self.objects_list)-1, 0, QTableWidgetItem(self.objects_list[-1].name))

    def execute_command(self, command):
        if command['type'] == 'set_model_range':
            self.transform_panel_cross_section_widget.set_slider_cs_range(command['params']['range'])
