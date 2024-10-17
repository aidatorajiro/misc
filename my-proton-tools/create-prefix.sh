#!/bin/bash

# an app id to copy compatdata from. please specify an app id of the proton-powered game that you own, after installing and running it once.
SAMPLEAPPID=1720850

cd ~/wineprefix

# copy compatdata to wineprefix
cp -r "$HOME/.local/share/Steam/steamapps/compatdata/$SAMPLEAPPID/" "$1"

# for safety, copy windows files rather than linking them
rm -rf "$1/pfx/drive_c/windows"
cp -Lr "$HOME/.local/share/Steam/steamapps/compatdata/$SAMPLEAPPID/pfx/drive_c/windows" "$1/pfx/drive_c/windows"

echo -e "#!/bin/bash\n~/my-proton-tools/my-proton.py $1 -r \"\$@\"" > $1-run.sh
echo -e "#!/bin/bash\n~/my-proton-tools/my-proton.py $1 \"\$@\"" > $1.sh

chmod +x $1-run.sh $1.sh
