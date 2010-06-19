"""
Miscellineous sprites.
"""
import math
from magicor.sprites import *

class Direction(AnimatedSprite):
    
    def __init__(self, x, y, direction):
        AnimatedSprite.__init__(
            self, x, y, 32, 32,
            {"right": [ImageFrame("sprites/arrow", 32, 32),
                       AnimationFrame(0, 0)],
             "left": [ImageFrame("sprites/arrow", 32, 32),
                       AnimationFrame(2, 0)],
             "down": [ImageFrame("sprites/arrow", 32, 32),
                       AnimationFrame(1, 0)],
             "up": [ImageFrame("sprites/arrow", 32, 32),
                       AnimationFrame(3, 0)],
             },
            "right"
            )
        self.direction = direction
        self._move = 0

    def _setDirection(self, direction):
        if not direction in ("left", "right", "up", "down"):
            warnings.warn("invalid Direction sprite direction: %s"%direction)
            direction = "right"
        self._direction = direction
        self._distance = 8
        self._speed = 32
        self.setAnimation(direction)

    direction = property(lambda x: x._direction, _setDirection)

    def update(self):
        self._move = (self._move + self._speed) % 360

    def draw(self, surface):
        if self._direction in ("left", "right"):
            ox = int(self._distance * math.sin(math.radians(self._move)))
            oy = 0
        else:
            ox = 0
            oy = int(self._distance * math.sin(math.radians(self._move)))
        AnimatedSprite.draw(self, surface, ox, oy)
