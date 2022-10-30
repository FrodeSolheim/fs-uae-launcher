# Compiling FS-UAE Launcher

NOTE: This documentation is somewhat out of date. Changes that should
be incorporated into this document include:

- The recommended way to set up a development environment is now via pipenv
  (pipenv install followed by pipenv shell).
- To build packages, scripts in fsbuild/ are used. See the YAML files
  in .github/workflows for examples.
- Official builds for x86-64 are built via GitHub actions, so the YAML files
  in .github/workflows should always be up to date.
- PyOpenGL is now an external dependency (for FS-UAE Arcade).
- Pyinstaller is now used to bundle together the app (instead of cx_Freeze).

## Running without installing

You can run fs-uae launcher from the source directory as long as the
dependencies are installed. In this case, you should have FS-UAE compiled in
it's own `fs-uae` source directory next to the fs-uae-launcher source
directory, for example:

    src/fs-uae/
    src/fs-uae-launcher/

See the next sections for installing requirements on the diffent supported
platforms.

## Ubuntu / Debian

The following packages are needed:

    sudo apt install python3 python3-pillow python3-pyqt6 \
        python3-pyqt6.qtopengl python3-requests python3-opengl \
        python3-rx python3-typing-extensions

To add support for .lha archives, you also need to have the lhafile
python package installed. You can get `python3-lhafile` from Frode's PPA,
or you can install with pip: `pip3 install lhafile`.

To compile some required files:

    ./bootstrap
    make

You can run the launcher directly from the source directory:

    ./fs-uae-launcher

In this case you should have a matching fs-uae source directory in
`../fs-uae`, and successully compiled fs-uae with `make` (no installation
needed). FS-UAE Launcher will then find the fs-uae and fs-uae-device-helper
binaries from this parallel source directory.

To install to /usr/local, you can run:

    ./bootstrap
    sudo make install

Remember to also install FS-UAE itself.

## Windows

The following instructions / notes assume that an MSYS2 shell has been
installed and configured for building FS-UAE. Though the dependencies
for FS-UAE Launcher do not depend on MSYS2 nor MINGW, the build scripts
are run from an MSYS2 shell.

FIXME: Write about dependencies for running the launcher from the source
directory:

    pacman -S mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-lhafile \
    mingw-w64-x86_64-python3-pillow mingw-w64-x86_64-python3-pyqt6 \
    mingw-w64-x86_64-python3-requests mingw-w64-x86_64-python3-setuptools

And finally, from the fs-uae-launcher source directory:

    ./bootstrap
    make

This will allow you to run fs-uae-launcher from the source directory by
executing (See also the section "Running without installing"):

    ./fs-uae-launcher

The following instructions must be followed in order to build the
distributable version.

Download Python 3.6.8 (or a newer _3.6.x_ version)

- https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe
- Install to default path (...\AppData\Local\Programs\...)
- Default settings, do _not_ add to PATH
- Answer yes to increase max path limit at the end?

Install Visual Studio Build Tools 2019 (vs_buildtools_xxx.yyy.exe)

- FIXME: Link to download page
- Install invidual components:
  - MSVC v140 - VS 2015 C++ build tools (v14.00)
  - Windows 10 SDK (10.0.18362)

Start Windows cmd shell (_not_ MSYS2) and run:

    SET PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\bin\10.0.18362.0\x64
    rc.exe

You might need to replace the version number `10.0.18362.0` in the PATH if you
installed a newer version. We run rc.exe just check that it exists (verify
thatyou do not get errors here). Then follow with:

    cd %LOCALAPPDATA%\Programs\Python\Python36
    python -m pip install --upgrade pip
    python -m pip install lhafile requests pillow pyqt6==6.4.0

In the MSYS2 MinGW 64-bit shell:

    git clone git@github.com:FrodeSolheim/cx_Freeze.git
    cd cx_Freeze
    ./install-windows.sh

## macOS

You need to have Xcode and command line tools instead.

Download and install Python 3 (64-bit only installer) for macOS from
[https://www.python.org/downloads/mac-osx/].

Open a new terminal to make sure the new python3 is on the PATH. You should
verify that pip3 is found in the correct place:

    $ which pip3
    /Library/Frameworks/Python.framework/Versions/3.9/bin/pip3

Then run:

    pip3 install lhafile pillow pyobjc pyqt6 requests rx typing_extensions

And finally, from the fs-uae-launcher source directory:

    ./bootstrap
    make

This will allow you to run fs-uae-launcher from the source directory by
executing (See also the section "Running without installing"):

    ./fs-uae-launcher

In order to compile an app bundle, you need to have cx_Freeze installed,
and in particular, a patched version from
[https://github.com/FrodeSolheim/cx_Freeze]. Download the latest version from
github, and run:

    python3 setup.py install

You also need to have gettext installed for compiling the translation files.
Make sure Homebrew for macOS is installed and run:

    brew install gettext

And then either link gettext into the system with `brew install link` or
add `/usr/local/opt/gettext/bin` to the PATH. You can do this temporarily
with:

    export PATH="/usr/local/opt/gettext/bin:$PATH"

Finally, you can run the following from the source directory:

    cd dist/macos
    make

This should leave you with a .tar.xz containing the app bundle in the source
root directory.
