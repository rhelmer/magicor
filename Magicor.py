#!/usr/bin/python
#
# Magicor
# Copyright 2006  Peter Gebauer. Licensed as Public Domain.
# (see LICENSE for more info)
import sys, os

def change_to_correct_path(): #taken from pygame wiki cookbook 
    import os, sys 
    exe_base_dir = os.path.abspath(os.path.dirname(sys.argv[0])) 
    os.chdir(exe_base_dir) 
    sys.path.append(exe_base_dir) 
 
if sys.platform=='win32': 
    change_to_correct_path() #usefull when running from another dir, desktop or appbar

from optparse import OptionParser
sys.path.append(".")
from magicor import GameEngine, getConfig, parse_printkeys
from magicor.states.intro import CopyrightNoticeState

parser = OptionParser(usage="%prog [options]")

if sys.platform=='win32':
    parser.add_option("-c", "--config", dest="configPath",
                  default = ".",
                  help="use this config path, default is magicor directory.")
    baseConf=".\magicor.conf"
else:
    parser.add_option("-c", "--config", dest="configPath",
                  default = "###CONFIG_PATH###",
                  help="use this default config, default ###CONFIG_PATH###")
    baseConf="~/.magicor/magicor.conf"

parser.add_option("-j", "--joystick",
                  action="store", type="int", dest="joystick",
                  default=None,
                  help="enable/disable joystick")
parser.add_option("-m", "--music",
                  action="store", type="int", dest="music",
                  default=None,
                  help="enable/disable music")
parser.add_option("-s", "--sound",
                  action="store", type="int",  dest="sound",
                  default=None,
                  help="enable/disable sound")
parser.add_option("-f", "--fullscreen",
                  action="store", type="int",  dest="fullscreen",
                  default=None,
                  help="enable/disable fullscreen")
parser.add_option("-d","--dev", type="int", dest= "devmode",
                  default=None, help="enable dev keys")
parser.add_option("-k","--keysprintdbg",type="string", dest="printkeys",default="",help="keys to enable selective printing of debug info. Separator is ':'")
(options, args) = parser.parse_args()

paths = [ options.configPath, baseConf ]
conf = getConfig(paths)

if sys.platform=='win32': # not clean but...
    conf["user_path"]='.'
    conf["data_path"]='data'

if options.joystick != None:
    conf["joystick"] = bool(options.joystick)
if options.music != None:
    conf["music"] = options.music
if options.sound != None:
    conf["sound"] = options.sound
if options.fullscreen != None:
    conf["fullscreen"] = bool(options.fullscreen)
if options.devmode != None:
    conf["devmode"] = bool(options.devmode)
parse_printkeys(options.printkeys)
gameEngine = GameEngine(conf)
gameEngine.start(CopyrightNoticeState(conf, None, gameEngine.screen))
