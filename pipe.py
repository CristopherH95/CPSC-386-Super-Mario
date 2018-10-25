from block import Block


class Pipe(Block):
    """Represents a pipe which may potentially lead to another map"""
    def __init__(self, x, y, image, screen, destination=None):
        super(Pipe, self).__init__(x, y, image, screen)
        self.destination = destination  # TODO: destination handling
