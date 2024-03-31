# My Proton Tools

This script enables you to run any executable files in proton environment.

Please note that proton is highly unstable for simpler or older games (renpy, rpg maker etc). For that purpose I recommend usual wine.

## Installation
Requires Python 3.11, Steam, Steam Linux Runtime installed via Steam, Proton installed via Steam or AUR

## Instruction

`my-proton.py` is the main script. You need to generate `dumpenvs` before running it.

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
7. create a new proton prefix (see `create-prefix-fn.sh`) or copy existing proton prefix located at `~/.local/share/Steam/steamapps/compatdata/[game id]` into `~/wineprefix/[wineprefix name]`

You can change proton version by specifying --proton and --runtime simultaneously. Also, if you use multiple proton versions, please dump different env file for different proton versions, and change --dumpenv accordingly.

## Usage

```
usage: Simple Proton wrapper [-h] [-p PRESET] [-l LANG] [--runtime RUNTIME] [--proton PROTON]
                             [--dumpenvs DUMPENVS] [-r]
                             prefixname [args ...]

This program allows you to run any exe files in a custom wine prefix. 

positional arguments:
  prefixname            The name of wineprefix. The wineprefix should be placed at `~/wineprefix/[wineprefix name]`
  args                  Args to be passed on wine or executed directly

options:
  -h, --help            show this help message and exit
  -p PRESET, --preset PRESET
                        path to the preset file, relative to this script.
  -l LANG, --lang LANG  wine language
  --runtime RUNTIME     Specify steam linux runtime container executable path relative to steamapps.
  --proton PROTON       Specify Proton Version as the path relative to steamapps.
  --dumpenvs DUMPENVS   Specify path to dumped env file (by copying /proc/xxx/environ).
  -r                    execute raw command such as `winetricks` or `wineserver -k`
```