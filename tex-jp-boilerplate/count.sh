#!/bin/bash

pdftotext "$1.pdf" - | python3 -c "import sys; import re; print(len(re.sub(r'\s', r'', sys.stdin.read())))" > count.tex