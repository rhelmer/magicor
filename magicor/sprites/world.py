"""
Sprites that are a part of the world (tubes, lava, etc)

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import random,math

from magicor.sprites import *
from magicor.sprites.blocks import Ice
from magicor.sprites.seekers import Seeker
from magicor import Text, g_groups

class Lava(AnimatedSprite):
    
    def __init__(self, x, y, blocksGroup, players, fireGroup,
                 worldGroup, dormant,bSpiting,t):
        if bSpiting: s="sprites/spiting_lava"
        else: s="sprites/lava"
        AnimatedSprite.__init__(
            self, x, y, 32, 64,
            {"default": (ImageFrame(s, 32, 64),
                         AnimationFrame((0+x/32)%12, 2),
                         AnimationFrame((1+x/32)%12, 2),
                         AnimationFrame((2+x/32)%12, 2),
                         AnimationFrame((3+x/32)%12, 2),
                         AnimationFrame((4+x/32)%12, 2),
                         AnimationFrame((5+x/32)%12, 2),
                         AnimationFrame((6+x/32)%12, 2),
                         AnimationFrame((7+x/32)%12, 2),
                         AnimationFrame((8+x/32)%12, 2),
                         AnimationFrame((9+x/32)%12, 2),
                         AnimationFrame((10+x/32)%12, 2),
                         AnimationFrame((11+x/32)%12, 2),
                         JumpFrame(1)),
            "dormant": (ImageFrame(s, 32, 64),
                        AnimationFrame(12, 8),),
            "erupt": (ImageFrame(s, 32, 64),
                      AnimationFrame(12, 2),
                      AnimationFrame(13, 2),
                      AnimationFrame(14, 2),
                      AnimationFrame(15, 2),
                      AnimationFrame(16, 2),
                      AnimationFrame(17, 2),
                      AnimationFrame(18, 2),
                      CallbackFrame(self.ignitePeers)),
##                      AnimationFrame(0, 4),
##                      AnimationFrame(1, 4),
##                      AnimationFrame(2, 4),
##                      AnimationFrame(3, 4),
##                      AnimationFrame(4, 4),
##                      AnimationFrame(5, 4),
##                      AnimationFrame(6, 4),
##                      AnimationFrame(7, 4),
##                      JumpFrame(8)),
             }
            )
        self.dormant = dormant
        self.bSpiting = bSpiting
        self.spitDelta = t
        self.spitCnt = t
        if dormant:
            self.setAnimation("dormant")
        self.worldGroup = worldGroup
        self.blocksGroup = blocksGroup
        self.players = players
        self.fireGroup = fireGroup

    def erupt(self):
        self.dormant = False
        self.setAnimation("erupt")
        self.resources.playSound("samples/erupt")

    def ignitePeers(self):
        self.setAnimation("default")
        for lava in self.worldGroup.getSprites(self.x - 1,
                                               self.y,
                                               0,
                                               self.height,
                                               self,
                                               Lava):
            if lava.dormant:
                lava.erupt()
        for lava in self.worldGroup.getSprites(self.x + self.width,
                                               self.y,
                                               0,
                                               self.height,
                                               self,
                                               Lava):
            if lava.dormant:
                lava.erupt()

    def update(self):
        AnimatedSprite.update(self)
        if self.dormant:
            for fire in self.fireGroup.sprites():
                if fire.x == self.x and fire.y == self.y:
                    self.erupt()
        else:
            for block in self.blocksGroup.sprites():
                if (isinstance(block, Ice)
                    and block.x == self.x and block.y == self.y):
                    block.melt()
            for player in self.players.sprites():
                if (player.x == self.x
                    and player.y == self.y
                    and not player.dead):
                    player.die()
                    
            if self.bSpiting:
                if self.spitCnt>0:
                    self.spitCnt -=1
                else:
                    #create a new lump
                    self.spitCnt = self.spitDelta
            

class Tube(PhysicsSprite):
    
    def __init__(self, x, y, level, direction, name, blocks,
                 worldGroup, players):
        PhysicsSprite.__init__(
            self, level, x, y, 32, 32,
            {"default": (ImageFrame("sprites/tube-endings", 32, 32),
                         AnimationFrame(0, 0)),
             "left": (ImageFrame("sprites/tube-endings", 32, 32),
                         AnimationFrame(0, 0)),
             "right": (ImageFrame("sprites/tube-endings", 32, 32),
                         AnimationFrame(3, 0)),
             "up": (ImageFrame("sprites/tube-endings", 32, 32),
                         AnimationFrame(1, 0)),
             "down": (ImageFrame("sprites/tube-endings", 32, 32),
                         AnimationFrame(2, 0))
             },
            blocks
            )
        self.name = name
        self.direction = direction
        self.worldGroup = worldGroup
        self.players = players
        self.text = Text(None, self.resources["fonts/info"], 800)
        self.coverSurface = None
        self.setAnimation(direction)

    def testFall(self):
        return False

    def bounce(self, player):
        if self.direction == "left":
            player.x = self.x - 4
            player.moving = -7
            player.direction = 1
            player.setAnimation("tube-right")
            self.tubed = True
        elif self.direction == "right":
            player.x = self.x + 4
            player.moving = 7
            player.direction = -1
            self.tubed = True
            player.setAnimation("tube-left")
        elif self.direction == "up":
            player.y = self.y -4
            player.x = self.x
            player.moving = 0
            player.vertical = -6
            self.tubed = True
        elif self.direction == "down":
            player.y = self.y + 4
            player.x = self.x
            player.moving = 0
            player.vertical = 7
            self.tubed = True

    def blocked(self):
        if (self.direction == "left" and self.blockedLeft()
            or self.direction == "right" and self.blockedRight()
            or self.direction == "up" and self.blockedAbove()
            or self.direction == "down" and self.blockedBelow()):
            return True
        return False
            
    def getMatching(self):
        if self.name:
            for tube in self.worldGroup:
                if (isinstance(tube, Tube)
                    and tube != self
                    and tube.name == self.name
                    and not tube.blocked()):
                    return tube
        else:
            tubes = []
            for tube in self.worldGroup:
                if isinstance(tube, Tube) and tube != self:
                    tubes.append(tube)
            if tubes:
                return tubes[random.randint(0, len(tubes) - 1)]
        return None

    def output(self, player):
        tube = self.getMatching()
        if tube:
            if tube.direction == "right":
                player.x = tube.x + 4
                player.moving = 7
                player.direction = 1
                player.setAnimation("tube-right")
                player.tubed = True
                player.y = tube.y
            elif tube.direction == "left":
                player.x = tube.x - 4
                player.moving = -7
                player.direction = -1
                player.setAnimation("tube-left")
                player.tubed = True
                player.y = tube.y
            elif tube.direction == "down":
                self.tubed = True
                player.x = tube.x
                player.y = tube.y
                player.vertical = 8
            elif tube.direction == "up":
                self.tubed = True
                player.x = tube.x
                player.y = tube.y
                player.vertical = -8

    def draw(self, surface):
        PhysicsSprite.draw(self, surface)

class Trapola(AnimatedSprite):
    def __init__(self, x, y):
        self.explodeStage = 0 # frame count from explosion
        AnimatedSprite.__init__( self, x, y, 32, 34,
            {"default": (ImageFrame("sprites/trapola2_q", 32, 34),
                         AnimationFrame(0, 3),
                         AnimationFrame(1, 3),
                         AnimationFrame(2, 3),
                         AnimationFrame(3, 3),
                         AnimationFrame(4, 3),
                         AnimationFrame(5, 3),
                         AnimationFrame(6, 3),
                         AnimationFrame(7, 3),
                         AnimationFrame(8, 3),
                         AnimationFrame(9, 3),
                         AnimationFrame(10, 3),
                         AnimationFrame(11, 3),
                         JumpFrame(1)
                         ),
             "explode": (ImageFrame("sprites/trapola2b_exp", 64, 64),
                         AnimationFrame(0, 2),
                         AnimationFrame(1, 2),
                         AnimationFrame(2, 2),
                         AnimationFrame(3, 2),
                         AnimationFrame(4, 2),
                         AnimationFrame(5, 2),
                         AnimationFrame(6, 2),
                         AnimationFrame(7, 2),
                         AnimationFrame(8, 2),
                         AnimationFrame(9, 2),
                         AnimationFrame(10, 2),
                         AnimationFrame(11, 2),
                         AnimationFrame(12, 2),
                         AnimationFrame(13, 2),
                         AnimationFrame(14, 2),
                         AnimationFrame(15, 2),
                         #JumpFrame(15)
                         KillFrame()
                         )
            }
        )

    def eventExplode(self):
        #HERE: start box animation, including sound effects
        self.explodeStage=1
        self.setAnimation("explode")
        # setAnimation at fault or missing feature?
        self.width = 64
        self.height = 64

    def physics(self):
        if self.explodeStage==0:
            #if any sprite except decoration and light touches, then trigger the trapola
            for k,group in g_groups.items():
                if k!='decorations' and k!='world':
                    s=pygame.sprite.spritecollideany(self,group)
                    if s:
                        self.eventExplode()
                        break
                        
        else:
            self.explodeStage +=1
            if self.explodeStage<2*8+2 and self.explodeStage%8==1:
                #release a wave of seekers
                x=self.x+8; y=self.y+8
                da=math.radians(360./8.)
                a0=(self.explodeStage/8-1)*math.radians(360./16.)
                target = None
                for s in g_groups['players']:
                    target = s
                    break
                if target is None:
                    return
                for i in range(0,8):
                    heading = [math.cos(i*da+a0),math.sin(i*da+a0)]
                    g_groups['stones'].add(Seeker(x+heading[0]*4., y+heading[1]*4., heading,3.,target))


    def draw(self, surface, offsetX = 0, offsetY = 0):
        if self.explodeStage!=0:
            #correct for bigger size
            offsetX -= 16
            offsetY -= 16
        AnimatedSprite.draw(self, surface, offsetX, offsetY)

