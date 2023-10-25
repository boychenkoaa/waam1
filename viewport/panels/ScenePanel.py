from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt6.QtWidgets import QLabel, QTabWidget, QDial, QSpinBox, QDoubleSpinBox, QMenu, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap

import math


class ScenePanel(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()

        self.parent = parent
        self.table_id_list = []
        self.initUI()
        self.cells_changed_interrupt_active = True

        self.gui_mediator = None
        self.link_to_scene_properties = None

    def initUI(self):
        self.hide_item_pixmap = QIcon('viewport/resources/hide.png')
        self.swap_item_pixmap = QIcon('viewport/resources/swap.png')
        self.contour_pixmap = QPixmap('viewport/resources/contour.png')
        self.line_pixmap = QPixmap('viewport/resources/line.png')
        self.polygon_pixmap = QPixmap('viewport/resources/polygon.png')

        self.gui_layout = QVBoxLayout()

        self.setLayout(self.gui_layout)

        self.table = QTableWidget(0, 4)
        self.gui_layout.addWidget(self.table)
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable changing

        self.table.setColumnWidth(0, 30)
        self.table.setColumnWidth(1, 42)
        self.table.setColumnWidth(2, 42)
        self.table.setColumnWidth(3, 42)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        tab_bar_left = QTabWidget()
        self.gui_layout.addWidget(tab_bar_left)

        self.offset_contour_widget = OffsetContourWidget(self)
        tab_bar_left.addTab(self.offset_contour_widget, "Offset")

        self.raster_contour_widget = RasterContourWidget(self)
        tab_bar_left.addTab(self.raster_contour_widget, "Raster")

        self.table.cellChanged.connect(self.cells_changed)

        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_context_menu)
        self.table.itemSelectionChanged.connect(self.cells_selection_changed)

    def clear(self):
        self.table.clear()
        self.table.setRowCount(0)
        self.table_id_list.clear()

    def add_element(self, element):
        label_type = QLabel()
        label_type.setScaledContents(True)

        if element.type == 'PLine':
            label_type.setPixmap(self.line_pixmap)
        elif element.type == 'Contour':
            label_type.setPixmap(self.contour_pixmap)
        elif element.type == 'Polygon':
            label_type.setPixmap(self.polygon_pixmap)
        else:
            print("Unknown geometry type:", element.type)
            return None

        self.cells_changed_interrupt_active = False

        row_number = self.table.rowCount()
        self.table.setRowCount(row_number+1)

        self.table_id_list.append(element.id)
        self.table.setCellWidget(row_number, 0, label_type)

        hide_item = QTableWidgetItem()
        hide_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        hide_item.setIcon(self.hide_item_pixmap)

        if True:  # add link to visible
            hide_item.setCheckState(Qt.CheckState.Checked)
        else:
            hide_item.setCheckState(Qt.CheckState.Unchecked)

        self.table.setItem(row_number, 1, QTableWidgetItem(str(element.id)))
        self.table.setItem(row_number, 2, hide_item)

        self.cells_changed_interrupt_active = True

    def add_tmp_element(self, element):
        pass

    def clear_tmp_elements(self):
        pass

    # def update_from_storage(self, msg):
    #     self.table_id_list.clear()
    #     if msg == 'upload_all':
    #         self.cells_changed_interrupt_active = False
    #         self.table.setRowCount(len(self.storage.scene_objects))
    #         counter = 0
    #
    #         for element in self.storage.scene_objects:
    #             element_properties = element[1][1]
    #
    #             label_type = QLabel()
    #             label_type.setScaledContents(True)
    #             if 'type' in element_properties.keys():
    #                 if element_properties['type'] == 'line':
    #                     label_type.setPixmap(self.line_pixmap)
    #                 elif element_properties['type'] == 'contour':
    #                     label_type.setPixmap(self.contour_pixmap)
    #
    #             self.table.setCellWidget(counter, 0, label_type)
    #
    #             self.table.setItem(counter, 1, QTableWidgetItem(element_properties['name']))
    #
    #             hide_item = QTableWidgetItem()
    #             hide_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
    #             hide_item.setIcon(self.hide_item_pixmap)
    #
    #             if element_properties['visible']:
    #                 hide_item.setCheckState(Qt.CheckState.Checked)
    #             else:
    #                 hide_item.setCheckState(Qt.CheckState.Unchecked)
    #             self.table.setItem(counter, 2, hide_item)
    #
    #             swap_item = QTableWidgetItem()
    #             swap_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
    #             swap_item.setIcon(self.swap_item_pixmap)
    #
    #             if element_properties['reverse']:
    #                 swap_item.setCheckState(Qt.CheckState.Checked)
    #             else:
    #                 swap_item.setCheckState(Qt.CheckState.Unchecked)
    #             self.table.setItem(counter, 3, swap_item)
    #
    #             self.table_id_list.append(element[0])
    #             counter += 1
    #         self.cells_changed_interrupt_active = True

    def cells_changed(self, row, column):
        if self.cells_changed_interrupt_active:
            check_state_visible = False
            # check_state_reverse = False
            if self.table.item(row, 2).checkState() == Qt.CheckState.Checked:
                check_state_visible = True

            # print("CELL CHANGED", row, column, check_state_visible)

            request = {"type": "set_visible_by_id", "params": {"id": self.table_id_list[row],
                                                               "visible": check_state_visible}}
            self.gui_mediator.execute_command(request)

            # if self.table.item(row, 3).checkState() == Qt.CheckState.Checked:
            #     check_state_reverse = True
            # changed_params = {"name": self.table.item(row, 1).text(),
            #                   "visible": check_state_visible,
            #                   "reverse": check_state_reverse}
            #
            # self.storage.change_objects_properties([[self.table_id_list[row], [None, changed_params]]])

    def cells_selection_changed(self):
        if self.cells_changed_interrupt_active:
            selected_items = self.table.selectedItems()
            selected_ids = []
            for item in selected_items:
                num_row = self.table.row(item)
                selected_ids.append(self.table_id_list[num_row])
            request = {"type": "select_by_id", "params": {"ids": selected_ids}}
            self.gui_mediator.execute_query(request)

    def on_context_menu(self, pos):
        # print(self.storage.link_to_scene_properties)
        # selected_ids = self.storage.link_to_scene_properties['selected_lines']

        context = QMenu(self)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_object)
        context.addAction(delete_action)

        convert_to_contour_action = QAction("Convert to contour", self)
        convert_to_contour_action.triggered.connect(self.convert_to_contour)
        context.addAction(convert_to_contour_action)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy)
        context.addAction(copy_action)

        convert_to_poly_action = QAction("Convert to poly", self)
        convert_to_poly_action.triggered.connect(self.convert_to_poly)
        context.addAction(convert_to_poly_action)

        # set_invisible_action = QAction("Set invisible", self)
        # set_invisible_action.triggered.connect(lambda x: self.set_invisible(selected_ids))
        # context.addAction(set_invisible_action)
        #
        # set_visible_action = QAction("Set visible", self)
        # set_visible_action.triggered.connect(lambda x: self.set_visible(selected_ids))
        # context.addAction(set_visible_action)
        #
        # reverse_action = QAction("Swap direction", self)
        # reverse_action.triggered.connect(lambda x: self.swap_direction(selected_ids))
        # context.addAction(reverse_action)

        context.exec(self.mapToGlobal(pos))

    # def set_invisible(self, id_list):
    #     for element in id_list:
    #         self.table.item(self.table_id_list.index(element), 2).setCheckState(Qt.CheckState.Unchecked)
    #
    # def set_visible(self, id_list):
    #     for element in id_list:
    #         self.table.item(self.table_id_list.index(element), 2).setCheckState(Qt.CheckState.Checked)
    #
    # def swap_direction(self, id_list):
    #     for element in id_list:
    #         current_state = self.table.item(self.table_id_list.index(element), 3).checkState()
    #         if current_state == Qt.CheckState.Checked:
    #             self.table.item(self.table_id_list.index(element), 3).setCheckState(Qt.CheckState.Unchecked)
    #         else:
    #             self.table.item(self.table_id_list.index(element), 3).setCheckState(Qt.CheckState.Checked)

    def delete_object(self):
        request = {"type": "delete_selected_objects"}
        self.gui_mediator.execute_command(request)

    def convert_to_contour(self):
        request = {"type": "convert_selected_to_contour"}
        self.gui_mediator.execute_command(request)

    def copy(self):
        request = {"type": "copy_selected_objects"}
        self.gui_mediator.execute_command(request)

    def convert_to_poly(self):
        request = {"type": "convert_selected_to_poly"}
        self.gui_mediator.execute_command(request)

    # def change_object_params(self, params_dict_list):
    #     change_result = self.mediator.notify(self, ["change_params_in_storage", params_dict_list])

    # def add_offset_line_function(self):
    #     scene_properties = self.storage.get_scene_properties()
    #     selected_ids = scene_properties['selected_lines']
    #     self.storage.add_offset_line(selected_ids)

    # def set_lines_selection(self, id_list):
    #     self.cells_changed_interrupt_active = False
    #
    #     for i in range(len(self.table_id_list)):
    #         tmp_id = self.table_id_list[i]
    #         if tmp_id in id_list:
    #             self.table.selectRow(i)
    #
    #     self.cells_changed_interrupt_active = True


class OffsetContourWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self.parent = parent

        gui_layout = QVBoxLayout()
        self.setLayout(gui_layout)

        # Unlock raster configure
        self.pushbutton_unlock_offset = QPushButton("Make offset")
        gui_layout.addWidget(self.pushbutton_unlock_offset)

        gui_layout.addStretch(1)

        # Ofset step spinbox configure
        offset_step_layout = QHBoxLayout()
        label_offset_step = QLabel("Offset step:")
        self.spinbox_offset_step = QDoubleSpinBox()
        self.spinbox_offset_step.setRange(0, 20)
        self.spinbox_offset_step.setValue(3.0)  # READ FROM CONFIGURE FILE
        self.spinbox_offset_step.setSingleStep(0.1)
        offset_step_layout.addWidget(label_offset_step)
        offset_step_layout.addWidget(self.spinbox_offset_step)
        gui_layout.addLayout(offset_step_layout)

        # Unlock raster configure
        self.pushbutton_offset_reverse = QPushButton("Reverse")
        gui_layout.addWidget(self.pushbutton_offset_reverse)

        gui_layout.addStretch(1)

        # Apply&continue configure
        self.pushbutton_apply_and_continue = QPushButton("Apply and Continue")
        gui_layout.addWidget(self.pushbutton_apply_and_continue)

        # Buttons configure
        buttons_layout = QHBoxLayout()
        self.pushbutton_apply = QPushButton("Apply")
        self.pushbutton_cancel = QPushButton("Cancel")
        buttons_layout.addWidget(self.pushbutton_apply)
        buttons_layout.addWidget(self.pushbutton_cancel)
        gui_layout.addLayout(buttons_layout)

        gui_layout.addStretch(1)

        self.spinbox_offset_step.setEnabled(False)
        self.pushbutton_offset_reverse.setEnabled(False)
        self.pushbutton_apply_and_continue.setEnabled(False)
        self.pushbutton_apply.setEnabled(False)
        self.pushbutton_cancel.setEnabled(False)

        self.pushbutton_unlock_offset.clicked.connect(self.pushbutton_unlock_offset_function)
        self.pushbutton_apply.clicked.connect(self.pushbutton_apply_function)
        self.pushbutton_cancel.clicked.connect(self.pushbutton_cancel_function)

        self.spinbox_offset_step.valueChanged.connect(self.calculate_offset)

    def pushbutton_unlock_offset_function(self):
        self.pushbutton_unlock_offset.setEnabled(False)

        self.spinbox_offset_step.setEnabled(True)
        self.pushbutton_offset_reverse.setEnabled(True)
        self.pushbutton_apply_and_continue.setEnabled(True)
        self.pushbutton_apply.setEnabled(True)
        self.pushbutton_cancel.setEnabled(True)

        self.calculate_offset()

    def pushbutton_apply_function(self):
        selected_ids = self.parent.link_to_scene_properties['selected_ids']
        dist = [self.spinbox_offset_step.value()]  # self.spinbox_offset_step.

        if len(selected_ids) > 0:
            request = {"type": "apply_offset",
                       "params": {"id": selected_ids[0], "distance list": dist, "without shrink": True,
                                  "cut holes": True}}
            self.parent.gui_mediator.execute_command(request)

        self.pushbutton_unlock_offset.setEnabled(True)

        self.spinbox_offset_step.setEnabled(False)
        self.pushbutton_offset_reverse.setEnabled(False)
        self.pushbutton_apply_and_continue.setEnabled(False)
        self.pushbutton_apply.setEnabled(False)
        self.pushbutton_cancel.setEnabled(False)

    def pushbutton_cancel_function(self):
        self.pushbutton_unlock_offset.setEnabled(True)

        self.spinbox_offset_step.setEnabled(False)
        self.pushbutton_offset_reverse.setEnabled(False)
        self.pushbutton_apply_and_continue.setEnabled(False)
        self.pushbutton_apply.setEnabled(False)
        self.pushbutton_cancel.setEnabled(False)

    def calculate_offset(self):
        # пока только для одного примитива (id)
        selected_ids = self.parent.link_to_scene_properties['selected_ids']
        # тут не работало, я просто значение написала, это список отступов для буфера, проверить, чтобы всегда > 0
        dist = [self.spinbox_offset_step.value()]  # self.spinbox_offset_step.
        # остальные параметры я заполнила по умолчанию, по идее должно быть что-то типа двух галочек
        # "simple buffer": True, "difference": True
        if len(selected_ids) > 0:
            request = {"type": "make_offset", "params": {"id": selected_ids[0], "distance list": dist, "without shrink": True, "cut holes": True}}
            self.parent.gui_mediator.execute_command(request)


class RasterContourWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self.parent = parent

        self.interrupt_active = True

        gui_layout = QVBoxLayout()
        self.setLayout(gui_layout)

        # Unlock raster configure
        self.pushbutton_unlock_raster = QPushButton("Rasterize")
        gui_layout.addWidget(self.pushbutton_unlock_raster)

        # Raster dial configure
        self.dial_raster_angle = QDial()
        self.dial_raster_angle.setRange(0, 360)
        self.dial_raster_angle.setValue(180)
        self.dial_raster_angle.setWrapping(True)
        gui_layout.addWidget(self.dial_raster_angle)

        # Raster angle spinbox configure
        angle_layout = QHBoxLayout()
        label_angle = QLabel("Raster angle:")
        self.spinbox_angle = QSpinBox()
        self.spinbox_angle.setRange(0, 360)
        self.spinbox_angle.setValue(180)
        angle_layout.addWidget(label_angle)
        angle_layout.addWidget(self.spinbox_angle)
        gui_layout.addLayout(angle_layout)

        # Raster step spinbox configure
        raster_step_layout = QHBoxLayout()
        label_raster_step = QLabel("Raster step:")
        self.spinbox_raster_step = QDoubleSpinBox()
        self.spinbox_raster_step.setRange(0, 10)
        self.spinbox_raster_step.setValue(3.0)  # READ FROM CONFIGURE FILE
        self.spinbox_raster_step.setSingleStep(0.1)
        raster_step_layout.addWidget(label_raster_step)
        raster_step_layout.addWidget(self.spinbox_raster_step)
        gui_layout.addLayout(raster_step_layout)

        # Raster delete segments spinbox configure
        raster_segments_limit_layout = QHBoxLayout()
        label_raster_segments_limit = QLabel("Del. <, mm:")
        self.spinbox_segments_limit = QDoubleSpinBox()
        self.spinbox_segments_limit.setRange(0, 50)
        self.spinbox_segments_limit.setValue(15.0)  # READ FROM CONFIGURE FILE
        self.spinbox_segments_limit.setSingleStep(1.0)
        raster_segments_limit_layout.addWidget(label_raster_segments_limit)
        raster_segments_limit_layout.addWidget(self.spinbox_segments_limit)
        gui_layout.addLayout(raster_segments_limit_layout)

        # Buttons configure
        buttons_layout = QHBoxLayout()
        self.pushbutton_apply = QPushButton("Apply")
        self.pushbutton_cancel = QPushButton("Cancel")
        buttons_layout.addWidget(self.pushbutton_apply)
        buttons_layout.addWidget(self.pushbutton_cancel)
        gui_layout.addLayout(buttons_layout)

        self.dial_raster_angle.setEnabled(False)
        self.spinbox_angle.setEnabled(False)
        self.spinbox_raster_step.setEnabled(False)
        self.spinbox_segments_limit.setEnabled(False)
        self.pushbutton_apply.setEnabled(False)
        self.pushbutton_cancel.setEnabled(False)

        self.pushbutton_unlock_raster.clicked.connect(self.pushbutton_unlock_raster_function)
        self.pushbutton_apply.clicked.connect(self.pushbutton_apply_function)
        self.pushbutton_cancel.clicked.connect(self.pushbutton_cancel_function)

        self.dial_raster_angle.valueChanged.connect(lambda val: self.dial_raster_angle_changed(val))
        self.spinbox_angle.valueChanged.connect(lambda val: self.spinbox_angle_changed(val))
        self.spinbox_raster_step.valueChanged.connect(self.calculate_raster)
        self.spinbox_segments_limit.valueChanged.connect(self.calculate_raster)

    def pushbutton_unlock_raster_function(self):
        self.pushbutton_unlock_raster.setEnabled(False)

        self.dial_raster_angle.setEnabled(True)
        self.spinbox_angle.setEnabled(True)
        self.spinbox_raster_step.setEnabled(True)
        self.spinbox_segments_limit.setEnabled(True)
        self.pushbutton_apply.setEnabled(True)
        self.pushbutton_cancel.setEnabled(True)

        self.calculate_raster()

    def pushbutton_apply_function(self):
        selected_ids = self.parent.link_to_scene_properties['selected_ids']
        slope_k = self.dial_raster_angle.value()
        bead_width = self.spinbox_raster_step.value()
        initial_indent = self.spinbox_raster_step.value()

        request = {"type": "apply_raster",
                   "params": {"id": selected_ids[0],
                              "slope": (270 - slope_k) % 360,
                              "bead width": bead_width,
                              "initial indent": None,
                              "line count": None}}
        self.parent.gui_mediator.execute_command(request)

        self.pushbutton_unlock_raster.setEnabled(True)

        self.dial_raster_angle.setEnabled(False)
        self.spinbox_angle.setEnabled(False)
        self.spinbox_raster_step.setEnabled(False)
        self.spinbox_segments_limit.setEnabled(False)
        self.pushbutton_apply.setEnabled(False)
        self.pushbutton_cancel.setEnabled(False)

    def pushbutton_cancel_function(self):
        self.pushbutton_unlock_raster.setEnabled(True)

        self.dial_raster_angle.setEnabled(False)
        self.spinbox_angle.setEnabled(False)
        self.spinbox_raster_step.setEnabled(False)
        self.spinbox_segments_limit.setEnabled(False)
        self.pushbutton_apply.setEnabled(False)
        self.pushbutton_cancel.setEnabled(False)

    def dial_raster_angle_changed(self, angle):
        if self.interrupt_active:
            self.interrupt_active = False
            self.spinbox_angle.setValue(angle)
            self.interrupt_active = True

            self.calculate_raster()

    def spinbox_angle_changed(self, angle):
        if self.interrupt_active:
            self.interrupt_active = False
            self.dial_raster_angle.setValue(angle)
            self.interrupt_active = True

            self.calculate_raster()

    def calculate_raster(self):
        selected_ids = self.parent.link_to_scene_properties['selected_ids']
        slope_k = self.dial_raster_angle.value()
        bead_width = self.spinbox_raster_step.value()
        initial_indent = self.spinbox_raster_step.value()

        if len(selected_ids) > 0:
            request = {"type": "rasterize",
                       "params": {"id": selected_ids[0],
                                  "slope": (270 - slope_k) % 360,  # -math.tan((slope_k-90)*math.pi/180)
                                  "bead width": bead_width,
                                  "initial indent": None,
                                  "line count": None}}
            self.parent.gui_mediator.execute_command(request)
