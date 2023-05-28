"""
Player implementation.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import time
from magicor.sprites import *
from magicor.sprites.blocks import *
from magicor.sprites.world import Tube
from magicor.sprites.lights import Burning, IceDust

class Player(PhysicsSprite):
    IMAGE = "sprites/player-penguin"

    def __init__(self, x, y,
                 level,
                 players,
                 blocksGroup,
                 fireGroup,
                 worldGroup,
                 lightGroup,
                 enemyGroup,
                 eyecandy = True):
        PhysicsSprite.__init__(
            self,
            level,
            x, y, 32, 32,
            {"default":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(0, 0),
              ),
             "die":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(28, 4),
              AnimationFrame(29, 4),
              JumpFrame(1),
              ),
             "falling":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/fall"),
              AnimationFrame(16, 4),
              AnimationFrame(17, 4),
              JumpFrame(2),
              ),
             "happy":
             (ImageFrame(self.IMAGE, 32, 48),
              MoveFrame(0, -10),
              AnimationFrame(16, 4),
              MoveFrame(0, -4),
              AnimationFrame(17, 4),
              MoveFrame(0, -2),
              AnimationFrame(16, 4),
              MoveFrame(0, 2),
              AnimationFrame(17, 4),
              MoveFrame(0, 4),
              AnimationFrame(17, 4),
              MoveFrame(0, 10),
              AnimationFrame(16, 4),
              SoundFrame("samples/done"),
              AnimationFrame(34, 64),
              ),
             # right side
             "stand-right":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(0, 8),
              AttributeFrame("direction", 1),
              ),
             "crouch-right":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(18, 8),
              ),
             "walk-right":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/walk"),
              AnimationFrame(1, 2),
              AnimationFrame(2, 2),
              SoundFrame("samples/walk"),
              AnimationFrame(1, 2),
              AnimationFrame(0, 2),
              ),
             "crawl-right":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(19, 4),
              AnimationFrame(18, 4),
              ),
             "jump-right":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/jump"),
              MoveFrame(8, 0),
              AnimationFrame(6, 4),
              MoveFrame(8, -16),
              AnimationFrame(7, 4),
              MoveFrame(8, 0),
              AnimationFrame(8, 4),
              MoveFrame(8, -16),
              AnimationFrame(0, 0),
              CallbackFrame(self.doneJumping),
              ),
             "jump-tube-right":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/jump"),
              MoveFrame(8, 0),
              AnimationFrame(6, 4),
              MoveFrame(8, -16),
              AnimationFrame(7, 4),
              MoveFrame(8, 0),
              AnimationFrame(8, 4),
              MoveFrame(8, -16),
              AnimationFrame(26, 0),
              CallbackFrame(self.doneJumping),
              ),
             "push-right":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/push"),
              AnimationFrame(12, 2),
              AnimationFrame(13, 2),
              AnimationFrame(12, 2),
              AnimationFrame(0, 0),
              AttributeFrame("pushing", False),
              ),
             "tube-right":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(26, 0),
              ),
             "freeze-right":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(30, 2),
              AnimationFrame(31, 4),
              AnimationFrame(30, 2),
              AnimationFrame(0, 0),
              AttributeFrame("freezing", False),
              ),
             "crouch-freeze-right":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(22, 2),
              AnimationFrame(23, 4),
              AnimationFrame(22, 2),
              AnimationFrame(18, 0),
              AttributeFrame("freezing", False),
              ),
             "land-right":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/playerland"),
              AnimationFrame(18, 4),
              AnimationFrame(0, 0),
              ),
             # left side
             "stand-left":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(3, 8),
              AttributeFrame("direction", -1),
              ),
             "crouch-left":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(20, 8),
              ),
             "walk-left":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/walk"),
              AnimationFrame(4, 2),
              AnimationFrame(5, 2),
              SoundFrame("samples/walk"),
              AnimationFrame(4, 2),
              AnimationFrame(3, 2),
              ),
             "crawl-left":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(21, 4),
              AnimationFrame(20, 4),
              ),
             "jump-left":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/jump"),
              MoveFrame(-8, -0),
              AnimationFrame(9, 4),
              MoveFrame(-8, -16),
              AnimationFrame(10, 4),
              MoveFrame(-8, 0),
              AnimationFrame(11, 4),
              MoveFrame(-8, -16),
              AnimationFrame(3, 0),
              CallbackFrame(self.doneJumping),
              ),
             "jump-tube-left":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/jump"),
              MoveFrame(-8, -0),
              AnimationFrame(9, 4),
              MoveFrame(-8, -16),
              AnimationFrame(10, 4),
              MoveFrame(-8, 0),
              AnimationFrame(11, 4),
              MoveFrame(-8, -16),
              AnimationFrame(27, 0),
              CallbackFrame(self.doneJumping),
              ),
             "push-left":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/push"),
              AnimationFrame(14, 2),
              AnimationFrame(15, 2),
              AnimationFrame(14, 2),
              AnimationFrame(3, 0),
              AttributeFrame("pushing", False),
              ),
             "tube-left":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(27, 0),
              ),
             "freeze-left":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(32, 2),
              AnimationFrame(33, 4),
              AnimationFrame(32, 2),
              AnimationFrame(3, 0),
              AttributeFrame("freezing", False),
              ),
             "crouch-freeze-left":
             (ImageFrame(self.IMAGE, 32, 48),
              AnimationFrame(24, 2),
              AnimationFrame(25, 4),
              AnimationFrame(24, 2),
              AnimationFrame(20, 0),
              AttributeFrame("freezing", False),
              ),
             "land-left":
             (ImageFrame(self.IMAGE, 32, 48),
              SoundFrame("samples/playerland"),
              AnimationFrame(20, 4),
              AnimationFrame(3, 0),
              ),
             },
            blocksGroup)
        self.eyecandy = eyecandy
        self.players = players
        self.dead = False
        self.dieX = 0
        self.dieY = 0
        self.freezing = False
        self.direction = 1
        self._deadCounter = 0
        self._finished = False
        self.jumping = False
        self.pushing = False
        self.fireGroup = fireGroup
        self.vertical = 0
        self.worldGroup = worldGroup
        self.enemyGroup = enemyGroup
        self.lightGroup = lightGroup
        self._iceType = NormalIce
        self.setAnimation("stand-right")

    def canMove(self):
        return (self.moving == 0
                and not self.falling
                and not self.jumping
                and not self.pushing
                and not self.tubed
                and not self.dead
                and not self._finished
                and not self.freezing)

    def eventFalling(self):
        self.setAnimation("falling")

    def eventStop(self):
        if self.direction < 0:
            self.setAnimation("land-left")
        elif self.direction > 0:
            self.setAnimation("land-right")

    def goLeft(self):
        if self.canMove() and self.isDone():
            if self.direction < 0:
                if (self.blockedAbove()
                    or (self.blockedLeftAbove()
                        and not self.blockedLeft())):
                    self.setAnimation("crawl-left")
                else:
                    self.setAnimation("walk-left")
                self.moving = -8
            else:
                if self.blockedAbove():
                    self.setAnimation("crouch-left")
                else:
                    self.setAnimation("stand-left")
                self.direction = -1

    def goRight(self):
        if self.canMove() and self.isDone():
            if self.direction > 0:
                if (self.blockedAbove()
                    or (self.blockedRightAbove()
                        and not self.blockedRight())):
                    self.setAnimation("crawl-right")
                else:
                    self.setAnimation("walk-right")
                self.moving = 8
            else:
                if self.blockedAbove():
                    self.setAnimation("crouch-right")
                else:
                    self.setAnimation("stand-right")
                self.direction = 1

    def goDown(self):
        if self.canMove() and not self.tubed:
            tube = self.worldGroup.getSprite(self.x,
                                             self.y + 32,
                                             self.width,
                                             0,
                                             self,
                                             Tube)
            matching = tube and tube.getMatching() or None
            if (tube and tube.direction == "up"
                and matching and not matching.blocked()):
                self.x = tube.x
                self.tubed = True
                self.moving = 0
                self.vertical = 8
                if self.direction > 0:
                    self.setAnimation("tube-right")
                else:
                    self.setAnimation("tube-left")

    def goUp(self):
        if self.canMove() and not self.tubed:
            tube = self.worldGroup.getSprite(self.x,
                                             self.y - 32,
                                             self.width,
                                             0,
                                             self,
                                             Tube)
            matching = tube and tube.getMatching() or None
            if (tube and tube.direction == "down"
                and matching and not matching.blocked()):
                self.x = tube.x
                self.tubed = True
                self.moving = 0
                self.vertical = -8
                if self.direction > 0:
                    self.setAnimation("tube-right")
                else:
                    self.setAnimation("tube-left")

    def standing(self):
        if self.direction > 0:
            if self.blockedAbove():
                if (not self._animationName.startswith("crouch")
                    and not self._animationName.startswith("crawl")):
                    self.setAnimation("crouch-right")
            else:
                if (not self._animationName.startswith("stand")
                    and not self._animationName.startswith("walk")):
                    self.setAnimation("stand-right")
        elif self.direction < 0:
            if self.blockedAbove():
                if (not self._animationName.startswith("crouch")
                    and not self._animationName.startswith("crawl")):
                    self.setAnimation("crouch-left")
            else:
                if (not self._animationName.startswith("stand")
                    and not self._animationName.startswith("walk")):
                    self.setAnimation("stand-left")
        self.x = (self.x / 32) * 32
        self.y = (self.y / 32) * 32

    def manipulateIce(self):
        if self.canMove():
            if (self.direction > 0
                and self.x / 32 < self.level.width - 1
                and not self.level[self.x / 32 + 1, self.y / 32 + 1]
                and not self.fireGroup.getSprite(self.x + self.width,
                                                 self.y + self.height,
                                                 self.width,
                                                 self.height,
                                                 self)
                and not self.enemyGroup.getSprite(self.x + self.width,
                                                 self.y + self.height,
                                                 self.width,
                                                 self.height,
                                                 self)
                ):
                block = self.blocksGroup.getSprite(self.x + self.width,
                                                self.y + self.height,
                                                self.width,
                                                self.height,
                                                self)
                x, y = (self.x / 32) * 32 + 32, (self.y / 32) * 32 + 32
                if block:
                    block.life = 0
                    block.kill()
                else:
                    i = self._iceType(x, y,
                                      self.level, self.blocksGroup,
                                      self.lightGroup, self.players,
                                      self.enemyGroup,
                                      self.eyecandy)
                    i.setAnimation("create")
                    self.lightGroup.add(IceDust(self.x + 20,
                                                self.y,
                                                x, y, 1))
                    self.resources.playSound("samples/createice")
                if self.blockedAbove():
                    self.setAnimation("crouch-freeze-right")
                else:
                    self.setAnimation("freeze-right")
                self.freezing = True
            elif (self.direction < 0
                  and self.x / 32 > 0
                  and not self.level[(self.x - 1) / 32,
                                     self.y / 32 + 1]
                  and not self.fireGroup.getSprite(self.x - self.width,
                                                   self.y + self.height,
                                                   self.width,
                                                   self.height,
                                                   self)
                  and not self.enemyGroup.getSprite(self.x - self.width,
                                                    self.y + self.height,
                                                    self.width,
                                                    self.height,
                                                    self)
                  ):
                block = self.blocksGroup.getSprite(self.x - self.width,
                                                self.y + self.height,
                                                self.width,
                                                self.height,
                                                self)
                x, y = (self.x / 32) * 32 - 32, (self.y / 32) * 32 + 32
                if block:
                    block.life = 0
                    block.kill()
                else:
                    i = self._iceType(x, y,
                                      self.level, self.blocksGroup,
                                      self.lightGroup, self.players,
                                      self.enemyGroup,
                                      self.eyecandy)
                    i.setAnimation("create")
                    self.lightGroup.add(IceDust(self.x - 20,
                                                self.y,
                                                x, y, -1))
                    self.resources.playSound("samples/createice")
                if self.blockedAbove():
                    self.setAnimation("crouch-freeze-left")
                else:
                    self.setAnimation("freeze-left")
                self.freezing = True

    def testFall(self):
        return bool(not self.blockedBelow()
                    and not self.jumping
                    and not self.pushing
                    and not self.tubed
                    and not self.dead
                    and not self._finished
                    and not self.freezing)

    def die(self):
        if not self.dead:
            self.dead = True
            self._finished = False
            self._deadCounter = 0
            self.dieX = random.randint(-40, 40) / 10.0
            self.dieY = random.randint(-80, -60) / 10.0
            self.setAnimation("die")
            self.resources.playSound("samples/playerdie")

    def finished(self):
        if not self.dead and not self._finished and self.canMove():
            self.setAnimation("happy")
            self._finished = True

    def doAction(self,action):
        if action=='die':
            self.die()

    def physics(self):
        if self.dead:
            self.x += self.dieX
            self.y += self.dieY
            self.dieY += 0.5
            self._deadCounter += 1
            if self._deadCounter % 4 == 0:
                self.lightGroup.add(Burning(self.x - random.randint(8, 24),
                                            self.y - random.randint(8, 24),
                                            0,
                                            -1)
                                )
        elif not self._finished:
            PhysicsSprite.physics(self)
            y = (self.y - self.height + 1) // 32
            if not self.jumping and not self.pushing:
                if (self.moving > 6
                    and self.blockedRight()):
                    tube = self.worldGroup.getSprite(self.x + self.width,
                                                     self.y,
                                                     0,
                                                     self.height,
                                                     self,
                                                     Tube)
                    matching = tube and tube.getMatching() or None
                    if (tube and tube.direction == "left"
                        and matching and not matching.blocked()):
                        if not self.tubed:
                            self.tubed = True
                            self.moving += 1
                            self.setAnimation("tube-right")
                    else:
                        block = self.blocksGroup.getSprite(self.x + self.width,
                                                           self.y,
                                                           0,
                                                           self.height,
                                                           self,
                                                           Ice)
                        if ((not block or block.blockedRight())
                            and not self.blockedAbove()):
                            tube = self.worldGroup.getSprite(self.x
                                                             + self.width,
                                                             self.y
                                                             - self.height,
                                                             self.width,
                                                             self.height,
                                                             self,
                                                             Tube)
                            if ((tube and tube.direction == "left")
                                or not self.blockedRightAbove()):
                                self.jumping = True
                                if tube:
                                    self.setAnimation("jump-tube-right")
                                    self.tubed = True
                                else:
                                    self.setAnimation("jump-right")
                                self.moving = 0
                        elif (block and not block.blockedRight() and
                            block.y+4<self.y+32): #block.top+4<self.bottom
                            self.pushing = True
                            block.push(1)
                            self.setAnimation("push-right")
                            self.moving = 0
                elif (self.moving < -6
                      and self.blockedLeft()):
                    tube = self.worldGroup.getSprite(self.x - 1,
                                                     self.y,
                                                     0,
                                                     self.height,
                                                     self,
                                                     Tube)
                    matching = tube and tube.getMatching() or None
                    if (tube and tube.direction == "right"
                        and matching and not matching.blocked()):
                        if not self.tubed:
                            self.tubed = True
                            self.moving -= 1
                            self.setAnimation("tube-left")
                    else:
                        block = self.blocksGroup.getSprite(self.x - 1,
                                                           self.y,
                                                           0,
                                                           self.height,
                                                           self,
                                                           Ice)
                        if ((not block or block.blockedLeft())
                            and not self.blockedAbove()):
                            tube = self.worldGroup.getSprite(self.x
                                                             - self.width,
                                                             self.y
                                                             - self.height,
                                                             self.width,
                                                             self.height,
                                                             self,
                                                             Tube)
                            if ((tube and tube.direction == "right")
                                or not self.blockedLeftAbove()):
                                self.jumping = True
                                if tube:
                                    self.setAnimation("jump-tube-left")
                                    self.tubed = True
                                else:
                                    self.setAnimation("jump-left")
                                self.moving = 0
                        elif ( block and not block.blockedLeft() and
                               block.y+4<self.y+32): #block.top+4<self.bottom
                            self.pushing = True
                            block.push(-1)
                            self.setAnimation("push-left")
                            self.moving = 0
                elif self.moving == 0 and self.tubed and self.vertical == 0:
                    tube = self.worldGroup.getSpriteAt(self.x,
                                                       self.y,
                                                       self,
                                                       Tube)
                    if tube:
                        tube.output(self)
                    else:
                        self.tubed = False
                        self.standing()
                elif self.vertical > 0:
                    self.y += 4
                    self.vertical -= 1
                elif self.vertical < 0:
                    self.y -= 4
                    self.vertical += 1
                elif self.moving == 0 and self.isDone():
                    self.standing()
            # big if end (jumping,  etc)
            if self.x < 0:
                self.x = 0
            elif self.x + self.width > self.level.width * 32:
                self.x = self.level.width * 32 - self.width
        # end if dead
        if self.y - self.height > self.level.height * 32:
            self.kill()
            return

    def doneJumping(self):
        self.jumping = False
        self.x = (self.x / 32) * 32
        self.y = (self.y / 32) * 32

    def draw(self, surface):
        surface.blit(self.image,
                     (self.x, self.y - 16),
                     (self._frameIndex * self.width,
                      0, self.width, self.height + 16)
                     )

    def hack_info_vel(self):
        if self.vertical:
            self.veldir[1]=self.vertical//abs(self.vertical)
            self.fasteness = 4
        else: self.veldir[1]=0
        if ( self.jumping
             or self.freezing
             or self.pushing ):
            self.veldir[0]=0
            self.fasteness = 0
        elif not self.moving and self.isDone:
            self.veldir[0] = 0
            self.fasteness = 0
        else:
            self.veldir[0] = self.direction
            self.fasteness = 4
