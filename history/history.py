import json


class History(object):

    def __init__(self, board_name):
        self.board_name = board_name
        self.history_list = self.__load_history()

    def __load_history(self):
        try:
            with open(f"history/{self.board_name}.json", 'r+') as f:
                return json.load(f)
        except FileNotFoundError:
            return list()

    def __save_history(self):
        try:
            with open(f"history/{self.board_name}.json", 'w+') as f:
                json.dump(self.history_list, f)
        except Exception as e:
            print(f"Save history fail: {e}")

    def save(self):
        self.__save_history()
