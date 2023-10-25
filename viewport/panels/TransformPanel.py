from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QSlider, QLabel, QFrame
from PyQt6.QtGui import QMatrix4x4

from viewport.panels.guiparameters import *


class ModelTransformPanel(QWidget):
    def __init__(self, parent=None, project_mediator=None, *args, **kwargs):
        super().__init__()
        self.parent = parent
        self.project_mediator = project_mediator

        self.initUI()

        self.transform_mat = QMatrix4x4()
        self.transform_mat.setToIdentity()

        self.rotate_x_angle = 0
        self.rotate_y_angle = 0
        self.rotate_z_angle = 0
        self.movement_x = 0
        self.movement_y = 0
        self.movement_z = 0.0

    def initUI(self):
        self.setMaximumWidth(300)
        self.gui_layout = QVBoxLayout()
        self.setLayout(self.gui_layout)

        label_window_info = QLabel("Setup model position\nparameters:\n")
        self.gui_layout.addWidget(label_window_info)

        separatorLine = QFrame()
        separatorLine.setFrameShape(QFrame.Shape.HLine)
        separatorLine.setFrameShadow(QFrame.Shadow.Raised)
        self.gui_layout.addWidget(separatorLine)

        buttons_layout = QVBoxLayout()
        self.gui_layout.addLayout(buttons_layout)

        rotX_buttons_layout = QHBoxLayout()
        rotY_buttons_layout = QHBoxLayout()
        rotZ_buttons_layout = QHBoxLayout()
        moveX_buttons_layout = QHBoxLayout()
        moveY_buttons_layout = QHBoxLayout()
        moveZ_buttons_layout = QHBoxLayout()

        buttons_layout.addLayout(moveX_buttons_layout)
        buttons_layout.addLayout(moveY_buttons_layout)
        buttons_layout.addLayout(moveZ_buttons_layout)

        separatorLine2 = QFrame()
        separatorLine2.setFrameShape(QFrame.Shape.HLine)
        separatorLine2.setFrameShadow(QFrame.Shadow.Raised)
        buttons_layout.addWidget(separatorLine2)

        buttons_layout.addLayout(rotX_buttons_layout)
        buttons_layout.addLayout(rotY_buttons_layout)
        buttons_layout.addLayout(rotZ_buttons_layout)

        # Initialize movement buttons

        move_x_plus_button = QPushButton("X+")
        moveX_buttons_layout.addWidget(move_x_plus_button)
        move_x_plus_button.clicked.connect(self.move_x_plus_button_function)
        move_x_plus_button.setMaximumWidth(50)
        move_x_minus_button = QPushButton("X-")
        moveX_buttons_layout.addWidget(move_x_minus_button)
        move_x_minus_button.clicked.connect(self.move_x_minus_button_function)
        move_x_minus_button.setMaximumWidth(50)

        self.move_x_spinbox = QDoubleSpinBox()
        moveX_buttons_layout.addWidget(self.move_x_spinbox)
        self.move_x_spinbox.setRange(-2000, 2000)
        self.move_x_spinbox.setSingleStep(movement_single_step_spinbox)
        self.move_x_spinbox.valueChanged.connect(self.move_x_spinbox_changed)

        move_y_plus_button = QPushButton("Y+")
        moveY_buttons_layout.addWidget(move_y_plus_button)
        move_y_plus_button.clicked.connect(self.move_y_plus_button_function)
        move_y_plus_button.setMaximumWidth(50)
        move_y_minus_button = QPushButton("Y-")
        moveY_buttons_layout.addWidget(move_y_minus_button)
        move_y_minus_button.clicked.connect(self.move_y_minus_button_function)
        move_y_minus_button.setMaximumWidth(50)

        self.move_y_spinbox = QDoubleSpinBox()
        moveY_buttons_layout.addWidget(self.move_y_spinbox)
        self.move_y_spinbox.setRange(-2000, 2000)
        self.move_y_spinbox.setSingleStep(movement_single_step_spinbox)
        self.move_y_spinbox.valueChanged.connect(self.move_y_spinbox_changed)

        move_z_plus_button = QPushButton("Z+")
        moveZ_buttons_layout.addWidget(move_z_plus_button)
        move_z_plus_button.clicked.connect(self.move_z_plus_button_function)
        move_z_plus_button.setMaximumWidth(50)
        move_z_minus_button = QPushButton("Z-")
        moveZ_buttons_layout.addWidget(move_z_minus_button)
        move_z_minus_button.clicked.connect(self.move_z_minus_button_function)
        move_z_minus_button.setMaximumWidth(50)

        self.move_z_spinbox = QDoubleSpinBox()
        moveZ_buttons_layout.addWidget(self.move_z_spinbox)
        self.move_z_spinbox.setRange(-2000, 2000)
        self.move_z_spinbox.setSingleStep(movement_single_step_spinbox)
        self.move_z_spinbox.valueChanged.connect(self.move_z_spinbox_changed)

        # Initialize rotation buttons

        rot_x_plus_button = QPushButton("Rot X+")
        rotX_buttons_layout.addWidget(rot_x_plus_button)
        rot_x_plus_button.clicked.connect(self.rot_x_plus_button_function)
        rot_x_plus_button.setMaximumWidth(50)
        rot_x_minus_button = QPushButton("Rot X-")
        rotX_buttons_layout.addWidget(rot_x_minus_button)
        rot_x_minus_button.clicked.connect(self.rot_x_minus_button_function)
        rot_x_minus_button.setMaximumWidth(50)

        self.rot_x_spinbox = QDoubleSpinBox()
        rotX_buttons_layout.addWidget(self.rot_x_spinbox)
        self.rot_x_spinbox.setRange(-180, 180)
        self.rot_x_spinbox.setSingleStep(rotation_single_step_spinbox)
        self.rot_x_spinbox.valueChanged.connect(self.rot_x_spinbox_changed)

        rot_y_plus_button = QPushButton("Rot Y+")
        rotY_buttons_layout.addWidget(rot_y_plus_button)
        rot_y_plus_button.clicked.connect(self.rot_y_plus_button_function)
        rot_y_plus_button.setMaximumWidth(50)
        rot_y_minus_button = QPushButton("Rot Y-")
        rotY_buttons_layout.addWidget(rot_y_minus_button)
        rot_y_minus_button.clicked.connect(self.rot_y_minus_button_function)
        rot_y_minus_button.setMaximumWidth(50)

        self.rot_y_spinbox = QDoubleSpinBox()
        rotY_buttons_layout.addWidget(self.rot_y_spinbox)
        self.rot_y_spinbox.setRange(-180, 180)
        self.rot_y_spinbox.setSingleStep(rotation_single_step_spinbox)
        self.rot_y_spinbox.valueChanged.connect(self.rot_y_spinbox_changed)

        rot_z_plus_button = QPushButton("Rot Z+")
        rotZ_buttons_layout.addWidget(rot_z_plus_button)
        rot_z_plus_button.clicked.connect(self.rot_z_plus_button_function)
        rot_z_plus_button.setMaximumWidth(50)
        rot_z_minus_button = QPushButton("Rot Z-")
        rotZ_buttons_layout.addWidget(rot_z_minus_button)
        rot_z_minus_button.clicked.connect(self.rot_z_minus_button_function)
        rot_z_minus_button.setMaximumWidth(50)

        self.rot_z_spinbox = QDoubleSpinBox()
        rotZ_buttons_layout.addWidget(self.rot_z_spinbox)
        self.rot_z_spinbox.setRange(-180, 180)
        self.rot_z_spinbox.setSingleStep(rotation_single_step_spinbox)
        self.rot_z_spinbox.valueChanged.connect(self.rot_z_spinbox_changed)

        buttons_layout.addStretch(1)

    def rot_x_plus_button_function(self):
        self.rotate_x_angle += rotation_single_step_button
        self.rot_x_spinbox.setValue(self.rotate_x_angle)
        self.recalc_transform_mat()

    def rot_x_minus_button_function(self):
        self.rotate_x_angle -= rotation_single_step_button
        self.rot_x_spinbox.setValue(self.rotate_x_angle)
        self.recalc_transform_mat()

    def rot_x_spinbox_changed(self):
        self.rotate_x_angle = self.rot_x_spinbox.value()
        self.recalc_transform_mat()

    def rot_y_plus_button_function(self):
        self.rotate_y_angle += rotation_single_step_button
        self.rot_y_spinbox.setValue(self.rotate_y_angle)
        self.recalc_transform_mat()

    def rot_y_minus_button_function(self):
        self.rotate_y_angle -= rotation_single_step_button
        self.rot_y_spinbox.setValue(self.rotate_y_angle)
        self.recalc_transform_mat()

    def rot_y_spinbox_changed(self):
        self.rotate_y_angle = self.rot_y_spinbox.value()
        self.recalc_transform_mat()

    def rot_z_plus_button_function(self):
        self.rotate_z_angle += rotation_single_step_button
        self.rot_z_spinbox.setValue(self.rotate_z_angle)
        self.recalc_transform_mat()

    def rot_z_minus_button_function(self):
        self.rotate_z_angle -= rotation_single_step_button
        self.rot_z_spinbox.setValue(self.rotate_z_angle)
        self.recalc_transform_mat()

    def rot_z_spinbox_changed(self):
        self.rotate_z_angle = self.rot_z_spinbox.value()
        self.recalc_transform_mat()

    def move_x_plus_button_function(self):
        self.movement_x += movement_single_step_button
        self.move_x_spinbox.setValue(self.movement_x)
        self.recalc_transform_mat()

    def move_x_minus_button_function(self):
        self.movement_x -= movement_single_step_button
        self.move_x_spinbox.setValue(self.movement_x)
        self.recalc_transform_mat()

    def move_x_spinbox_changed(self):
        self.movement_x = self.move_x_spinbox.value()
        self.recalc_transform_mat()

    def move_y_plus_button_function(self):
        self.movement_y += movement_single_step_button
        self.move_y_spinbox.setValue(self.movement_y)
        self.recalc_transform_mat()

    def move_y_minus_button_function(self):
        self.movement_y -= movement_single_step_button
        self.move_y_spinbox.setValue(self.movement_y)
        self.recalc_transform_mat()

    def move_y_spinbox_changed(self):
        self.movement_y = self.move_y_spinbox.value()
        self.recalc_transform_mat()

    def move_z_plus_button_function(self):
        self.movement_z += movement_single_step_button
        self.move_z_spinbox.setValue(self.movement_z)
        self.recalc_transform_mat()

    def move_z_minus_button_function(self):
        self.movement_z -= movement_single_step_button
        self.move_z_spinbox.setValue(self.movement_z)
        self.recalc_transform_mat()

    def move_z_spinbox_changed(self):
        self.movement_z = self.move_z_spinbox.value()
        self.recalc_transform_mat()

    def recalc_transform_mat(self):
        self.transform_mat.setToIdentity()
        self.transform_mat.translate(self.movement_x, self.movement_y, self.movement_z)
        self.transform_mat.rotate(self.rotate_x_angle, 1, 0, 0)
        self.transform_mat.rotate(self.rotate_y_angle, 0, 1, 0)
        self.transform_mat.rotate(self.rotate_z_angle, 0, 0, 1)

        request = {"type": "set_active_object_transform_mat", "params": {"transform_mat": self.transform_mat}}
        self.project_mediator.execute_command(request)

        # self.parent.update_model_transform_mat(self.transform_mat)


class CSTransformPanel(QWidget):
    def __init__(self, parent=None, project_mediator=None, *args, **kwargs):
        super().__init__()

        self.parent = parent
        self.project_mediator = project_mediator

        self.initUI()

        self.interrupt_active = True

        self.transform_mat = QMatrix4x4()
        self.transform_mat.setToIdentity()

        self.rotate_x_angle = 0
        self.rotate_y_angle = 0
        self.rotate_z_angle = 0
        self.movement_x = 0
        self.movement_y = 0
        self.movement_z = 0.0
        self.slider_value = 0.0

    def initUI(self):
        self.setMaximumWidth(300)
        self.gui_layout = QVBoxLayout()
        self.setLayout(self.gui_layout)

        label_window_info = QLabel("Setup CS position\nparameters:\n")
        self.gui_layout.addWidget(label_window_info)

        separatorLine = QFrame()
        separatorLine.setFrameShape(QFrame.Shape.HLine)
        separatorLine.setFrameShadow(QFrame.Shadow.Raised)
        self.gui_layout.addWidget(separatorLine)

        buttons_layout = QVBoxLayout()
        self.gui_layout.addLayout(buttons_layout)

        rotX_buttons_layout = QHBoxLayout()
        rotY_buttons_layout = QHBoxLayout()
        rotZ_buttons_layout = QHBoxLayout()
        moveX_buttons_layout = QHBoxLayout()
        moveY_buttons_layout = QHBoxLayout()
        moveZ_buttons_layout = QHBoxLayout()

        slider_layout = QHBoxLayout()
        slider_layout_configure = QVBoxLayout()
        layout_layer_height = QHBoxLayout()

        buttons_layout.addLayout(moveX_buttons_layout)
        buttons_layout.addLayout(moveY_buttons_layout)
        buttons_layout.addLayout(moveZ_buttons_layout)

        separatorLine2 = QFrame()
        separatorLine2.setFrameShape(QFrame.Shape.HLine)
        separatorLine2.setFrameShadow(QFrame.Shadow.Raised)
        buttons_layout.addWidget(separatorLine2)

        buttons_layout.addLayout(rotX_buttons_layout)
        buttons_layout.addLayout(rotY_buttons_layout)
        buttons_layout.addLayout(rotZ_buttons_layout)

        separatorLine3 = QFrame()
        separatorLine3.setFrameShape(QFrame.Shape.HLine)
        separatorLine3.setFrameShadow(QFrame.Shadow.Raised)
        buttons_layout.addWidget(separatorLine3)

        buttons_layout.addLayout(slider_layout)

        # Add cross section slider
        self.slice_slider = QSlider()
        slider_layout.addWidget(self.slice_slider)
        self.slice_slider.valueChanged.connect(lambda val: self.slider_value_changed(val))
        slider_layout.addLayout(slider_layout_configure)

        slider_layout_configure.addStretch(1)
        slider_layout_configure.addLayout(layout_layer_height)

        label_layer_height = QLabel("Layer height:")
        layout_layer_height.addWidget(label_layer_height)

        self.spinbox_layer_height = QDoubleSpinBox()
        self.spinbox_layer_height.setValue(1.0)
        layout_layer_height.addWidget(self.spinbox_layer_height)
        self.spinbox_layer_height.setRange(0, layer_height_range_spinbox)
        # self.spinbox_layer_height.valueChanged.connect(self.move_y_spinbox_changed)

        button_layer_height_up = QPushButton("↑")
        slider_layout_configure.addWidget(button_layer_height_up)
        button_layer_height_up.clicked.connect(self.button_layer_height_up_function)

        label_cs_height = QLabel("Current CS height:")
        slider_layout_configure.addWidget(label_cs_height)

        self.spinbox_current_cs_height = QDoubleSpinBox()
        slider_layout_configure.addWidget(self.spinbox_current_cs_height)
        self.spinbox_current_cs_height.valueChanged.connect(self.spinbox_current_cs_height_changed_function)

        button_layer_height_down = QPushButton("↓")
        slider_layout_configure.addWidget(button_layer_height_down)
        button_layer_height_down.clicked.connect(self.button_layer_height_down_function)

        slider_layout_configure.addStretch(1)

        # buttons_layout.addStretch(1)

        # Initialize movement buttons

        move_x_plus_button = QPushButton("X+")
        moveX_buttons_layout.addWidget(move_x_plus_button)
        move_x_plus_button.clicked.connect(self.move_x_plus_button_function)
        move_x_plus_button.setMaximumWidth(50)
        move_x_minus_button = QPushButton("X-")
        moveX_buttons_layout.addWidget(move_x_minus_button)
        move_x_minus_button.clicked.connect(self.move_x_minus_button_function)
        move_x_minus_button.setMaximumWidth(50)

        self.move_x_spinbox = QDoubleSpinBox()
        moveX_buttons_layout.addWidget(self.move_x_spinbox)
        self.move_x_spinbox.setRange(-2000, 2000)
        self.move_x_spinbox.setSingleStep(movement_single_step_spinbox)
        self.move_x_spinbox.valueChanged.connect(self.move_x_spinbox_changed)

        move_y_plus_button = QPushButton("Y+")
        moveY_buttons_layout.addWidget(move_y_plus_button)
        move_y_plus_button.clicked.connect(self.move_y_plus_button_function)
        move_y_plus_button.setMaximumWidth(50)
        move_y_minus_button = QPushButton("Y-")
        moveY_buttons_layout.addWidget(move_y_minus_button)
        move_y_minus_button.clicked.connect(self.move_y_minus_button_function)
        move_y_minus_button.setMaximumWidth(50)

        self.move_y_spinbox = QDoubleSpinBox()
        moveY_buttons_layout.addWidget(self.move_y_spinbox)
        self.move_y_spinbox.setRange(-2000, 2000)
        self.move_y_spinbox.setSingleStep(movement_single_step_spinbox)
        self.move_y_spinbox.valueChanged.connect(self.move_y_spinbox_changed)

        move_z_plus_button = QPushButton("Z+")
        moveZ_buttons_layout.addWidget(move_z_plus_button)
        move_z_plus_button.clicked.connect(self.move_z_plus_button_function)
        move_z_plus_button.setMaximumWidth(50)
        move_z_minus_button = QPushButton("Z-")
        moveZ_buttons_layout.addWidget(move_z_minus_button)
        move_z_minus_button.clicked.connect(self.move_z_minus_button_function)
        move_z_minus_button.setMaximumWidth(50)

        self.move_z_spinbox = QDoubleSpinBox()
        moveZ_buttons_layout.addWidget(self.move_z_spinbox)
        self.move_z_spinbox.setRange(-2000, 2000)
        self.move_z_spinbox.setSingleStep(movement_single_step_spinbox)
        self.move_z_spinbox.valueChanged.connect(self.move_z_spinbox_changed)

        # Initialize rotation buttons

        rot_x_plus_button = QPushButton("Rot X+")
        rotX_buttons_layout.addWidget(rot_x_plus_button)
        rot_x_plus_button.clicked.connect(self.rot_x_plus_button_function)
        rot_x_plus_button.setMaximumWidth(50)
        rot_x_minus_button = QPushButton("Rot X-")
        rotX_buttons_layout.addWidget(rot_x_minus_button)
        rot_x_minus_button.clicked.connect(self.rot_x_minus_button_function)
        rot_x_minus_button.setMaximumWidth(50)

        self.rot_x_spinbox = QDoubleSpinBox()
        rotX_buttons_layout.addWidget(self.rot_x_spinbox)
        self.rot_x_spinbox.setRange(-180, 180)
        self.rot_x_spinbox.setSingleStep(rotation_single_step_spinbox)
        self.rot_x_spinbox.valueChanged.connect(self.rot_x_spinbox_changed)

        rot_y_plus_button = QPushButton("Rot Y+")
        rotY_buttons_layout.addWidget(rot_y_plus_button)
        rot_y_plus_button.clicked.connect(self.rot_y_plus_button_function)
        rot_y_plus_button.setMaximumWidth(50)
        rot_y_minus_button = QPushButton("Rot Y-")
        rotY_buttons_layout.addWidget(rot_y_minus_button)
        rot_y_minus_button.clicked.connect(self.rot_y_minus_button_function)
        rot_y_minus_button.setMaximumWidth(50)

        self.rot_y_spinbox = QDoubleSpinBox()
        rotY_buttons_layout.addWidget(self.rot_y_spinbox)
        self.rot_y_spinbox.setRange(-180, 180)
        self.rot_y_spinbox.setSingleStep(rotation_single_step_spinbox)
        self.rot_y_spinbox.valueChanged.connect(self.rot_y_spinbox_changed)

        rot_z_plus_button = QPushButton("Rot Z+")
        rotZ_buttons_layout.addWidget(rot_z_plus_button)
        rot_z_plus_button.clicked.connect(self.rot_z_plus_button_function)
        rot_z_plus_button.setMaximumWidth(50)
        rot_z_minus_button = QPushButton("Rot Z-")
        rotZ_buttons_layout.addWidget(rot_z_minus_button)
        rot_z_minus_button.clicked.connect(self.rot_z_minus_button_function)
        rot_z_minus_button.setMaximumWidth(50)

        self.rot_z_spinbox = QDoubleSpinBox()
        rotZ_buttons_layout.addWidget(self.rot_z_spinbox)
        self.rot_z_spinbox.setRange(-180, 180)
        self.rot_z_spinbox.setSingleStep(rotation_single_step_spinbox)
        self.rot_z_spinbox.valueChanged.connect(self.rot_z_spinbox_changed)

    def rot_x_plus_button_function(self):
        self.rotate_x_angle += rotation_single_step_button
        self.rot_x_spinbox.setValue(self.rotate_x_angle)
        self.recalc_transform_mat()

    def rot_x_minus_button_function(self):
        self.rotate_x_angle -= rotation_single_step_button
        self.rot_x_spinbox.setValue(self.rotate_x_angle)
        self.recalc_transform_mat()

    def rot_x_spinbox_changed(self):
        self.rotate_x_angle = self.rot_x_spinbox.value()
        self.recalc_transform_mat()

    def rot_y_plus_button_function(self):
        self.rotate_y_angle += rotation_single_step_button
        self.rot_y_spinbox.setValue(self.rotate_y_angle)
        self.recalc_transform_mat()

    def rot_y_minus_button_function(self):
        self.rotate_y_angle -= rotation_single_step_button
        self.rot_y_spinbox.setValue(self.rotate_y_angle)
        self.recalc_transform_mat()

    def rot_y_spinbox_changed(self):
        self.rotate_y_angle = self.rot_y_spinbox.value()
        self.recalc_transform_mat()

    def rot_z_plus_button_function(self):
        self.rotate_z_angle += rotation_single_step_button
        self.rot_z_spinbox.setValue(self.rotate_z_angle)
        self.recalc_transform_mat()

    def rot_z_minus_button_function(self):
        self.rotate_z_angle -= rotation_single_step_button
        self.rot_z_spinbox.setValue(self.rotate_z_angle)
        self.recalc_transform_mat()

    def rot_z_spinbox_changed(self):
        self.rotate_z_angle = self.rot_z_spinbox.value()
        self.recalc_transform_mat()

    def move_x_plus_button_function(self):
        self.movement_x += movement_single_step_button
        self.move_x_spinbox.setValue(self.movement_x)
        self.recalc_transform_mat()

    def move_x_minus_button_function(self):
        self.movement_x -= movement_single_step_button
        self.move_x_spinbox.setValue(self.movement_x)
        self.recalc_transform_mat()

    def move_x_spinbox_changed(self):
        self.movement_x = self.move_x_spinbox.value()
        self.recalc_transform_mat()

    def move_y_plus_button_function(self):
        self.movement_y += movement_single_step_button
        self.move_y_spinbox.setValue(self.movement_y)
        self.recalc_transform_mat()

    def move_y_minus_button_function(self):
        self.movement_y -= movement_single_step_button
        self.move_y_spinbox.setValue(self.movement_y)
        self.recalc_transform_mat()

    def move_y_spinbox_changed(self):
        self.movement_y = self.move_y_spinbox.value()
        self.recalc_transform_mat()

    def move_z_plus_button_function(self):
        self.movement_z += movement_single_step_button
        self.move_z_spinbox.setValue(self.movement_z)
        self.recalc_transform_mat()

    def move_z_minus_button_function(self):
        self.movement_z -= movement_single_step_button
        self.move_z_spinbox.setValue(self.movement_z)
        self.recalc_transform_mat()

    def move_z_spinbox_changed(self):
        self.movement_z = self.move_z_spinbox.value()
        self.recalc_transform_mat()

    def recalc_transform_mat(self):
        self.transform_mat.setToIdentity()
        self.transform_mat.rotate(self.rotate_x_angle, 1, 0, 0)
        self.transform_mat.rotate(self.rotate_y_angle, 0, 1, 0)
        self.transform_mat.rotate(self.rotate_z_angle, 0, 0, 1)
        self.transform_mat.translate(self.movement_x, self.movement_y, self.movement_z + self.slider_value)

        request = {"type": "set_cs_plane_transform_mat", "params": {"transform_mat": self.transform_mat}}
        self.project_mediator.execute_command(request)

        # self.parent.update_cs_transform_mat(self.transform_mat)

    def set_slider_cs_range(self, range):
        self.slice_slider.setRange(0, range*100)
        self.spinbox_current_cs_height.setRange(0, range)

    def spinbox_current_cs_height_changed_function(self):
        pass

        # self.slice_slider.setValue(self.spinbox_current_cs_height.value())

    def slider_value_changed(self, val):
        if self.interrupt_active:
            self.slider_value = val/100
            self.spinbox_current_cs_height.setValue(self.slider_value)
            self.recalc_transform_mat()

    def button_layer_height_up_function(self):
        layer_height = self.spinbox_layer_height.value()
        current_height = self.spinbox_current_cs_height.value()
        print("Up")

    def button_layer_height_down_function(self):
        layer_height = self.spinbox_layer_height.value()
        current_height = self.spinbox_current_cs_height.value()
        print("Down")

    # def slice_height_changed(self, val):
    #     self.spinbox_current_cs_height.setValue(val/100)
    #     self.slice_height = val / 100
    #     tmp_mat = QMatrix4x4()
    #     tmp_mat.setToIdentity()
    #     tmp_mat.translate(0, 0, val/100)
    #     # self.window3d.change_cross_plane_transform_mat(tmp_mat)
    #     self.calculate_slice()
