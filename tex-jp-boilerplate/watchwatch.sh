#!/bin/bash

. paper-name.sh
npx chokidar "$PAPER_NAME.tex" -c "bash buildbuild.sh"
