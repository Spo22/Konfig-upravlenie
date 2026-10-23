#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
for fixture in minimal files deep; do
    echo "VFS fixture: $fixture"
    ./run.sh --headless --vfs "examples/vfs/$fixture" \
        --script examples/startup/vfs_check.txt
done
