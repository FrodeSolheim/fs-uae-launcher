#!/bin/sh
set -e
SCRIPTDIR=`dirname "$0"`
export PYTHONPATH="$SCRIPTDIR/../..:$PYTHONPATH"
python3 -m launcher.extra.colorizeicon "$@"
