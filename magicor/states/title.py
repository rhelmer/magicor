"""
All title-like (intros, level selection, etc) states are here.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import math, warnings, random, os
import pygame

from magicor import Text
from magicor.level import Level
from magicor.resources import ResourceNotFound
from magicor.states import MenuState, BaseState
from magicor.states.play import PlayState
from magicor.states.options import MainOptionsState
from magicor.sprites.lights import Sun
from magicor.sprites.decorations import WalkingPenguin
from magicor.sprites import AnimationGroup

class TitleState(MenuState):

    def __init__(self, config, data, screen, startMusic = True):
        MenuState.__init__(self,
                           config, data,
                           screen,
                           [("play",
                             LevelSelectState,
                             config, data, screen),
                            ("Options",
                             MainOptionsState,
                             config, data, screen, self),
                            ("Quit", None),
                            ]
                           )
        self.eyecandy = self.config.getBool("eyecandy")
        self.resources.addResources("sprites/")
        self.angle = 0
        self.rippleAngle = 0
        self.logo = self.resources.loadImage("images/magicor", False)
        self.logoSurface = pygame.Surface(
            (800, self.logo.get_height() + 128), pygame.HWSURFACE, 32)
        self.sky = self.resources.loadImage("images/title-sky", False)
        self.ice = self.resources.loadImage("images/title-ice", False)        
        self.ice.set_colorkey(0)
        self.clouds = self.resources.loadImage("images/title-clouds", False)
        self.cloudX = 0
        self.shutter = 16
        self.sun = AnimationGroup()
        self.lights = AnimationGroup()
        self.sun.add(Sun(368, 100, self.lights))
        x = -32
        for i in xrange(10):
            self.lights.add(WalkingPenguin(x, 450, 550, self.ice))
            x -= random.randint(32, 128)
        self.lights.sort(lambda a, b: cmp(a.y, b.y))
        if self.logo:
            self.distRect = pygame.Rect((0, 0, 1, self.logo.get_height()))
        if startMusic:
            self.resources.playMusic("music/soft-trance")
                                     
    def control(self):
        if self.controls.escape:
            self.setNext(None)
        MenuState.control(self)
        
    def run(self):
        self.control()
        if self.eyecandy:
            self.screen.blit(self.sky, (0, 0))
            self.sun.update()
            self.sun.draw(self.screen)
            self.screen.blit(self.clouds, (self.cloudX, 0))
            self.screen.blit(self.clouds, (self.cloudX -  800, 0))
            self.cloudX = (self.cloudX + 1) % 800
            self.screen.blit(self.ice, (0, 250))
            self.lights.update()
            self.lights.draw(self.screen)
        else:
            self.screen.blit(self.sky, (0, 0))
            self.screen.blit(self.ice, (0, 250))
        if self.logo:
            if self.eyecandy:
                self.logoSurface.set_colorkey(None)
                self.logoSurface.fill(0)
                angle = self.angle
                middle = self.logoSurface.get_width() / 2 \
                         - self.logo.get_width() / 2
                for x in xrange(self.logo.get_width()):
                    self.distRect.left = x
                    y = 64 * math.sin(math.radians(angle))
                    self.logoSurface.blit(self.logo,
                                          (middle + x, 64 + y),
                                          self.distRect)
                    angle = (angle + 1) % 360
                angle = self.rippleAngle
                for y in xrange(256):
                    x = 64 * math.sin(math.radians(angle))
                    self.logoSurface.set_colorkey(0)
                    self.screen.blit(self.logoSurface,
                                     (x, y),
                                     (0, y, 800, 1))
                    angle = (angle + 0.8) % 360
                self.angle = (self.angle + 1.5) % 360
                self.rippleAngle = (self.rippleAngle + 1.5) % 360
            else:
                self.screen.blit(self.logo,
                                 (400 - self.logo.get_width() / 2, 40))
        self.renderMenu(260, self.screen)
        if self.shutter > 0:
            for y in xrange(0, 600, 32):
                for x in xrange(0, 800, 32):
                    self.screen.fill(0, (x + 16 - self.shutter,
                                         y + 16 - self.shutter,
                                         self.shutter * 2,
                                         self.shutter * 2))
            self.shutter -= 1


class LevelSelectState(BaseState):
    NUM_OPTIONS = 3

    def __init__(self, config, data, screen):
        BaseState.__init__(self, config, data, screen)
        self.resources.addResources("tiles/")
        self.levels = []
        self.eyecandy = self.config.get("eyecandy")
        self.selected = 0
        self.top = 0
        self.resources.setDefaultTile(
            self.resources[self.config["default_tile"]])
        self.scaleAngle = 0
        self.selectDelay = 0
        self.loaded = False
        self.shadeSurface = pygame.Surface((screen.get_width(),
                                            screen.get_height()),
                                           pygame.HWSURFACE, 32)
        self.shadeSurface.fill(0)
        self.shadeSurface.set_alpha(64)
        self.renderSurface = pygame.Surface((640, 576), pygame.HWSURFACE, 32)
        self.renderSurface.set_colorkey(0)
        self.scrollAngle = 0
        self.screen.fill(0)
        self.rotoAngle = 0
        self.text = Text(self.screen, self.resources["fonts/info"])
        self.levelPaths = {}
        for path, levelInfo in self.resources.loadLevelData():
            for filename, data in levelInfo:
                theme = os.path.dirname(filename[len(path):])[1:]
                if not theme.startswith("_") or config.get("devmode"):
                    level = Level(data)
                    level.theme = theme or None
                    self.levels.append(level)
                    self.levelPaths[level] = path + filename
        self.levels.sort(lambda x, y:
                         cmp(x.theme, y.theme)
                         or cmp(x.title, y.title))
	#start possibly at a level never tried
	for i in xrange(len(self.levels)):
		if (not self.config.getInt("time_"+self.levels[i].title)):
			self.selected = i
			break
        if self.data.lastLevelFinished:
            for i in xrange(len(self.levels)):
                if (self.levels[i].id == self.data.lastLevelFinished
                    and i < len(self.levels) - 1):
                    self.selected = (i + 1) % len(self.levels)
                    break
        elif self.data.lastLevel:
            for i in xrange(len(self.levels)):
                if self.levels[i].id == self.data.lastLevel:
                    self.selected = i
                    break
        if config.getBool("music"):
            self.resources.playMusic("music/menu")
        self.updateInfo()
        
    def control(self):
        if self.controls.escape:
            self.setNext(TitleState(self.config, self.data, self.screen))
            self.resources.stopMusic()
            self.controls.clear()
        elif self.controls.start or self.controls.action:
            self.resources.stopMusic()
            self.resources.playSound("samples/start")
            self.setNext(PlayState(self.config,
                                   self.data,
                                   self.screen,
                                   self.levels[self.selected],
                                   LevelSelectState))
        elif self.controls.up:
            self.resources.playSound("samples/menu")
            self.selected = (self.selected - 1) % len(self.levels)
            self.loaded = False
            self.selectDelay = 2
            self.updateInfo()
        elif self.controls.down:
            self.resources.playSound("samples/menu")
            self.loaded = False
            self.selected = (self.selected + 1) % len(self.levels)
            self.selectDelay = 2
            self.updateInfo()

    def updateInfo(self):
        rendered = False
        while not rendered and self.levels:
            if self.levels:
                try:
                    if not self.loaded:
                        self.resources.clearLevelResources()
                        lp = self.levelPaths[self.levels[self.selected]]
                        self.resources.addLevelResources(lp)
                        self.loaded = True
                    if self.selected < 0:
                        self.selected = len(self.levels) - 1
                    elif self.selected >= len(self.levels):
                        self.selected = 0
                    self.data.lastLevel = self.levels[self.selected].id
                    self.renderLevel(self.renderSurface)
                    rendered = True
                except (ValueError, ResourceNotFound), e:
                    warnings.warn("Unable to init level-Resource not found: %s"%e)
                    del self.levels[self.selected]

    def run(self):
        if self.selectDelay:
            self.selectDelay -= 1
        else:
            self.control()
        width, height = self.screen.get_width(), self.screen.get_height()
        if self.levels:
            if self.eyecandy:
                scale = 0.8 + 0.2 * math.sin(math.radians(self.scaleAngle))
                self.scaleAngle = (self.scaleAngle + 5) % 360
                sf = pygame.transform.rotozoom(
                    self.renderSurface,
                    4 * math.sin(math.radians(self.rotoAngle)),
                    scale)
                sf.set_colorkey(0)
                self.screen.blit(
                    sf,
                    (int(self.screen.get_width() / 2 - 320 * scale),
                     int(self.screen.get_height() / 2 - 288 *scale)))
                self.rotoAngle = (self.rotoAngle + 1) % 360
                self.screen.blit(self.shadeSurface, (0, 0))
                dx = 4 * math.cos(math.radians(self.scrollAngle))
                dy = 4 * math.sin(math.radians(self.scrollAngle))
                self.screen.blit(self.shadeSurface, (dx, dy)) ##@@
                self.scrollAngle = (self.scrollAngle + 3) % 360
            # end eyecandy section
            else:
                self.screen.fill(0)
                self.screen.blit(self.renderSurface, (80, 0))
            for i in xrange(self.selected - self.NUM_OPTIONS,
                            self.selected + self.NUM_OPTIONS):
                y = 128 + (i - self.selected) * self.text.font.get_height()
                if i == self.selected:
                    self.text.font = self.resources["fonts/info"]
                else:
                    self.text.font = self.resources["fonts/info-inactive"]
                if i >= 0 and i < len(self.levels):
			if (self.config.getInt("time_"+self.levels[i].title)):
				time = self.config.getInt("time_"+self.levels[i].title)
				minutes, seconds = divmod(time, 60)
				self.text.draw(self.levels[i].title+" ("+str(minutes)+"m"+str(seconds)+"s)", 0, y)
			else:
				self.text.draw(self.levels[i].title, 0, y)

            self.text.font = self.resources["fonts/info"]
            #self.text.draw("difficulty %s"
            #               %(self.levels[self.selected].difficulty or "not set"), 0, 268,
            #               False)
            self.text.draw("Credits %s"
                           %self.levels[self.selected].credits, 0, 300)
            if self.levels[self.selected].description:
                self.text.draw(self.levels[self.selected].description, 0, 400)
        else:
            self.screen.fill(0)
            self.text.draw("Error: no levels found!", 0, 0)

    def renderLevel(self, surface):
        level = self.levels[self.selected]
        surface.fill(0)
        for y in xrange(level.height):
            for x in xrange(level.width):
                v = level[x, y]
                if v and v != "!":
                    resource = self.resources.getTile("%s"%v)
                    surface.blit(resource,
                                 (x * 32, y * 32), (0, 0, 32, 32))
        for sprite in level.sprites:
            v, offset, w, h = None, 0, 32, 32
            x, y = sprite.x, sprite.y
            if sprite.name == "tube":
                v = "sprites/tube-endings"
                if sprite.args.startswith("up"):
                    offset = 1
                elif sprite.args.startswith("down"):
                    offset = 2
                elif sprite.args.startswith("right"):
                    offset = 3
                w, h = 32, 32
            elif sprite.name == "ice":
                v = "sprites/ice-normal"
                if sprite.args == "connect-left":
                    offset = 5
                elif sprite.args == "connect-right":
                    offset = 6
                elif sprite.args == "connect":
                    offset = 7
                else:
                    offset = 4
                w, h = 32, 32
            elif sprite.name == "fire":
                v = "sprites/fire-normal"
                w, h = 32, 32
            elif sprite.name == "player":
                v = "sprites/player-penguin"
                w, h = 32, 32
                if sprite.args == "left":
                    offset = 3
            elif sprite.name in ("walking-enemy", "climbing-enemy"):
                spl = sprite.args.split(" ", 3)
                if len(spl) == 4:
                    v = spl[1]
                    if spl[0] == "left":
                        offset = 3
                    s = int(spl[3])
            elif sprite.name == "stationary-enemy":
                spl = sprite.args.split(" ", 3)
                if len(spl) == 4:
                    v = spl[1]
                    offset = ["up", "left", "down", "right"].index(spl[0]) * 4
            elif sprite.name == "lava":
                w, h = 32, 64                
                offset = sprite.args == "dormant" and 4 or 0
                v = "sprites/lava"
            elif sprite.name == "decoration":
                spl = sprite.args.split(" ", 3)
                v = spl[0]
                w, h ,s = (int(s) for s in spl[1:])
            elif sprite.name == "direction":
                v = "sprites/arrow"
                offset = ["right", "down", "left", "up"].index(sprite.args)
            elif sprite.name == "trapola":
                w, h = 32, 32    
                v = "sprites/trapola2_q"
            elif sprite.name == "ball":
                w, h = 8, 8
                v = "sprites/ball_b"
            if v:
                surface.blit(self.resources["%s"%v],
                             (x * 32, y * 32),
                             (offset * w, 0, w, h))
