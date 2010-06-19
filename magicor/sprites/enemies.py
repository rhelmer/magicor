"""
Enemies are moving objects that can kill the player.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import math, random
from magicor.sprites import *
from magicor.sprites.player import Player
from magicor.sprites.blocks import Ice
from magicor.sprites.world import Lava
from magicor.resources import getResources

class Enemy(PhysicsSprite):
    """
    Walking enemies walk on a platform.
    Animation offsets will be as follows

    default: 0
    walk-right: 1, 0, 2, 0
    walk-left: 4, 3, 5, 3
    die: 6, 7, 8, 9, kill
    """

    def __init__(self, x, y, w, h, frames,
                 imageResource, soundResource,
                 level, blocksGroup, players, fireGroup, worldGroup):
        PhysicsSprite.__init__(
            self, level, x, y, w, h, frames,
            blocksGroup
            )
        self.players = players
        self.dead = False
        self.worldGroup = worldGroup
        self.fireGroup = fireGroup

    def die(self):
        if not self.dead:
            self.dead = True
            self.setAnimation("die")
            self.dx = random.randint(-16, 16) / 4.0
            self.dy = random.randint(-16, 0) / 4.0

    def physics(self):
        if self.dead:
            self.x += self.dx
            self.y += self.dy
            self.dy += 0.5
            if self.y > self.level.height * 32:
                self.kill()
        else:
            PhysicsSprite.physics(self)
            lava = self.worldGroup.getSprite(self.x, self.y,
                                             self.width, self.height,
                                             self,
                                             Lava)
            if lava and not lava.dormant:
                self.die()
                return
            if self.fireGroup.getSprite(self.x, self.y,
                                        self.width, self.height,
                                        self):
                self.die()
                return
            for player in self.players.getSprites(self.x,
                                                  self.y,
                                                  self.width,
                                                  self.height):
                if not player.dead:
                    player.die()
            if not self.testBlocks():
                self.move()

    def move(self):
        pass

    def testBlocks(self):
            block = self.blocksGroup.getSprite(self.x,
                                               self.y,
                                               self.width,
                                               self.height,
                                               self)
            if block:
                if block.falling > 0:
                    self.y = block.y + block.height
                    if self.blockedBelow():
                        self.die()
                elif block.moving < 0:
                    self.x = block.x - self.width
                    self.y = block.y
                elif block.moving > 0:
                    self.x = block.x + block.width
                    self.y = block.y
                return True
            return False


class WalkingEnemy(Enemy):

    def __init__(self, x, y, direction,
                 imageResource, soundResource, speed,
                 level, blocksGroup, players, fireGroup, worldGroup):
        w = getResources()[imageResource].get_width() / 10
        h = getResources()[imageResource].get_height()
        Enemy.__init__(self, x, y, w, h,
                       {"default": (ImageFrame(imageResource, w, h),
                                    AnimationFrame(0, 0),),
                        "die": (ImageFrame(imageResource, w, h),
                                SoundFrame(soundResource),
                                AnimationFrame(6, 2),
                                AnimationFrame(7, 2),
                                AnimationFrame(8, 2),
                                AnimationFrame(9, 2),
                                JumpFrame(2),),
                        "walk-right": (ImageFrame(imageResource, w, h),
                                       AnimationFrame(1, 4),
                                       AnimationFrame(0, 4),
                                       AnimationFrame(2, 4),
                                       AnimationFrame(0, 4),
                                       JumpFrame(1)),
                        "walk-left": (ImageFrame(imageResource, w, h),
                                      AnimationFrame(4, 4),
                                      AnimationFrame(3, 4),
                                      AnimationFrame(5, 4),
                                      AnimationFrame(3, 4),
                                      JumpFrame(1)),
                        },                       
                       imageResource, soundResource,
                       level, blocksGroup, players, fireGroup, worldGroup)
        self.speed = speed
        if not direction in ("right", "left"):
            raise ValueError(
                "walking enemy can only have direction left or right")
        self.setAnimation("walk-%s"%direction)        
        
    def move(self):
            if self._animationName == "walk-right":
                if (self.blockedRight()
                    or not self.blockedRightBelow()
                    or self.fireGroup.getSprite(self.x + self.width, self.y,
                                                0, self.height,
                                                self)
                    or self.worldGroup.getSprite(self.x + self.width, self.y,
                                                 0, self.height,
                                                 self,
                                                 Lava)
                    ):
                    self.setAnimation("walk-left")
                else:
                    self.x += self.speed
            elif self._animationName == "walk-left":
                if (self.blockedLeft()
                    or not self.blockedLeftBelow()
                    or self.fireGroup.getSprite(self.x - 1, self.y,
                                                0, self.height,
                                                self)
                    or self.worldGroup.getSprite(self.x - 1, self.y,
                                                 0, self.height,
                                                 self,
                                                 Lava)
                    ):
                    self.setAnimation("walk-right")
                else:
                    self.x -= self.speed


class ClimbingEnemy(Enemy):

    def __init__(self, x, y, direction,
                 imageResource, soundResource, speed,
                 level, blocksGroup, players, fireGroup, worldGroup):
        w = getResources()[imageResource].get_width() / 10
        h = getResources()[imageResource].get_height()
        Enemy.__init__(self, x, y, w, h,
                       {"default": (ImageFrame(imageResource, w, h),
                                    AnimationFrame(0, 0),),
                        "die": (ImageFrame(imageResource, w, h),
                                SoundFrame(soundResource),
                                AnimationFrame(6, 2),
                                AnimationFrame(7, 2),
                                AnimationFrame(8, 2),
                                AnimationFrame(9, 2),
                                JumpFrame(2),),
                        "climb-up": (ImageFrame(imageResource, w, h),
                                     AnimationFrame(1, 4),
                                     AnimationFrame(0, 4),
                                     AnimationFrame(2, 4),
                                     AnimationFrame(0, 4),
                                     JumpFrame(1)),
                        "climb-down": (ImageFrame(imageResource, w, h),
                                       AnimationFrame(4, 4),
                                       AnimationFrame(3, 4),
                                       AnimationFrame(5, 4),
                                       AnimationFrame(3, 4),
                                       JumpFrame(1)),
                        },                       
                       imageResource, soundResource,
                       level, blocksGroup, players, fireGroup, worldGroup)
        self.speed = speed
        if not direction in ("up", "down"):
            raise ValueError(
                "climbing enemy can only have direction up or down")
        self.setAnimation("climb-%s"%direction)        

    def testFall(self):
        return False
    
    def move(self):
            if self._animationName == "climb-up":
                if (self.blockedAbove()
                    or self.fireGroup.getSprite(self.x, self.y - 1,
                                                self.width, 0,
                                                self)
                    or self.worldGroup.getSprite(self.x, self.y - 1,
                                                 self.width, 0,
                                                 self,
                                                 Lava)
                    ):
                    self.setAnimation("climb-down")
                else:
                    self.y -= self.speed
            elif self._animationName == "climb-down":
                if (self.blockedBelow()
                    or self.fireGroup.getSprite(self.x, self.y + self.height,
                                                self.width, 0,
                                                self)
                    or self.worldGroup.getSprite(self.x, self.y + self.height,
                                                 self.width, 0,
                                                 self,
                                                 Lava)
                   ):
                    self.setAnimation("climb-up")
                else:
                    self.y += self.speed


class StationaryEnemy(Enemy):

    def __init__(self, x, y, direction,
                 imageResource, soundResource, trigger,
                 level, blocksGroup, players, fireGroup, worldGroup):
        w = getResources()[imageResource].get_width() / 16
        h = getResources()[imageResource].get_height()
        Enemy.__init__(self, x, y, w, h,
                       {"default": (None,),
                        "up": (ImageFrame(imageResource, w, h),
                                    AnimationFrame(0, 0),),
                        "left": (ImageFrame(imageResource, w, h),
                                 AnimationFrame(4, 0),),
                        "down": (ImageFrame(imageResource, w, h),
                                 AnimationFrame(8, 0),),
                        "right": (ImageFrame(imageResource, w, h),
                                  AnimationFrame(12, 0),),
                        "attack-up": (ImageFrame(imageResource, w, h),
                                   SoundFrame(soundResource),
                                   AnimationFrame(1, 2),
                                   AnimationFrame(2, 2),
                                   AnimationFrame(3, 2),
                                   AttributeFrame("lethal", True),
                                   AnimationFrame(2, 2),
                                   AnimationFrame(1, 2),
                                   AttributeFrame("lethal", False),
                                   SetFrame("up"),),
                        "attack-left": (ImageFrame(imageResource, w, h),
                                   SoundFrame(soundResource),
                                   AnimationFrame(5, 2),
                                   AnimationFrame(6, 2),
                                   AnimationFrame(7, 2),
                                   AttributeFrame("lethal", True),
                                   AnimationFrame(6, 2),
                                   AnimationFrame(5, 2),
                                   AttributeFrame("lethal", False),
                                   SetFrame("left"),),
                        "attack-down": (ImageFrame(imageResource, w, h),
                                   SoundFrame(soundResource),
                                   AnimationFrame(9, 2),
                                   AnimationFrame(10, 2),
                                   AnimationFrame(11, 2),
                                   AttributeFrame("lethal", True),
                                   AnimationFrame(10, 2),
                                   AnimationFrame(9, 2),
                                   AttributeFrame("lethal", False),
                                   SetFrame("down"),),
                        "attack-right": (ImageFrame(imageResource, w, h),
                                   SoundFrame(soundResource),
                                   AnimationFrame(13, 2),
                                   AnimationFrame(14, 2),
                                   AnimationFrame(15, 2),
                                   AttributeFrame("lethal", True),
                                   AnimationFrame(14, 2),
                                   AnimationFrame(13, 2),
                                   AttributeFrame("lethal", False),
                                   SetFrame("right"),),
                        },
                       imageResource, soundResource,
                       level, blocksGroup, players, fireGroup, worldGroup)
        if not direction in ("up", "down", "left", "right"):
            raise ValueError("stationary enemy can only have direction "
                             "up, down, left or right")
        self.direction = direction
        self.lethal = False
        self.trigger = trigger
        self._counter = 0
        self.setAnimation("%s"%direction)

    def move(self):
        pass

    def blockedLeft(self):
        return False

    def blockedRight(self):
        return False

    def physics(self):
        sprites = (self.players.getSprites(self.x, self.y,
                                           self.width, self.height) +
                   self.blocksGroup.getSprites(self.x, self.y,
                                               self.width, self.height)
                   )
        if sprites:
            for sprite in sprites:
                    if self.lethal:
                        if isinstance(sprite, Player) and not sprite.dead:
                            sprite.die() 
                        elif isinstance(sprite, Ice) and sprite.alive():
                            sprite.life=0
                            sprite.kill()
                    elif (self._counter == 0
                          and not self._animationName.startswith("attack")):
                        self.setAnimation("attack-%s"%self.direction)
                        self._counter = self.trigger
                    elif self._counter > 0:
                        self._counter -= 1
        elif self._counter != self.trigger:
            self._counter = self.trigger
        
            
