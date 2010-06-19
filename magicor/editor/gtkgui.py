"""
GTK frontend for the editor.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import math
import os
import gc
import gtk
from gtk import glade

from magicor.editor import Editor, EditorException
from magicor.level import Level, LevelSprite
from magicor.editor.brushes import *


class GtkLevel(gtk.DrawingArea):

    def __init__(self, level, menuCallback = None):
        gtk.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.POINTER_MOTION_MASK
                        | gtk.gdk.BUTTON_PRESS_MASK
                        | gtk.gdk.BUTTON_RELEASE_MASK)
        self._brushes = {}
        self._render = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                      True, 8, 640, 576)
        self._background = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                          True, 8, 640, 576)
        self.bgFile = None
        self._scaledRender = None
        self.brush = None        
        self.connect("expose-event", self.expose)
        self.connect("motion-notify-event", self.pointerMove)
        self.connect("button-press-event", self.pointerPress)
        self.connect("button-release-event", self.pointerRelease)
        self.connect("size-allocate", self.sizeAllocate)
        self._drawing = False
        self._moving = None
        self.setLevel(level)
        self._menuCallback = menuCallback
        self._selected = None
        self.grid = False
        self.updateBackground(None)

    def updateBackground(self, pixbuf):
        if pixbuf:
            width, height = pixbuf.get_width(), pixbuf.get_height()
            for y in xrange(0, 576, height):
                for x in xrange(0, 640, width):
                    if x >= 640 or y >= 576:
                        return # no point in continuing.
                    if x + width >= 640:
                        w = 640 - x
                    else:
                        w = width
                    if y + height >= 576:
                        h = 576 - y
                    else:
                        h = height
                    pixbuf.copy_area(0, 0, w, h,
                                     self._background, x, y)
        else:
            self._background.fill(0x000000ff)

    def _spritesSorting(self, a, b):
        return cmp(a._sort, b._sort)

    def setLevel(self, level):
        self._level = level
        self.redraw()

    def setBrush(self, key, brush):
        self._brushes[key] = brush

    def _getBrushKeyName(self, name, args):
        if name == "ice":
            key = "ice%s"%(args and " %s"%args or "")
        elif name.endswith("-enemy"):
            argsv = args.split(" ")
            key = "%s %s %s"%(name, argsv[1], argsv[2])
        elif name == "decoration":
            argsv = args.split(" ")
            key = "%s %s"%(name, argsv[0])
        else:
            key = "%s"%name
        return key

    def getBrushCopy(self, name, args):
        key = self._getBrushKeyName(name, args)
        if self._brushes.has_key(key):
            brush = self._brushes[key].copy()            
            brush.update(args)
            return brush
        return None

    def renderBrush(self, x, y, brush):
        if isinstance(brush, EraseBrush):
            self._level[x, y] = None
            for sprite in self.getSprites(x, y):
                br = self.getBrushCopy(sprite.name, sprite.args)
                if br:
                    w = int(math.ceil(br.width / 32.0))
                    h = int(math.ceil(br.height / 32.0))
                    self.render(sprite.x - 1, sprite.y - 1, w + 1, h + 1)
                    del br
                self._level.sprites.remove(sprite)
        elif isinstance(brush, TileBrush):
            self._level[x, y] = "%s"%brush
        elif isinstance(brush, SpriteBrush):            
            for sprite in self.getSprites(x, y):
                if brush.name == sprite.name:
                    self._level.sprites.remove(sprite)
            spl = str(brush).split(" ", 1)
            name = spl[0]
            args = len(spl) > 1 and " ".join(spl[1:]) or None
            self._level.sprites.append(LevelSprite(x, y, name, args))
        self._level.sprites.sort(self._spritesSorting)
        if brush:
            w = int(math.ceil(brush.width / 32.0))
            h = int(math.ceil(brush.height / 32.0))
        else:
            w, h = 1, 1
        if w < 1:
            w = 1
        if h < 1:
            h = 1
        self.render(x - 1, y - 1, w + 1, h + 1)

    def pixbufRectangle(self, pixbuf, pixel, rectangle = None):
        width, height =  pixbuf.get_width(), pixbuf.get_height()
        if rectangle:
            if rectangle.x < 0:
                rectangle.x = 0
            elif rectangle.x >= width:
                rectangle.x = width - 1
            if rectangle.y < 0:
                rectangle.y = 0
            elif rectangle.y >= height:
                rectangle.y = height - 1
            if rectangle.x + rectangle.width >= width:
                rectangle.width = width - rectangle.x - 1
            if rectangle.y + rectangle.height >= height:
                rectangle.height = height - rectangle.y - 1
        else:
            rectangle = (0, 0, width, height)
        if (rectangle.x >= 0 and rectangle.y >= 0
            and rectangle.width > 0 and rectangle.height > 0):
            sub = pixbuf.subpixbuf(rectangle.x, rectangle.y,
                                   rectangle.width, rectangle.height)
            sub.fill(pixel)
            del sub

    def render(self, x, y, w = 1, h = 1):
        if w < 1:
            w = 1
        if h < 1:
            h = 1
        if x < 0:
            x = 0
        elif x > 20:
            x = 20
        if y < 0:
            y = 0
        elif y > 18:
            y = 18
        if x + w > 20:
            w =  20 - x
        if y + h > 18:
            h =  18 - y        
        self._background.copy_area(x * 32, y * 32,
                                   w * 32, h * 32,
                                   self._render,
                                   x * 32, y * 32)
        for yy in xrange(y, y + h):
            for xx in xrange(x, x + w):
                if xx >= 0 and yy >= 0 and xx < 20 and yy < 18:
                    v = self._level[xx, yy]
                    if v and v != "!" and self._brushes.has_key("tile %s"%v):
                        brush = self._brushes["tile %s"%v]
                        brush.pixbuf.copy_area(
                            brush.width * brush.offset, 0,
                            brush.width, brush.height, self._render,
                            xx * 32, yy * 32)
        for s in self._level.sprites:
            brush = self.getBrushCopy(s.name, s.args)
            if brush:
                bw = brush.width / 32
                bh = brush.height / 32
                if bw < 1:
                    bw = 1
                if bh < 1:
                    bh = 1
            if (brush
                and s.x + bw - 1 >= x and s.x < x + w
                and s.y + bh - 1 >= y and s.y < y + h):
                width, height = brush.width, brush.height
                left, top = brush.left, brush.top
                xx, yy = s.x * 32 + left, s.y * 32 + top
                if (xx >= 0 and yy >= 0
                    and xx < self._render.get_width()
                    and yy < self._render.get_height()):
                    if xx + width >= self._render.get_width():
                        width = self._render.get_width() - xx
                    if yy + height >= self._render.get_height():
                        height = self._render.get_height() - yy
                    if height > 0 and width > 0:
                        sub = brush.pixbuf.subpixbuf(
                            brush.width * brush.offset, 0, width, height)
                        sub.composite(
                            self._render, # dest pixbuf
                            xx, yy, # destination pos
                            width, height, # dest geometry
                            xx, yy, # offset
                            1.0, 1.0, # scale
                            gtk.gdk.INTERP_NEAREST, # interpolation
                            255 # overall alpha
                            )
                        del sub
                del brush
        self.unsetScaled()

    def convertToMatrix(self, px, py):
        width, height = self.window.get_size()
        fx = width / float(self._render.get_width())
        fy = height / float(self._render.get_height())
        return int(px / (fx * 32)), int(py / (fy * 32)), fx, fy

    def unsetScaled(self):
        del self._scaledRender        
        self._scaledRender = None

    def scaleRender(self, width, height):
        if not self._scaledRender:
            self._scaledRender = self._render.scale_simple(
                width, height, gtk.gdk.INTERP_NEAREST)
        return self._scaledRender

    def getSprites(self, x, y):
        return self._getSprites(x, y, False)

    def getSprite(self, x, y):
        return self._getSprites(x, y, True)
    
    def _getSprites(self, x, y, single = True):
        ret = []
        for s in self._level.sprites:
            key = self._getBrushKeyName(s.name, s.args)
            brush = self._brushes.get(key)
            if brush:
                w, h = brush.width / 32, brush.height / 32
                if w < 1:
                    w = 1
                if h < 1:
                    h = 1
                if (x >= s.x and y >= s.y
                    and x < s.x + w
                    and y < s.y + h):
                    if single:
                        return s
                    else:
                        ret.append(s)
        return single and None or ret

    def updateSprite(self, args):
        if self._selected:
            for s in self._level.sprites:
                if s.x == self._selected.x and s.y == self._selected.y:
                    s.args = args
                    self.render(s.x - 1, s.y - 1, 2, 2)
                    self.queue_draw()
                    return

    def draw(self, px, py, brush):
        x, y, fx, fy = self.convertToMatrix(px, py)
        if brush:
            bw, bh = brush.width, brush.height
        else:
            bw, bh = 32, 32
        width, height = self.window.get_size()
        if isinstance(brush, PlayerBrush):
            for sprite in self._level.sprites:
                if sprite.name == "player":
                    self.renderBrush(sprite.x, sprite.y, EraseBrush())
            self.renderBrush(x, y, brush)
            self.queue_draw_area(0, 0, width, height)
        else:
            self.renderBrush(x, y, brush)
            self.queue_draw_area(0, 0, width, height)

    def redraw(self):
        self.render(0, 0, 20, 18)
        self.queue_draw()
        
    def sizeAllocate(self, widget, event):
        self.redraw()

    def expose(self, widget, event):
        width, height = widget.window.get_size()
        area = event.area
        if area.x < 0:
            area.x = 0
        if area.y < 0:
            area.y = 0
        if area.x >= width:
            area.x = width - 1
        if area.y >= height:
            area.y = height - 1
        if area.x + area.width >= width:
            area.width = width - area.x
        if area.y + area.height >= height:
            area.height = height - area.y
        sr = self.scaleRender(width, height)
        ctx = widget.style.fg_gc[gtk.STATE_NORMAL]
        widget.window.draw_rectangle(ctx, True, area.x, area.y,
                                     area.width, area.height)
        widget.window.draw_pixbuf(ctx, sr,
                                  area.x, area.y,
                                  area.x, area.y, area.width, area.height)
        if self.grid:
            ctx = widget.style.bg_gc[gtk.STATE_NORMAL]
            width, height = self.window.get_size()
            fx = width / float(self._render.get_width())
            fy = height / float(self._render.get_height())
            for yy in xrange(18):
                widget.window.draw_lines(ctx,
                                         ((0, int(yy * 32 * fy)),
                                          (width, int(yy * 32 * fy))))
            for xx in xrange(20):
                widget.window.draw_lines(ctx,
                                         ((int(xx * 32 * fx), 0),
                                          (int(xx * 32 * fx), height)))

    def pointerMove(self, widget, event):
        if self._drawing:
            self.draw(event.x, event.y, self.brush)
        elif self._moving:
            x, y, fx, fy = self.convertToMatrix(event.x, event.y)
            if x >= 0 and y >= 0 and x < 20 and y < 18:
                oldX, oldY = self._moving.x, self._moving.y
                key = self._getBrushKeyName(self._moving.name,
                                            self._moving.args)
                if self._brushes.has_key(key):
                    w = int(math.ceil(self._brushes[key].width / 32.0))
                    h = int(math.ceil(self._brushes[key].height / 32.0))
                else:
                    w, h = 1, 1
                if w < 1:
                    w = 1
                if h < 1:
                    h = 1
                self._moving.x = x
                self._moving.y = y
                self.render(oldX - 1, oldY - 1, w + 1, h + 1)
                self.render(x - 1, y - 1, w + 1, h + 1)
                width, height = self.window.get_size()
                self.queue_draw_area(0, 0, width, height)
    
    def pointerPress(self, widget, event):
        if event.button == 1:
            x, y, fx, fy = self.convertToMatrix(event.x, event.y)
            sprite = self.getSprite(x, y)
            if (self.brush                
                and (isinstance(self.brush, (EraseBrush, TileBrush))
                     or not sprite or sprite.name != self.brush.name)):
                self._drawing = True
                self._moving = False
                self.draw(event.x, event.y, self.brush)
            else:
                self._moving = sprite
                self._drawing = False
            self._selected = None
        elif event.button == 3 and self._menuCallback:
            x, y, fx, fy = self.convertToMatrix(event.x, event.y)
            sprite = self.getSprite(x, y)
            self._moving = None
            self._drawing = False
            if sprite:
                self._selected = sprite
                self._menuCallback(sprite)
            else:
                self._selected = None
        else:
            self._drawing = False
            self._selected = None
            self._moving = None

    def pointerRelease(self, widget, event):
        self._drawing = False
        self._moving = None
        

class GtkEditor(Editor):
    MODE_NONE = 0
    MODE_DRAW = 1
    MODE_SELECT = 2

    def __init__(self, config, loadfile = None):
        Editor.__init__(self, config, loadfile)
        gladeFile = "%s/editor/magicor-editor.glade"%config.get("data_path", "data")
        try:
            self.glade = glade.XML(gladeFile)
        except RuntimeError, re:
            raise RuntimeError("%s; glade file %s"%(re, gladeFile))
        self.glade.signal_autoconnect(self)
        if loadfile:
            self.setTitle(os.path.basename(loadfile))
        self.propertiesDialogs = [("PlayerDialog", None),
                                  ("FireDialog", None),
                                  ("IceDialog", None),
                                  ("TubeDialog", None),
                                  ("WalkingEnemyDialog", None),
                                  ("ClimbingEnemyDialog", None),
                                  ("StationaryEnemyDialog", None),
                                  ("DecorationDialog", None),
                                  ("DirectionDialog", None),
                                  ]
        for deletable, menu in [("PalletteDialog", "MenuPallette"),
                                ("AboutDialog", None),
                                ("ScrollToolDialog", None),
                                ("PreferencesDialog", None),
                                ("ErrorDialog", None),
                                ("OpenDialog", None),
                                ("SaveDialog", None),
                                ("SettingsDialog", "MenuSettings"),
                                ] + self.propertiesDialogs:
            if menu:
                menuWidget = self.glade.get_widget(menu)
            else:
                menuWidget = None
            self.glade.get_widget(deletable).connect(
                "delete-event", self.on_dialogs_delete_event, menuWidget)
            self.glade.get_widget(deletable).connect(
                "close", self.on_dialogs_close_event, menuWidget)
        box = self.glade.get_widget("MainBox")
        self.gtklevel = GtkLevel(self.level, self.on_level_menu)
        box.pack_start(self.gtklevel, True, True, 0)
        self.gtklevel.grid = self.config.getBool("grid")
        self.gtklevel.show()
        self.tooltips = gtk.Tooltips()
        self._lastFilePickerHandler = None
        self._setupPallette()
        self.getLevelSettings()
        self.rememberWindows()
        self.glade.get_widget("MainWindow").present()
        gtk.main()

    def _setupPallette(self):
        i1 = 0
        i2 = 0
        self.brush = None
        table = self.glade.get_widget("PalletteTable")
        tileTable = self.glade.get_widget("TileTable")
        for brush in self.brushes:
            button = gtk.ToggleButton()
            if isinstance(brush, ResourceBrush):
                image = gtk.Image()
                filename = self.getImageFilename(brush.resource)
                if not filename:
                    del button
                    continue
                pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
                brush.pixbuf = pixbuf # hack, setting arbitrary attribute
                if isinstance(brush, IceBrush):
                    key = "%s%s"%(brush.name,
                                  brush.connect and " %s"%brush.connect
                                  or "")
                    tip = "ice%s"%(brush.connect and " %s"%brush.connect
                                   or "")
                elif isinstance(brush, EnemyBrush):
                    tip = brush.id
                    key = brush.id
                elif isinstance(brush, DecorationBrush):
                    tip = "%s %s"%(brush.name, brush.resource)
                    key = "%s %s"%(brush.name, brush.resource)
                elif isinstance(brush, SpriteBrush):
                    key = brush.name
                    tip = brush.name
                else:
                    tip = "tile %s"%brush.resource
                    key = "tile %s"%brush.resource
                if isinstance(brush, (WalkingEnemyBrush,
                                      ClimbingEnemyBrush)):
                    brush.width = pixbuf.get_width() / 10
                    brush.height = pixbuf.get_height()
                elif isinstance(brush, StationaryEnemyBrush):
                    brush.width = pixbuf.get_width() / 16
                    brush.height = pixbuf.get_height()
                self.gtklevel.setBrush(key, brush)                
                icon = self.getCroppedPixbuf(pixbuf,
                                             brush.width * brush.offset,
                                             0,
                                             brush.width,
                                             brush.height
                                             )
                image.set_from_pixbuf(icon)
                button.add(image)
            elif isinstance(brush, EraseBrush):
                tip = "Erase"
            else:
                tip = None
            button.connect("toggled", self.on_toggle_brush, brush)
            if isinstance(brush, TileBrush):
                y, x = divmod(i1, 4)
                tileTable.attach(button, x, x + 1, y, y + 1)
                i1 += 1
            else:
                y, x = divmod(i2, 4)
                table.attach(button, x, x + 1, y, y + 1)
                i2 += 1
            if tip:
                self.tooltips.set_tip(button, tip)
            button.show_all()

    def getCroppedPixbuf(self, original, x, y, width, height):
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                True,
                                8,
                                width,
                                height)
        original.copy_area(x, y, width, height,
                           pixbuf, 0, 0)
        return pixbuf

    def setStatus(self, text):
        statusbar = self.glade.get_widget("StatusBar")
        statusbar.push(statusbar.get_context_id("status"), text)

    def getLevelSettings(self):
        self.glade.get_widget("TitleEntry").set_text(self.level.title or "")
        self.glade.get_widget("CreditsEntry").set_text(
            self.level.credits or "")
        self.glade.get_widget("MusicEntry").set_text(self.level.music or "")
        self.glade.get_widget("BackgroundEntry").set_text(
            self.level.background or "")
        self.glade.get_widget("ShadowsCheck").set_active(
            self.level.shadows or False)
        if self.level.background != self.gtklevel.bgFile:
            filename = self.getImageFilename(self.level.background)
            if filename:
                pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
                self.gtklevel.updateBackground(pixbuf)
                self.bgFile = filename
                self.gtklevel.redraw()
        self.gtklevel.setLevel(self.level)

    def setBrushOptions(self, brush):
        for child in self.glade.get_widget("OptionsBox").get_children():
            child.hide()
        if isinstance(brush, PlayerBrush):
            self.glade.get_widget("PlayerBrushTable").show()
            active = (brush.direction != None
                      and ["right", "left"].index(brush.direction) or 0)
            w = self.glade.get_widget("PlayerBrush.DirectionComboBox")
            w.set_active(active)
            w.connect("changed", self.on_PlayerBrush_DirectionComboBox_changed,
                      brush)
        elif isinstance(brush, FireBrush):
            self.glade.get_widget("FireBrushTable").show()
            w = self.glade.get_widget("FireBrush.NoFallingCheck")
            w.set_active(brush.noFalling)
            w.connect("toggled", self.on_FireBrush_NoFallingCheck_toggled,
                      brush)
        #elif isinstance(brush, IceBrush):
        #    self.glade.get_widget("IceBrushTable").show()
        #    active = [None, "connect", "connect-right", "connect-left"]\
        #             .index(brush.connect)
        #    w = self.glade.get_widget("IceBrush.ConnectComboBox")
        #    w.set_active(active)
        #    w.connect("changed", self.on_IceBrush_ConnectComboBox_changed,
        #              brush)
        elif isinstance(brush, LavaBrush):
            self.glade.get_widget("LavaBrushTable").show()
            w = self.glade.get_widget("LavaBrush.DormantCheck")
            w.set_active(brush.dormant)
            w.connect("toggled", self.on_LavaBrush_DormantCheck_toggled, brush)
        elif isinstance(brush, TubeBrush):
            self.glade.get_widget("TubeBrushTable").show()
            w = self.glade.get_widget("TubeBrush.IDEntry")
            w.set_text(brush.id or "")
            w.connect("changed", self.on_TubeBrush_IDEntry_changed, brush)
        elif isinstance(brush, WalkingEnemyBrush):
            self.glade.get_widget("WalkingEnemyBrushTable").show()
            w = self.glade.get_widget("WalkingEnemyBrush.SpeedSpin")
            w.set_value(float(brush.speed or 0))
            w.connect("changed",
                      self.on_WalkingEnemyBrush_SpeedSpin_changed,
                      brush)
            w = self.glade.get_widget("WalkingEnemyBrush.DirectionComboBox")
            w.set_active(["left", "right"].index(brush.direction))
            w.connect("changed",
                      self.on_WalkingEnemyBrush_DirectionComboBox_changed,
                      brush)
        elif isinstance(brush, ClimbingEnemyBrush):
            self.glade.get_widget("ClimbingEnemyBrushTable").show()
            w = self.glade.get_widget("ClimbingEnemyBrush.SpeedSpin")
            w.set_value(float(brush.speed or 0))
            w.connect("changed",
                      self.on_ClimbingEnemyBrush_SpeedSpin_changed,
                      brush)
            w = self.glade.get_widget("ClimbingEnemyBrush.DirectionComboBox")
            w.set_active(["up", "down"].index(brush.direction))
            w.connect("changed",
                      self.on_ClimbingEnemyBrush_DirectionComboBox_changed,
                      brush)
        elif isinstance(brush, StationaryEnemyBrush):
            self.glade.get_widget("StationaryEnemyBrushTable").show()
            w = self.glade.get_widget("StationaryEnemyBrush.TriggerSpin")
            w.set_value(float(brush.trigger or 0))
            w.connect("changed",
                      self.on_StationaryEnemyBrush_TriggerSpin_changed,
                      brush)
            w = self.glade.get_widget("StationaryEnemyBrush.DirectionComboBox")
            w.set_active(["up", "left", "down", "right"].index(
                brush.direction))
            w.connect("changed",
                      self.on_StationaryEnemyBrush_DirectionComboBox_changed,
                      brush)
        elif isinstance(brush, DecorationBrush):
            self.glade.get_widget("DecorationBrushTable").show()
            w = self.glade.get_widget("DecorationBrush.SpeedSpin")
            w.set_value(brush.speed)
            w.connect("changed",
                      self.on_DecorationBrush_SpeedSpin_changed,
                      brush)
        elif isinstance(brush, DirectionBrush):
            self.glade.get_widget("DirectionBrushTable").show()
            w = self.glade.get_widget("DirectionBrush.DirectionComboBox")
            w.set_active(
                ["right", "down", "left", "up"].index(brush.direction))
            w.connect("changed",
                      self.on_DirectionBrush_DirectionComboBox_changed,
                      brush)

    def rememberWindows(self):
        windows = ["PalletteDialog", 
                   "AboutDialog",
                   "ScrollToolDialog",
                   "PreferencesDialog",
                   "SettingsDialog",
                   "MainWindow"]
        for window in windows:
            widget = self.glade.get_widget(window)
            if self.config.has_key(window):
                if window == "PalletteDialog":
                    self.glade.get_widget("MenuPallette").set_active(True)
                elif window == "SettingsDialog":
                    self.glade.get_widget("MenuSettings").set_active(True)
                else:
                    widget.show()
                try:
                    v = self.config[window]
                    x, y, w, h = [int(s.strip()) for s in v.split(", ")]
                    widget.move(x, y)
                    widget.resize(w, h)
                except ValueError:
                    pass
            elif window != "MainWindow":
                if window == "PalletteDialog":
                    self.glade.get_widget("MenuPallette").set_active(False)
                elif window == "SettingsDialog":
                    self.glade.get_widget("MenuSettings").set_active(False)
                else:
                    widget.hide()

    def persistWindows(self):
        windows = ["PalletteDialog", 
                   "AboutDialog",
                   "ScrollToolDialog",
                   "PreferencesDialog",
                   "SettingsDialog",
                   "MainWindow"]
        for window in windows:
            widget = self.glade.get_widget(window)
            if widget.get_property("visible"):
                w, h = widget.get_size()
                x, y = widget.get_position()
                self.config[window] = "%d, %d, %d, %d"%(x, y, w, h)
            elif self.config.has_key(window):
                del self.config[window]
        if self.gtklevel.grid:
            self.config["grid"] = "1"
        else:
            self.config["grid"] = "0"
        self.saveConfig()

    def setTitle(self, title):
        mw = self.glade.get_widget("MainWindow")
        if title:
            mw.set_title("Magicor Level Editor - %s"%title)
        else:
            mw.set_title("Magicor Level Editor")
        
    #
    # GTK event callbacks
    #
    def on_MainWindow_delete_event(self, window, event):
        self.on_quit(window)
    
    def on_quit(self, widget):
        if self.config.getBool("remember_windows"):
            self.persistWindows()
        gtk.main_quit()

    def on_toggle_brush(self, button, brush):
        table1 = self.glade.get_widget("PalletteTable")
        table2 = self.glade.get_widget("TileTable")
        if button.get_active():
            for child in table1.get_children() + table2.get_children():
                if child != button and hasattr(child, "set_active"):
                    child.set_active(False)
            self.gtklevel.brush = brush
        else:
            for child in table1.get_children() + table2.get_children():
                if child.get_active():
                    return
            self.gtklevel.brush = None
        self.setBrushOptions(brush)
        
    def on_new(self, widget):
        self.clear()
        self.setStatus("")
        self.gtklevel.setLevel(self.level)        
        self.getLevelSettings()

    def on_open(self, widget):
        self.glade.get_widget("OpenDialog").show()

    def on_save(self, widget):
        if not self.saved:
            self.glade.get_widget("SaveDialog").show()
        else:
            try:
                self.saveLevel(self.saved)
                self.setStatus("Saved file %s."%self.saved)
            except EditorException, ee:
                self.setStatus("")
                self.glade.get_widget("ErrorLabel").set_text("%s"%ee)
                self.glade.get_widget("ErrorDialog").show()
            
    def on_about(self, widget):
        self.glade.get_widget("AboutDialog").show()

    def on_preferences(self, widget):
        self.glade.get_widget("PreferencesDialog").show()
        self.glade.get_widget("Preferences.RememberCheck").set_active(
            self.config.getBool("remember_windows"))
        self.glade.get_widget("Preferences.DataPathEntry").set_text(
            self.config.get("data_path", ""))

    def on_save_as(self, widget):
        self.glade.get_widget("SaveDialog").show()

    def on_ErrorDialog_response(self, dialog, response):
        dialog.hide()

    def on_AboutDialog_response(self, dialog, response):
        dialog.hide()

    def on_PreferencesDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            self.config["remember_windows"] = (
                self.glade.get_widget("Preferences.RememberCheck")
                .get_active() and "yes" or "no")
            t = self.glade.get_widget("Preferences.DataPathEntry").get_text()
            if t.strip():
                self.config["data_path"] = t.strip()
            elif self.config.has_key("data_path"):
                del self.config["data_path"]
            self.saveConfig()
        
    def on_OpenDialog_response(self, dialog, response):        
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            try:
                self.level = self.loadLevel(dialog.get_filename())
                self.setTitle(os.path.basename(dialog.get_filename()))
                self.setStatus("Loaded file %s."%dialog.get_filename())
                self.gtklevel.setLevel(self.level)
                self.getLevelSettings()
            except EditorException, ee:
                self.setStatus("")
                self.glade.get_widget("ErrorLabel").set_text("%s"%ee)
                self.glade.get_widget("ErrorDialog").show()
        
    def on_SaveDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            try:
                self.saveLevel(dialog.get_filename())
                self.setTitle(os.path.basename(dialog.get_filename()))
                self.setStatus("Saved file %s."%dialog.get_filename())
            except EditorException, ee:
                self.setStatus("")
                self.glade.get_widget("ErrorLabel").set_text("%s"%ee)
                self.glade.get_widget("ErrorDialog").show()

    def on_dialogs_delete_event(self, widget, event, menu):
        widget.hide()
        if menu and hasattr(menu, "set_active"):
            menu.set_active(False)
        return True

    def on_dialogs_close_event(self, widget, menu):
        if menu and hasattr(menu, "set_active"):
            menu.set_active(False)

    #
    # Dialogs
    #
    
    def on_SettingsDialog_BackgroundButton_clicked(self, widget):
        w = self.glade.get_widget("FilePickerDialog")
        if self._lastFilePickerHandler != None:
            w.disconnect(self._lastFilePickerHandler)
        else:
            w.set_current_folder(
                os.path.abspath(self.config.get("data_path", "data")))
        self._lastFilePickerHandler = w.connect(
            "response", self.on_FilePickerDialog_response, "background")
        f = gtk.FileFilter()
        f.add_pattern("*.png")
        f.add_pattern("*.jpg")
        w.set_filter(f)
        w.show()
        
    def on_SettingsDialog_MusicButton_clicked(self, widget):
        w = self.glade.get_widget("FilePickerDialog")
        if self._lastFilePickerHandler != None:
            w.disconnect(self._lastFilePickerHandler)
        else:
            w.set_current_folder(
                os.path.abspath(self.config.get("data_path", "data")))
        self._lastFilePickerHandler = w.connect(
            "response", self.on_FilePickerDialog_response, "music")
        f = gtk.FileFilter()
        f.add_pattern("*.xm")
        f.add_pattern("*.mod")
        f.add_pattern("*.ogg")
        f.add_pattern("*.mp3")
        w.set_filter(f)
        w.show()

    def on_FilePickerDialog_response(self, dialog, response, attr):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            spl = dialog.get_filename().split(os.path.sep)
            if spl[-1].startswith("_"):
                spl[-1] = spl[-1][1:]
            fn = "/".join(spl[-2:]).split(".")[0]
            if attr == "background":
                self.level.background =  fn
                self.glade.get_widget("BackgroundEntry").set_text(
                    self.level.background or "")
            elif attr == "music":            
                self.level.music = fn
                self.glade.get_widget("MusicEntry").set_text(
                    self.level.music or "")
    
    def on_PalletteDialog_response(self, widget, response):
        if response == gtk.RESPONSE_CLOSE:
            widget.hide()
            self.glade.get_widget("MenuPallette").set_active(False)

    def on_MenuPallette_activate(self, widget):
        if widget.get_active():
            self.glade.get_widget("PalletteDialog").show()
        else:
            self.glade.get_widget("PalletteDialog").hide()
           
    def on_MenuGrid_activate(self, widget):
        if widget.get_active():
            self.gtklevel.grid = True
            self.gtklevel.redraw()
        else:
            self.gtklevel.grid = False
            self.gtklevel.redraw()

    def on_SettingsDialog_response(self, widget, response):
        if response != gtk.RESPONSE_APPLY:
            self.glade.get_widget("MenuSettings").set_active(False)
        if response in (gtk.RESPONSE_OK, gtk.RESPONSE_APPLY):
            self.level.title = self.glade.get_widget("TitleEntry").get_text()
            self.level.credits = self.glade.get_widget(
                "CreditsEntry").get_text()
            self.level.music = self.glade.get_widget("MusicEntry").get_text()
            self.level.background = self.glade.get_widget(
                "BackgroundEntry").get_text()
            self.level.shadows = self.glade.get_widget(
                "ShadowsCheck").get_active()
            self.getLevelSettings()

    def on_MenuSettings_activate(self, widget):
        if widget.get_active():
            self.glade.get_widget("SettingsDialog").show()
        else:
            self.glade.get_widget("SettingsDialog").hide()

        
    # Properties dialog responses

    def on_PlayerDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            if (self.glade.get_widget("PlayerDialog.DirectionComboBox")
                .get_active() == 0):
                self.gtklevel.updateSprite("right")
            else:
                self.gtklevel.updateSprite("left")

    def on_FireDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            self.gtklevel.updateSprite(
                (self.glade.get_widget("FireDialog.NoFallingCheck")
                 .get_active()))

    def on_IceDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            self.gtklevel.updateSprite((None,
                                        "connect",
                                        "connect-right",
                                        "connect-left")[
                (self.glade.get_widget("IceDialog.ConnectComboBox")
                 .get_active())])

    def on_LavaDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            self.gtklevel.updateSprite(
                (self.glade.get_widget("LavaDialog.DormantCheck")
                 .get_active() and "" or "dormant"))

    def on_TubeDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            a = (self.glade.get_widget("TubeDialog.DirectionComboBox")
                 .get_active())
            direction = ["left", "up", "down", "right"][a]
            id_ = self.glade.get_widget("TubeDialog.IDEntry").get_text()
            if id_:
                self.gtklevel.updateSprite("%s %s"%(direction, id_))
            else:
                self.gtklevel.updateSprite("%s"%direction)

    def on_WalkingEnemyDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            args = " ".join(self.gtklevel._selected.args.split(" ", 3)[1:-1])
            speed = int(self.glade.get_widget(
                "WalkingEnemyDialog.SpeedSpin").get_value())
            direction = ["left", "right"][self.glade.get_widget(
                "WalkingEnemyDialog.DirectionComboBox").get_active()]
            self.gtklevel.updateSprite("%s %s %d"%(direction, args, speed))

    def on_ClimbingEnemyDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            args = " ".join(self.gtklevel._selected.args.split(" ", 3)[1:-1])
            speed = int(self.glade.get_widget("ClimbingEnemyDialog.SpeedSpin")
                        .get_value())
            direction = ["up", "down"][self.glade.get_widget(
                "ClimbingEnemyDialog.DirectionComboBox").get_active()]
            self.gtklevel.updateSprite("%s %s %d"%(direction, args, speed))

    def on_StationaryEnemyDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            args = " ".join(self.gtklevel._selected.args.split(" ", 3)[1:-1])
            trigger = int(self.glade.get_widget(
                "StationaryEnemyDialog.TriggerSpin").get_value())
            direction = ["up", "left", "down", "right"][self.glade.get_widget(
                "StationaryEnemyDialog.DirectionComboBox").get_active()]
            self.gtklevel.updateSprite("%s %s %d"%(direction, args, trigger))

    def on_DecorationDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            speed = int(self.glade.get_widget(
                "DecorationDialog.SpeedSpin").get_value())
            args = " ".join(self.gtklevel._selected.args.split(" ", 3)[:-1])
            self.gtklevel.updateSprite("%s %d"%(args, speed))

    def on_DirectionDialog_response(self, dialog, response):
        dialog.hide()
        if response == gtk.RESPONSE_OK:
            direction = ["right", "down", "left", "up"][self.glade.get_widget(
                "DirectionDialog.DirectionComboBox").get_active()]
            self.gtklevel.updateSprite("%s"%direction)
            
        
    # Brush options

    def on_PlayerBrush_DirectionComboBox_changed(self, w, b):
        b.direction = ("right", "left")[w.get_active()]

    def on_FireBrush_NoFallingCheck_toggled(self, w, b):
        b.noFalling = w.get_active()

    def on_IceBrush_ConnectComboBox_changed(self, w, b):
        b.connect = (None, "connect", "connect-right", "connect-left")\
                    [w.get_active()]

    def on_LavaBrush_DormantCheck_toggled(self, w, b):
        b.dormant = w.get_active() and "" or "dormant"

    def on_TubeBrush_IDEntry_changed(self, w, b):
        b.id = w.get_text()

    def on_WalkingEnemyBrush_DirectionComboBox_changed(self, w, b):
        b.direction = ["left", "right"][w.get_active()]

    def on_WalkingEnemyBrush_SpeedSpin_changed(self, w, b):
        b.speed = int(w.get_value())

    def on_ClimbingEnemyBrush_DirectionComboBox_changed(self, w, b):
        b.direction = ["up", "down"][w.get_active()]

    def on_ClimbingEnemyBrush_SpeedSpin_changed(self, w, b):
        b.speed = int(w.get_value())

    def on_StationaryEnemyBrush_DirectionComboBox_changed(self, w, b):
        b.direction = ["up", "left", "down", "right"][w.get_active()]

    def on_StationaryEnemyBrush_TriggerSpin_changed(self, w, b):
        b.trigger = int(w.get_value())

    def on_DecorationBrush_SpeedSpin_changed(self, w, b):
        b.speed = int(w.get_value())

    def on_DirectionBrush_DirectionComboBox_changed(self, w, b):
        b.direction = ["right", "down", "left", "up"][w.get_active()]
        
    # Level menu callback

    def on_level_menu(self, sprite):
        brush = self.gtklevel.getBrushCopy(sprite.name, sprite.args)
        for n, m in self.propertiesDialogs:
            self.glade.get_widget(n).hide()
        if brush:
            if isinstance(brush, PlayerBrush):
                (self.glade.get_widget("PlayerDialog.DirectionComboBox")
                 .set_active(brush.direction == "left" and 1 or 0))
                dialog = self.glade.get_widget("PlayerDialog")
            elif isinstance(brush, FireBrush):
                (self.glade.get_widget("FireDialog.NoFallingCheck")
                 .set_active(brush.noFalling))
                dialog = self.glade.get_widget("FireDialog")
            elif isinstance(brush, IceBrush):
                (self.glade.get_widget("IceDialog.ConnectComboBox")
                 .set_active([None,
                              "connect",
                              "connect-right",
                              "connect-left"].index(brush.connect)))
                dialog = self.glade.get_widget("IceDialog")
            elif isinstance(brush, LavaBrush):
                (self.glade.get_widget("LavaDialog.DormantCheck")
                 .set_active(brush.dormant))
                dialog = self.glade.get_widget("LavaDialog")
            elif isinstance(brush, TubeBrush):
                d = ["left", "up", "down", "right"].index(brush.direction)
                (self.glade.get_widget("TubeDialog.DirectionComboBox")
                 .set_active(d))
                (self.glade.get_widget("TubeDialog.IDEntry")
                 .set_text(brush.id or ""))
                dialog = self.glade.get_widget("TubeDialog")
            elif isinstance(brush, WalkingEnemyBrush):
                n = "WalkingEnemyDialog"
                dialog = self.glade.get_widget(n)
                d = ["left", "right"].index(brush.direction)
                self.glade.get_widget("%s.DirectionComboBox"%n).set_active(d)
                self.glade.get_widget("%s.SpeedSpin"%n).set_value(
                    float(brush.speed or 0))
            elif isinstance(brush, ClimbingEnemyBrush):
                n = "ClimbingEnemyDialog"
                dialog = self.glade.get_widget(n)
                d = ["up", "down"].index(brush.direction)
                self.glade.get_widget("%s.DirectionComboBox"%n).set_active(d)
                self.glade.get_widget("%s.SpeedSpin"%n).set_value(
                    float(brush.speed or 0))
            elif isinstance(brush, StationaryEnemyBrush):
                n = "StationaryEnemyDialog"
                dialog = self.glade.get_widget(n)
                d = ["up", "left", "down", "right"].index(brush.direction)
                self.glade.get_widget("%s.DirectionComboBox"%n).set_active(d)
                self.glade.get_widget("%s.TriggerSpin"%n).set_value(
                    float(brush.trigger or 0))
            elif isinstance(brush, DecorationBrush):
                dialog = self.glade.get_widget("DecorationDialog")
                self.glade.get_widget("DecorationDialog.SpeedSpin").set_value(
                    float(brush.speed or 0))
            elif isinstance(brush, DirectionBrush):
                dialog = self.glade.get_widget("DirectionDialog")
                self.glade.get_widget(
                    "DirectionDialog.DirectionComboBox").set_active(
                    ["right", "down", "left", "up"].index(brush.direction))
            else:
                dialog = None
            for widget, menu in self.propertiesDialogs:
                self.glade.get_widget(widget).hide()
            if dialog:
                dialog.show()
                dialog.present()
                x, y, mods = dialog.get_screen().get_root_window()\
                             .get_pointer()
                dialog.move(x, y)

    # tools

    def on_ScrollToolDialog_response(self, dialog, response):
        dialog.hide()

    def on_ScrollToolDialog_UpButton_clicked(self, w):
        tmp = [None] * 20
        for x in xrange(20):
            tmp[x] = self.gtklevel._level[x, 0]
        for y in xrange(17):
            for x in xrange(20):
                self.gtklevel._level[x, y] = self.gtklevel._level[x, y + 1]
        for x in xrange(20):
            self.gtklevel._level[x, y + 1] = tmp[x]
        for sprite in self.gtklevel._level.sprites:
            sprite.y -= 1
            if sprite.y < 0:
                sprite.y = 17
        self.gtklevel.redraw()

    def on_ScrollToolDialog_DownButton_clicked(self, w):
        tmp = [None] * 20
        for x in xrange(20):
            tmp[x] = self.gtklevel._level[x, 17]
        for y in xrange(17, 0, -1):
            for x in xrange(20):
                self.gtklevel._level[x, y] = self.gtklevel._level[x, y - 1]
        for x in xrange(20):
            self.gtklevel._level[x, 0] = tmp[x]
        for sprite in self.gtklevel._level.sprites:
            sprite.y += 1
            if sprite.y > 17:
                sprite.y = 0
        self.gtklevel.redraw()

    def on_ScrollToolDialog_LeftButton_clicked(self, w):
        tmp = [None] * 18
        for y in xrange(18):
            tmp[y] = self.gtklevel._level[0, y]
        for y in xrange(18):
            for x in xrange(0, 19):
                self.gtklevel._level[x, y] = self.gtklevel._level[x + 1, y]
        for y in xrange(18):
            self.gtklevel._level[19, y] = tmp[y]
        for sprite in self.gtklevel._level.sprites:
            sprite.x -= 1
            if sprite.x < 0:
                sprite.x = 19
        self.gtklevel.redraw()

    def on_ScrollToolDialog_RightButton_clicked(self, w):
        tmp = [None] * 18
        for y in xrange(18):
            tmp[y] = self.gtklevel._level[19, y]
        for y in xrange(18):
            for x in xrange(19, 0, - 1):
                self.gtklevel._level[x, y] = self.gtklevel._level[x - 1, y]
        for y in xrange(18):
            self.gtklevel._level[0, y] = tmp[y]
        for sprite in self.gtklevel._level.sprites:
            sprite.x += 1
            if sprite.x > 19:
                sprite.x = 0
        self.gtklevel.redraw()

    def on_MenuScroll_activate(self, b):
        self.glade.get_widget("ScrollToolDialog").show()
        
