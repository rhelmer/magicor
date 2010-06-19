
set pythonpath = "c:\python24\python.exe"

rem *** be very carefull with the following line, you can wipe out your entire HD
rd  /Q /S .\magi 
mkdir .\magi
copy ..\magicor.py .\magi\*.*
copy ..\magicor.conf .\magi\*.*
svn export ..\magicor .\magi\magicor

rem aca se podria borrar el subdir editor, pero de momento no lo hacemos

rem hide a problem with magicor.conf path search
%pythonpath% undirty.py

rem build a binary distribution with py2exe
copy make_bin_distro.py .\magi\*.*
cd magi
%pythonpath%  make_bin_distro.py py2exe
cd ..
svn export ..\data .\magi\dist\data
rd  /Q /S .\magi\dist\data\levels\_test 

copy ..\magicor.conf .\magi\dist\*.*

rem add cleaned docs, convert line endings
copy ..\LICENSE .\magi\dist\LICENCE.TXT
%pythonpath% un2dos.py
copy readme_win.txt .\magi\dist\README.TXT

copy penguin_icon3.ico .\magi\dist\penguin_icon3.ico

rem at this point winstaller\magi\dist is a binary distribution.
rem The installer will be built from this binary distro
"C:\Archivos de programa\Inno Setup 5\Compil32.exe" /cc inno_script.iss

rem cleanup
rem *** be very carefull with the following line, you can wipe out your entire HD
rd  /Q /S .\magi 



