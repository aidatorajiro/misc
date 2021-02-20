echo "import time\nt = time.time()\nwhile True:\n    try:\n        j = input()\n        t2 = time.time()\n        if t2 - t > 1:\n            print(j)\n            t = t2\n    except EOFError:\n        break" > temp.py
command 2>&1 | python temp.py
