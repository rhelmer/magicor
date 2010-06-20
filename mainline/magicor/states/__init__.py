"""
Magicor states are defined here.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import math, random, os, warnings
import pygame
from pygame.locals import *

from magicor import State, Text, Controls
from magicor.level import Level
from magicor.resources import getResources

class StateData(object):

    def __init__(self, **kwargs):
        self.lastLevel = kwargs.get("lastLevel")
        self.lastLevelFinished = kwargs.get("lastLevelFinished")
        self.controls = kwargs.get("controls")

        

class BaseState(State):

    def __init__(self, config, data, screen):
        State.__init__(self, config)
        self.resources = getResources()
        if config.get("joystick", 1) and pygame.joystick.get_count() > 0:
            self.joystick = self.resources.getJoystick(0)
            self.numAxes = self.joystick.get_numaxes()
            self.numButtons = self.joystick.get_numbuttons()
        else:
            self.joystick = None
            self.numAxes = 0
            self.numButtons = 0
        if not data:
            data = StateData(
                controls = Controls(
                {config.get("key-up", K_UP): "keyUp",
                 config.get("key-down", K_DOWN): "keyDown",
                 config.get("key-left", K_LEFT): "keyLeft",
                 config.get("key-right", K_RIGHT): "keyRight",
                 config.get("key-escape", K_ESCAPE): "keyEscape",
                 config.get("key-action", K_SPACE): "keyAction",
                 config.get("key-start", K_RETURN): "keyStart",
                 },
                {config.get("joy-up", "axis 5 neg"): "joyUp",
                 config.get("joy-down", "axis 5 pos"): "joyDown",
                 config.get("joy-left", "axis 4 neg"): "joyLeft",
                 config.get("joy-right", "axis 4 pos"): "joyRight",
                 config.get("joy-action", "button 0"): "joyAction",
                 config.get("joy-escape", "button 8"): "joyEscape",
                 config.get("joy-start", "button 9"): "joyStart",
                 },
                self.numAxes,
                self.numButtons))
        self.data = data
        self.controls = data.controls
        self.screen = screen
        self.resources = getResources()
        self.resources.addResources("tiles")
        self.resources.addResources("sprites")
        self.resources.addResources("samples")
        self.resources.addResources("fonts")

    def eventJoystick(self):
        if self.config.get("joystick", 1) and self.joystick:
            for axis in xrange(self.numAxes):
                self.controls.setAxis(axis, self.joystick.get_axis(axis))
            for button in xrange(self.numButtons):
                self.controls.setButton(button,
                                        self.joystick.get_button(button))

    def eventKeyDown(self, event):
        self.controls.setKey(event.key)

    def eventKeyUp(self, event):
        self.controls.unsetKey(event.key)


class MenuState(BaseState):

    def __init__(self, config, data, screen, selectors):
        BaseState.__init__(self, config, data, screen)
        self.resources.addResources("fonts/")
        self.activeFont = self.resources["fonts/info"]
        self.inactiveFont = self.resources["fonts/info-inactive"]
        self.selectors = selectors
        self.selected = 0
        self.text = Text(screen, self.activeFont, screen.get_width())

    def renderMenu(self, y, surface = None):
        if not surface:
            surface = self.screen
        i = 0
        middle = surface.get_width() / 2
        for selector in self.selectors:
            if self.selected == i:
                self.text.font = self.activeFont
            else:
                self.text.font = self.inactiveFont
            self.text.draw(selector[0].lower(),
                           middle - self.text.getWidth(selector[0]) / 2,
                           y + i * self.text.font.get_height(),
                           False)
            i += 1
            
    def control(self):
        if self.controls.up:
            self.selected = (self.selected - 1) % len(self.selectors)
            self.resources.playSound("samples/menu")
        elif self.controls.down:
            self.selected = (self.selected + 1) % len(self.selectors)
            self.resources.playSound("samples/menu")
        elif self.controls.start or self.controls.action:
            self.resources.playSound("samples/start")
            stCls = self.selectors[self.selected][1]
            if stCls:
                self.setNext(stCls(*self.selectors[self.selected][2:]))
            else:
                self.setNext(None)
        self.controls.clear()


class ErrorState(BaseState):

    def __init__(self, config, data, screen, message, previous):
        BaseState.__init__(self, config, data, screen)
        self.previous = previous
        self.text = Text(screen, self.resources["fonts/info"],
                         screen.get_width())
        self.message = message

    def control(self):
        if self.controls.start or self.controls.escape:
            self.setNext(self.previous(self.config,
                                       self.data,
                                       self.screen))

    def run(self):
        self.control()
        self.screen.fill(0)
        self.text.draw(self.message,
                       self.screen.get_width() / 2
                       - self.text.getWidth(self.message) / 2,
                       self.screen.get_height() / 2
                       - self.text.font.get_height() / 2)
