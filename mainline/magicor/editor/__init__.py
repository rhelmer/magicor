"""
A very simple level editor.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import copy
import warnings
import os
from magicor.level import Level
from magicor.editor.brushes import *

class EditorException(Exception):
    """
    Raised by Magicor-specific exceptions caught in the Editor instance.
    """

class Editor(object):
    VERSION = "1.0"
    SUPPORTED_IMAGES = ("png", "jpg", "gif")
    SUPPORTED_SOUND = ("wav", ".au")
    SUPPORTED_MUSIC = ("ogg", "mod", ".xm")

    def __init__(self, config, loadfile = None):
        self.config = config
        self.undos = []
        self.maxUndos = config.get("maxUndos", 16)
        self.paths = ["~/.magicor", config.get("data_path", "data")]
        self.level = Level()
        self.saved = None
        self.setDefaultBrushes()
        if loadfile:
            self.level = self.loadLevel(loadfile)
            self.saved = loadfile

    def pushUndo(self):
        if self.level:
            if len(self.undos) >= self.maxUndos:
                self.undos = self.undos[1 + len(self.undos) - self.maxUndos:]
            self.undos.append(copy.deepcopy(self.level))

    def popUndo(self):
        if self.undos:
            self.level = self.undos.pop()

    def loadLevel(self, filename):
        self.pushUndo()
        try:
            f = file(filename)
            data = f.read()
            f.close()
        except IOError as ioe:
            raise EditorException(ioe)
        self.saved = filename
        return Level(data)

    def saveLevel(self, filename, level = None):
        if not level:
            level = self.level
        output = "# Generated by Magicor-LevelEditor %s\n%s"%(self.VERSION,
                                                              level)
        f = file(filename, "w")
        f.write(output)
        f.close()
        self.saved = filename

    def getImageFilename(self, resource):
        return self.getFilename(resource, self.SUPPORTED_IMAGES)

    def getFilename(self, resource, types_):
        for path in self.paths + ["%s%slevels"%(p, os.path.sep)
                                  for p in self.paths]:
            name = "%s%s%s"%(path, os.path.sep, resource)
            resourcePath = resource.split("/")
            altname = "%s%s%s%s_%s"%(path,
                                     os.path.sep,
                                     "/".join(resourcePath[:-1]),
                                     os.path.sep,
                                     resourcePath[-1])
            for type_ in types_:
                fn = "%s.%s"%(name, type_)
                altfn = "%s.%s"%(altname, type_)
                if os.path.isfile(fn):
                    return fn
                elif os.path.isfile(altfn):
                    return altfn
        return None

    def _loadBrushes(self, paths):
        ret = []
        for path in paths:
            fn = "%s/brushes"%path
            if os.path.isfile(fn):
                f = file(fn)
                data = f.read()
                f.close()
                ret += self._parseBrushes(data)
        return ret

    def loadBrushes(self):
        ret = []
        paths = [] + self.paths
        levelPaths = ["%s%slevels"%(p, os.path.sep)
                      for p in self.paths]
        for lp in levelPaths:
            if os.path.isdir(lp):
                for f in os.listdir(lp):
                    if not f.startswith("."):
                        fn = "%s/%s"%(lp, f)
                        if os.path.isdir(fn):
                            paths.append(fn)
        return self._loadBrushes(paths)
                
    def _parseBrushes(self, data):
        ret = []
        data = data.replace("\r", "")
        for line in (s.strip() for s in data.split("\n")):
            spl = line.split(" ")
            if len(spl) == 2 and spl[0] == "tile":
                ret.append(TileBrush(spl[1]))
            elif len(spl) == 4 and spl[0] == "walking-enemy":
                ret.append(WalkingEnemyBrush(spl[1],
                                             spl[2],
                                             "right",
                                             int(spl[3])))
            elif len(spl) == 4 and spl[0] == "climbing-enemy":
                ret.append(ClimbingEnemyBrush(spl[1],
                                              spl[2],
                                              "up",
                                              int(spl[3])))
            elif len(spl) == 4 and spl[0] == "stationary-enemy":
                ret.append(StationaryEnemyBrush(spl[1],
                                                spl[2],
                                                "up",
                                                int(spl[3])))
            elif len(spl) == 4 and spl[0] == "decoration":
                ret.append(DecorationBrush(spl[1],
                                           int(spl[2]),
                                           int(spl[3]),
                                           8))
        return ret

    def setDefaultBrushes(self):
        self.brushes = [EraseBrush(),
                        PlayerBrush(),
                        FireBrush(),
                        IceBrush(),
                        IceBrush("connect"),
                        IceBrush("connect-left"),
                        IceBrush("connect-right"),
                        LavaBrush(),
                        TubeBrush("left"),
                        TubeBrush("up"),
                        TubeBrush("right"),
                        TubeBrush("down"),
                        DirectionBrush("right"),
                        TrapolaBrush()
                        ] + self.loadBrushes()

    def clear(self):
        self.pushUndo()
        self.saved = None
        self.level = Level()

    def saveConfig(self):
        fn = "%s/magicor-editor.conf"%self.config.get("user_path",
                                                      "~/.magicor")
        self.config.saveFile(fn)
        
