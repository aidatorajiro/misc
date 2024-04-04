#!/usr/bin/python3

PRESET_PATH_DEFAULT = 'dumpenvs_preset_minimum'

manual = """
This program allows you to run any exe files in a custom wine prefix. 

[Instruction]

1. start a steam app via proton, and get its pid
2. `cat /proc/[pid of the game]/environ > dumpenvs` in the directory this program exists
3. run this program once and generate `dumpenvs_keys` and `dumpenvs_keys_values`
4. (optional) Create a prefix file.
    1. copy `dumpenvs_keys_values` and rename it.
    2. in the copied file, replace string values next to the keys with 'v', 'p', 'c' or 'd' or delete the line, so that we can successfully load the environment variables required to run wine.
    ```
    v = keep value, c = create cache dir (WIP), d = delete value, a = append value, p = prepend value
    ```
    3. by changing `PRESET_PATH_DEFAULT` in this script or passing `-p` argument, specify the path of edited file, relative to the program location.
7. copy existing proton prefix located at `~/.local/share/Steam/steamapps/compatdata/[game id]` into `~/wineprefix/[wineprefix name]`

[Note]

You can change proton version by specifying --proton and --runtime simultaneously,
Also, please dump separate env file and change --dumpenv accordingly if you use multiple proton versions...
"""

import os
import shutil
import subprocess
import sys
import argparse

parser = argparse.ArgumentParser(
                    prog='Simple Proton wrapper',
                    description=manual,
                    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('prefixname', help='The name of wineprefix. The wineprefix should be placed at `~/wineprefix/[wineprefix name]`')

parser.add_argument('args', nargs='*', help='Args to be passed on wine or executed directly')

parser.add_argument('-p', '--preset', help="path to the preset file, relative to this script.", default='dumpenvs_preset_minimum')

parser.add_argument('-l', '--lang', help="wine language", default='ja_JP.UTF-8')

parser.add_argument('--runtime', help="Specify steam linux runtime container executable path relative to steamapps.", default='SteamLinuxRuntime_sniper/run-in-sniper')

parser.add_argument('--proton', help="Specify Proton Version the path relative to steamapps.", default='Proton - Experimental')

parser.add_argument('--dumpenvs', help="Specify path to dumped env file (by copying /proc/xxx/environ).", default='dumpenvs')

parser.add_argument('-r', help="execute raw command such as `winetricks` or `wineserver -k`", action='store_true')

if '-r' in sys.argv:
    args_r_index = sys.argv.index('-r')
    args = parser.parse_args(sys.argv[1:args_r_index+1])
    args_r_remain = sys.argv[args_r_index+1:]
else:
    args = parser.parse_args()

PFX_TO_BE_MADE = args.prefixname
PRESET_PATH = args.preset
SNIPER_PATH = os.path.expanduser('~/.local/share/Steam/steamapps/common/%s' % args.runtime)

tool_path = os.path.abspath(os.path.dirname(__file__))

proton_root = os.path.expanduser("~/.local/share/Steam/steamapps/common/%s/" % args.proton)
if not os.path.exists(proton_root):
    proton_root = "/usr/share/steam/compatibilitytools.d/proton"
    if not os.path.exists(proton_root):
        raise FileNotFoundError('Proton executable not found.')

with open(os.path.join(tool_path, args.dumpenvs), 'rb') as f:
    dumpenvs = [x.split(b'=', 1) for x in f.read().split(b'\0') if x != b'']

with open(os.path.join(tool_path, 'dumpenvs_keys_values'), 'w') as f:
    f.write('\n'.join([x[0].decode() + ' ' + x[1].decode().replace('\n', '<<<LF>>>') for x in dumpenvs]))

with open(os.path.join(tool_path, 'dumpenvs_keys'), 'w') as f:
    f.write('\n'.join([x[0].decode() for x in dumpenvs]))

final_env = {}

# v: copy value
# c: cache (specify cache path at next arg)
# d: delete
# r: replace with some value
# a: append some value
# p: prepend some value

with open(os.path.join(tool_path, PRESET_PATH)) as f:
    preset = f.read()

PFX_BASEPATH = os.path.expanduser('~/wineprefix/' + PFX_TO_BE_MADE)

table = {}

for x in preset.split('\n'):
    row = x.split(' ', 2)
    table[row[0]] = row[1:]

for k, v in dumpenvs:
    try:
        t = table[k.decode()]
    except KeyError:
        continue
    match t[0]:
        case 'v':
            final_env[k] = v
        case 'c':
            os.makedirs(os.path.join(PFX_BASEPATH, t[1]), exist_ok=True)
            final_env[k] = os.path.join(PFX_BASEPATH, t[1])
        case 'd':
            pass
        case 'r':
            final_env[k] = t[1]
        case 'a':
            final_env[k] = v + t[1]
        case 'p':
            final_env[k] = t[1] + v
        case _:
            raise NotImplementedError()

final_env[b'LANG'] = args.lang
final_env[b'STEAM_COMPAT_DATA_PATH'] = PFX_BASEPATH
final_env[b'WINEPREFIX'] = os.path.join(PFX_BASEPATH, 'pfx')
final_env[b'WINE_GST_REGISTRY_DIR'] = os.path.join(PFX_BASEPATH, 'gstreamer-1.0')

print(final_env)

proc_env = os.environb.copy()
proc_env.update(final_env)

if args.r:
    proc_args = args_r_remain
else:
    winepath = os.path.join(proton_root, 'files', 'bin', 'wine')
    if not os.path.exists(winepath):
        winepath = os.path.join(proton_root, 'dist', 'bin', 'wine')
    proc_args = [winepath] + args.args

import pickle
with open(os.path.join(tool_path, 'inner', 'arg-pickle'), 'wb') as f:
    pickle.dump([proc_args, proc_env], f)

subprocess.run([SNIPER_PATH, os.path.join(tool_path, 'inner', 'my-proton-inner.py')])