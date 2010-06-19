
# Run the build process by entering 'make_bin_distro.py py2exe' or
# 'python make_bin_distro.py py2exe' in a console prompt.
#
# If everything works well, you should find a subdirectory named 'dist'
# containing some files, among them magicor.exe


from distutils.core import setup
import py2exe

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "1.0.0",
    description = "py2exe script",
    name = "magicor game",

    # targets to build
    windows = ["Magicor.py"],
    )
