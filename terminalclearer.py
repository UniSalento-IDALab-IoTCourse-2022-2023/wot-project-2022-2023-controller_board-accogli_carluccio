import os

class TerminalClearer:
    def __init__(self):
        pass

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

