import json
import shutil
import os

with open("notes.json") as f:
    j = json.load(f)
    i = 0
    for n in j:
        i += 1
        if n["text"]:
            text = n["text"]
        else:
            text = "ぬるぽ"
        if n["folder"]:
            folder = n["folder"]
        else:
            folder = "default"
        if n["title"]:
            title = str(i) + " " + n["title"]
        else:
            title = str(i)
        title = title.replace("/", " ")
        title = title.replace(":", " ")
        if n["embeddedObjects"]:
            for d in n["embeddedObjects"]:
                if d["type"] == "FILE":
                    if d["data"]:
                        if not os.path.exists(os.path.join("out", folder)):
                            os.mkdir(os.path.join("out", folder))
                        shutil.copyfile(d["data"], os.path.join("out", folder, d["data"]))
                        text += "\n![%s](%s)" % (d["data"], d["data"])
                elif d["type"] == "TABLE":
                    if d["data"]:
                        print("unsupported")
                else:
                    print("unsupported")
        if n["links"]:
            print("unsupported")
        if not os.path.exists(os.path.join("out", folder)):
            os.mkdir(os.path.join("out", folder))
        with open(os.path.join("out", folder, title + ".md"), "w") as f:
            f.write(text)

