#!/bin/sh

set -e

. fsbuild/plugin.pre.sh

mkdir -p $PLUGIN_BINDIR

if [ "$SYSTEM_OS" = "macOS" ]; then
cp -a fsbuild/_build/pyinstaller/$PACKAGE_NAME.app $PLUGIN_BINDIR/$PACKAGE_NAME_PRETTY.app
else
cp -a fsbuild/_build/pyinstaller/$PACKAGE_NAME/* $PLUGIN_BINDIR/
fi

mkdir -p $PLUGIN_DATADIR
cp -a data/* $PLUGIN_DATADIR/

mkdir -p $PLUGIN_DATADIR/arcade
cp -a ./arcade/data $PLUGIN_DATADIR/arcade/
mkdir -p $PLUGIN_DATADIR/launcher
cp -a ./launcher/data $PLUGIN_DATADIR/launcher/
mkdir -p $PLUGIN_DATADIR/fsgamesys
cp -a ./fsgamesys/data $PLUGIN_DATADIR/fsgamesys/
mkdir -p $PLUGIN_DATADIR/fsui
cp -a ./fsui/data $PLUGIN_DATADIR/fsui/
mkdir -p $PLUGIN_DATADIR/workspace
cp -a ./workspace/data $PLUGIN_DATADIR/workspace/

PLUGIN_SKIP_APPIFY=1
PLUGIN_SKIP_STANDALONE=1

. fsbuild/plugin.post.sh
