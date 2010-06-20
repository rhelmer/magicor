"""
Lights make up eye-candy like sparkles, dust and what not.
They are drawn above all other sprites.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import random
from magicor.sprites import *

class BlueSparkle(AnimatedSprite):

    def __init__(self, x, y):
        AnimatedSprite.__init__(
            self, x, y, 128, 128,
            {"default": (ImageFrame("sprites/sparkle-star", 128, 128),
                         AnimationFrame(0, 1),
                         AnimationFrame(1, 2),
                         AnimationFrame(2, 3),
                         AnimationFrame(3, 4),
                         KillFrame())}
            )

    def physics(self):
        self.y -= 8
        if self.y + self.height < 0:
            self.kill()


class YellowLight(AnimatedSprite):

    def __init__(self, x, y):
        AnimatedSprite.__init__(
            self, x, y, 96, 96,
            {"default": (ImageFrame("sprites/light-yellow", 96, 96),
                         AnimationFrame(0, 1),
                         AnimationFrame(1, 1),
                         AnimationFrame(2, 1),
                         AnimationFrame(3, 1),
                         JumpFrame(1))})


class YellowSpark(AnimatedSprite):

    def __init__(self, x, y, dx, dy):
        AnimatedSprite.__init__(
            self, x, y, 96, 96,
            {"default": (ImageFrame("sprites/light-yellow", 96, 96),
                         AnimationFrame(0, 1),
                         AnimationFrame(1, 1),
                         AnimationFrame(2, 1),
                         AnimationFrame(3, 1),
                         AnimationFrame(1, 1),
                         AnimationFrame(2, 1),
                         AnimationFrame(3, 1),
                         AnimationFrame(2, 1),
                         AnimationFrame(3, 1),
                         KillFrame())})
        self.dx = dx
        self.dy = dy

    def physics(self):
        self.x += self.dx
        self.y += self.dy


class Burning(AnimatedSprite):

    def __init__(self, x, y, dx, dy):
        AnimatedSprite.__init__(
            self, x, y, 64, 64,
            {"default": (ImageFrame("sprites/burning", 64, 64),
                         AnimationFrame(0, 1),
                         AnimationFrame(1, 1),
                         AnimationFrame(2, 2),
                         AnimationFrame(3, 2),
                         AnimationFrame(4, 2),
                         AnimationFrame(5, 4),
                         AnimationFrame(6, 4),
                         KillFrame())})
        self.dx = dx
        self.dy = dy


    def physics(self):
        self.x += self.dx
        self.y += self.dy
        

class IceDust(AnimatedSprite):

    def __init__(self, x, y, iceX, iceY, direction):
        AnimatedSprite.__init__(
            self, x, y, 32, 32,
            {"right": (ImageFrame("sprites/dust", 32, 32),
                       AnimationFrame(0, 1),
                       AnimationFrame(1, 1),
                       AnimationFrame(2, 1),
                       AnimationFrame(3, 1),
                       AnimationFrame(4, 1),
                       AnimationFrame(10, 1),
                       AnimationFrame(11, 1),
                       AnimationFrame(12, 1),
                       KillFrame()),
             "left": (ImageFrame("sprites/dust", 32, 32),
                       AnimationFrame(5, 1),
                       AnimationFrame(6, 1),
                       AnimationFrame(7, 1),
                       AnimationFrame(8, 1),
                       AnimationFrame(9, 1),
                       AnimationFrame(10, 1),
                       AnimationFrame(11, 1),
                       AnimationFrame(12, 1),
                       KillFrame()),
             },
            "right"
            )
        if direction > 0:
            self.setAnimation("right")
        elif direction < 0:
            self.setAnimation("left")
        else:
            raise ValueError("direction must be -1 or 1")
        self.iceX = iceX
        self.iceY = iceY
        self.direction = direction


    def physics(self):
        self.x += self.direction
        self.y += 2
        

class SunLight(AnimatedSprite):

    def __init__(self, x, y):
        AnimatedSprite.__init__(
            self, x, y, 128, 128,
            {"default": (ImageFrame("sprites/sunlight", 128, 128),
                         AnimationFrame(0, 1),
                         )
             })


class Sun(AnimatedSprite):

    def __init__(self, x, y, lightGroup):
        AnimatedSprite.__init__(
            self, x, y, 64, 64,
            {"default": (ImageFrame("sprites/sun", 64, 64),
                         AnimationFrame(0, 1),
                         )
             })
        self.light = SunLight(x - 32, y - 32)
        self.lightGroup = lightGroup
        self.lightGroup.add(self.light)

    def update(self):
        AnimatedSprite.update(self)
        self.light.x = self.x - 32
        self.light.y = self.y - 32
        
