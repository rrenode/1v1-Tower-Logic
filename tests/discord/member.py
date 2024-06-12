from role import Role

class member:
    def __init__(self, id : int, name : str) -> None:
        self.id : int = id
        self.name : str = name
        self.roles : list[Role] = []