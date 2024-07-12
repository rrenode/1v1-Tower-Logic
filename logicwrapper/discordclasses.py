class Borders:
    HORIZONTAL = "|============================================================|"
    VERTICAL = "|"

class Embed:    
    def __init__(self, title, description, author, color = 0x000000):
        self.title = title
        self.description = description
        self.author = author
        self.color = color
    
    def __str__(self):        
        pass