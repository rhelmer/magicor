"""
Contains level parsing and handling types.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""

import warnings, md5

_SORT = ["player", "lava", "decoration", "ice", "fire", "tube"]

class DataParser(object):

    def __init__(self, data = None):
        if data:
            self.parse(data)

    def handle(self, command, rest, lc):
        pass

    def parse(self, data):
        lines = data.replace("\r", "").split("\n")
        lc = 1
        for line in lines:
            if line.strip():
                spl = [l.strip() for l in line.split(" ", 1)]
                if not spl[0].startswith("#"):
                    if len(spl) == 2:
                        command, rest = spl
                        self.handle(command, rest, lc)
                    else:
                        warnings.warn("invalid data on lin %d"%lc)
            # end line-empty test
            lc += 1


class LevelSprite(object):

    def __init__(self, x, y, name, args):
        self.x = x
        self.y = y
        self.name = name
        self.args = args
        try:
            self._sort = _SORT.index(name)
        except ValueError:
            self._sort = 99999

    def __str__(self):
        if self.args != None:
            return "sprite %d %d %s %s"%(self.x, self.y,
                                         self.name, self.args)
        return "sprite %d %d %s"%(self.x, self.y, self.name)


class Level(DataParser):
    DIFFICULTIES = ("easy", "normal", "hard")

    def __init__(self, data = None):
        DataParser.__init__(self)
        if data:
            id_ = md5.new()
            id_.update(data)
            self.id = id_.hexdigest()
        else:
            self.id = None
        self.width = 20
        self.height = 18
        self.title = None
        self.credits = None
        self.description = None
        self.hint = None
        self.difficulty = None
        self.shadows = True
        self.theme = None
        self.background = None
        self.music = None
        self.sprites = []
        self.tiles = None
        if data:
            self.parse(data)
        if not self.tiles:
            self.clearTiles()

    def clearTiles(self):
        self.tiles = []
        for i in xrange(self.height):
            self.tiles.append([None] * self.width)

    def handle(self, command, rest, lc):
        if command == "title":
            self.title = rest
        elif command == "description":
            self.description = rest
        elif command == "shadows":
            r = rest.strip().lower()
            if r in ("false", "no", "0"):
                self.shadows = False
            else:
                self.shadows = True
        elif command == "credits":
            self.credits = rest
        elif command == "hint":
            self.hint = rest
        elif command == "difficulty":
            if rest in self.DIFFICULTIES:
                self.difficulty = rest
            else:
                self.difficulty = None
        elif command == "background":
            spl = rest.split("/")
            self.background = rest
        #elif command == "width":
        #    try:
        #        self.width = int(rest)
        #    except ValueError:
        #        self.width = 20
        #        warnings.warn("invalid width, setting to %d"%self.width)
        elif command == "music":
            self.music = rest
        #elif command == "height":
        #    try:
        #        self.height = int(rest)
        #    except ValueError:
        #        self.height = 18
        #        warnings.warn("invalid height, setting to %d"%self.height)
        elif command == "tile":
            if not self.tiles:
                self.clearTiles()
            spl = rest.split(" ", 2)
            if len(spl) == 3:
                try:
                    x = int(spl[0])
                except ValueError:
                    x = 0
                    warnings.warn("tile on row %d has non-integer X pos"%lc)
                try:
                    y = int(spl[1])
                except ValueError:
                    y = 0
                    warnings.warn("tile on row %d has non-integer Y pos"%lc)
                name = spl[2].strip()
                self[x, y] = name
            else:
                warnings.warn("tile on row %d has invalid arguments, ignoring"%lc)
        elif command == "sprite":
            spl = rest.split(" ", 3)
            if len(spl) >= 3:
                try:
                    x = int(spl[0])
                except ValueError:
                    x = 0
                    warnings.warn("sprite on row %d has non-integer X pos"%lc)
                try:
                    y = int(spl[1])
                except ValueError:
                    y = 0
                    warnings.warn("sprite on row %d has non-integer Y pos"%lc)
                if len(spl) > 3:
                    self.sprites.append(LevelSprite(x,
                                                    y,
                                                    spl[2].strip(),
                                                    spl[3].strip()))
                else:
                    self.sprites.append(LevelSprite(x, y, spl[2].strip(),
                                                    None))
            else:
                warnings.warn("sprite on row %d has invalid arguments, ignoring"%lc)
        # no matching commands
        else:
            warnings.warn("unknown command '%s' on row %d"%(command, lc))
            
    def __getitem__(self, v):
        try:
            return self.tiles[v[1]][v[0]]
        except IndexError:
            raise IndexError("coordinate (%d, %d) out of range"%v)

    def __setitem__(self, v, value):
        try:
            self.tiles[v[1]][v[0]] = value
        except IndexError:
            raise IndexError("coordinate (%d, %d) out of range"%v)

    def _sortSprites(self, a, b):
        if a.name != b.name:
            return cmp(a.name, b.name)
        if a.x != b.x:
            return cmp(a.x, b.x)
        return cmp(a.y, b.y)

    def __str__(self):
        output = ["title %s"%(self.title or ""),
                  "credits %s"%(self.credits or ""),
                  "description %s"%(self.description or ""),
                  "hint %s"%(self.hint or ""),
                  "",
                  "background %s"%(self.background or ""),
                  "music %s"%(self.music or ""),
                  "shadows %d"%(self.shadows and 1 or 0),
                  ""]
        if self.tiles:
            oldLen = len(output)
            for row in xrange(self.height):
                for col in xrange(self.width):
                    if self[col, row]:
                        output.append("tile %d %d %s"%
                                      (col, row, self[col, row]))
            if oldLen != len(output) and self.sprites:
                output.append("")
        if self.sprites:
            self.sprites.sort(self._sortSprites)
            for sprite in self.sprites:
                output.append("%s"%sprite)
        return "\n".join(output)
