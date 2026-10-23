#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if ./run.sh --headless --vfs examples/vfs/minimal \
    --script examples/startup/stop_on_error.txt; then
    echo 'Expected the startup script to fail' >&2
    exit 1
fi
if ./run.sh --headless --vfs examples/vfs/nonexistent \
    --script examples/startup/vfs_check.txt; then
    echo 'Expected the missing VFS to fail' >&2
    exit 1
fi
