from block import Block


class Pipe(Block):
    """Represents a pipe which may potentially lead to another map"""
    def __init__(self, x, y, image, screen, destination=None, spawn='player', horiz=False, music='BG-Main.wav'):
        super(Pipe, self).__init__(x, y, image, screen)
        self.destination = str(destination) if destination else None
        self.spawn = spawn
        self.horiz = horiz
        self.music = music

    @classmethod
    def pipe_from_tmx_obj(cls, obj, screen):
        """Create a Pipe from tmx object data"""
        if 'destination' in obj.properties:
            destination = obj.properties['destination']
        else:
            destination = None
        if 'spawn' in obj.properties:
            spawn = obj.properties['spawn']
        else:
            spawn = 'player'
        if 'horiz' in obj.properties:
            horiz = obj.properties['horiz']
        else:
            horiz = False
        if 'music' in obj.properties:
            music = obj.properties['music']
        else:
            music = 'BG-Main.wav'
        return cls(obj.x, obj.y, obj.image, screen, destination=destination, spawn=spawn, horiz=horiz, music=music)

    def check_enter(self, other):
        """Returns None if no destination or cannot enter,
        otherwise returns the map load function and spawn point name"""
        if not self.destination:
            return None
        pts = [other.rect.topleft, other.rect.midtop, other.rect.topright]
        for pt in pts:
            if self.rect.collidepoint(pt) and other.state['crouch']:    # FIXME: alter state variable to real one
                return self.destination, self.spawn
