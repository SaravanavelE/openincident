class EasyTask:

    def __init__(self):
        self.done = False

    def get_state(self):
        return {
            "status": "service_down"
        }

    def step(self, action):

        if action == "restart_service":
            self.done = True
            return self.get_state(), 0.98, True

        return self.get_state(), 0.05, False