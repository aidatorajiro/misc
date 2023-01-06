gcc bridges.m -framework Foundation -framework AppKit -framework Python -F/usr/local/Frameworks -fPIC -shared -o bridges.so

python3 run.py