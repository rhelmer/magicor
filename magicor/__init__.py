"""
The main magicor package.

Contains the base types for sprites, maps and the
game itself.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import os, warnings, textwrap

from pygame.locals import *
import pygame, pygame.image, pygame.sprite,  pygame.mixer
from pygame.mixer import music

from magicor.resources import getResources

_CONFIG = None
g_groups = {}
g_printkeys = {}
g_devflags = { "F5":False, "F6":False, "F7":False ,"F8":False }

def toggle_devflag( key ):
    global g_devflags
    if g_devflags.has_key(key):
        g_devflags[key] = not g_devflags[key]

def dbgPrint(key,cond,*args):
    global g_printkeys
    if cond and g_printkeys.has_key(key):
        print args

def parse_printkeys(s):
    global g_printkeys
    kl=s.split(":")
    for k in kl:
        g_printkeys[k]=True
        print "In parse printkeys: found key:>%s<"%k

def set_group(key, val):
    global g_groups
    g_groups[key]=val

class Text(object):
    TEXT_INDEX = "abcdefghijklmnopqrstuvwxyz0123456789.,!?"

    def __init__(self, surface, font, maxWidth = None):
        self.setSurface(surface, maxWidth)
        self.setFont(font)

    def setSurface(self, surface, maxWidth = None):
        self.surface = surface
        if maxWidth:
            self.maxWidth = maxWidth
        else:
            self.maxWidth = surface.get_width()
        
    def setFont(self, font):
        self.font = font
        self.width = self.font.get_width() / len(self.TEXT_INDEX)
        self.height = self.font.get_height()

    def getWidth(self, s):
        width = self.font.get_width() / len(self.TEXT_INDEX)
        return width * len(s)

    def draw(self, s, x, y, wrap = True):
        s = s.lower()
        srcr = pygame.Rect((0, 0,
                            self.width,
                            self.height))
        if wrap:
            ss = textwrap.wrap(s, self.maxWidth / self.width)
        else:
            ss = [s]
        yy = y
        for l in ss:
            xx = x
            for c in l:
                i = self.TEXT_INDEX.find(c)
                if i >= 0:
                    srcr.left = i * self.width
                    self.surface.blit(self.font, (xx, yy), srcr)
                xx += self.width
                if xx - x >= self.maxWidth:
                    break
            yy += self.height

class State(object):
    """
    A state does something in a game's run-method.
    It can animate a title, run a map, show a movie, etc.
    """
    def __init__(self, config):
        self.config = config
        self._next = self

    def setNext(self, next):
        self._next = next

    def run(self):
        raise NotImplementedError()

    def eventJoystick(self):
        pass

    def eventQuit(self, event):
        self._next = None

    def next(self):
        return self._next

    def eventKeyDown(self, event):
        print event
        pass

    def eventKeyUp(self, event):
        pass

    def control(self):
        raise NotImplementedError()
    

class Controls(object):

    def __init__(self, keys, joystick, numAxes, numButtons):
        self.keys = keys
        self.joystick = joystick
        self.joyStates = {}
        for i in xrange(numAxes):
            self.joyStates["axis %d"%i] = None
        for i in xrange(numButtons):
            self.joyStates["button %d"%i] = 0
        self.button = None
        self.keyUp = False
        self.keyDown = False
        self.keyLeft = False
        self.keyRight = False
        self.keyAction = False
        self.keyEscape = False
        self.keyStart = False
        self.joyUp = False
        self.joyDown = False
        self.joyLeft = False
        self.joyRight = False
        self.joyAction = False
        self.joyEscape = False
        self.joyStart = False
        self.joyState = None

    def setKey(self, key):
        if key and self.keys.has_key(key):
            setattr(self, self.keys[key], True)
        self.key = key

    def unsetKey(self, key):
        if key and self.keys.has_key(key):
            setattr(self, self.keys[key], False)
        self.key = None

    def _setAxes(self, key, pos, neg):
        self.joyState = None
        if self.joystick.has_key("%s neg"%key):
            setattr(self, self.joystick["%s neg"%key], neg)
        if self.joystick.has_key("%s pos"%key):
            setattr(self, self.joystick["%s pos"%key], pos)

    def setAxis(self, axis, value):
        key = "axis %d"%axis
        if self.joyStates[key] != value:
            self._setAxes(key, value > 0, value < 0)
            self.joyStates[key] = value
            if value < 0:
                self.joyState = "%s neg"%key
            elif value > 0:
                self.joyState = "%s pos"%key
            else:
                self.joyState = None

    def setButton(self, button, value):
        key = "button %d"%button
        if self.joyStates[key] != value:
            if self.joystick.has_key(key):
                setattr(self, self.joystick[key], bool(value))
            self.joyStates[key] = value
            if value:
                self.joyState = key

    def clear(self, value = False):
        for control in self.keys.values() + self.joystick.values():
            if control:
                setattr(self, control, value)
        self.key = None
        self.joyState = None

    @property
    def up(self):
        return self.keyUp or self.joyUp

    @property
    def down(self):
        return self.keyDown or self.joyDown

    @property
    def left(self):
        return self.keyLeft or self.joyLeft

    @property
    def right(self):
        return self.keyRight or self.joyRight

    @property
    def action(self):
        return self.keyAction or self.joyAction

    @property
    def escape(self):
        return self.keyEscape or self.joyEscape

    @property
    def start(self):
        return self.keyStart or self.joyStart

class GameEngine(object):
    """
    The base gametype initializes PyGame, sets up a display, loads
    resources and handles map and sprites. (everything)
    To make the code more readable (and possible more reusable), subclass
    and write events and handling somewhere else.
    """

    def __init__(self, config = {}):
        self.byFrame = False
        self.doFrame = True
        pygame.display.init()
        pygame.display.set_caption("Magicor")
        pygame.mouse.set_visible(False)
        for k in ("sound", "joystick", "music", "eyecandy"):
            if not config.has_key(k):
                config[k] = 1
            if (not config.has_key(k)
                or config.getInt(k) < 0
                or config.getInt(k) > 100):
                config[k] = 100
        if config.getBool("sound") or config.getBool("music"):
            try:
                pygame.mixer.init(44100, -16, True, 4096)
                pygame.mixer.set_num_channels(8)
            except pygame.error, e:
                warnings.warn("unable to init audio; %s"%e)
                config["sound"] = 0
                config["music"] = 0
        if config.getBool("joystick", True):
            pygame.joystick.init()
        fullscreen = config.getBool("fullscreen", False) and pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(
            (800, 600),
             pygame.DOUBLEBUF
            | pygame.HWSURFACE
            | fullscreen,
            32
            )
        self.config = config
        paths = []
        paths.append(config.get("user_path", "~/.magicor"))
        paths.append(config.get("data_path", "data"))
        if not self.config.has_key("default_tile"):
            self.config["default_tile"] = "tiles/stone"
        self.resources = getResources(paths=paths,
                                      sound=config.getBool("sound"),
                                      music=config.getBool("music"))
        self.resources.soundVol = self.config.getInt("sound_vol")
        self.resources.musicVol = self.config.getInt("music_vol")
        self.clock = pygame.time.Clock()

    def handleEvents(self, state, events):
        if events:
            for event in events:
                if ( self.config.get("devmode", False)
                     and event.type == pygame.KEYDOWN ):
                    self.doFrame = True
                    if event.key==pygame.K_F11:
                        self.byFrame = not self.byFrame
                    if event.key==pygame.K_F5:
                        toggle_devflag("F5")
                    if event.key==pygame.K_F6:
                        toggle_devflag("F6")
                    if event.key==pygame.K_F7:
                        toggle_devflag("F7")
                    if event.key==pygame.K_F8:
                        toggle_devflag("F8")
                        
                en = "event%s"%pygame.event.event_name(event.type)
                f = getattr(state, en, None)
                if callable(f):
                    f(event)

    def start(self, state):
        self.doFrame = True
        while state:
            if self.byFrame:
                self.doFrame = False
            self.handleEvents(state, pygame.event.get())
            state.eventJoystick()
            if self.doFrame:
                state.run()
                pygame.display.flip()
            self.clock.tick(25)
            state = state.next()
        

class ConfigDict(dict):

    def __init__(self, d = {}):
        dict.__init__(self, d)

    @classmethod
    def parse(cls, s):
        d = cls()
        lc = 1
        lines = s.replace("\r", "").split("\n")
        for line in lines:
            if not line.strip().startswith("#"):
                spl = [ss.strip() for ss in line.split("=", 1)]
                if len(spl) == 2:
                    if spl[1].strip():
                        try:
                            d[spl[0]] = int(spl[1])
                        except ValueError:
                            d[spl[0]] = spl[1]
                    else:
                        d[spl[0]] = None
                elif line:
                    warnings.warn("invalid stuff in config on line %d"%lc)
            lc += 1
        return d

    @classmethod
    def parseFile(cls, filename):
        filename = os.path.normpath(
            os.path.abspath(
            os.path.expanduser(
            os.path.expandvars(filename))))
        try:
            f = file(filename)
            data = f.read()
            f.close()
            return cls.parse(data)
        except IOError, ie:
            warnings.warn("error loading config '%s'; %s"%(filename, ie))
        return None

    def serialize(self):
        ret = []
        for k, v in self.items():
            if v is None:
                ret.append("%s ="%k)
            else:
                ret.append("%s = %s"%
                           (k,
                            str(v).replace("\r", "").replace("\n", "")))
        ret.sort()
        return "%s\n"%"\n".join(ret)

    def getBool(self, key, default = False):
        if not self.has_key(key):
            return default
        if str(self.get(key)).strip().lower() in ("false", "0", "no"):
            return False
        return True

    def getInt(self, key, default = 0):
        if not self.has_key(key):
            return default
        try:
            return int(self.get(key, default))
        except ValueError:
            pass
        return 0

    def saveFile(self, filename):
        filename = os.path.normpath(
            os.path.abspath(
            os.path.expanduser(
            os.path.expandvars(filename))))        
        if not os.path.isdir(os.path.dirname(filename)):
            os.mkdir(os.path.dirname(filename))
        try:
            f = file(filename, "w")
            f.write(self.serialize())
            f.close()
        except IOError, ie:
            warnings.warn("error writing config '%s'; %s"%(filename, ie))
        print "saved config %s"%filename


def getConfig(paths = ["."]):
    global _CONFIG
    if not _CONFIG:
        _CONFIG = ConfigDict()
        done = []
        for path in paths:
            if not path in done:
                path = os.path.normpath(
                    os.path.expandvars(os.path.expanduser(path)))
                c = ConfigDict.parseFile(path)
                if c:
                    _CONFIG.update(c)
                done.append(path)
    return _CONFIG
