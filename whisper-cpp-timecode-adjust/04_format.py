#!/bin/python3
import json
from typing import Union
from utils import *

with open('out.json') as f:
    obj = json.load(f)

concatenated = sum(obj, [])

last_print_tc: Union[None, tuple[int, int, int, float]] = None
period = 60

for line in concatenated:
    start: tuple[int, int, int, float] = tuple(line['start'])
    end: tuple[int, int, int, float] = tuple(line['end'])
    text = line['text']
    if last_print_tc is None:
        last_print_tc = start
        print()
        print_timecode(start)
        print()
    else:
        sec_diff = from_timecode(start) - from_timecode(last_print_tc)
        if sec_diff > period:
            last_print_tc = start
            print()
            print_timecode(start)
            print()
    print(text)
