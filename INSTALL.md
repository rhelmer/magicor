(windows: use wordpad to read this file)
Installation for non windows OSes, GNU-oriented:

Requirements:
  - python >= 3.11
  - pygame >= 2.4.0
  - sdl2 >= 2.26
  - SDL_mixer >= 2.6
  - SDL_image >= 2.6

  - GNU make (or equivalent, optional for proper installation)
  - rsync (optional for making dist target)

Additional requirements for the editor:
  - GTK 2.0
  - libglade2
  - PyGTK

Install dependencies macOS using [Homebrew](https://brew.sh/):
  ```sh
  brew install python3 sdl2 sdl2_image sdl2_mixer
  pip3 install virtualenv
  python3 -m virtualenv
  pip install -r requirements.txt
  ```
  Now you may run `python3 Magicor.py` to run Magicor, or see the next
  section to install it on your system in `/usr/local/games/magicor`.

Installation instructions for GNU/BSD and macOS (and similar):
  1. Edit the file 'Makefile', change the variables to suit your system.
  2. Type 'make install'.
  3. Spend the entire day playing Magicor. :-)


Windows installation & operation :
To play the game you need to have python and pygame installed.
To use the level editor you need to have aditional modules, see 'editor dependencies'

Install:
  unpack to the desired directory, by example d:\magicor
Play the game:
  doubleclick magicor.py in the directory where you unpacked
Level editing:
  doubleclick Magicor-LevelEditor.py
  note: resize of the main window will change aspect ratio 

Editor dependencies:
To run the level editor you need aditionally pyGTK, GTK 2.0 and libglade2.
For those that dont have them let me show how I settled this dependencies.
Keep in mind that I was on python 2.4, without any of the extra dependencies,
you may need to adjust if your starting point is other. 

So: 
Go 'pygtk on win32' http://www.pcpm.ucl.ac.be/~gustin/win32_ports/pygtk.html
There you have descriptions, instructions and direct download links  for variations ( python 2.3 and  2.4, pygtk 2.6 and 2.8 )

I chosed the 'pygtk 2.8 Python 2.4 (with pycairo support)' variation, downloaded the two related  files: pygtk-2.8.6-1.win32-py2.4.exe and pycairo-1.0.2-1.win32-py2.4.exe.

The dependencies section tells we need runtimes and sugest devel runtimes from 
'gladewin32 project'  http://gladewin32.sourceforge.net/
Well, at this page there are lots of variations, I chosed the Gtk+/Win32 Development Environment from  the 2.8.20 release, the file was gtk-dev-2.8.20-win32-1.exe
http://gladewin32.sourceforge.net/modules/wfdownloads/visit.php?lid=103
(the devel included glade2)

To install all this stuff (order is significative):
  run gtk-dev-2.8.20-win32-1.exe , I let default values when ofered any adjustements
  run pygtk-2.8.6-1.win32-py2.4.exe
  run pycairo-1.0.2-1.win32-py2.4.exe

Done!!.
Notes:
.The page 'pygtk on win32' was down the first day, latter it come ok.
.At 'gladewin32 project' the last runtimes come with glade3. The editor was done with glade2, so  probably is better to stick with the one that I downloaded.
 
