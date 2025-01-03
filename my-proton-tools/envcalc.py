import os

def envcalc(DUMPENVS_PATH: str, PFX_TO_BE_MADE: str, PRESET_PATH: str, LANG: str, LOGID: str) -> dict[bytes, bytes]:
    tool_path = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(tool_path, DUMPENVS_PATH), 'rb') as f:
        dumpenvs = [x.split(b'=', 1) for x in f.read().split(b'\0') if x != b'']

    with open(os.path.join(tool_path, 'dumpenvs_%s_keys_values' % LOGID), 'w') as f:
        f.write('\n'.join([x[0].decode() + ' ' + x[1].decode().replace('\n', '<<<LF>>>') for x in dumpenvs]))

    with open(os.path.join(tool_path, 'dumpenvs_%s_keys' % LOGID), 'w') as f:
        f.write('\n'.join([x[0].decode() for x in dumpenvs]))

    final_env: dict[bytes, bytes] = {}

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
                final_env[k] = os.path.join(PFX_BASEPATH, t[1]).encode()
            case 'd':
                pass
            case 'r':
                final_env[k] = t[1]
            case 'a':
                final_env[k] = v + t[1]
            case 'p':
                final_env[k] = t[1] + v
            case x:
                raise NotImplementedError(k)

    final_env[b'LANG'] = LANG.encode()

    return final_env

def add_wine_prefix(final_env: dict[bytes, bytes], PFX_TO_BE_MADE: str) -> dict[bytes, bytes]:
    PFX_BASEPATH = os.path.expanduser('~/wineprefix/' + PFX_TO_BE_MADE)

    new_env = final_env.copy()
    new_env[b'STEAM_COMPAT_DATA_PATH'] = PFX_BASEPATH.encode()
    new_env[b'WINEPREFIX'] = os.path.join(PFX_BASEPATH, 'pfx').encode()
    new_env[b'WINE_GST_REGISTRY_DIR'] = os.path.join(PFX_BASEPATH, 'gstreamer-1.0').encode()

    return new_env