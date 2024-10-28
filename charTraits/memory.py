class Memory:
    """Class to represent a character's memory"""
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content

    def get_content(self):
        return self.content
