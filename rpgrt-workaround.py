# A simple script to fix the issue RPG_RT.exe not working when using wine-crossover etc. Requires ffmpeg to convert all mp3 files into wav.
# As of 2024-03-27, somehow Wineskin's winecx 23.7.1 can play mp3, but Gcenx's wine-crossover can't. (because gstreamer not availiable? idk.)
# There is a large performance loss even if you use Wineskin, so it is recommended to convert mp3 into wav.
# Also, you should run "winetricks fontsmooth=disable" to avoid font issue when running RPG_RT.exe, and absolutely set LANG="ja_JP.UTF-8" if your system locale is not japanese.
# TODO: if Sound folder contains mp3, it also should be fixed...

import os
import glob
import subprocess
import shutil

subprocess.run(["mv", "./Music", "./Music_orig"])

subprocess.run(["mkdir", "./Music"])

for p in glob.glob("./Music_orig/*"):
    if not p.endswith("/.DS_Store"):
        if p.endswith(".wav"):
            shutil.copy(p, "./Music/" + os.path.basename(p))
        else:
            subprocess.run(["ffmpeg", "-i", p, "./Music/" + os.path.splitext(os.path.basename(p))[0] + ".wav"])
