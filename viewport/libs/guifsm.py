# right_mouse_button_pressed
# left_mouse_button_pressed
# right_mouse_button_released
# left_mouse_button_released
# left_mouse_button_doubleclicked
# escape_button_pressed
# backspace_button_pressed
# enter_button_pressed
#
#
# ui_add_line_button
# state:
# 	pressed
# 	released
# ui_add_line_button_pressed
# ui_add_point_button_pressed
#
# ui_vertex_mode_pressed
# ui_edge_mode_pressed
# ui_object_mode_pressed
#
#
# add_last_point
# add_point

import sys
from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt


def prime(fn):
    def wrapper(*args, **kwargs):
        v = fn(*args, **kwargs)
        v.send(None)
        return v
    return wrapper


class GuiFSM:
    def __init__(self, parent):
        self.parent = parent
        self.state1 = self._create_state_1()
        self.state2 = self._create_state_2()
        self.state3 = self._create_state_3()
        self.state4 = self._create_state_4()
        self.state5 = self._create_state_5()
        self.state6 = self._create_state_6()
        self.state7 = self._create_state_7()

        self.current_state = self.state1
        self.stopped = False

        self.counter = 0

    @prime
    def _create_state_1(self):
        while True:
            command = yield
            if command[0] == 'left_mouse_button_pressed':
                request = {"type": "select_by_pos"}
                result = self.parent.redirect_request('backend', request)

                if result == "vertex_selected":
                    self.parent.redirect_request('changing_line', ['start_moving_vertex'])
                    self.current_state = self.state5
                    self.parent.set_label_text("State changed to s5 " + str(self.counter))
                    self.counter += 1

                elif result == "edge_selected":
                    self.current_state = self.state6
                    self.parent.set_label_text("State changed to s6 " + str(self.counter))
                    self.counter += 1

                elif result == "object_selected":
                    self.current_state = self.state7
                    self.parent.set_label_text("State changed to s7 " + str(self.counter))
                    self.counter += 1
                # request = {"type": "get_selection_mode"}
                # result = self.parent.redirect_request('backend', request)
                # if result == 'vertex':
                #     request = {"type": "select_vertex_by_position", "params": {"shift": False}}
                #     result = self.parent.redirect_request('backend', request)
                #     if result == "vertex_selected":
                #         self.parent.redirect_request('changing_line', ['start_moving_vertex'])
                #         self.current_state = self.state5
                #         self.parent.set_label_text("State changed to s5 " + str(self.counter))
                #         self.counter += 1
                # if result == 'edge':
                #     result = self.parent.redirect_request('backend', ['select_edge'])
                #     if result == "edge_selected":
                #         self.current_state = self.state6
                #         self.parent.set_label_text("State changed to s6 " + str(self.counter))
                #         self.counter += 1
                # elif result == 'object':
                #     request = {"type": "select_object"}
                #     result = self.parent.redirect_request('backend', request)
                #     if result == "line_selected":
                #         self.current_state = self.state7
                #         self.parent.set_label_text("State changed to s7 " + str(self.counter))
                #         self.counter += 1

            elif command[0] == 'ui_add_line_button_pressed':
                self.current_state = self.state2
                self.parent.set_gui_element_state(['ui_add_line_button', 'pressed'])
                self.parent.set_label_text("State changed to s2 " + str(self.counter))
                self.counter += 1
            else:
                pass

    @prime
    def _create_state_2(self):
        while True:
            command = yield
            if command[0] == 'ui_add_line_button_pressed':
                self.current_state = self.state1
                self.parent.set_gui_element_state(['ui_add_line_button', 'released'])
                self.parent.set_label_text("State changed to s1 " + str(self.counter))
                self.counter += 1
            elif command[0] == 'escape_button_pressed':
                # Cansel dynamic line drawing
                self.current_state = self.state1
                self.parent.set_gui_element_state(['ui_add_line_button', 'released'])
                self.parent.set_label_text("State changed to s1 " + str(self.counter))
                self.counter += 1
            elif command[0] == 'left_mouse_button_pressed':
                self.current_state = self.state3
                self.parent.redirect_request('dynamic_line', ['add_point', command[1]])
                self.parent.set_label_text("State changed to s3 " + str(self.counter))
                self.counter += 1
            else:
                pass

    @prime
    def _create_state_3(self):
        while True:
            command = yield
            if command[0] == 'ui_add_line_button_pressed':
                # reset dynamic lyne drawing
                self.parent.redirect_request('dynamic_line', ['cancel_line_creation', command[1]])
                self.current_state = self.state1
                self.parent.set_gui_element_state(['ui_add_line_button', 'released'])
                self.parent.set_label_text("State changed to s1 " + str(self.counter))
                self.counter += 1
            elif command[0] == 'backspace_button_pressed':
                # delete last point from dynamic line
                result = self.parent.redirect_request('dynamic_line', ['delete_last_segment', command[1]])
                if result == 'line_is_empty':
                    self.current_state = self.state2
                    self.parent.set_label_text("State changed to s2 " + str(self.counter))
                    self.counter += 1
            elif command[0] == 'escape_button_pressed':
                # Cansel dynamic line drawing
                self.parent.redirect_request('dynamic_line', ['cancel_line_creation', command[1]])
                self.current_state = self.state2
                self.parent.set_label_text("State changed to s2 " + str(self.counter))
                self.counter += 1
            elif command[0] == 'left_mouse_button_doubleclicked':
                # Finish dynamic line drawing
                self.current_state = self.state2
                self.parent.redirect_request('dynamic_line', ['add_last_point', command[1]])
                self.parent.set_label_text("State changed to s2 " + str(self.counter))
                self.counter += 1
            elif command[0] == 'enter_button_pressed':
                # Finish dynamic line drawing
                self.current_state = self.state2
                self.parent.redirect_request('dynamic_line', ['add_last_point', command[1]])
                self.parent.set_label_text("State changed to s2 " + str(self.counter))
                self.counter += 1
            elif command[0] == 'left_mouse_button_pressed':
                # Add point to dynamic line without state changing
                self.parent.redirect_request('dynamic_line', ['add_point', command[1]])
                self.parent.set_label_text("State changed to s3 " + str(self.counter))
                self.counter += 1
            else:
                pass

    @prime
    def _create_state_4(self):
        while True:
            command = yield
            if command[0] == 'left_mouse_button_pressed':
                request = {"type": "select_by_pos"}
                result = self.parent.redirect_request('backend', request)

                if result == "vertex_selected":
                    self.parent.redirect_request('changing_line', ['start_moving_vertex'])
                    self.current_state = self.state5
                    self.parent.set_label_text("State changed to s5 " + str(self.counter))
                    self.counter += 1
                else:
                    self.current_state = self.state1
                    # Clear selection - FUTURE
                    self.parent.set_label_text("State changed to s1 " + str(self.counter))
                    self.counter += 1

                # request = {"type": "get_selection_mode"}
                # result = self.parent.redirect_request('backend', request)
                # if result == 'vertex':
                #     request = {"type": "select_vertex_by_position", "params": {"shift": False}}
                #     result = self.parent.redirect_request('backend', request)
                #     # result = self.parent.redirect_request('backend', ['select_vertex'])
                #     if result == "vertex_selected":
                #         self.parent.redirect_request('changing_line', ['start_moving_vertex'])
                #         self.current_state = self.state5
                #         self.parent.set_label_text("State changed to s5 " + str(self.counter))
                #         self.counter += 1
                #     else:
                #         self.current_state = self.state1
                #         self.parent.set_label_text("State changed to s1 " + str(self.counter))
                #         self.counter += 1

            elif command[0] == 'delete_button_pressed':
                print("Delete vertex")
                delete_result = self.parent.redirect_request('backend', ['delete_selected_vertex'])
                if delete_result is True:
                    print("Vertex deleted", delete_result)
                    self.current_state = self.state1
                    self.parent.set_label_text("State changed to s1 " + str(self.counter))
                    self.counter += 1

            elif (command[0] == 'escape_button_pressed') or \
                 (command[0] == 'ui_edge_mode_pressed') or \
                 (command[0] == 'ui_object_mode_pressed'):
                self.parent.redirect_request('backend', ['cancel_selection'])
                self.current_state = self.state1
                self.parent.set_label_text("State changed to s1 " + str(self.counter))
                self.counter += 1
            elif command[0] == 'ui_add_line_button_pressed':
                self.parent.redirect_request('backend', ['cancel_selection'])
                self.parent.set_gui_element_state(['ui_add_line_button', 'pressed'])
                self.current_state = self.state2
                self.parent.set_label_text("State changed to s2 " + str(self.counter))
                self.counter += 1
            else:
                pass

    @prime
    def _create_state_5(self):
        while True:
            command = yield
            if command[0] == 'left_mouse_button_released':
                self.parent.redirect_request('changing_line', ['stop_moving_vertex'])
                self.current_state = self.state4
                self.parent.set_label_text("State changed to s4 " + str(self.counter))
                self.counter += 1
            else:
                pass

    @prime
    def _create_state_6(self):
        while True:
            command = yield
            if command[0] == 'left_mouse_button_pressed':
                request = {"type": "select_by_pos"}
                result = self.parent.redirect_request('backend', request)

                # result = self.parent.redirect_request('backend', ['select_edge'])
                if result == "edge_selected":
                    pass
                else:
                    request = {"type": "cancel_selection"}
                    self.parent.redirect_request('backend', request)

                    self.current_state = self.state1
                    self.parent.set_label_text("State changed to s1 " + str(self.counter))
                    self.counter += 1

            elif (command[0] == 'escape_button_pressed') or \
                 (command[0] == 'ui_vertex_mode_pressed') or \
                 (command[0] == 'ui_object_mode_pressed'):
                self.parent.redirect_request('backend', ['cancel_selection'])
                self.current_state = self.state1
                self.parent.set_label_text("State changed to s1 " + str(self.counter))
                self.counter += 1

            elif command[0] == 'ui_add_point_button_pressed':
                self.parent.redirect_request('backend', ['add_median_point'])
                self.current_state = self.state1
                self.parent.set_label_text("State changed to s1 " + str(self.counter))
                self.counter += 1
                # self.parent.send_notification('changing_line', ['stop_moving_vertex'])
                # self.current_state = self.state4
                # self.parent.set_label_text("State changed to s4 " + str(self.counter))
                # self.counter += 1
            else:
                pass

    @prime
    def _create_state_7(self):
        while True:
            command = yield
            if command[0] == 'left_mouse_button_pressed':
                request = {"type": "select_by_pos"}
                result = self.parent.redirect_request('backend', request)
                if result == "object_selected":
                    pass
                else:
                    request = {"type": "cancel_selection"}
                    self.parent.redirect_request('backend', request)

                    self.current_state = self.state1
                    self.parent.set_label_text("State changed to s1 " + str(self.counter))
                    self.counter += 1

            elif (command[0] == 'escape_button_pressed') or \
                    (command[0] == 'ui_vertex_mode_pressed') or \
                    (command[0] == 'ui_edge_mode_pressed'):
                self.parent.redirect_request('backend', ['cancel_selection'])
                self.current_state = self.state1
                self.parent.set_label_text("State changed to s1 " + str(self.counter))
                self.counter += 1
            else:
                pass

    def send(self, command, mouse_pos):
        try:
            self.current_state.send((command, mouse_pos))
        except StopIteration:
            self.stopped = True


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setMinimumSize(500, 300)

        self.fsm = GuiFSM(self)

        self.central_widget = QWidget()
        gui_layout = QHBoxLayout()
        self.central_widget.setLayout(gui_layout)
        self.setCentralWidget(self.central_widget)

        self.button_add_line = QPushButton("Add lines")
        gui_layout.addWidget(self.button_add_line)
        self.button_add_line.clicked.connect(self.button_add_line_function)
        self.button_add_line.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.label_information = QLabel(self)
        self.label_information.setText("Msg: -")
        gui_layout.addWidget(self.label_information)

        self.check_state = QPushButton("Check state")
        gui_layout.addWidget(self.check_state)
        self.check_state.clicked.connect(self.check_state_function)

        # self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def button_add_line_function(self):
        self.fsm.send("ui_add_line_button_pressed", None)

    def set_label_text(self, text):
        self.label_information.setText("Msg: " + text)

    def set_gui_element_state(self, command):
        print(command)
        if command[0] == "ui_add_line_button":
            if command[1] == "pressed":
                self.button_add_line.setDown(True)
                self.button_add_line.setCheckable(True)
            elif command[1] == "released":
                self.button_add_line.setDown(False)
                self.button_add_line.setCheckable(False)

    def check_state_function(self):
        print(self.fsm.current_state, self.fsm.stopped)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self.fsm.send("right_mouse_button_pressed", [0, 0])

        if e.button() == Qt.MouseButton.LeftButton:
            self.fsm.send("left_mouse_button_pressed", [0, 0])

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self.fsm.send("right_mouse_button_released", [0, 0])

        if e.button() == Qt.MouseButton.LeftButton:
            self.fsm.send("left_mouse_button_released", [0, 0])

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.fsm.send("left_mouse_button_doubleclicked", [0, 0])
    #
    # def mouseMoveEvent(self, e):
    #     pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape.value:
            self.fsm.send("escape_button_pressed", None)

        elif event.key() == Qt.Key.Key_Backspace.value:
            self.fsm.send("backspace_button_pressed", None)

        elif event.key() == 16777220:  # Qt.Key.Key_Enter.value
            self.fsm.send("enter_button_pressed", None)

    def send_notification(self, receiver, msg):
        if receiver == "dynamic_line":
            print(receiver, msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()

    ex.show()
    sys.exit(app.exec())
