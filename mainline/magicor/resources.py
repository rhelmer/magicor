"""
Handles a singleton resources instance.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import os
import pygame.image
import pygame.mixer
from pygame.mixer import music

_RESOURCES = None

class ResourceNotFound(Exception):

    def __init__(self, resourceKey):
        Exception.__init__(self, resourceKey)
        self.resource = resourceKey


class Resources(object):
    """
    Resource managing class. Caches all resources found in the
    sticky attribute. (second, optional init argument)
    Ommiting or passing None to the sticky argument means all are sticky.
    """
    SUPPORTED_IMAGES = ("png", "jpg", "gif")
    SUPPORTED_MUSIC = ("ogg", "mp3", "mod", "xm")
    SUPPORTED_SOUNDS = ("wav",)
    SUPPORTED_FILES = SUPPORTED_IMAGES + SUPPORTED_MUSIC + SUPPORTED_SOUNDS

    def __init__(self, paths, sound, music):
        self.sound = sound
        self.joystick = None
        self.music = music
        self.soundVol = 100
        self.musicVol = 100
        self.lastMusic = None
        self.paths = [
            os.path.normpath(
            os.path.abspath(
            os.path.expanduser(
            os.path.expandvars(path)))) for path in paths]
        self._resources = {}
        self._defaultTile = None
        self._level = {}
        print("resources using paths: %s"%", ".join(paths))

    def __getitem__(self, key):
        if key in self._level:
            return self._level[key]
        elif key in self._resources:
            return self._resources[key]
        raise ResourceNotFound(key)

    def get(self, key, default = None):
        if key in self._resources:
            return self._resources[key]
        elif key in self._level:
            return self._level[key]
        return default

    def findAlternative(self, path, name, suffixes):
        name1 = name
        spl = name.split('/')
        name2 = "%s%s_%s"%(os.path.sep.join(spl[:-1]), os.path.sep, spl[-1])
        for suffix in suffixes:
            fn1 = "%s%s%s.%s"%(path, os.path.sep, name1, suffix)
            fn2 = "%s%s%s.%s"%(path, os.path.sep, name2, suffix)
            if os.path.isfile(fn1):
                return fn1
            elif os.path.isfile(fn2):
                return fn2
        return None

    def _loadImage(self, path, name):
        fn = self.findAlternative(path, name, self.SUPPORTED_IMAGES)
        if fn:
            return pygame.image.load(fn)
        return None

    def _loadMusic(self, path, name):
        if self.music:
            fn = self.findAlternative(path, name, self.SUPPORTED_MUSIC)
            if fn:
                music.load(fn)
                return fn
        return None

    def _loadSound(self, path, name):
        if self.sound:
            fn = "%s%s%s.wav"%(path, os.path.sep, name)
            if os.path.isfile(fn):
                return pygame.mixer.Sound(fn)
        return None

    def loadData(self, filename):
        f = open(filename)
        data = f.read()
        f.close()
        return data

    def has_key(self, key):
        return key in self._resources

    def clear(self, prefix = None):
        if prefix:
            for d in (self._resources, self._level):
                for k in list(d.keys()):
                    if k.startswith(prefix):
                        del d[k]
        else:
            print("resources cleared")
            self._resources = {}
            self._level = {}

    def _loadSomething(self, name, loadFunc, keep):
        for path in self.paths + ["%s%slevels"%(p, os.path.sep)
                                  for p in self.paths]:
            ret = loadFunc(path, name)
            if ret:
                if keep:
                    self._resources[name.replace(os.path.sep, "/")] = ret
                return ret
        return None

    def loadImage(self, name, keep = True):
        return self._loadSomething(name, self._loadImage, keep)

    def playMusic(self, name, loop=-1):
        if self._loadSomething(name, self._loadMusic, False):
            music.set_volume(self.musicVol * 0.01)
            music.play(loop)
        self.lastMusic = name

    def stopMusic(self):
        if pygame.mixer.get_init():
            music.stop()

    def loadSound(self, name, keep):
        return self._loadSomething(name, self._loadSound, keep)

    def _addResources(self, ret, path, prefix = None):
        if prefix:
            while prefix.endswith('/'):
                prefix = prefix[:-1]
            p = "%s%s%s"%(path, os.path.sep, prefix)
        else:
            p = path
        p = p.replace("/", os.path.sep)
        print("using path %s"%p)
        if os.path.isdir(p):
            for f in os.listdir(p):
                if (os.path.isfile("%s%s%s"%(p, os.path.sep, f))
                    and f[:-4] not in ret
                    and not f[:-4].startswith("_")):
                    if f[:-4].startswith("_"):
                        f = f[1:-4]
                    if prefix:
                        name = "%s%s%s"%(prefix, '/', f[:-4])
                    else:
                        name = f[:-4]
                    if f[-3:] in self.SUPPORTED_IMAGES:
                        r = self._loadImage(path, name)
                    elif f[-3:] in self.SUPPORTED_SOUNDS:
                        r = self._loadSound(path, name)
                    else:
                        r = None
                    name = name.replace(os.path.sep, "/")
                    if r and name not in ret:
                        ret[name] = r
                        if self._resources == ret:
                            print("loaded resource '%s'"%name)
                        else:
                            print("loaded level resource '%s'"%name)
        return ret

    def playSound(self, key):
        if self.sound:
            self[key].set_volume(self.soundVol * 0.01)
            self[key].play()

    def addResources(self, prefix = None):
        for path in self.paths:
            self._addResources(self._resources, path, prefix)

    def addLevelResources(self, filename):
        path = os.path.dirname(filename)
        s = path.split(os.sep)
        d = os.sep.join(s[:-1])
        pre = s[-1]
        self._addResources(self._level, d, pre)
        for p in ("%s%slevels"%(s, os.path.sep) for s in self.paths):
            self._addResources(self._level, p, pre)

    def clearLevelResources(self):
        self._level = {}

    def _loadLevelData(self, path, recurse = True):
        ret = []
        if os.path.isdir(path):
            for f in os.listdir(path):
                fn = "%s%s%s"%(path, os.path.sep, f)
                if os.path.isfile(fn) and f.endswith(".lvl"):
                    data = self.loadData(fn)
                    if data:
                        ret.append((fn, data))
                elif os.path.isdir(fn) and recurse:
                    ret += self._loadLevelData(fn, False)
        return ret

    def setDefaultTile(self, surface):
        self._defaultTile = surface

    def getTile(self, name):
        return self.get(name, self._defaultTile)

    def loadLevelData(self):
        ret = []
        for path in ("%s%slevels"%(p, os.path.sep) for p in self.paths):
            print("searching levels in path %s"%path)
            levelInfo = self._loadLevelData(path)
            if levelInfo:
                ret.append((path, levelInfo))
        return ret

    def getJoystick(self, num):
        if not self.joystick:
            self.joystick = pygame.joystick.Joystick(num)
            self.joystick.init()
        return self.joystick

    def __str__(self):
        return str(self._resources)

def getResources(**kwargs):
    global _RESOURCES
    if not _RESOURCES:
        _RESOURCES = Resources(kwargs.get("paths", ["data"]),
                               kwargs.get("sound", 1),
                               kwargs.get("music", 1))
    return _RESOURCES
