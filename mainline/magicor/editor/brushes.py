"""
Brushes for the editor pallette.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import copy

class BrushException(Exception):
    """
    Raised when brushes get invalid values.
    """

class Brush(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def copy(self):
        replica = copy.copy(self)
        if hasattr(self, "pixbuf"):
            replica.pixbuf = self.pixbuf
        return replica


class EraseBrush(Brush):

    def __init__(self):
        Brush.__init__(self, 32, 32)


class ResourceBrush(Brush):

    def __init__(self, resource, width, height, offset):
        Brush.__init__(self, width, height)
        self.resource = resource
        self.offset = offset

    def update(self, resource):
        self.resource = resource


class TileBrush(ResourceBrush):

    def __init__(self, resource):
        ResourceBrush.__init__(self, resource, 32, 32, 0)

    def __str__(self):
        return "%s"%self.resource


class SpriteBrush(ResourceBrush):

    def __init__(self, name, resource, width, height, offset,
                 left = 0, top = 0):
        ResourceBrush.__init__(self, resource, width, height, offset)
        self.name = name
        self.left = left
        self.top = top

    def __str__(self):
        return "%s"%self.name                    

class PlayerBrush(SpriteBrush):

    def __init__(self, direction = "right"):
        SpriteBrush.__init__(self,
                             "player",
                             "sprites/player-penguin",
                             32, 48,
                             0, 0, -16)
        self.direction = direction

    def _setDirection(self, value):
        if value not in (None, "right", "left"):
            raise ValueError("invalid direction '%s'"%value)
        self._direction = value
        self.offset = value == "left" and 4 or 0

    def _getDirection(self):
        return self._direction

    direction = property(_getDirection, _setDirection)
        
    def __str__(self):
        if self.direction:
            return "%s %s"%(self.name, self.direction)
        return SpriteBrush.__str__(self)

    def update(self, args):
        self.direction = args


class FireBrush(SpriteBrush):

    def __init__(self, noFalling = False):
        SpriteBrush.__init__(self,
                             "fire",
                             "sprites/fire-normal",
                             32, 32, 0)                             
        self.noFalling = noFalling

    def _setNoFalling(self, value):
        if value == "nofall" or value:
            self._noFalling = True
        else:
            self._noFalling = False

    def _getNoFalling(self):
        return self._noFalling

    noFalling = property(_getNoFalling, _setNoFalling)

    def __str__(self):
        if self.noFalling:
            return "%s nofall"%self.name
        return SpriteBrush.__str__(self)

    def update(self, args):
        self.noFalling = args


class IceBrush(SpriteBrush):

    def __init__(self, connect = None):
        SpriteBrush.__init__(self,
                             "ice",
                             "sprites/ice-normal",
                             32, 32, 4)
        self.connect = connect

    def _setConnect(self, value):
        self._connect = value
        if value == "connect":
            self.offset = 7
        elif value == "connect-right":
            self.offset = 6
        elif value == "connect-left":
            self.offset = 5
        else:
            self.offset = 4
            self._connect = None

    def _getConnect(self):
        return self._connect

    connect = property(_getConnect, _setConnect)

    def update(self, args):
        self.connect = args

    def __str__(self):
        if self.connect:
            return "%s %s"%(self.name, self.connect)
        return SpriteBrush.__str__(self)


class LavaBrush(SpriteBrush):

    def __init__(self, dormant = False):
        SpriteBrush.__init__(self,
                             "lava",
                             "sprites/lava",
                             32, 64, 0)
        self.dormant = dormant

    def _setDormant(self, value):
        if value == "dormant" or value:
            self._dormant = True
            self.offset = 4
        else:
            self._dormant = False
            self.offset = 0

    def _getDormant(self):
        return self._dormant

    dormant = property(_getDormant, _setDormant)

    def __str__(self):
        if self.dormant:
            return "%s dormant"%self.name
        return SpriteBrush.__str__(self)

    def update(self, args):
        self.dormant = args


class TubeBrush(SpriteBrush):

    def __init__(self, direction = "left", id_ = None):
        SpriteBrush.__init__(self,
                             "tube",
                             "sprites/tube-endings",
                             32, 32, 0)
        self.direction = direction
        self.id = id_

    def _setDirection(self, value):
        if value == "up":
            self.offset = 1
            self._direction = "up"
        elif value == "down":
            self.offset = 2
            self._direction = "down"
        elif value == "right":
            self.offset = 3
            self._direction = "right"
        else:
            self.offset = 0
            self._direction = "left"

    def _getDirection(self):
        return self._direction

    direction = property(_getDirection, _setDirection)

    def update(self, args):
        spl = args.split(" ", 1)
        if len(spl) == 2:
            self.direction, self.id = spl
        else:
            self.id = None
            self.direction = spl[0]

    def __str__(self):
        if self.id:
            return "%s %s %s"%(self.name, self.direction, self.id)
        return "%s %s"%(self.name, self.direction)


class EnemyBrush(SpriteBrush):

    def __init__(self, id_, name, resource, w, h, offset):
        SpriteBrush.__init__(self, name, resource, w, h, offset)
        self.id = id_


class WalkingEnemyBrush(EnemyBrush):

    def __init__(self, imageResource, soundResource, direction, speed):
        EnemyBrush.__init__(self,
                            "walking-enemy %s %s"%(imageResource,
                                                   soundResource),
                            "walking-enemy",
                            imageResource,
                            32, 32, 0)
        self.soundResource = soundResource
        self.speed = speed
        self.direction = direction

    def _setDirection(self, value):
        self._direction = value
        if value == "right":
            self.offset = 0
            self._direction = "right"
        else:
            self.offset = 3
            self._direction = "left"

    def _getDirection(self):
        return self._direction

    direction = property(_getDirection, _setDirection)

    def update(self, args):
        spl = args.split(" ", 3)
        if len(spl) == 4:
            self.direction = spl[0]
            self.speed = int(spl[3])

    def __str__(self):
        return "%s %s %s %s %d"%(self.name, self.direction,
                                 self.resource,
                                 self.soundResource,
                                 self.speed)


class ClimbingEnemyBrush(EnemyBrush):

    def __init__(self, imageResource, soundResource, direction, speed):
        EnemyBrush.__init__(self,
                            "climbing-enemy %s %s"%(imageResource,
                                                    soundResource),
                             "climbing-enemy",
                             imageResource,
                             32, 32, 0)
        self.soundResource = soundResource
        self.speed = speed
        self.direction = direction

    def _setDirection(self, value):
        self._direction = value
        if value == "up":
            self.offset = 0
            self._direction = "up"
        else:
            self.offset = 3
            self._direction = "down"

    def _getDirection(self):
        return self._direction

    direction = property(_getDirection, _setDirection)

    def update(self, args):
        spl = args.split(" ", 3)
        if len(spl) == 4:
            self.direction = spl[0]
            self.speed = int(spl[3])

    def __str__(self):
        return "%s %s %s %s %d"%(self.name, self.direction,
                                 self.resource,
                                 self.soundResource,
                                 self.speed)


class StationaryEnemyBrush(EnemyBrush):

    def __init__(self, imageResource, soundResource, direction, trigger):
        EnemyBrush.__init__(self,
                            "stationary-enemy %s %s"%(imageResource,
                                                      soundResource),
                            "stationary-enemy",
                            imageResource,
                            32, 32, 0)
        self.soundResource = soundResource
        self.trigger = trigger
        self.direction = direction

    def _setDirection(self, value):
        self._direction = value
        if value == "up":
            self.offset = 0
            self._direction = "up"
        elif value == "left":
            self.offset = 4
            self._direction = "left"
        elif value == "right":
            self.offset = 12
            self._direction = "right"
        else:
            self.offset = 8
            self._direction = "down"

    def _getDirection(self):
        return self._direction

    direction = property(_getDirection, _setDirection)

    def update(self, args):
        spl = args.split(" ", 3)
        if len(spl) == 4:
            self.direction = spl[0]
            self.trigger = int(spl[3])

    def __str__(self):
        return "%s %s %s %s %d"%(self.name,
                                 self.direction,
                                 self.resource,
                                 self.soundResource,
                                 self.trigger)


class DecorationBrush(SpriteBrush):

    def __init__(self, resource, w, h, speed):
        SpriteBrush.__init__(self,
                             "decoration",
                             resource, w, h, 0)
        self.speed = speed

    def update(self, args):
        spl = args.split(" ", 3)
        if len(spl) == 4:
            self.speed = int(spl[3])

    def __str__(self):
        return "%s %s %d %d %d"%(self.name,
                                 self.resource,
                                 self.width,
                                 self.height,
                                 self.speed)


class DirectionBrush(SpriteBrush):

    def __init__(self, direction):
        SpriteBrush.__init__(self,
                             "direction",
                             "sprites/arrow",
                             32, 32, 0)
        self.direction = direction

    def update(self, args):
        self.direction = args

    def _setDirection(self, direction):
        if not direction in ("right", "down", "left", "up"):
            direction = "right"
        self.offset = ["right", "down", "left", "up"].index(direction)
        self._direction = direction

    direction = property(lambda x: x._direction, _setDirection)

    def __str__(self):
        return "%s %s"%(self.name, self.direction)

class TrapolaBrush(SpriteBrush):
    def __init__(self):
        SpriteBrush.__init__(self,
                             "trapola",
                             "sprites/trapola2_q",
                             32,32,
                             0,0,0)

##class BallBrush(ResourceBrush):
##    def __init__(self):
##        SpriteBrush.__init__(self,
##                             "ball",
##                             "sprites/ball_b",
##                             8,8,
##                             0,14,14)
