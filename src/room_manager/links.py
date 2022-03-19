class Links:
    def __init__(self):
        self.mineral_id = None
        self.controller_id = None
        self.source_ids = []
        self.other_ids = []
        self.storage_id = None
        self.terminal_id = None
    def get_mineral(self):
        return Game.getObjectById(self.mineral_id)
    def get_controller(self):
        return Game.getObjectById(self.controller_id)
    def get_sources(self):
        return [Game.getObjectById(s) for s in self.source_ids]
    def get_storage(self):
        return Game.getObjectById(self.storage_id)
    def get_terminal(self):
        return Game.getObjectById(self.terminal_id)
    def get_others(self):
        return [Game.getObjectById(s) for s in self.other_ids]
    def operational(self):
        return self.controller_id is not None and len(self.source_ids) == 2  # TODO: == number of sources in the room
    def __str__(self):
        return f"mineral={self.mineral_id}, controller={self.controller_id}, sources={self.source_ids}, storage={self.storage_id}, terminal={self.terminal_id}"


