import json

path_to_config_dir = 'config/'
workspace_file = 'workspace.json'


class ConfigParameters:
    working_dir = 'path_to_working_dir'


class ConfigManager:

    @staticmethod
    def read_workspace_property(prop):
        with open(path_to_config_dir + workspace_file, 'r') as f:
            data = json.load(f)
        return data['workspace'][prop]

    @staticmethod
    def write_workspace_property(prop, value):
        with open(path_to_config_dir + workspace_file, 'r+') as f:
            data = json.load(f)
            data['workspace'].update({prop: value})
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
