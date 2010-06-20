
from math import atan2, sqrt, pi, radians,degrees
from magicor.sprites import *

def norm2(vec2):
    return sqrt(vec2[0]*vec2[0]+vec2[1]*vec2[1])

def angle_from_heading(v): # v must be unit vector
    a=degrees(atan2(v[1],v[0]))
    if a<0:
        a+=360
    return int(a/22.5)

def mov1_seeker(self):
    self.x+=self.heading[0]*self.fasteness
    self.y+=self.heading[1]*self.fasteness
    rpos = [self.x-self.xx0, self.y-self.yy0]
    if norm2(rpos)>64:
        self.event_mov1_terminated()

def mov2_seeker(self):
    other_heading = [(self.target.x+self.target.width/2.)-(self.x+self.width/2.),
                     (self.target.y+self.target.height/2.)-(self.y+self.height/2.)]
    d=norm2(other_heading)
    if d<1.e-6: d=1.
    other_heading = [other_heading[0]/d, other_heading[1]/d]
    a=0.9
    new_heading = [ a*self.heading[0]+(1.-a)*other_heading[0],
                    a*self.heading[1]+(1.-a)*other_heading[1] ]
    n2=norm2(new_heading)
    self.heading = [new_heading[0]/n2, new_heading[1]/n2]
    angle1=angle_from_heading(self.heading)
    if self.angle0!=angle1:
        self.setAnimation("%d"%angle1,False)
        self.angle0 = angle1
    terminal_fasteness = 6.
    self.fasteness = a*self.fasteness+(1.-a)*terminal_fasteness
    if d<4.:
        self.target.die()
    self.x+=self.heading[0]*self.fasteness
    self.y+=self.heading[1]*self.fasteness


class Seeker(AnimatedSprite):
    def __init__(self, x, y, heading,fasteness,target):
        self.xx0 = x; self.yy0=y
        self.fasteness = fasteness
        self.target = target
        #normalize heading, just in case
        n2=norm2(heading)
        if n2<1.e-6:
            n2=heading[1]=1.0
        self.heading =[ heading[0]/n2 , heading[1]/n2 ]
        self.angle0 = angle_from_heading(self.heading)
        initial_anim = "%d"%self.angle0

        self.subgroup = 'seeker'
        d={"default":   (ImageFrame("sprites/seeker3x18", 18, 18),
                        CallbackFrame(self.setAnimation, initial_anim))}
        for i in range(0,16):
            d["%d"%i]=(
                ImageFrame("sprites/seeker3x18", 18, 18),
                AnimationFrame(i*4,2),
                AnimationFrame(i*4+1,2),
                AnimationFrame(i*4+2,2),
                AnimationFrame(i*4+3,2),
                JumpFrame(i*4) )
                
        self.mov = mov1_seeker

        AnimatedSprite.__init__(self, x, y, 18, 18, d ,'default')

    def event_mov1_terminated(self):
        self.mov=mov2_seeker

    def physics(self):
        self.mov(self)
