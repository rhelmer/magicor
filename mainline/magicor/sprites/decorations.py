"""
Decorative sprites are drawn behind all other sprites.
Arbitrary resource and animation information is passed on creation.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import random
from magicor.sprites import *

class Decoration(AnimatedSprite):

    def __init__(self, resource, x, y, width, height, speed):
        AnimatedSprite.__init__(
            self, x, y, width, height,
            {"default": [ImageFrame(resource, width, height)]
             }
            )
        for i in range(self.resources[resource].get_width() // width):
            self._animations["default"].append(AnimationFrame(i, speed))
        self._animations["default"].append(JumpFrame(1))


class WalkingPenguin(AnimatedSprite):


    def __init__(self, x, miny, maxy, background):
        y = random.randint(miny, maxy)
        AnimatedSprite.__init__(
            self, x, y, 32, 48,
            {"default": (ImageFrame("sprites/player-penguin", 38, 48),
                         AnimationFrame(0, 4),
                         AnimationFrame(1, 4),
                         AnimationFrame(2, 4),
                         AnimationFrame(1, 4),
                         JumpFrame(1))
             }
            )
        self.footstep = self.resources.loadImage("images/footstep")
        self.miny = miny
        self.maxy = maxy
        self.background = background
        self._counter = 0
        self.movement = 0
        self._index = random.randint(1, 4)

    def update(self):
        AnimatedSprite.update(self)
        self.x += 1
        self.y += self.movement
        if self.y < self.miny:
            self.y = self.miny
        elif self.y > self.maxy:
            self.y = self.maxy
        if self.x > 800:
            self.x = random.randint(-64, -32)
            self.y = random.randint(self.miny, self.maxy)
        if self._counter == 10:
            self.background.blit(self.footstep, (self.x + 16, self.y - 206))
            self.movement = random.randint(-1, 1) * 0.2
        elif self._counter > 19:
            self.background.blit(self.footstep, (self.x + 16, self.y - 208))
            self.movement = random.randint(-1, 1) * 0.2
            self._counter = -1
        self._counter += 1
