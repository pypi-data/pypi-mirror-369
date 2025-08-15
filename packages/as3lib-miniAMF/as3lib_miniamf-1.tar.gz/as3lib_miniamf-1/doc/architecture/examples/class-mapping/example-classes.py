class User(object):
    def __init__(self, name, password):
        self.name = name
        self.password = password

class Permission(object):
    def __init__(self, type):
        self.type = type
