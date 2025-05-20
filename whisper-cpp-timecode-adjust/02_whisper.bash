#!/bin/bash
set -eo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"

export LD_LIBRARY_PATH="$SCRIPT_DIR/bin/lib:$SCRIPT_DIR/bin/lib64"

find ./orig/ -name "*.wav" | xargs -n1 -I{} bash -c "./bin/bin/whisper-cli -m ./whisper.cpp/models/ggml-large-v3.bin -l en -f '{}' > '{}.txt'"
