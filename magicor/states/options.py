"""
All option-related states are here.

Copyright 2006  Peter Gebauer. Licensed as Public Domain.
(see LICENSE for more info)
"""
import warnings
import pygame
from pygame.mixer import music
from magicor import Text
from magicor.states import BaseState

class Option(object):

    def __init__(self, title):
        self.title = title
        

class ValueOption(Option):

    def __init__(self, title, value, key):
        Option.__init__(self, title)
        self.value = value
        self.key = key
    

class BoolOption(ValueOption):

    def __init__(self, title, value, key):
        ValueOption.__init__(self, title, value, key)

class IntOption(ValueOption):

    def __init__(self, title, value, key, min_, max_):
        ValueOption.__init__(self, title, value, key)
        self.max = max_
        self.min = min_

class KeyOption(ValueOption):

    def __init__(self, title, value, key):
        ValueOption.__init__(self, title, value, key)

class JoyOption(ValueOption):

    def __init__(self, title, value, key):
        ValueOption.__init__(self, title, value, key)

class StateOption(Option):

    def __init__(self, title, state):
        self.title = title
        self.state = state


class OptionsState(BaseState):
    
    def __init__(self, config, data, screen, previous):
        BaseState.__init__(self, config, data, screen)
        self.previous = previous
        self.selected = 0
        self.scrollY = [0] * screen.get_width()
        self.options = []
        self.text = Text(self.screen, self.resources["fonts/info"])

    def control(self):
        if self.controls.escape:
            self.previous.controls = self.controls
            if not isinstance(self.previous, OptionsState):
                fn = "%s/magicor.conf"%self.config.get("user_path",
                                                       "~/.magicor")
                self.config.saveFile(fn)
            self.setNext(self.previous)
            self.previous.setNext(self.previous)
            self.controls.clear()
        elif self.controls.up:
            self.resources.playSound("samples/menu")
            self.selected = (self.selected - 1) % len(self.options)
            self.controls.clear()
        elif self.controls.down:
            self.resources.playSound("samples/menu")
            self.selected = (self.selected + 1) % len(self.options)
            self.controls.clear()
        elif self.controls.start or self.controls.action:
            self.activateOption(self.selected)
            self.controls.clear()
        elif self.controls.left or self.controls.right:            
            self.changeOption(self.selected,
                              self.controls.left and -1 or 1)

    def addOption(self, option, callback = None):
        self.options.append((option, callback))

    def drawOption(self, y, option):
        self.text.draw(option.title, 0, y)
        if hasattr(option, "value"):
            if isinstance(option, BoolOption):
                value = option.value and "true" or "false"
            elif isinstance(option, KeyOption) and option.value:
                value = pygame.key.name(option.value)
            else:
                value = "%s"%option.value
            self.text.draw(value,
                           self.screen.get_width()
                           - self.text.getWidth("%s"%value),
                           y)

    def run(self):
        self.control()
        self.screen.fill(0)
        line = 0
        for option in (o[0] for o in self.options):
            y = line * self.text.font.get_height()
            if line == self.selected:
                self.screen.fill(0xff,
                                 (0, y,
                                  self.screen.get_width(),
                                  self.text.font.get_height()))
            self.drawOption(y, option)
            line += 1

    def _updateOption(self, option, callback, oldValue = None):
        if isinstance(option, ValueOption):
            self.config[option.key] = \
                                    option.value
        if callback and not callback() and isinstance(option, ValueOption):
            option.value = oldValue
            self.config[option.key] = oldValue
            print self.config.getBool(option.key)

    def activateOption(self, selected):
        option, callback = self.options[selected]
        if hasattr(option, "value"):
            oldValue = option.value
        else:
            oldValue = None
        if isinstance(option, BoolOption):
            if option.value:
                option.value = 0
            else:
                option.value = 1
        elif isinstance(option, StateOption):
            self.setNext(option.state(
                self.config, self.data, self.screen, self))
        self._updateOption(option, callback, oldValue)

    def changeOption(self, selected, direction):
        option, callback = self.options[selected]
        if isinstance(option, IntOption):
            option.value += direction
            if option.value < option.min:
                option.value = option.min
            elif option.value > option.max:
                option.value = option.max
        self._updateOption(option, callback)

class MainOptionsState(OptionsState):
    
    def __init__(self, config, data, screen, previous):
        OptionsState.__init__(self, config, data, screen, previous)
        self.addOption(BoolOption("fullscreen",
                                  config.getBool("fullscreen"),
                                  "fullscreen"),
                       self.toggleFullscreen)
        self.addOption(BoolOption("sound",
                                  config.getBool("sound"),
                                  "sound"),
                       self.toggleSound)
        self.addOption(BoolOption("music",
                                  config.getBool("music"),
                                  "music"),
                       self.toggleMusic)
        self.addOption(BoolOption("eyecandy",
                                  config.getBool("eyecandy"),
                                  "eyecandy"),
                       self.toggleEyecandy)
        self.addOption(IntOption("sound vol",
                                 config.getInt("sound_vol"),
                                 "sound_vol", 0, 100),
                       self.changeSoundVol)
        self.addOption(IntOption("music vol",
                                 config.getInt("music_vol"),
                                 "music_vol", 0, 100),
                       self.changeMusicVol)
        self.addOption(StateOption("keyboard controls", KeyOptionsState))
        self.addOption(StateOption("joystick controls", JoystickOptionsState))
        
    def toggleSound(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(44100, -16, True, 1024)
                pygame.mixer.set_num_channels(8)
            except pygame.error, e:
                warnings.warn("unable to init audio; %s"%e)
                return False
        self.resources.sound = self.config.getBool("sound")
        if self.resources.sound:
            self.resources.addResources("samples/")
        return True
        
    def toggleMusic(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(44100, -16, True, 1024)
                pygame.mixer.set_num_channels(8)
            except pygame.error, e:
                warnings.warn("unable to init audio; %s"%e)
                return False
        self.resources.music = self.config.getBool("music")
        if self.resources.music and self.resources.lastMusic:
            self.resources.playMusic(self.resources.lastMusic)
        else:
            self.resources.stopMusic()
        return True

    def toggleEyecandy(self):
        if hasattr(self.previous, "eyecandy"):
            self.previous.eyecandy = self.config.getBool("eyecandy")
        return True
            
    def toggleFullscreen(self):
        if self.config.get("fullscreen"):
            pygame.display.set_mode((self.screen.get_width(),
                                     self.screen.get_height()),
                                    pygame.HWSURFACE | pygame.FULLSCREEN,
                                    32)
        else:
            pygame.display.set_mode((self.screen.get_width(),
                                     self.screen.get_height()),
                                    pygame.HWSURFACE,
                                    32)
        return True

    def changeSoundVol(self):
        self.resources.soundVol = self.config.getInt("sound_vol")
        if self.config.getBool("sound"):
            self.resources.playSound("samples/menu")
        return True

    def changeMusicVol(self):
        self.resources.musicVol = self.config.getInt("music_vol")
        music.set_volume(self.resources.musicVol * 0.01)
        return True

    
class KeyOptionsState(OptionsState):

    def __init__(self, config, data, screen, previous):
        OptionsState.__init__(self, config, data, screen, previous)
        self.addOption(KeyOption("up",
                                  config.get("key-up", pygame.K_UP),
                                  "key-up"),
                       self.doKeyBinding)
        self.addOption(KeyOption("down",
                                  config.get("key-down", pygame.K_DOWN),
                                  "key-down"),
                       self.doKeyBinding)
        self.addOption(KeyOption("left",
                                  config.get("key-left", pygame.K_LEFT),
                                  "key-left"),
                       self.doKeyBinding)
        self.addOption(KeyOption("right",
                                  config.get("key-right", pygame.K_RIGHT),
                                  "key-right"),
                       self.doKeyBinding)
        self.addOption(KeyOption("action",
                                  config.get("key-action", pygame.K_SPACE),
                                  "key-action"),
                       self.doKeyBinding)
        #self.addOption(KeyOption("escape",
        #                          config.get("key-escape", pygame.K_ESCAPE),
        #                          "key-escape"),
        #               self.doKeyBinding)
        self.addOption(KeyOption("start",
                                  config.get("key-start", pygame.K_RETURN),
                                  "key-start"),
                       self.doKeyBinding)
        self.bindKey = None

    

    def doKeyBinding(self):
        option = self.options[self.selected][0]
        self.bindKey = option.key
        self.controls.clear()

    def control(self):
        if self.bindKey:
            option = self.options[self.selected][0]
            if option.value:
                value = pygame.key.name(option.value)
            else:
                value = "%s"%option.value
            self.screen.fill(0,
                             (self.screen.get_width()
                              - self.text.getWidth(value),
                              self.selected * self.text.font.get_height(),
                              self.text.getWidth(value),
                              self.text.font.get_height()
                              )
                             )
            if self.controls.key:
                if self.controls.key == pygame.K_ESCAPE:
                    self.bindKey = None
                    self.controls.clear()
                else:
                    option.value = self.controls.key
                    self.controls.clear()
                    self.config[option.key] = option.value
                    keyHandle = "key%s"%option.key[4:].capitalize()
                    for k, v in self.controls.keys.items():
                        if v == keyHandle:
                            del self.controls.keys[k]
                    for o in (oo[0] for oo in self.options):
                        if o.value == option.value and o != option:
                            o.value = None
                            self.config[o.key] = None
                            self.controls.keys[o.key] = None
                    self.controls.keys[option.value] = keyHandle
                    self.bindKey = None
        else:
            OptionsState.control(self)

    def run(self):
        if self.bindKey:
            self.control()
            self.text.draw("press a key to bind, escape scapes", 0,
                           600 - self.text.font.get_height() * 2)
        else:
            OptionsState.run(self)
            

class JoystickOptionsState(OptionsState):

    def __init__(self, config, data, screen, previous):
        OptionsState.__init__(self, config, data, screen, previous)
        self.addOption(JoyOption("up",
                                  config.get("joy-up", "axis 5 neg"),
                                  "joy-up"),
                       self.doJoyBinding)
        self.addOption(JoyOption("down",
                                  config.get("joy-down", "axis 5 pos"),
                                  "joy-down"),
                       self.doJoyBinding)
        self.addOption(JoyOption("left",
                                  config.get("joy-left", "axis 4 neg"),
                                  "joy-left"),
                       self.doJoyBinding)
        self.addOption(JoyOption("right",
                                  config.get("joy-right", "axis 4 pos"),
                                  "joy-right"),
                       self.doJoyBinding)
        self.addOption(JoyOption("action",
                                  config.get("joy-action", "button 0"),
                                  "joy-action"),
                       self.doJoyBinding)
        self.addOption(JoyOption("escape",
                                  config.get("joy-escape", "button 8"),
                                  "joy-escape"),
                       self.doJoyBinding)
        self.addOption(JoyOption("start",
                                  config.get("joy-start", "button 9"),
                                  "joy-start"),
                       self.doJoyBinding)
        self.bindJoy = None

    

    def doJoyBinding(self):
        option = self.options[self.selected][0]
        self.bindJoy = option.key        
        self.controls.clear()

    def control(self):
        if self.bindJoy:
            option = self.options[self.selected][0]
            value = "%s"%option.value
            self.screen.fill(0x0,
                             (self.screen.get_width()
                              - self.text.getWidth(value),
                              self.selected * self.text.font.get_height(),
                              self.text.getWidth(value),
                              self.text.font.get_height()
                              )
                             )
            if self.controls.joyState:
                if self.controls.key == pygame.K_ESCAPE:
                    self.bindJoy = None
                    self.controls.clear()
                else:
                    option.value = self.controls.joyState
                    self.controls.clear()
                    self.config[option.key] = option.value
                    joyHandle = "joy%s"%option.key[4:].capitalize()
                    for k, v in self.controls.joystick.items():
                        if v == joyHandle:
                            del self.controls.joystick[k]
                    for o in (oo[0] for oo in self.options):
                        if o.value == option.value and o != option:
                            o.value = None
                            self.config[o.key] = None
                            self.controls.joystick[o.key] = None
                    self.controls.joystick[option.value] = joyHandle
                    self.bindJoy = None
        else:            
            OptionsState.control(self)

    def run(self):
        self.control()
        if self.bindJoy:
            self.text.draw("move joystick or press buttons, escape scapes", 0,
                           600 - self.text.font.get_height() * 2)
        else:
            OptionsState.run(self)
