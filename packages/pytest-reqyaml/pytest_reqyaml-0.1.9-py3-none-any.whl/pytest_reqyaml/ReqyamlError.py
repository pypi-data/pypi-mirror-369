class JsonpathError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class NameMissingError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message