# proton uses dxvk by default.

export PATH=$PATH:/usr/share/steam/compatibilitytools.d/proton
export PATH=$PATH:/usr/share/steam/compatibilitytools.d/proton/dist/bin

PFX_TO_BE_MADE=$HOME/protondata
mkdir -p $PFX_TO_BE_MADE/pfx
touch $PFX_TO_BE_MADE/tracked_files
STEAM_COMPAT_CLIENT_INSTALL_PATH=$HOME/.local/share/Steam STEAM_COMPAT_DATA_PATH=$PFX_TO_BE_MADE proton run

