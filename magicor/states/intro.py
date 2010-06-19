"""
Intro like states.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import time
from magicor import Text
from magicor.states import BaseState
from magicor.states.title import TitleState

class CopyrightNoticeState(BaseState):

    def __init__(self, config, data, screen):
        BaseState.__init__(self, config, data, screen)
        self.text = Text(screen, self.resources["fonts/info"])
        self.lines = ["magicor",
                      "",
                      "copyright 2006",
                      "peter gebauer",
                      "",
                      "licensed as public domain",
                      "",
                      "",
                      "enjoy!"]
        self.resources.playMusic("music/soft-trance", -1)
        self.startTime = time.time()
        self.logos = [self.resources.loadImage("images/gnu-logo", False),
                      self.resources.loadImage("images/linux-logo", False),
                      self.resources.loadImage("images/python-logo", False),
                      self.resources.loadImage("images/sdl-logo", False),
                      self.resources.loadImage("images/pygame-logo", False)
                      ]
        self.totalWidth = sum((s.get_width() + 16 for s in self.logos))
        self.highest = max((s.get_height() for s in self.logos))
        self.startX = screen.get_width() / 2 - self.totalWidth / 2
        
    def control(self):
        if (self.controls.escape
            or self.controls.start
            or self.controls.action
            or time.time() - self.startTime > 5):
            self.setNext(TitleState(self.config,
                                    self.data,
                                    self.screen,
                                    False))

    def run(self):
        self.control()
        self.screen.fill(0)
        y = 64
        for l in self.lines:
            if l:
                self.text.draw(l,
                               self.screen.get_width() / 2
                               - self.text.getWidth(l) / 2,
                               y)
            y += self.text.font.get_height()
        y = self.screen.get_height() - self.highest / 2
        x = self.startX
        for l in self.logos:
            self.screen.blit(l, (x, y - l.get_height() / 2))
            x += l.get_width() + 16
        
