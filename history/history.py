import os
import json


class History(object):

    def __init__(self, file_name):
        self.path = f"history/{file_name}.json"
        self.history = self.__load_history()

    def save(self):
        return self.__save_history()

    def insert(self, object, index=0):
        self.history.insert(index, object)
        return self.history

    def __load_history(self):
        if not os.path.exists(self.path):
            with open(self.path, 'w+') as f:
                json.dump(list(), f)
        try:
            with open(self.path, 'r+') as f:
                return json.load(f)
        except FileNotFoundError:
            return list()
        except Exception as e:
            print(f"Load history file failure: {e}")

    def __save_history(self):
        try:
            with open(self.path, 'w+') as f:
                json.dump(self.history, f)
        except Exception as e:
            print(f"Save history file failure: {e}")
