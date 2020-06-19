## general purpose ts donwloader

import re, base64, json

with open("in.har") as f:
    data = f.read()

prs = json.loads(data)


streams = []

for e in prs['log']['entries']:
    url = e['request']['url']
    if re.match(r".+/.+?\.ts", url):
        cont = e['response']['content']
        stream = cont['text']
        if cont['encoding'] == 'base64':
            stream = base64.b64decode(stream)
        streams.append(stream)

concat = b"".join(streams)

with open("out.ts", "wb") as f:
    f.write(concat)