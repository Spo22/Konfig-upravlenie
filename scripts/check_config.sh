#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --headless --vfs examples/vfs/minimal \
    --script examples/startup/config_ok.txt
./run.sh --headless --vfs examples/vfs/files \
    --script examples/startup/config_ok.txt
