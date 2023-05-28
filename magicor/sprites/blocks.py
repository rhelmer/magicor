"""
Block sprites.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import random

from magicor.sprites import *
from magicor import g_groups


class BlocksGroup(AnimationGroup):
    """
    A group of ices used to synchronize animation.
    """
    SHINE_INTERVAL = 50

    def __init__(self, *sprites):
        AnimationGroup.__init__(self, *sprites)
        self.shine = self.SHINE_INTERVAL + random.randint(0, 200)

    def isMoving(self):
        for s in self.sprites():
            if s.moving != 0 or s.falling:
                return True
        return False

    def update(self):
        AnimationGroup.update(self)
        if self.shine > 0:
            self.shine -= 1
        else:
            self.shine = self.SHINE_INTERVAL + random.randint(0, 200)
            for s in self.sprites():
                s.shine(s.x / 32 + s.y / 32)

    def draw(self, surface):
        for s in (ss for ss in self.sprites() if ss.eyecandy):
            s.updateZoom(surface)
        AnimationGroup.draw(self, surface)

class IcePiece(AnimatedSprite):

    def __init__(self, x, y, piece, group):
        AnimatedSprite.__init__(
            self, x, y, 32, 32,
            {"default": (ImageFrame("sprites/ice-normal", 32, 32),)}
            )
        group.add(self)
        if piece == 0:
            self._frameIndex = 9
            self.dx = random.randint(-4, -1)
            self.dy = random.randint(-4, -1)
        elif piece == 1:
            self._frameIndex = 10
            self.dx = random.randint(1, 4)
            self.dy = random.randint(-4, -1)
        elif piece == 2:
            self._frameIndex = 11
            self.dx = random.randint(1, 4)
            self.dy = random.randint(-2, -1)
        elif piece == 3:
            self._frameIndex = 12
            self.dx = random.randint(-4, -1)
            self.dy = random.randint(-2, -1)
        else:
            raise ValueError("ice piece must be 0-3")

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.75
        if self.y > 600:
            self.kill()


class Ice(PhysicsSprite):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    BOTH = 3

    def __init__(self, x, y, level, blocksGroup, imgResource, life,
                 lightsGroup, players, enemies, eyecandy = True):
        PhysicsSprite.__init__(
            self,
            level,
            x, y, 32, 32,
            {"default": (ImageFrame(imgResource, 32, 32),
                         AnimationFrame(4, 0),
                         AttributeFrame("created", True),
                         ),
             "create": (ImageFrame(imgResource, 32, 32),
                        AnimationFrame(0, 1),
                        AnimationFrame(1, 1),
                        AnimationFrame(2, 1),
                        AnimationFrame(3, 1),
                        AttributeFrame("created", True),
                        CallbackFrame(self.addConnections),
                        ),
            "left": (ImageFrame(imgResource, 32, 32),
                      AnimationFrame(5, 0),
                     AttributeFrame("created", True),
                      ),
             "right": (ImageFrame(imgResource, 32, 32),
                       AnimationFrame(6, 0),
                       AttributeFrame("created", True),
                       ),
             "both": (ImageFrame(imgResource, 32, 32),
                      AnimationFrame(7, 0),
                      AttributeFrame("created", True),
                      ),
             },
            blocksGroup)
        blocksGroup.add(self)
        self.eyecandy = eyecandy
        self.created = False
        self.players = players
        self.lightsGroup = lightsGroup
        self.enemyGroup = enemies
        self.left = None
        self.right = None
        self.life = life
        self.rumble = False
        self._shine = -1
        self.zoomSurface = None
        self.frostImage = self.resources["sprites/frost"]

    def shine(self, delay):
        self._shine = delay

    def blockedBelow(self):
        return bool(PhysicsSprite.blockedBelow(self)
                    or self.players.getSprite(self.x,
                                              self.y + self.height,
                                              self.width, 0, self)
                    )

    def blockedLeft(self):
        enemy = self.enemyGroup.getSprite(self.x - 1,
                                          self.y,
                                          0,
                                          self.height,
                                          self)
        return bool(PhysicsSprite.blockedLeft(self) or
                    (enemy and enemy.blockedLeft())
                    or self.players.getSprite(self.x - 1, self.y,
                                              0, self.height, self))

    def blockedRight(self):
        enemy = self.enemyGroup.getSprite(self.x + self.width,
                                          self.y,
                                          0,
                                          self.height,
                                          self)
        return bool(PhysicsSprite.blockedRight(self) or
                    (enemy and enemy.blockedRight())
                    or self.players.getSprite(self.x + self.width, self.y,
                                              0, self.height, self))

    def getZoom(self, source, x, y):
        tmp = pygame.Surface((16, 16), pygame.HWSURFACE, 32)
        tmp.blit(source, (0, 0),
                 (x + 8, y + 8, 16, 16))
        return pygame.transform.scale2x(tmp)

    def updateZoom(self, surface):
        if not self.zoomSurface:
            self.zoomSurface = self.getZoom(surface, self.x, self.y)

    def draw(self, surface):
        if self.rumble:
            ox = random.randint(0, 1) * 2 - 1
            oy = random.randint(0, 1) * 2 - 1
            self.rumble = False
        else:
            ox = 0
            oy = 0
        if self.eyecandy:
            surface.blit(self.zoomSurface, (self.x, self.y))
            if self.left == self:
                surface.blit(self.frostImage,
                             (self.x-32, self.y), (0, 0, 64, 32))
            if self.right == self:
                surface.blit(self.frostImage,
                             (self.x, self.y), (0, 0, 64, 32))
        AnimatedSprite.draw(self, surface, ox, oy)
        if self._shine >= 0 and self._shine < 2:
            surface.fill(0xffffff,
                         (self.rect.left + ox
                          + 16 - self._shine * 16,
                          self.rect.top + oy,
                          16,
                          self.rect.height))
        if self._shine >= 0:
            self._shine -= 1
        if self.life < 16:
            surface.blit(self.image,
                         (self.rect.left + ox,
                          self.rect.top + oy,
                          self.rect.width,
                          self.rect.height),
                         (8 * self.width,
                          0, self.width, self.image.get_height())
                         )

    def melt(self):
        self.moving = 0
        self.life -= 1
        self.rumble = True

    def setConnectionAnimation(self):
        if self.left and self.right:
            self.setAnimation("both")
        elif self.left:
            self.setAnimation("left")
        elif self.right:
            self.setAnimation("right")
        else:
            self.setAnimation("default")

    def kill(self):
        if self.alive():
            self.removeConnections()
            if self.life <= 0:
                self.resources.playSound("samples/icebreak")
                if self.eyecandy:
                    IcePiece(self.x, self.y, 0, self.lightsGroup)
                    IcePiece(self.x, self.y, 1, self.lightsGroup)
                    IcePiece(self.x, self.y, 2, self.lightsGroup)
                    IcePiece(self.x, self.y, 3, self.lightsGroup)
        PhysicsSprite.kill(self)

    def removeConnections(self):
        if self.left and self.left != self:
            self.left.right = None
            self.left.setConnectionAnimation()
        if self.right and self.right != self:
            self.right.left = None
            self.right.setConnectionAnimation()
        self.left = None
        self.right = None
        self.setConnectionAnimation()

    def addConnections(self, direction = 0):
        if direction <= 0 and self.blockedLeft():
            self.left = self
        if direction >= 0 and self.blockedRight():
            self.right = self
        if direction <= 0:
            block = self.blocksGroup.getSprite(self.x - 1,
                                               self.y,
                                               0,
                                               self.height,
                                               self,
                                               Ice)
            if block:
                block.right = self
                block.setConnectionAnimation()
                self.left = block
        if direction >= 0:
            block = self.blocksGroup.getSprite(self.x + 32,
                                               self.y,
                                               0,
                                               self.height,
                                               self,
                                               Ice)
            if block:
                block.left = self
                block.setConnectionAnimation()
                self.right = block
        self.setConnectionAnimation()

    def testFall(self):
        if (not self.created
            or self.blockedBelow()
            or self.right == self
            or self.left == self):
            return False
        right = self.right
        while right:
            if right.blockedBelow() or right == right.right:
                self.y = right.y
                return False
            right = right.right
        left = self.left
        while left:
            if left.blockedBelow() or left == left.left:
                self.y = left.y
                return False
            left = left.left
        return True

    def physics(self):
        if (self.life <= 0
            or self.x + self.width < 0
            or self.x > self.level.width * 32
            or self.y > self.level.height * 32):
            self.kill()
        else:
            x, y = self.x, self.y
            PhysicsSprite.physics(self)
            if x != self.x or y != self.y:
                self.zoomSurface = None
            if ((self.moving > 0 and self.blockedRight())
                or (self.moving < 0 and self.blockedLeft())):
                self.stopMoving()

    def stopMoving(self):
        if self.moving != 0:
            self.resources.playSound("samples/blockhit")
            self.moving = 0

    def push(self, direction):
        global g_groups
        fire=g_groups['fires'].getSpriteAt(self.x, self.y-32, None, None)
        if fire is not None:
            fire.followMe = self
        if direction < 0:
            self.moving = -99999
        elif direction > 0:
            self.moving = 99999

    def eventStop(self):
        self.resources.playSound("samples/blockland")
#        self.zoomSurface = None

    def hack_info_vel(self):
        if self.falling:
            self.veldir= [0,1]
            self.fasteness = 4
        else:
            self.veldir[1]=0
            if not self.moving:
                self.veldir[0]=0
                self.fasteness = 0
            else:
                self.fasteness = 4
                if self.moving>0: self.veldir[0]=1
                else: self.veldir[0]=-1

class NormalIce(Ice):

    def __init__(self, x, y, level, blocksGroup, lightsGroup, players,
                 enemies, zoom):
        Ice.__init__(self, x, y, level, blocksGroup,
                     "sprites/ice-normal", 32, lightsGroup, players, enemies,
                     zoom)
