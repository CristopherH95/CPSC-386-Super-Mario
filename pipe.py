from block import Block


class Pipe(Block):
    """Represents a pipe which may potentially lead to another map"""
    def __init__(self, x, y, image, screen, destination=None):
        super(Pipe, self).__init__(x, y, image, screen)
        self.destination = 'map/' + str(destination)  # TODO: destination handling

    def check_enter(self, other):
        """Returns None if no destination or cannot enter,
        otherwise returns the map load function and spawn point name"""
        if not self.destination:
            return None
        pts = [other.rect.topleft, other.rect.midtop, other.rect.topright]
        for pt in pts:
            if self.rect.collidepoint(pt) and other.state['crouch']:    # FIXME: alter state variable to real one
                return self.destination, 'pipe_out'
