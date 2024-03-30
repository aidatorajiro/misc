#!/usr/bin/python3

import os
import pickle
import subprocess

tool_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(tool_path, 'arg-pickle'), 'rb') as f:
    [proc_args, proc_env] = pickle.load(f)

os.remove(os.path.join(tool_path, 'arg-pickle'))

proc_env_2 = os.environb.copy()
proc_env_2.update(proc_env)

subprocess.run(proc_args, env=proc_env_2)