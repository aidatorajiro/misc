#!/bin/bash

if [ ! -d ./venv ]; then
  python3 -m venv venv
  venv/bin/pip3 install -r ./requirements.txt
fi

mkdir upload

mkdir download

venv/bin/uvicorn --reload main:app --host 0.0.0.0
