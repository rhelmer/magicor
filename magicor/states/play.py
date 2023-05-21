"""
All in-game states are defined here.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import pygame, time, os, warnings
from pygame.mixer import music

from magicor import Text, set_group
from magicor.resources import ResourceNotFound
from magicor.states import MenuState, BaseState, ErrorState
from magicor.states.options import MainOptionsState
from magicor.sprites import AnimationGroup
from magicor.sprites.blocks import BlocksGroup, Ice, NormalIce
from magicor.sprites.world import Lava, Tube, Trapola
from magicor.sprites.fires import Fire
from magicor.sprites.player import Player
from magicor.sprites.stones import Ball
from magicor.sprites.decorations import Decoration
from magicor.sprites.enemies import (WalkingEnemy,
                                     ClimbingEnemy,
                                     StationaryEnemy)
from magicor.sprites.misc import Direction

class PlayMenuState(MenuState):

    def __init__(self, config, data, screen, play):
        MenuState.__init__(self,
                           config, data,
                           screen,
                           [("retry", PlayState, config, data, screen,
                             play.level, play.previous, False),
                            ("options", MainOptionsState,
                             config, data, screen, self),
                            ("level selection",
                             play.previous, config, data, screen),
                            ("quit", None)
                            ]
                           )
        self.play = play
        self.source = pygame.Surface(self.screen.get_size())
        self.source.blit(self.screen, (0, 0))
        for y in range(0, self.screen.get_height(), 2):
            self.source.fill(0, (0, y, self.screen.get_width(), 1))
        for x in range(0, self.screen.get_width(), 2):
            self.source.fill(0, (x, 0, 1, self.screen.get_height()))
        self.resources.playSound("samples/menu")

    def control(self):
        if self.controls.escape:
            self.play.setNext(self.play)
            self.setNext(self.play)
            self.controls.clear()
        MenuState.control(self)

    def run(self):
        self.control()
        self.screen.blit(self.source, (0, 0))
        self.renderMenu(200)

    def next(self):
        return self._next

class PlayState(BaseState):

    def __init__(self, config, data, screen, level, previous,
                 restartMusic = True):
        BaseState.__init__(self, config, data, screen)
        self.resources.addResources("sprites/")
        self.resources.addResources("sounds/")
        self.resources.setDefaultTile(
            self.resources[self.config["default_tile"]])
        self.level = level
        self.blocks = BlocksGroup()
        set_group( 'blocks', self.blocks )
        self.decorations = AnimationGroup()
        self.fires = AnimationGroup()
        set_group( 'fires', self.fires )
        self.world = AnimationGroup()
        set_group( 'world', self.world )
        self.lights = AnimationGroup()
        self.enemies = AnimationGroup()
        set_group( 'enemies', self.enemies )
        self.players = AnimationGroup()
        set_group( 'players', self.players )
        self.stones = AnimationGroup()
        set_group( 'stones', self.stones )
        self.hudSprites = AnimationGroup()
        self.starting = 17
        self.startTime = time.time()
        self.ending = 0
        self.player = None
        self.text = Text(self.screen, self.resources["fonts/info"])
        self.scroller = pygame.Surface(
            (screen.get_width() + self.text.width, self.text.height),
            pygame.HWSURFACE, 32)
        self.text.setSurface(self.scroller)
        self.renderSurface = pygame.Surface((level.width * 32,
                                             level.height * 32),
                                            pygame.HWSURFACE, 32)
        self.scroller.set_colorkey(0)
        self.scroller.fill(0)
        self.scrollText = "welcome to %s, good luck!    "%self.level.title
        self.scrollIndex = 0
        self.previous = previous
        self.background = None
        if level.background:
            self.background = self.resources.loadImage("%s"%level.background,
                                                       False)
        self.levelSurface = pygame.Surface((level.width * 32,
                                            level.height * 32),
                                           pygame.HWSURFACE, 32)
        try:
            self.initializeSprites()
            self.renderLevel(self.levelSurface)
            if (config.getBool("music")
                and self.level.music
                and restartMusic):
                self.resources.playMusic("%s"%self.level.music, -1)
        except (ValueError, ResourceNotFound) as e:
            warnings.warn("unable to init level: %s"%e)

            self.setNext(ErrorState(config, data, screen,
                                    "error loading level",
                                    self.previous))


    def initializeSprites(self):
        for s in self.level.sprites:
            x, y, name, arg = s.x, s.y, s.name, s.args
            if name == "player":
                self.player = Player(x * 32, y * 32,
                                     self.level,
                                     self.players,
                                     self.blocks,
                                     self.fires,
                                     self.world,
                                     self.lights,
                                     self.enemies,
                                     self.config.getBool("eyecandy"))
                if arg == "left":
                    self.player.setAnimation("stand-left")
                self.players.add(self.player)
            elif name.startswith("ice"):
                ice = NormalIce(x * 32,
                                y * 32,
                                self.level,
                                self.blocks,
                                self.lights,
                                self.players,
                                self.enemies,
                                self.config.getBool("eyecandy"))
                if arg == "connect":
                    ice.addConnections()
                elif arg == "connect-left":
                    ice.addConnections(-1)
                elif arg == "connect-right":
                    ice.addConnections(1)
            elif name == "lava":
                ##->@@spitting lava modifications
                bSpiting = False
                t=None
                if arg is None:
                    bDormant=False
                else:
                    spl=arg.split(' ')
                    if  spl[0]=='dormant':
                        bDormant=True
                    else:
                        bSpiting=True
                        bDormant=bool(spl[0]=='spit_dorm')
                        if len(spl)<2: t=16
                        else: t = int(spl[3])
                self.world.add(Lava(x * 32, y * 32,
                                    self.blocks,
                                    self.players,
                                    self.fires,
                                    self.world,
                                    bDormant,
                                    bSpiting,
                                    t))
                ##<-@@spitting lava modifications
            elif name == "fire":
                self.fires.add(Fire(x * 32, y * 32,
                                    self.level,
                                    self.blocks,
                                    self.lights,
                                    self.players,
                                    arg != "nofall"))
            elif name == "tube":
                spl = arg.split(" ", 1)
                if len(spl) < 1:
                    raise ValueError("tube sprites require direction and "
                                     "optional name arguments")
                elif len(spl) == 2:
                    name = spl[1]
                else:
                    name = None
                tube = Tube(x * 32, y * 32,
                            self.level,
                            spl[0], name,
                            self.blocks,
                            self.world,
                            self.players)
                self.world.add(tube)
                self.level[x, y] = "!"
            elif name == "decoration":
                spl = arg.split(" ", 3)
                if len(spl) < 4:
                    raise ValueError("decoration sprites requires resource, "
                                     "width, height and speed arguments")
                self.decorations.add(
                    Decoration(spl[0],
                               x * 32, y * 32,
                               int(spl[1]),
                               int(spl[2]),
                               int(spl[3].strip()))
                    )
            elif name in ("walking-enemy", "climbing-enemy"):
                spl = arg.split(" ", 3)
                if len(spl) != 4:
                    raise ValueError("walking/climbing-emeny sprites requires "
                                     "direction, image resource, sound "
                                     "resource and speed "
                                     "arguments")
                s = int(spl[3])
                if name.startswith("walking"):
                    type_ = WalkingEnemy
                else:
                    type_ = ClimbingEnemy
                self.enemies.add(type_(x * 32, y * 32,
                                       spl[0],
                                       spl[1],
                                       spl[2],
                                       s,
                                       self.level,
                                       self.blocks,
                                       self.players,
                                       self.fires,
                                       self.world))
            elif name == "stationary-enemy":
                spl = arg.split(" ", 3)
                if len(spl) != 4:
                    raise ValueError("stationary-emeny sprites requires "
                                     "direction, image resource, "
                                     "sound resource "
                                     "and trigger period")
                t = int(spl[3])
                self.enemies.add(StationaryEnemy(x * 32, y * 32,
                                                 spl[0],
                                                 spl[1],
                                                 spl[2],
                                                 t,
                                                 self.level,
                                                 self.blocks,
                                                 self.players,
                                                 self.fires,
                                                 self.world))
            elif name == "ball":
                 bReadOk, direction, fasteness, dvy = Ball.parse(arg)
                 if bReadOk:
                     self.stones.add(Ball(self.level, x*32, y*32,direction,fasteness,dvy))

            elif name == "trapola":
                self.world.add(Trapola(x*32,y*32-1))
                if not self.level[x,y]:
                    #TODO: put a suitable tile if empty - at this time level
                    #designers should put a tile behind the trapola
                    self.level[x, y] = "!"

            elif name == "direction":
                self.hudSprites.add(Direction(x * 32, y * 32, arg))
        if not self.player:
            raise ValueError("no player on level")

    def shouldRender(self, x, y):
        v = self.level[x, y]
        if v and v != "!":
            return v
        return None

    def renderLevel(self, surface):
        if self.background:
            w, h = self.background.get_width(), self.background.get_height()
            for y in range(0, 576, h):
                for x in range(0, 640, w):
                    surface.blit(self.background, (x, y))
            surface.fill(0, (0, 576, 640, 64))
        else:
            surface.fill(0)
        for y in range(self.level.height):
            for x in range(self.level.width):
                if self.shouldRender(x, y):
                    if self.level.shadows:
                        surface.blit(
                            self.resources["tiles/shadow"], (x * 32, y * 32))
                    surface.blit(self.resources.getTile("%s"%self.level[x, y]),
                                 (x * 32, y * 32), (0, 0, 32, 32))
                elif (x > 0 and y > 0
                      and self.shouldRender(x - 1, y)
                      and self.shouldRender(x, y - 1)):
                    surface.blit(
                        self.resources.getTile("%s"%self.level[x - 1, y]),
                        (x * 32, y * 32),
                        (32, 0, 32, 32))
                elif (x < self.level.width - 1
                      and y > 0
                      and self.shouldRender(x + 1, y)
                      and self.shouldRender(x, y - 1)):
                    surface.blit(
                        self.resources.getTile("%s"%self.level[x + 1, y]),
                        (x * 32, y * 32),
                        (64, 0, 32, 32))
                elif (x < self.level.width - 1
                      and y < self.level.height - 1
                      and self.shouldRender(x + 1, y)
                      and self.shouldRender(x, y + 1)):
                    surface.blit(
                        self.resources.getTile("%s"%self.level[x + 1, y]),
                        (x * 32, y * 32),
                        (96, 0, 32, 32))
                elif (x > 0
                      and y < self.level.height - 1
                      and self.shouldRender(x - 1, y)
                      and self.shouldRender(x, y + 1)):
                    surface.blit(
                        self.resources.getTile("%s"%self.level[x - 1, y]),
                        (x * 32, y * 32),
                        (128, 0, 32, 32))
        for s in self.world.sprites():
            if isinstance(s, Tube):
                self.renderSurface.blit(
                    self.resources["tiles/shadow"], (s.x, s.y))

    def drawScroller(self):
        if (self.scrollIndex % 8 == 0
            and self.scrollIndex / 8 < len(self.scrollText)):
            self.text.draw(self.scrollText[self.scrollIndex // 8],
                           800, 0, False)
        self.scrollIndex += 1
        if self.scrollIndex > len(self.scrollText) * 8:
            self.scrollIndex = 0
            played = int(time.time() - self.startTime)
            hours, minutes = divmod(played, 3600)
            minutes, seconds = divmod(minutes, 60)
            self.scrollText = "%s, %02dh %02dm %02ds.    "%(
                self.level.title,
                hours,
                minutes,
                seconds)
        self.scroller.set_colorkey(None)
        self.scroller.blit(self.scroller,
                           (0, 0),
                           (3, 0, self.scroller.get_width() - 3,
                            self.scroller.get_height()))
        self.scroller.set_colorkey(0)
        self.screen.blit(self.scroller,
                         (0, self.screen.get_height() - self.text.height))

    def control(self):
        if self.controls.escape:
            self.setNext(PlayMenuState(self.config,
                                       self.data,
                                       self.screen,
                                       self))
            self.controls.clear()
        elif self.controls.left:
            self.player.goLeft()
        elif self.controls.right:
            self.player.goRight()
        elif self.controls.down:
            self.player.goDown()
        elif self.controls.up:
            self.player.goUp()
        elif self.controls.action:
            self.player.manipulateIce()
            self.controls.clear()

    def run(self):
        self.screen.fill(0)
        if self.starting > 0 or self.ending < 0:
            if self.starting > 0:
                self.starting -= 1
                v = self.starting
            if self.ending < 0:
                self.ending += 1
                v = 16 + self.ending
                if self.ending == 0:
                    if self.player._finished:
                        this_time = int(time.time() - self.startTime)
                        if "time_"+self.level.title in self.config:
                            best_time = min(self.config.getInt("time_"+self.level.title), this_time)
                        else:
                            best_time = this_time
                        print("best time for "+self.level.title+" is "+str(best_time))
                        self.config["time_"+self.level.title] = best_time
                        fn = "%s/magicor.conf"%self.config.get("user_path", "~/.magicor")
                        self.config.saveFile(fn)

                        self._next = self.previous(
                                        self.config,
                                        self.data,
                                        self.screen)
                    else:
                        self._next = PlayState(self.config,
                                                self.data,
                                                self.screen,
                                                self.level,
                                                self.previous,
                                                False)
                    return
            self.renderSurface.blit(self.levelSurface, (0, 0))
            self.fires.animate()
            self.fires.draw(self.renderSurface)
            self.enemies.draw(self.renderSurface)
            self.world.animate()
            self.lights.update()
            self.lights.draw(self.renderSurface)
            self.blocks.draw(self.renderSurface)
            self.players.draw(self.renderSurface)
            self.world.draw(self.renderSurface)
            self.stones.draw(self.renderSurface)
            self.decorations.animate()
            self.decorations.draw(self.renderSurface)
            self.hudSprites.update()
            self.hudSprites.draw(self.renderSurface)
            self.screen.blit(self.renderSurface, (80, 16))
            self.drawScroller()
            for y in range(0, self.screen.get_height(), 32):
                self.screen.fill(0,
                                 (0,
                                  y + 16 - v,
                                  self.screen.get_width(),
                                  v * 2)
                                 )
        else:
            if ((not self.player.alive()
                 or (self.player._finished and self.player.isDone()))
                 and not self.ending):
                self.ending = -17
            elif (not self.player._finished and self.fires.count() == 0
                  and not self.player.dead):
                self.player.finished()
                self.data.lastLevelFinished = self.level.id
            self.renderSurface.blit(self.levelSurface, (0, 0))
            self.fires.update()
            self.fires.draw(self.renderSurface)
            self.players.update()
            self.enemies.update()
            self.enemies.draw(self.renderSurface)
            self.world.update()
            self.blocks.update()
            self.stones.update()
            self.blocks.draw(self.renderSurface)
            self.players.draw(self.renderSurface)
            self.world.draw(self.renderSurface)
            self.decorations.update()
            self.decorations.draw(self.renderSurface)
            self.stones.draw(self.renderSurface)
            if self.config.get("eyecandy"):
                self.lights.update()
                self.lights.draw(self.renderSurface)
            self.hudSprites.update()
            self.hudSprites.draw(self.renderSurface)
            self.screen.blit(self.renderSurface, (80, 16))
            self.drawScroller()
            self.control()
