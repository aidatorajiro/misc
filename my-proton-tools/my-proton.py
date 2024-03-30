#!/usr/bin/python3

manual = """
This program allows you to run any exe files in a custom wine prefix. 

[Instruction]
1. start a steam app via proton, and get its pid
2. `cat /proc/[pid of the game]/environ > dumpenvs` in the directory this program exists
3. run this program once and generate `dumpenvs_keys` and `dumpenvs_keys_values`
4. copy `dumpenvs_keys_values` and rename it.
5. edit the copied file, replacing string values next to the keys with 'v', 'p', 'c' or 'd' or deleting the line
   v = keep value, c = create cache dir (WIP), d = delete value
6. set `PRESET_PATH` in this script to the path of edited file, relative to the program location
7. copy existing proton prefix located at `~/.local/share/Steam/steamapps/compatdata/[game id]` into `~/wineprefix/[wineprefix name]`
"""

import os
import subprocess
import sys
import argparse

parser = argparse.ArgumentParser(
                    prog='Simple Proton wrapper',
                    description=manual,
                    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('prefixname', help='The name of wineprefix. The wineprefix should be placed at `~/wineprefix/[wineprefix name]`')

parser.add_argument('args', nargs='*', help='Args to be passed on wine or executed directly')

parser.add_argument('-p', '--preset', help="path to the preset file, relative to this script. (eg. dumpenvs_preset_minimum)")

parser.add_argument('-l', '--lang', help="wine language (eg. ja_JP.UTF-8)")

parser.add_argument('-r', help="execute raw command such as `winetricks` or `wineserver -k`", action='store_true')

if '-r' in sys.argv:
    args_r_index = sys.argv.index('-r')
    args = parser.parse_args(sys.argv[1:args_r_index+1])
    args_r_remain = sys.argv[args_r_index+1:]
else:
    args = parser.parse_args()

PFX_TO_BE_MADE = args.prefixname
PRESSURE_PATH = os.path.expanduser("~/.local/share/Steam/ubuntu12_64/steam-runtime-sniper/var/tmp-SGAKL2/")
PRESET_PATH = args.preset or 'dumpenvs_preset_minimum'
SPIDER_PATH = os.path.expanduser('~/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/run-in-sniper')

tool_path = os.path.abspath(os.path.dirname(__file__))

proton_root = os.path.expanduser("~/.local/share/Steam/steamapps/common/Proton - Experimental/")
if not os.path.exists(proton_root):
    proton_root = "/usr/share/steam/compatibilitytools.d/proton"

with open(os.path.join(tool_path, 'dumpenvs'), 'rb') as f:
    dumpenvs = [x.split(b'=', 1) for x in f.read().split(b'\0') if x != b'']

with open(os.path.join(tool_path, 'dumpenvs_keys_values'), 'w') as f:
    f.write('\n'.join([x[0].decode() + ' ' + x[1].decode().replace('\n', '<<<LF>>>') for x in dumpenvs]))

with open(os.path.join(tool_path, 'dumpenvs_keys'), 'w') as f:
    f.write('\n'.join([x[0].decode() for x in dumpenvs]))

final_env = {}

# v: copy value
# c: cache (specify cache path at next arg)
# d: delete

with open(os.path.join(tool_path, PRESET_PATH)) as f:
    preset = f.read()

table = {}

for x in preset.split('\n'):
    row = x.split(' ')
    table[row[0]] = row[1:]

def path_replace(path, part):
    return path.replace(part.encode(), os.path.join(PRESSURE_PATH, part[1:]).encode())

for k, v in dumpenvs:
    try:
        t = table[k.decode()]
    except KeyError:
        continue
    match t[0]:
        case 'v':
            final_env[k] = v
        case 'c':
            raise NotImplementedError()
        case 'd':
            pass
        case _:
            raise NotImplementedError()

final_env[b'LANG'] = args.lang or b'ja_JP.UTF-8'
final_env[b'STEAM_COMPAT_DATA_PATH'] = os.path.expanduser('~/wineprefix/' + PFX_TO_BE_MADE)
final_env[b'WINEPREFIX'] = os.path.expanduser('~/wineprefix/' + PFX_TO_BE_MADE + '/pfx')

print(final_env)

proc_env = os.environb.copy()
proc_env.update(final_env)

if args.r:
    proc_args = args_r_remain
else:
    proc_args = [os.path.join(proton_root, 'files', 'bin', 'wine')] + args.args

import pickle
with open(os.path.join(tool_path, 'inner', 'arg-pickle'), 'wb') as f:
    pickle.dump([proc_args, proc_env], f)

subprocess.run([SPIDER_PATH, os.path.join(tool_path, 'inner', 'my-proton-inner.py')])