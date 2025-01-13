#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"

. paper-name.sh

export PATH=/usr/local/texlive/2024/bin/x86_64-linux:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin

latexmk -synctex=1 -interaction=nonstopmode -file-line-error -lualatex -outdir="$(pwd)" "$PAPER_NAME.tex"

bash ./count.sh "$PAPER_NAME"

cp "$PAPER_NAME.pdf" "$PAPER_NAME_RENAME_TO.pdf"