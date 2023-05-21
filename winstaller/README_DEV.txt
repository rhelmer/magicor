
Building the Windows installer:
You need to have:
	a python + pygame installation that works well with magicor
	py2exe module, used to build an intermediary binary installation
	Inno Setup ( a free tool, follow links in py2exe page if you need to download )
	svn (subversion)
	A checkout of the magicor relevant version to be built.
	windows XP OS 

By the way of reference, I have
	python 2.4.3
	pygame 1.7.1
	py2exe 0.6.5
	inno setup 5.1.8.0
	subversion (svn) 1.3.2 

	win xp + sp2

The last rev of Magicor tested was rev 175


Not all is fully automated and fancy:

.Edit make_installer.bat to set correct paths for
	python.exe
	Inno setup compiler

.Edit inno_script.iss to set the magicor version ( currently set to 1.0 )

.Theres no error control. Check the output.

How to build:
You must work from a checkout for the relevant version, under control of svn.
If your working copy has all the files at the desired version, it is ok to to use to build. Files in your working copy not added to the project are not included.
*Check* that you have a magicor.conf with the desired values at the standart location prior to build.
After you adjust paths and version, create a console, cd to winstaller dir and run make_installer.bat


