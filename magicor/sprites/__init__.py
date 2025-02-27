"""
Sprites animation library.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import pygame.sprite
from magicor.resources import getResources
from operator import itemgetter
from magicor import g_printkeys,g_devflags,dbgPrint

class Frame(object):
    """
    Base type for animation frames.
    """

    def __str__(self):
        return "<Frame>"

class ResourceFrame(Frame):
    """
    Any type of animation frame resource.
    """

    def __init__(self, resource):
        self.resource = resource

    def __str__(self):
        return "<ResourceFrame>"

class ImageFrame(ResourceFrame):

    def __init__(self, surface, width, height):
        ResourceFrame.__init__(self, surface)
        self.width = width
        self.height = height

    def __str__(self):
        return "<ImageFrame %dx%d>"%(self.width, self.height)


class SoundFrame(ResourceFrame):

    def __init__(self, sound):
        ResourceFrame.__init__(self, sound)

    def __str__(self):
        return "<SoundFrame>"


class JumpFrame(Frame):

    def __init__(self, index):
        Frame.__init__(self)
        self.index = index

    def __str__(self):
        return "<JumpFrame %d>"%self.index


class MoveFrame(Frame):

    def __init__(self, x, y):
        Frame.__init__(self)
        self.x = x
        self.y = y

    def __str__(self):
        return "<MoveFrame %.2f, %.2f>"%(self.x, self.y)


class AnimationFrame(Frame):

    def __init__(self, frame, delay):
        Frame.__init__(self)
        self.frame = frame
        self.delay = delay

    def __str__(self):
        return "<AnimationFrame %d %d>"%(self.frame, self.delay)


class SetFrame(Frame):

    def __init__(self, animationName):
        Frame.__init__(self)
        self.animationName = animationName

    def __str__(self):
        return "<SetFrame '%s'>"%self.animationName


class KillFrame(Frame):

    def __str__(self):
        return "<KillFrame>"


class AttributeFrame(Frame):

    def __init__(self, attr, value):
        Frame.__init__(self)
        self.attr = attr
        self.value = value

    def __str__(self):
        return "<AttributeFrame %s=%s>"%(self.attr, self.value)


class CallbackFrame(Frame):

    def __init__(self, callback, *args, **kwargs):
        Frame.__init__(self)
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return "<CallbackFrame %s>"%self.callback.__name__


class AnimationGroup(pygame.sprite.Group):
    """
    A group of animated objects.
    """

    def __init__(self, *sprites):
        pygame.sprite.Group.__init__(self, *sprites)
        self.r = pygame.Rect((0, 0, 0, 0))

    def draw(self, surface):
        for sprite in self.sprites():
            sprite.draw(surface)

    def sort(self, f = None):
        if not f:
            f = self.sortFunc
        self.sprites().sort(key=lambda b: b.y)

    def add(self, *sprites):
        pygame.sprite.Group.add(self, *sprites)
        # self.sprites().sort(key=lambda b: b.y)

    def remove(self, *sprites):
        pygame.sprite.Group.remove(self, *sprites)

    def getSpriteAt(self, x, y, exclude, type_ = None):
        for sprite in self.sprites():
            if (sprite != exclude
                and sprite.x == x
                and sprite.y == y
                and (not type_ or isinstance(sprite, type_))
                ):
                return sprite
        return None

    def count(self):
        return len(self.sprites())

    def getSprite(self, x, y, width, height, exclude = None, type_ = None):
        return self._getSprites(x, y, width, height, exclude, type_)

    def getSprites(self, x, y, width, height, exclude = None, type_ = None):
        return self._getSprites(x, y, width, height, exclude, type_, False)

    def _getSprites(self, x, y, width, height, exclude, type_, single = True):
        ret = []
        self.r.left = x
        self.r.top = y
        self.r.width = width if width > 0 else 1
        self.r.height = height if height > 0 else 1
        for sprite in self.sprites():
            if (sprite != exclude
                and self.r.colliderect(sprite.rect)
                and (not type_ or isinstance(sprite, type_))
                ):
                if single:
                    return sprite
                ret.append(sprite)
        if single:
            return None
        return ret

    def animate(self):
        for s in self.sprites():
            s.animate()

    def update(self):
        for s in self.sprites():
            s.update()

class AnimatedSprite(pygame.sprite.Sprite):
    """
    A sprite type that animates.
    """

    def __init__(self, x, y, w, h, animations, default = None):
        """
        Arguments:
        animations          A dictionary containing lists of animation frames.
        groups              Sequence of sprite groups.
        default             Default animation key.
        """
        pygame.sprite.Sprite.__init__(self)
        self.resources = getResources()
        self._animations = animations
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self._frameIndex = 0
        self.rect = pygame.Rect((x, y, w, h))
        if default:
            self.setAnimation(default)
        else:
            self.setAnimation("default")

    def isDone(self):
        animation = self._animations[self._animationName]
        return bool(not animation or self._index >= len(animation))

    def setAnimation(self, name, bResetIndex=True):
        """
        Use specified set of animation.
        Raises KeyError if the animation set is not found.
        """
        if name not in self._animations:
            raise KeyError("no animation named '%s' for sprite %s"
                           %(name, type(self)))
        self._animationName = name
        self._index = 0
        self._count = 0
        self.image = None
        self.flags = {}
        self._srcRect = pygame.Rect((0, 0, 0, 0))
        for frame in self._animations[name]:
            if isinstance(frame, ImageFrame):
                self.image = self.resources[frame.resource]
                self.rect.left = self.x
                self.rect.top = self.y
                self.rect.width = frame.width
                self.rect.height = frame.height
                if self.width is None:
                    self.width = frame.width
                if self.height is None:
                    self.height = frame.height
            elif self.image and isinstance(frame, AnimationFrame):
                self._frameIndex = frame.frame
                break

    def animate(self):
        """
        Animates the sprite.
        """
        name = self._animationName
        animation = self._animations[self._animationName]
        while self._index < len(animation):
            if name != self._animationName:
                name = self._animationName
                animation = self._animations[self._animationName]
            frame = animation[self._index]
            if isinstance(frame, ImageFrame):
                self.image = self.resources[frame.resource]
                self.rect.left = self.x
                self.rect.top = self.y
                self.rect.width = frame.width
                self.rect.height = frame.height
                self._index += 1
            elif isinstance(frame, SetFrame):
                self.setAnimation(frame.animationName)
            elif isinstance(frame, JumpFrame):
                self._index = frame.index
            elif isinstance(frame, KillFrame):
                self.kill()
                break
            elif isinstance(frame, AnimationFrame):
                if self._count == 0:
                    self._frameIndex = frame.frame
                self._count += 1
                if self._count > frame.delay:
                    self._index += 1
                    self._count = 0
                else:
                    break
            elif isinstance(frame, MoveFrame):
                self.x += frame.x
                self.y += frame.y
                self._index += 1
            elif isinstance(frame, SoundFrame):
                self.resources.playSound(frame.resource)
                self._index += 1
            elif isinstance(frame, AttributeFrame):
                if hasattr(self, frame.attr):
                    setattr(self, frame.attr, frame.value)
                self._index += 1
            elif isinstance(frame, CallbackFrame):
                frame.callback(*frame.args, **frame.kwargs)
                self._index += 1
            else:
                raise TypeError("invalid frame, %s in sprite %s"
                                %(frame, self))

    def physics(self):
        pass

    def update(self):
        if self.alive():
            self.physics()
            self.animate()
        self.rect.x = self.x
        self.rect.y = self.y
        self.rect.width = self.width
        self.rect.height = self.height

    def draw(self, surface, offsetX = 0, offsetY = 0):
        """
        Draw the sprite using animation specs.
        """
        surface.blit(self.image,
                     (self.x + offsetX, self.y + offsetY),
                     (self._frameIndex * self.width,
                      0, self.width, self.height)
                     )

    def colliding(self, group):
        ret = []
        for s in self.group.sprites():
            if (s != self
                and ((self.x >= s.x
                      and self.x <= s.x + s.width
                      and self.y >= s.y
                      and self.y <= s.y + s.height)
                     or
                     (s.x >= self.x
                      and s.x <= self.x + self.width
                      and s.y >= self.y
                      and s.y <= self.y + self.height)
                     )):
                ret.append(s)
        return ret


class PhysicsSprite(AnimatedSprite):

    def __init__(self, level, x, y, w, h, animations, blocksGroup,
                 default = None):
        AnimatedSprite.__init__(self, x, y, w, h, animations, default)
        self.blocksGroup = blocksGroup
        self.moving = 0
        self.tubed = False
        self.falling = False
        self.veldir = [0,0]
        self.fasteness = 0
        self.level = level

    def testFall(self):
        return (not self.blockedBelow())

    def eventFalling(self):
        pass

    def eventStop(self):
        pass

    def hack_info_vel(self):
        """build self.veldir and self.fasteness from native params"""
        pass

    def doAction(self,action):
        if action=='die':
            self.kill()

    def physics(self):
        x, y = self.x / 32, self.y / 32
        right, bottom = (self.x + 32) / 32, (self.y + 32) / 32
        if self.falling:
            if self.blockedBelow() or not self.testFall():
                self.falling = False
                self.eventStop()
            else:
                self.y += 4
        else:
            if (y >= self.level.height * 32 or self.testFall()):
                self.falling = True
                self.moving = 0
                self.eventFalling()
            elif self.moving > 0:
                if (x >= self.level.width - 1
                    or self.tubed
                    or not self.blockedRight()):
                    self.x += 4
                self.moving -= 1
            elif self.moving < 0:
                if (x <= 0
                    or self.tubed
                    or not self.blockedLeft()):
                    self.x -= 4
                self.moving += 1

    def blockedLeft(self):
        x, y = (self.x - 1) / 32, self.y / 32
        if (self.x <= 0
            or self.level[x, y]
            or self.blocksGroup.getSprite(self.x - 1,
                                          self.y,
                                          0,
                                          self.height,
                                          self)
            ):
            return True
        return False

    def blockedRight(self):
        x, y = (self.x + self.width) / 32, self.y / 32
        if (self.x + self.width >= self.level.width * 32
            or self.level[x, y]
            or self.blocksGroup.getSprite(self.x + self.width,
                                          self.y, 0, self.height,
                                          self)
            ):
            return True
        return False

    def blockedLeftAbove(self):
        x, y = (self.x - 1) / 32, (self.y - 1) / 32
        if (self.x <= 0
            or self.level[x, y]
            or self.blocksGroup.getSprite(self.x - 1, self.y - 1,
                                          0, 0, self)
            ):
            return True
        return False

    def blockedRightAbove(self):
        x, y = (self.x + self.width) / 32, (self.y - 1) / 32
        if (self.x + self.width >= self.level.width * 32
            or self.level[x, y]
            or self.blocksGroup.getSprite(self.x + self.width,
                                          self.y - 1, 0, 0, self)
            ):
            return True
        return False

    def blockedBelow(self):
        x, y = self.x / 32, (self.y + self.height) / 32
        xr = (self.x + self.width - 1) / 32
        if (xr < 0 or xr > 20):
            return True
        elif (y < self.level.height
            and (self.level[x, y]
                 or self.level[xr, y]
                 or self.blocksGroup.getSprite(self.x,
                                               self.y + self.height,
                                               self.width, 0, self)
                 )
            ):
            return True
        return False

    def blockedAbove(self):
        x, y = self.x / 32, (self.y - 1) / 32
        xr = (self.x + self.width - 1) / 32
        if (xr < 0 or xr > 20 or self.level[xr, y]):
            return True
        elif (y >= 0
              and (self.level[x, y]
                   or self.blocksGroup.getSprite(self.x,
                                                 self.y - 1,
                                                 self.width, 0, self)
                 )
            ):
            return True
        return False

    def blockedRightBelow(self):
        x, y = (self.x + self.width) / 32, (self.y + self.height) / 32
        if (y < self.level.height
            and (self.x + self.width >= self.level.width * 32
                 or x > 20
                 or self.level[x, y]
                 or self.blocksGroup.getSprite(self.x + self.width,
                                               self.y + self.height,
                                               0, 0, self)
                 )
            ):
            return True
        return False

    def blockedLeftBelow(self):
        x, y = (self.x - 1) / 32, (self.y + self.height) / 32
        if (y < self.level.height
            and (self.x <= 0
                 or x < 0
                 or self.level[x, y]
                 or self.blocksGroup.getSprite(self.x - 1,
                                               self.y + self.height,
                                               0, 0, self)
                 )
            ):
            return True
        return False

##-> support functions for PhysicsStoneSprite

# bStop signals the cases where the sprite position must be updated to the last
#point where colision doenst occur; alternatively
# bNonBlockingInteraction = not bStop
def getSpritesTouched( self,toTravel ):
    #move the sprite to the tentative position; if no colision: done, else
    #for each sprite do: move self from initial position to tentative position in
    #steps of one, when colision detected freeTravel can be calc. The min free travel
    #will be the final free travel ( counting only the sprites with bStop = True )
    #if both sprites are small and fasteness is not small collision
    #can be missed
    x0=self.x; y0=self.y
    #q: we need the pygame sprite moved, this really do it? Y. remember to
    #restore prior to return
    self.rect.x += self.veldir[0]*toTravel
    self.rect.y += self.veldir[1]*toTravel
    r=self.radius
    minFreeTravel = toTravel
    tl=[]
    bGenStuck = False
    steps=int(toTravel)+1
    dbgPrint( 'sb', g_devflags['F5'], "@@in spriteTouch - tryMove=",toTravel,"  steps=",steps)
    dx=toTravel/float(steps)*self.veldir[0]
    dy=toTravel/float(steps)*self.veldir[1]
    for group,ignoreSubgroup, minOverlap,bStop, self_action, inflict_action in self.collisionTable:
        for s in pygame.sprite.spritecollide(self, group, False):
            if ((ignoreSubgroup is None) or
                (ignoreSubgroup is not None and s.subgroup!=ignoreSubgroup)
               ):
                dbgPrint( 'sb', g_devflags['F5'], "@@@ spriteTouched x,y,width,height",s.x,s.y,s.width,s.height)
                dbgPrint( 'sb', g_devflags['F5'], "@@@ sprite   Ball x,y,width,height",x0,y0,self.width,self.height)
                dbgPrint( 'sb', g_devflags['F5'], "@@@   moved  Ball x,y", self.rect.x,self.rect.y)
                ww=s.width-2.*minOverlap; hh=s.height-2.*minOverlap
                target=pygame.Rect(s.x+minOverlap,s.y+minOverlap,ww,hh)
                #####-> must be from the initial position
                px=x0+self.width/2.-r   ; py=y0+self.height/2.0-r
                bBump = False
                for i in range(0,steps):
                    dbgPrint( 'sb', g_devflags['F5'], "          probe left,right:",px,px+2*r)
                    if target.colliderect( px,py,2.*r,2.*r ):
                        bBump=True
                        break
                    px+=dx
                    py+=dy
                dbgPrint( 'sb', g_devflags['F5'], "bBump=",bBump,"  i=",i)
                if bBump:
                    if i==0 and bStop:
                        bStuck = True
                        bGenStuck = True
                        freeTravel = 0
                        overshot = toTravel
                    else:
                        bStuck = False
                        freeTravel = (i-1)/float(steps)*toTravel
                        overshot = toTravel - freeTravel
                else:
                    bStuck = False
                    freeTravel = toTravel
                    overshot = 0
                dbgPrint( 'sb', g_devflags['F5'], "overshot",overshot)
                tl.append( ( freeTravel, minOverlap, bStop,bStuck,
                             group, s,
                             self_action, inflict_action) )
                if bStop and freeTravel<minFreeTravel:
                    minFreeTravel=freeTravel
    get0=itemgetter(0) #to acces member 0 of tuple without unpacking
    tl = [ v for v in tl if get0(v)<=minFreeTravel ]
    self.rect.x = x0
    self.rect.y = y0
    return minFreeTravel, bGenStuck, tl

def collide_bounce(self,toTravel): ## to chek: maybe a dummy spriteTofollow is needed
    self.veldir = self.bounceDir
    if self.bounceFactor:
        toTravel = toTravel * self.bounceFactor
        self.fasteness *= self.bounceFactor
        if self.fasteness < 0.1:
            self.fasteness = 0
            toTravel = 0
            #maybe set mov_0 as movement, or call event stopped
    return toTravel

#stick is a variant of bounce when the stone loose al velocity
def collide_stick(self, bounceDir, toTravel, spriteToFollow=None):
    ## NOTE: probably wrong, never tested nor updated. Consider as placeholder.
    #maybe more work is needed when collisions with sprite and self is
    #following another sprite. Or we need an 'scrap' sister function that will be
    #the OnCollision when sprite is atached to a sprite.
    #if there is a timed event after stick , we need to add code to track this.
    self.veldir = bounceDir
    toTravel = 0
    self.fasteness = 0
    if spriteToFollow is not None:
        self.followMe = spriteToFollow
    if self._animations.has_key["stick"]: ## lava can have more than 1 stick
        #sequence: born, stick to world, loose stone
        self.setAnimation["stick"]
    elif self._animationName != "default":
        self.setAnimationName = "default"
    return toTravel

def mov_0(self):
    # NOTE: untested and unupdated. Consider a placeholder
    if self.followMe is not None:
        if not self.followMe.alive():
            self.followMe = None
            #### set mov_v
        else:
            prev_x=self.x
            self.x = self.followMe.x
            #tentative, maybe we dont need to detach
            if self.followMe.falling or not self.followMe.moving:
                self.followMe=None

    if self.unmovingTimelimit:
        self.unmovingTime -=1
        if self.unmovingTime <= 0:
            self.unmovingTerminated(self)
    #maybe collision code , with scrap and crush detection



def mov_h(self,toTravel):
    x0=self.x;y0=int(self.y)
    r=self.radius
    bOutOfScreen = False
    bBump = False
    nonColisionTravel = toTravel
    x1=x0+self.veldir[0]*toTravel
    if self.veldir[0]<0:
        if x1+self.width<0:
            bOutOfScreen = True
        elif self.level[int(x1)/32,y0/32]:
                #world colision
                x1 = (int(x1)/32+1)*32
                nonColisionTravel = x0-x1
                self.bounceDir = [1,0]
                bBump = True
        else:
            pass
    else:
        if x1>=self.level.width*32:
            bOutOfScreen = True
        elif self.level[int(x1+self.width)/32,y0/32]:
                #world colision
                excess=int(x1+self.width)%32 #+1 seems correct but looks worse
                x1 -= excess
                nonColisionTravel = x1-x0
                self.bounceDir = [-1,0]
                bBump = True
        else:
            pass
    return bBump, toTravel, nonColisionTravel, bOutOfScreen

def mov_v(self,toTravel):
    x0=int(self.x);y0=self.y
    r=self.radius
    bOutOfScreen = False
    bBump = False
    nonColisionTravel = toTravel
    y1=y0+self.veldir[1]*toTravel
    if self.veldir[1]<0:
        if y1+self.height<0:
            bOutOfScreen = True
        elif self.level[x0/32,int(y1)/32]:
                #world colision
                y1 = (int(y1)/32+1)*32
                nonColisionTravel = y0-y1
                self.bounceDir = [0,1]
                bBump = True
        else:
            pass
    else:
        if y1>=self.level.height*32:
            bOutOfScreen = True
        elif self.level[x0/32,int(y1+self.height)/32]:
                #world colision
                excess = int(y1+self.height)%32+1
                y1 -= excess
                nonColisionTravel = y1-y0
                self.bounceDir = [0,-1]
                bBump = True
        else:
            pass
    return bBump, toTravel, nonColisionTravel, bOutOfScreen


def mov_diagonal(self,toTravel):
    #asume fasteness <32
    x0=self.x;y0=self.y
    r=self.radius-1
    veldir = self.veldir
    level = self.level
    bOutOfScreen = False
    bBump = False
    nonColisionTravel = toTravel
    #tentative next pos
    x1=x0+veldir[0]*toTravel
    y1=y0+veldir[1]*toTravel
    #check out of screen
    if veldir[0]<0:
        if x1+self.width<0:
            bOutOfScreen = True
    else:
        if x1>=self.level.width*32:
            bOutOfScreen = True
    if veldir[1]<0:
        if y1+self.height<0:
            bOutOfScreen = True
    else:
        if y1>=self.level.height*32:
            bOutOfScreen = True
    if bOutOfScreen:
        return bBump, toTravel, toTravel, bOutOfScreen

    #test colision by checking  the posible colisions of three points
    #if a,b center of stone,
    #the case test are:
    #    (a,b)+r*cos(45)*veldir
    #    (a,b)+r*(veldir[0],0)
    #    (a,b)+r*(0,veldir[1])
    #and we need to test if colisions happens when moving
    #dt*fasteness*veldir
    a=x0+self.width/2.0
    b=y0+self.height/2.0

    aa=a+r*veldir[0]
    bb=b+r*veldir[1]

    steps = int(toTravel)+1;
    dx=self.fasteness/float(steps)*veldir[0]
    dy=self.fasteness/float(steps)*veldir[1]

    self.bounceDir = veldir
    for i in range(0,steps):
        aa += dx; a += dx
        bb += dy; b += dy
        #note: aa and bb seems the correct but with veldir >0 bounces prematurelly
        #with (aa-1) and (bb-1) looks better, albeit not perfect.
        if level[int(aa)/32,int(b)/32]:
            bBump=True
            self.bounceDir[0]=-veldir[0]
        if level[int(a)/32,int(bb)/32]:
            self.bounceDir[1]=-veldir[1]
            bBump = True
        if bBump:
            break

    if not bBump:
        aa=(x0+self.width/2.0)+r*0.7071*veldir[0]
        bb=(y0+self.height/2.0)+r*0.7071*veldir[1]
        for i in range(0,steps):
            aa += dx
            bb += dy
            if level[int(aa)/32,int(bb)/32]:
                bBump=True
                self.bounceDir[0]=-veldir[0]
                self.bounceDir[1]=-veldir[1]
            if bBump:
                break
    if bBump:
        nonColisionTravel = i/float(steps)*toTravel
    else:
        nonColisionTravel = toTravel

    return bBump, toTravel, nonColisionTravel, bOutOfScreen

def calcSpriteBounceDir( ts , s ):
    """ts sprite to bounce
    s obstacle sprite
    .move() must be mov_diag"""
    #for robustness the entire plane is partitioned in five regions:
    #the diagonals of sprite target grows to the infinite. points over the
    #diagonals are one region, the interior of each rotated quadrant are the
    #others. Then, sprite to bounce is asigned the region of its center.
    #Each region has an obvious meaning of tell bounce dir.
    #diagonals are:
    #   y= s.height/s.width(x-s.x)+ s.y
    #   y=-s.height/s.width(x-s.x)+ s.y+s.height
    # note: if minOverlap is refined to (minOverlap_x,minOverlap_y) then
    #       corrections will be needed
    #       algoritms that revert one or more components of veldir proven not
    #       robust.

    cx = ts.x+ts.width/2.
    cy = ts.y+ts.height/2.

    u = s.height/float(s.width)*(cx-s.x)
    d1 =  u + s.y - cy
    d2 = -u + s.y+s.height -cy
    dbgPrint( 'sb', g_devflags['F5'], "d1=",d1,"   d2=",d2)
    if abs(d1)<0.3 or abs(d2)<0.3:
        #into diagonals
        if s.x+s.width/2.<cx:
            ts.bounceDir[0]= 1
            if s.y+s.height/2.<cy:
                ts.bounceDir[1]= 1
            else:
                ts.bounceDir[1]=-1
        else:
            ts.bounceDir[0]=-1
            if s.y+s.height/2.<cy:
                ts.bounceDir[1]= 1
            else:
                ts.bounceDir[1]=-1
    else:
        #not in diagonals
        if d1>0:
            if d2>0:
                ts.bounceDir[1]=-1
                ts.bounceDir[0]=ts.veldir[0]
            else:
                ts.bounceDir[0]=1
                ts.bounceDir[1]=ts.veldir[1]
        else:
            if d2>0:
                ts.bounceDir[0]=-1
                ts.bounceDir[1]=ts.veldir[1]
            else:
                ts.bounceDir[1]= 1
                ts.bounceDir[0]=ts.veldir[0]

class PhysicsStoneSprite(AnimatedSprite):
    """ non living entities
    visual aspect must be near round, to facilitate colision detection"""
    def __init__(self, level, x, y, w, h, animations,radius, veldir,
                 fasteness, collisionTable=[], dvy=0., bounceFactor=1, subgroup="global"):
        AnimatedSprite.__init__(self, x, y, w, h, animations)
        self.level = level
        self.radius = radius
        self.veldir = veldir
        self.fasteness = fasteness
        if fasteness<0:
            self.move = mov_0
        elif veldir[0] and veldir[1]:
            self.move = mov_diagonal
        elif veldir[0]:
            self.move = mov_h
        else:
            self.move = mov_v

        self.subgroup = subgroup
        self.bounceFactor = bounceFactor
        self.dvy = dvy
        dbgPrint( 'sb', g_devflags['F5'], "##################### in constructor phstones: dvy=",self.dvy)
        self.collisionTable = collisionTable

        self.moving = fasteness>0
        self.tubed = False
        self.falling = False
        self.bounceDir = None

    def hack_info_vel(self): #must be NOP.
        pass

    def physics(self):
        maxBounces = 4
        x0 = self.x
        y0 = self.y
        r = self.radius
        dvy = self.dvy
        if dvy:
            dt = 1.0
            toTravel = 0.5*dvy + self.fasteness*self.veldir[1]
            if toTravel<0:
                toTravel = -toTravel
        else:
            toTravel = self.fasteness
        while toTravel and maxBounces:
            maxBounces -= 1
            dbgPrint( 'sb', g_devflags['F5'], "@@@@@@@@@@@@@@ maxBounces=",maxBounces)
            bBump, toTravel, nonColisionTravel, bOutOfScreen = self.move(self,toTravel)
            dbgPrint( 'sb', g_devflags['F5'],"    bBump=",bBump,"   toTravel=",toTravel,"  nonColisionTravel=",nonColisionTravel)
            maxTravel, bGenStuck, tl = getSpritesTouched( self, nonColisionTravel )
            dbgPrint( 'sb', g_devflags['F5'],"   maxTravel=",maxTravel,"   bGenStuck=",bGenStuck)
            x1 = x0 + maxTravel*self.veldir[0]
            y1 = y0 + maxTravel*self.veldir[1]
            self.x = x1; self.y=y1
            self.rect.x=x1; self.rect.y=y1
            #update toTravel, and fasteness if grav
            if not dvy:
                toTravel -= maxTravel
            else:
                if toTravel<=maxTravel:
                    used_dt = dt
                else:
                    used_dt = dt*maxTravel/toTravel
                    if used_dt<0:
                        used_dt = -used_dt
                dt -= used_dt
                if self.veldir[1]>0:
                    self.fasteness += used_dt*dvy
                else:
                    self.fasteness -= used_dt*dvy
                    if self.fasteness<0:
                        self.fasteness = -self.fasteness
                        self.veldir[1]=1
                toTravel = (0.5*dvy+self.fasteness*self.veldir[1])*dt
                if toTravel<0 :
                    toTravel = -toTravel
                if toTravel<1.e-6:
                    toTravel = 0
            dbgPrint( 'sb', g_devflags['F5'],"     decremented toTravel=",toTravel)

            x0=x1; y0=y1
            if bOutOfScreen:
                bOutOfScreen = ( x1+self.width<0 or x1>self.level.width or
                                 y1+self.height<0 or y1>self.level.height )

            #handle world colisions
            if nonColisionTravel==maxTravel:
                if bBump:
                    toTravel = self.OnWorldCollision(self,toTravel)
                    tl=[] # at the risk of loosing some touch, empty the list
                          # and let the next pass detect the touchs ( reason:
                          # bounce after bounce of world colision does bad -->
                          #UPDATE: badiness untested-unanalized for this version)

            #process all sprite touch
            for freeTravel, minOverlap, bStop,bStuck, collideGroup, spriteTouched,\
                                     self_action, inflict_action in tl:
                dbgPrint( 'sb', g_devflags['F5'],"@@@", self_action )
                if self_action =="bounceSelf" or self_action=="bounceBoth":
                    spriteTouched.hack_info_vel()
                    dbgPrint( 'sb', g_devflags['F5'], "bounce; veldir=[ %d , %d ]"%(self.veldir[0],self.veldir[1]))

                    #get bounce direction for self
                    if not(self.veldir[0] and self.veldir[1]):
                        self.bounceDir = [-self.veldir[0],-self.veldir[1]]
                    else:
                        calcSpriteBounceDir( self , spriteTouched )
                    dbgPrint( 'sb', g_devflags['F5'], "   bounceDir=[ %d , %d ]"%(self.bounceDir[0],self.bounceDir[1]))

                    #if not bounceBoth must handle the 'chase' case
                    if self_action=="bounceSelf":
                        fasteness = self.fasteness
                        #code can be added to reduce fasteness when rev chase
                        if (self.bounceDir[0] and
                            self.bounceDir[0]==spriteTouched.veldir[0] and
                            self.fasteness<spriteTouched.fasteness):
                            fasteness = spriteTouched.fasteness
                        if (self.bounceDir[1] and
                            self.bounceDir[1]==spriteTouched.veldir[1] and
                            self.fasteness<spriteTouched.fasteness):
                            fasteness = spriteTouched.fasteness
                        #adjust to travel after the bounce
                        #NOTE: maybe bounceFactor must be handled here, before
                        #the toTravel adjust
                        if ( toTravel and
                             ( fasteness!=self.fasteness
                               or (dvy and self.veldir[1]!=self.bounceDir[1]))
                             ):
                            if dvy:
                                dt = toTravel/(0.5*dvy+self.fasteness*self.veldir[1])
                                toTravel = (0.5*dvy+fasteness*self.bounceDir[1])*dt
                                if toTravel<0:
                                    toTravel = -toTravel
                            else:
                                if self.fasteness>1.e-6:
                                    toTravel *= fasteness/self.fasteness
                                else:
                                    toTravel = fasteness
                        self.fasteness = fasteness

                    else: #"bounceBoth" , untested
                        #'bounce' direction for spriteTouched, simetrical to bounceSelf
                        if isinstance( spriteTouched,PhysicsStoneSprite ):
                            if not(spriteTouched.veldir[0] and spriteTouched.veldir[1]):
                                spriteTouched.bounceDir = [-spriteTouched.veldir[0],-spriteTouched.veldir[1]]
                            else:
                                calcSpriteBounceDir( spriteTouched, self )
                                collide_bounce( spriteTouched , 0)
                        else:
                            #old style physycs sprite; they only move h or v
                            # TODO
                            pass
                        #spriteTouched.doAction("afterBeBounced")

                    toTravel = collide_bounce(self,toTravel)
                    dbgPrint( 'sb', g_devflags['F5'],"   after bounce toTravel=",toTravel)
### note: maybe the else must catch self_action=='atach'
                else:
                    self.doAction(self_action)
                spriteTouched.doAction(inflict_action)
            #good, all sprite touchs procesed
            if bOutOfScreen:
                self.kill()
                return
        #tryied to move k-times
        if toTravel:
            dbgPrint( 'sb', g_devflags['F5'], "@@@probably stuck-crushed. toTravel=",toTravel)


    def doAction(self,action):
        if action=='die':
            self.kill()

# probably we must add detection of "crushed"
