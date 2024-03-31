# proton uses dxvk by default, however, you have to load specific environment variables before launching wine.
# This script uses PROTON_DUMP_DEBUG_COMMANDS to get list of necessary environment variables
# Please use $PFX_TO_BE_MADE/run to run exe file in the prefix. (DO NOT directly invoke wine!!)

export PATH=/usr/share/steam/compatibilitytools.d/proton/dist/bin:$PATH

export PATH=/usr/share/steam/compatibilitytools.d/proton:$PATH

function create_proton_prefix() {
    PFX_TO_BE_MADE=$HOME/wineprefix/$1
    mkdir -p $PFX_TO_BE_MADE/pfx
    touch $PFX_TO_BE_MADE/tracked_files
    PROTON_DEBUG_DIR=$PFX_TO_BE_MADE PROTON_DUMP_DEBUG_COMMANDS=1 STEAM_COMPAT_CLIENT_INSTALL_PATH=$HOME/.local/share/Steam STEAM_COMPAT_DATA_PATH=$PFX_TO_BE_MADE proton run winecfg
    sed -e 's/c:\\\\windows\\\\system32\\\\steam.exe//' \
        -e '/cd /d' \
        -e '/WINEDEBUG/d' \
        -e 's/WINEPREFIX=/LANG=ja_JP.UTF-8 WINEPREFIX=/' $PFX_TO_BE_MADE/proton_$USER/run > $PFX_TO_BE_MADE/run
    sed '/WINEDLLOVERRIDES/d' $PFX_TO_BE_MADE/run > $PFX_TO_BE_MADE/run_without_override
    sed 's/.*wine64.*/$@/' $PFX_TO_BE_MADE/run > $PFX_TO_BE_MADE/run_cmd
    chmod +x $PFX_TO_BE_MADE/run # for standard run
    chmod +x $PFX_TO_BE_MADE/run_cmd # for tasks such as winetricks or wineserver -k
    chmod +x $PFX_TO_BE_MADE/run_without_override # for non-dxvk run
}
