class SequenceManager(object):
    def __init__(self, application_config):
        self.sequences = {}

    def start(self):
        pass

    def stop(self):
        pass

    def get_next_sequence(self, id):
        if id not in self.sequences:
            self.sequences[id] = 1
        current = self.sequences[id]
        self.sequences[id] += 1
        return current
