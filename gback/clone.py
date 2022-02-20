import urllib.request

page = 1

lst = []

while True:
    api = "https://api.github.com/users/aidatorajiro/repos?per_page=100&page=" + str(page)

    o = urllib.request.urlopen(api)

    d = o.read()

    o.close()

    import json

    j = json.loads(d)
    
    if len(j) == 0:
        break
    
    lst += list(map(lambda x: x['clone_url'], filter(lambda x: x['fork'] == False, j)))
    
    page += 1

import subprocess
import os
import re

for link in lst:
    key = re.match(r".+/(.+)\.git", link)[1]
    print(key)
    if not os.path.exists(key):
        subprocess.run(["git", "clone", link])