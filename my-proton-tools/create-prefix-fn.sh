# for advanced apps
create_proton_prefix () {
    PFX_TO_BE_MADE=$1
    mkdir $HOME/wineprefix/$1
    touch $HOME/wineprefix/$1/pfx.lock
    my-proton.py $1 winecfg
}

# for advanced apps
create_proton_prefix_8_0 () {
    PFX_TO_BE_MADE=$1
    mkdir $HOME/wineprefix/$1
    touch $HOME/wineprefix/$1/pfx.lock
    my-proton.py --proton='Proton 8.0' --dumpenvs=dumpenvs-8 $1 winecfg
}

# for other apps
create_wine_prefix () {
    
}