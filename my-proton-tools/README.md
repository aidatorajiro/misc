# My Proton Tools

This script enables you to run any executable files in proton environment.

Please note that proton is highly unstable for simpler or older games (renpy, rpg maker etc). For that purpose I recommend usual wine.

## Installation
Requires Python 3.11, Steam, Steam Linux Runtime installed via Steam, Proton installed via Steam or AUR

Tested in Arch Linux and Ubuntu with XFCE. Both snap and direct installation of steam supported.

## Instruction

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
