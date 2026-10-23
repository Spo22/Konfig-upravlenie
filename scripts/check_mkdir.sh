#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --headless --vfs examples/vfs/deep \
    --script examples/startup/all_commands.txt
if test -e examples/vfs/deep/projects/python/reports; then
    echo 'ERROR: mkdir unexpectedly changed source directory' >&2
    exit 1
fi
if ./run.sh --headless --vfs examples/vfs/deep \
    --script examples/startup/mkdir_errors.txt; then
    echo 'Expected duplicate mkdir failure' >&2
    exit 1
fi
if ./run.sh --headless --vfs examples/vfs/deep \
    --script examples/startup/mkdir_missing_parent.txt; then
    echo 'Expected missing-parent mkdir failure' >&2
    exit 1
fi
