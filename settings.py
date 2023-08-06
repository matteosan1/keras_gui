import json, os

class Settings:
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        settings_path = os.path.join(base_dir, "settings.json")
        with open(settings_path, "r") as f:
            self.data = json.load(f)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        
