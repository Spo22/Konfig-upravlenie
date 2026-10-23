#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --headless --vfs examples/vfs/deep \
    --script examples/startup/commands.txt
if ./run.sh --headless --vfs examples/vfs/deep \
    --script examples/startup/commands_errors.txt; then
    echo 'Expected invalid cd to stop the script' >&2
    exit 1
fi
