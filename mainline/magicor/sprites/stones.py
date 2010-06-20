"""
 flying  stones

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import math, random
from magicor.sprites import *
from magicor.sprites.blocks import Ice
from magicor import g_groups

class Ball(PhysicsStoneSprite):
    """ destroyed if touching fire or active lava. kills living things
    main params: movement_type, fasteness, position, velocity"""
    @classmethod
    def parse(cls,arg):

        spl = arg.split(" ", 4)
        veldir=[0,0]
        try:
            veldir[0]=int(spl[0])
            veldir[1]=int(spl[1])
            fasteness = float(spl[2])
            t=veldir[0]*veldir[1]
            if ( t!=0 and t!=1 ) or fasteness<0:
                raise ValueError
            if len(spl)<4:
                dvy = 0.
            else:
                dvy = float(spl[3])
                if dvy<0:
                    raise ValueError
            bReadOk = True
        except ValueError,IndexError:
            bReadOk = False
            warnings.warn( "Ball requires veldir_x , veldir_y , fasteness, [ dvy ]")
            print "in Ball.parse; returns ",bReadOk, veldir, fasteness
        print "in Ball.parse; returns ",bReadOk, veldir, fasteness, dvy
        return bReadOk, veldir, fasteness, dvy
        
    def __init__(self, level, x, y, veldir, fasteness, dvy=0.,bounceFactor=1.,subgroup="global"):
        PhysicsStoneSprite.__init__(
            self, level, x+16-4, y+16-4, 8, 8,
            {"default": (ImageFrame("sprites/ball_b", 8, 8),
                         AnimationFrame(0, 8),
                         JumpFrame(1),),
             "evaporate": (ImageFrame("sprites/ball_b", 8, 8),
                         AnimationFrame(1,2),
                         AnimationFrame(2,2),
                         AnimationFrame(3,2),
                         KillFrame())},
            4,
            veldir,fasteness,[],dvy
            )
        self.OnWorldCollision = collide_bounce
        self.collisionTable = [ (g_groups['fires'],None,4,False,'evaporate',None),
                                (g_groups['blocks'],None,1,True,'bounceSelf',None),
                                (g_groups['enemies'],None,3,True,'evaporate','die'),
                                (g_groups['players'],None,2,True,'bounceSelf',None)
                                ]

       
    def doAction(self,action):
        if action == 'evaporate':
            self.setAnimation('evaporate')
            return
        if action == 'die':
            self.kill()
            return
        print "Unknown action for Ball"


        
