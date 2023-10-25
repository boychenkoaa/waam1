import pickle


def saving_project_in_file(backend_data, file_name='data.pkl'):
    with open(file_name, 'wb') as file:
        pickle.dump(backend_data, file)
        file.close()


def loading_project_from_file(file_name='data.pkl'):
    with open(file_name, 'rb') as file:
        loaded_project_backend = pickle.load(file)
        file.close()
    return loaded_project_backend



