#!/usr/bin/python3


manual = """
This program allows you to run any exe files in a custom wine prefix. 

Please note that proton is highly unstable for simpler or older games (renpy, rpg maker etc). For that purpose I recommend usual wine.

[Instruction]

`my-proton.py` is the main script. You need to generate `dumpenvs` before running it. The following instruction supposes that this tool is placed in `$HOME/my-proton-tools`.

1. Search for the sniper/runtime path (e.g. `$HOME/.local/steamapps/common/SteamLinuxRuntime_sniper/run`) and edit it. Append `cat /proc/$$/environ > $HOME/my-proton-tools/dumpenvs_sniper` on the top.
2. Start a steam app via proton, and get its pid.
3. `cat /proc/[pid of the game]/environ > $HOME/my-proton-tools/dumpenvs_exe`
4. (optional) Create a prefix file.
    1. Run this program once and generate `dumpenvs_EXE_keys_values` and `dumpenvs_SNIPER_keys_values`
    2. Copy `dumpenvs_EXE_keys_values`/`dumpenvs_SNIPER_keys_values` and rename them to something else.
    3. In the copied files, replace string values next to the keys with 'v', 'p', 'c' or 'd' or delete the line, so that we can successfully load the environment variables required to run wine.
    ```
    v = keep value
    c = create cache dir
    d = delete value (same as just deleting the line)
    a = append value
    p = prepend value
    ```
    4. by passing `-s` (for sniper/runtime) or `-e` (for exe) argument, specify the path of edited files, relative to the tool location.
5. Run `create-prefix.sh` to safely create a new proton environment. (Please edit `SAMPLEAPPID` to specify the steam game id that you have previously played and is a windows-only game)

You can change proton version by specifying --proton and --runtime simultaneously. Also, if you use multiple proton versions, please dump different dumpenv files for different proton versions, and change `-s` and `-e` accordingly.
"""

import os
import subprocess
import sys
import argparse
from envcalc import envcalc, add_wine_prefix

parser = argparse.ArgumentParser(
                    prog='Simple Proton wrapper',
                    description=manual,
                    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('prefixname', help='The name of wineprefix. The wineprefix should be placed at `~/wineprefix/[wineprefix name]`')

parser.add_argument('args', nargs='*', help='Args to be passed on wine or executed directly')

parser.add_argument('-l', '--lang', help="wine language", default='ja_JP.UTF-8')

parser.add_argument('--runtime', help="Specify steam linux runtime container executable path relative to steamapps.", default='SteamLinuxRuntime_sniper/run-in-sniper')

parser.add_argument('--proton', help="Specify Proton Version the path relative to steamapps.", default='Proton - Experimental')

parser.add_argument('-s', '--preset_sniper', help="path to the preset file, relative to this script.", default='preset_sniper_wide')

parser.add_argument('-e', '--preset_exe', help="path to the preset file, relative to this script.", default='preset_exe_wide')

parser.add_argument('--dumpenvs_sniper', help="Specify path to dumped env file for sniper. (Can be obtained by adding 'cat /proc/$$/environ > $HOME/my-proton-tools/dumpenvs_sniper' to '$HOME/.local/steamapps/common/SteamLinuxRuntime_sniper/run')", default='dumpenvs_sniper')

parser.add_argument('--dumpenvs_exe', help="Specify path to dumped env file for exe files. (Can be obtained by running 'cat /proc/12345/environ > $HOME/my-proton-tools/dumpenvs_exe', where 12345 is the pid of the windows exe)", default='dumpenvs_exe')

parser.add_argument('-r', help="execute raw command such as `winetricks` or `wineserver -k`", action='store_true')

if '-r' in sys.argv:
    args_r_index = sys.argv.index('-r')
    args = parser.parse_args(sys.argv[1:args_r_index+1])
    args_r_remain = sys.argv[args_r_index+1:]
else:
    args = parser.parse_args()

sniper_path = os.path.expanduser('~/.local/share/Steam/steamapps/common/%s' % args.runtime)

tool_path = os.path.abspath(os.path.dirname(__file__))

proton_root = os.path.expanduser("~/.local/share/Steam/steamapps/common/%s/" % args.proton)
if not os.path.exists(proton_root):
    proton_root = "/usr/share/steam/compatibilitytools.d/proton"
    if not os.path.exists(proton_root):
        raise FileNotFoundError('Proton executable not found.')

calc_env_sniper = envcalc(args.dumpenvs_sniper, args.prefixname, args.preset_sniper, args.lang, "SNIPER")
proc_env_sniper = os.environb.copy()
proc_env_sniper.update(calc_env_sniper)

calc_env_exe = add_wine_prefix(envcalc(args.dumpenvs_exe, args.prefixname, args.preset_exe, args.lang, "EXE"), args.prefixname)
proc_env_exe = os.environb.copy()
proc_env_exe.update(calc_env_exe)

if args.r:
    proc_args = args_r_remain
else:
    winepath = os.path.join(proton_root, 'files', 'bin', 'wine')
    if not os.path.exists(winepath):
        winepath = os.path.join(proton_root, 'dist', 'bin', 'wine')
    proc_args = [winepath] + args.args

import pickle
with open(os.path.join(tool_path, 'inner', 'arg-pickle'), 'wb') as f:
    pickle.dump([proc_args, proc_env_exe], f)

subprocess.run([sniper_path, os.path.join(tool_path, 'inner', 'my-proton-inner.py')], env=proc_env_sniper)

