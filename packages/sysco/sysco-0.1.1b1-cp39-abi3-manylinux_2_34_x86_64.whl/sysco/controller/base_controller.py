class BaseController:
    def __init__(self):
        print("Controller loaded...")

    def get_input(self):
        raise NotImplementedError("Subclass must implement get_input()")
