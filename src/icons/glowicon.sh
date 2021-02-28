#!/bin/sh
set -e
SCRIPTDIR=`dirname "$0"`
if [ "$OS" = "Windows_NT" ]; then
export PYTHONPATH="$SCRIPTDIR/../..;$PYTHONPATH"
else
export PYTHONPATH="$SCRIPTDIR/../..:$PYTHONPATH"
fi
python3 -m launcher.extra.glowicon "$@"
