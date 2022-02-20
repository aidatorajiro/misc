import os
import subprocess

subdirs = list(map(os.path.abspath, os.walk("./").__next__()[1]))

for d in subdirs:
    print(d)
    os.chdir(d)
    subprocess.run(["git", "pull"])