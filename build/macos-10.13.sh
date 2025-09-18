#!/bin/sh 

python3.7 -m venv .venv

. .venv/bin/activate

python3 -m pip install pyqt5 lhafile macholib pillow pyobjc-core pyobjc-framework-cocoa pyobjc-framework-quartz pyopengl pyqt5 requests typing-extensions
python3 -m pip install pyinstaller

python -m build all
