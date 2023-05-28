#!/usr/bin/python
#
# Magicor Level Editor
# Copyright 2006  Peter Gebauer. Licensed as Public Domain.
# (see LICENSE for more info)
from optparse import OptionParser
import sys, os
sys.path.append(".")

##-->win
def change_to_correct_path(): #taken from pygame wiki cookbook
    import os, sys
    exe_base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(exe_base_dir)
    sys.path.append(exe_base_dir)

if sys.platform=='win32':
    change_to_correct_path() #usefull when running from another dir, desktop or appbar
##<--win

from magicor import getConfig
from magicor.editor.gtkgui import GtkEditor

parser = OptionParser()
##-->win
if sys.platform=='win32':
    parser.add_option("-c", "--config", dest="configPath",
                  default = ".",
                  help="use this config path, default is magicor directory.")
    baseConf="./magicor-editor.conf"
else:
    parser.add_option("-c", "--config", dest="configPath",
                  default = "###CONFIG_PATH###",
                  help="use this default config, default ###CONFIG_PATH###")
    baseConf="~/.magicor/magicor-editor.conf"
##<--win

(options, args) = parser.parse_args()

paths = [options.configPath, baseConf] ##@@

conf = getConfig(paths)
##-->win
if sys.platform=='win32': # not clean but...
    conf["user_path"]='.'
    conf["data_path"]='data'
##<--win
GtkEditor(conf, args and args[0] or None)
