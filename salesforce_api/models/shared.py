class Type:
    def __init__(self, name, members: list = None):
        self.name = name
        self.members = members or ['*']
