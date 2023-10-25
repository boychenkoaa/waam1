class UltraGlobalMediator:
    def __init__(self):
        self.connected_objects = []

    def execute_command(self, command):
        if command['type'] == 'make_slice':
            self.connected_objects[0].set_slice(command['params']['lines'])

    def connect_objects(self, list_of_objects):
        for element in list_of_objects:
            element.ugm = self
            self.connected_objects.append(element)
