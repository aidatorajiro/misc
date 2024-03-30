PFX_TO_BE_MADE=mypfx
PROTON_PATH="$HOME/.local/share/Steam/steamapps/common/Proton - Experimental"
LANG=ja_JP.UTF-8 STEAM_COMPAT_CLIENT_INSTALL_PATH=$HOME/.local/share/Steam STEAM_COMPAT_DATA_PATH=$HOME/wineprefix/$PFX_TO_BE_MADE $HOME/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/run-in-sniper "$PROTON_PATH/proton" run $@