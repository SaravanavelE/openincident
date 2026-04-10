class HardTask:

    def __init__(self):
        self.steps = 0
        self.stage = 0

    def get_state(self):
        return {
            "stage": self.stage
        }

    def step(self, action):

        if self.stage == 0 and action == "check_logs":
            self.stage = 1
            return self.get_state(), 0.3, False

        if self.stage == 1 and action == "clear_cache":
            self.stage = 2
            return self.get_state(), 0.5, False

        if self.stage == 2 and action == "restart_service":
            return self.get_state(), 0.99, True

        return self.get_state(), 0.05, False