Contents
-------
1  Copyright, license and contributors
2  About
3  Gameplay instructions
4  Troubleshoting
5  Special thanks


1  Copyright, license and contributors
--------------------------------------
Copyright 2006 Peter Gebauer, licensed as public domain. See LICENSE for
details.

First up, the game could not have reached the level of quality without
these people helping out:

 - Frederic Wagner: debian packages, levels and bugfixes.
 - Claudio Canepa: windows compability, levels and bugfixes.


2  About
--------
Magicor is a puzzle game similar to Solomons Key, but quite different.

 - Magicor was writen in Python language, using the pygame library
 - For updates, source code and other info go to: the Magicor project page:
   http://sourceforge.net/projects/magicor   ( Magicor project page )
   http://magicor.sourceforge.net            ( Magicor home page )
   http://sourceforge.net/forum/forum.php    ( Magicor forums )


3  Gameplay instructions
------------------------
THE GOAL OF THE GAME is to annihilate all burning fires. You do this
by pushing blocks of ice until they collide with a burning fire.
When the ice blocks hit burning fire the block and the fire are destroyed.
Once all fires are extinguished the level is completed.

You can't push blocks that are connected (either to a wall or another block
of ice) or blocked. If the ice block cannot be pushed and it's within climbing
range, the player will climb atop the block instead.

Blocks that are not connected to anything will free-fall unless there is
something below them (ground, another ice block or the player). Blocks falling
on fire will also extinguish the fire, just as a pushed block.

You can create and destroy ice blocks on the player's lower sides. That is
below and left/right to the player, not straight down or straight left/right.
With this magic technique you can fill gaps or destroy supporting ice blocks.

Touching enemies, traps, burning lava or burning fires will kill the 
player. The same as with falling down in oblivion.

Have fun!


4  Troubleshoting
-----------------
  - In old hardware you can set 'eyecandy=false' for better results ( from the options menu or by direct edit magicor.conf )
  - If you hear no sound, use the DirectX diagnostics and tools ( provided with windows ) and try to lower the hardware acceleration slider for sounds. By example old mobos for pentium 3 with via chipset dont give sound at full acceleration but run ok with one notch less.
  - Fullscreen is very slow at this time, dont use it.
  - At present time the level editor is not suported by the windows installer ; you must get the source version for this.


5 Special thanks
----------------
  - GNU
  - Debian
  - python.org
  - libSDL hackers
  - PyGame hackers
  - The Gimp hackers (wonderful tool! all graphics made with it)
  - Michael Krause (author of soundtracker, which I used to make the music) 

Thanks to all testers and puzzle-game fans out there!
