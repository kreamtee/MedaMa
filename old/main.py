import os, sys, json
from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import aiohttp, aiofiles
import uvicorn

import hitomi as parse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifespan start")
    yield
    print("lifespan end")

if not os.path.exists('cache'):
    os.mkdir('cache')
if not os.path.exists('image'):
    os.mkdir('image')

@app.get("/")
async def root(request: Request, response: Response, page: int = 1):
    idList = parse.getKorRange(10*(page-1), 10*page-1)
    galList = []
    for id in idList:
        galList.append(parse.data_from_id(id))
    response.headers['cache-control'] = 'max-age=364000'
    return templates.TemplateResponse("index.html", {"request": request, "galList": galList, "page": page})

@app.get("/top/{num}")
async def top(request: Request, num: int):
    idList = parse.getKorTop(num)
    galList = []
    for id in idList:
        galList.append(parse.data_from_id(id))
    return json.dumps(galList)

@app.get("/tag/{query}")
async def tagss(request: Request, query: str, page: int = 1):
    idList = parse.getFromParseTag(query)
    galList = []
    GAL = 12
    start = GAL*(page-1) + 1
    count = GAL
    for count in range(start-1, start-1+count):
        print(f'/tag/{query} {count}', flush=True)
        id = idList[count]
        galList.append(parse.data_from_id(id))
    return templates.TemplateResponse("index.html", {"request": request, "galList": galList, "page": page})

@app.get("/series/{query}")
async def seriess(request: Request, query: str, page: int = 1):
    idList = parse.getKRwithSeries(query)
    galList = []
    GAL = 10
    start = GAL*(page-1) + 1
    count = GAL
    for count in range(start-1, start-1+count):
        print(f'/tag/{query} {count}', flush=True)
        id = idList[count]
        galList.append(parse.data_from_id(id))
    return templates.TemplateResponse("index.html", {"request": request, "galList": galList, "page": page})

@app.get("/view/{id}")
async def view(request: Request, id: int):
    data = parse.data_from_id(id)
    return templates.TemplateResponse("reader.html", {"request": request, "data": data})

@app.get("/image/{id}/{page}")
async def img(request: Request, response: Response, id: int, page: int):
    if not os.path.exists(os.path.join(os.path.join('.','image'),str(id))):
        os.mkdir(os.path.join(os.path.join('.','image'),str(id)))
    file = parse.data_from_id(id)['files'][page-1]
    path = os.path.join(os.path.join(os.path.join('.','image'),str(id)),file['file'])
    header = {'Referer':f'https://hitomi.la/reader/{id}.html'}
    name = file['file']
    if not os.path.exists(path):
        print(f'[{id}] Fetching Image from Hitomi.la', flush=True)
        print(file['url'])
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file['url'], headers=header) as resp:
                    async with aiofiles.open(path, 'wb') as f:
                        await f.write(await resp.read())
        except Exception as e:
            print(e, flush=True)
    response.headers['cache-control'] = 'max-age=364000'
    return FileResponse(path)

@app.get("/reload/{id}/{page}")
async def img_reload(request: Request, id: int, page: int):
    if not os.path.exists(os.path.join(os.path.join('.','image'),str(id))):
        os.mkdir(os.path.join(os.path.join('.','image'),str(id)))
    file = parse.data_from_id(id)['files'][page-1]
    path = os.path.join(os.path.join(os.path.join('.','image'),str(id)),file['file'])
    header = {'Referer':f'https://hitomi.la/reader/{id}.html'}
    name = file['file']
    print(f'[{id}] Reloading Image from Hitomi.la', flush=True)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file['url'], headers=header) as resp:
                async with aiofiles.open(path, 'wb') as f:
                    await f.write(await resp.read())
    except Exception as e:
        print(e, flush=True)
    return FileResponse(path)

if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)