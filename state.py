class State:
    """
    This class represents automata's states, implementing State Design Pattern.
    Each method of it set True to one attribute, and False to all the others.
    """

    def __init__(self):
        self.is_stopped = True
        self.is_running = False
        self.is_paused = False

    def set_stopped(self):
        self.is_stopped = True
        self.is_running = False
        self.is_paused = False

    def set_running(self):
        self.is_stopped = False
        self.is_running = True
        self.is_paused = False

    def set_paused(self):
        self.is_stopped = False
        self.is_running = False
        self.is_paused = True
