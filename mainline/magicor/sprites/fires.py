"""
Fires or anything the player can destroy to complete the level.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import math, random
from magicor.sprites import *
from magicor.sprites.lights import YellowLight, YellowSpark
from magicor.sprites.blocks import Ice
from magicor import g_groups
from magicor.sprites.seekers import Seeker

class Fire(PhysicsSprite):

    def __init__(self, x, y, level, blocksGroup, lightsGroup, players,
                 canFall = True):
        PhysicsSprite.__init__(
            self, level, x, y, 32, 32,
            {"default": (ImageFrame("sprites/fire-normal", 32, 32),
                         AnimationFrame(0, 1),
                         AnimationFrame(1, 1),
                         AnimationFrame(2, 1),
                         AnimationFrame(3, 1),
                         AnimationFrame(4, 1),
                         AnimationFrame(5, 1),
                         JumpFrame(1))},
            blocksGroup
            )
        self.players = players
        self.light = YellowLight(x - 32, y - 32)
        self.canFall = canFall
        self.followMe = None
        lightsGroup.add(self.light)
        self.lightsGroup = lightsGroup

    def kill(self):
        PhysicsSprite.kill(self)
        self.light.kill()
        for i in range(16):
            angle = i * (360 / 16.0)
            dx = 8.0 * math.cos(math.radians(angle))
            dy = 8.0 * math.sin(math.radians(angle))
            self.lightsGroup.add(YellowSpark(self.x - 32, self.y - 32, dx, dy))

    def physics(self):
        if self.followMe is not None:
            #sliding
            if not self.followMe.alive():
                #the iceblock was killed
                self.x = self.x/32*32
                self.followMe = None
            else:
                prev_x=self.x
                self.x = self.followMe.x
                if self.followMe.falling or not self.followMe.moving:
                    self.x = self.x/32*32
                    self.followMe=None
                for s in pygame.sprite.spritecollide(self, self.blocksGroup, False): # usar sprite collision ?
                    if isinstance(s, Ice):
                        if s.falling and s.x == self.x and s.y == self.y:
                            s.kill()
                            self.resources.playSound("samples/bonus")
                            self.kill()
                            break
                        else:
                            self.x = (prev_x+self.width/2)/32*32
                            self.followMe = None
                #check world colisions
                if self.followMe is not None:
                    if self.followMe.moving>0:
                        if self.level[(self.x+self.width)/32,(self.y+self.height/2)/32]:
                            self.x = self.x/32*32
                            self.followMe = None
                    else:    
                        if self.level[self.x/32,(self.y+self.height/2)/32]:
                            self.x = (self.x/32+1)*32
                            self.followMe = None
                #enemies are not checked, they need to be flying enemies wich
                #can take damage from fire.
                self.light.x = self.x - 32 + random.randint(-4, 4)
                self.light.y = self.y - 32 + random.randint(-4, 4)
        else:
            #static or falling
            for s in self.blocksGroup.sprites():
                if isinstance(s, Ice) and s.x == self.x and s.y == self.y:
                    s.kill()
                    self.resources.playSound("samples/bonus")
                    self.kill()
                    break
            for player in self.players.sprites():
                if player.x == self.x and player.y == self.y and not player.dead:
                    player.die()
            if self.canFall and not self.blockedBelow():
                self.y += 4
                if 9>self.level.height*30-self.y>4:
                    # fire falling out of the level, lauch seekers to kill players
                    x=self.x+self.width/2.; y=self.y; da=math.radians(360./16.)
                    for s in g_groups['players']:
                        target = s
                        break
                    for i in range(0,16):
                        heading = [math.cos(i*da),math.sin(i*da)]
                        g_groups['stones'].add(Seeker(x+heading[0]*4., y+heading[1]*4., heading,3.,target))
            self.light.x = self.x - 32 + random.randint(-4, 4)
            self.light.y = self.y - 32 + random.randint(-4, 4)
            
