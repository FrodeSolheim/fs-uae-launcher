#!/bin/sh

set -e

. fsbuild/plugin.pre.sh

mkdir -p $PLUGIN_BINDIR

if [ "$SYSTEM_OS" = "macOS" ]; then
cp -a fsbuild/_build/pyinstaller/$PACKAGE_NAME.app $PLUGIN_BINDIR/
else
cp -a fsbuild/_build/pyinstaller/$PACKAGE_NAME/* $PLUGIN_BINDIR/
fi

mkdir -p $PLUGIN_DATADIR
cp -a data/* $PLUGIN_DATADIR/

mkdir -p $PLUGIN_DATADIR/arcade
cp -a ./arcade/res $PLUGIN_DATADIR/arcade/
mkdir -p $PLUGIN_DATADIR/launcher
cp -a ./launcher/res $PLUGIN_DATADIR/launcher/
mkdir -p $PLUGIN_DATADIR/fsgamesys
cp -a ./fsgamesys/res $PLUGIN_DATADIR/fsgamesys/
mkdir -p $PLUGIN_DATADIR/fsui
cp -a ./fsui/res $PLUGIN_DATADIR/fsui/
mkdir -p $PLUGIN_DATADIR/workspace
cp -a ./workspace/res $PLUGIN_DATADIR/workspace/

. fsbuild/plugin.post.sh
