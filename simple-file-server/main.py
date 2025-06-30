from typing import Union
import os
import re
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import pathvalidate
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

import datetime
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/upload")
def upload(file: UploadFile):
    fn = file.filename
    if fn is None:
        fn = ""
    fn = pathvalidate.sanitize_filename(fn)
    fn = str(datetime.datetime.now().timestamp()) + '.' + fn
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload", fn), 'wb') as f:
        f.write(file.file.read())
    return {"OK": "OK"}

# app.mount("/download", StaticFiles(directory="download", html = True), name="download")

@app.get("/download/{file_path:path}", response_class=HTMLResponse)
def list_files(request: Request, file_path:str):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "download", file_path)
    if os.path.exists(p):
        if os.path.isdir(p):
            files = os.listdir(p)
            files_paths = sorted([re.sub(r"^/", "", re.sub(r"/+", "/", f"{file_path}/{f}")) for f in files])
            print(files_paths)
            return templates.TemplateResponse(
                "filelist.html", {"request": request, "files": files_paths}
            )
        else:
            return FileResponse(p)
    else:
        raise HTTPException(status_code=404, detail="Item not found")