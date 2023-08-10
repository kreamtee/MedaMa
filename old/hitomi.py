## hitomi.py

import requests
import struct
import json
from bs4 import BeautifulSoup
import os
import re
import gg_dict

def custom_req_get(*args, **kwargs):
    print(args, kwargs)
    return requests.get(*args, **kwargs)

###### Image src Algorithm ######
# gg is from https://ltn.hitomi.la/gg.js
# functions are from https://ltn.hitomi.la/common.js
# loading function is in https://ltn.hitomi.la/gallery.js
######

class gg:
    b = '1691622002/'

    @staticmethod
    def m(g):
        return 0 if g in gg_dict.gg else 1

    @staticmethod
    def s(h):
        m = re.search(r"(..)(.)$", h)
        return str(int(m.group(2) + m.group(1), 16))

def subdomain_from_url(url, base='b'):
    b = 16
    r = re.compile(r"/[0-9a-f]{61}([0-9a-f]{2})([0-9a-f])")
    m = r.search(url)
    if not m:
        return 'a'
    
    g = int(m.group(2) + m.group(1), b)
    return chr(97 + gg.m(g)) + base

def url_from_url(url, base):
    return re.sub(r"//..?\.hitomi\.la/", f'//{subdomain_from_url(url, base)}.hitomi.la/', url)

def full_path_from_hash(hash):
    return gg.b + gg.s(hash) + '/' + hash

def real_full_path_from_hash(hash):
    return re.sub(r"^.*(..)(.)$", r"\2/\1/"+hash, hash)

def url_from_hash(galleryid, image, dir, ext):
    ext = ext or dir or image["name"].split('.')[-1]
    dir = dir or 'images'
    
    return f'https://a.hitomi.la/{dir}/{full_path_from_hash(image["hash"])}.{ext}'

def url_from_url_from_hash(galleryid, image, dir, ext, base):
    if base == 'tn':
        return url_from_url(f'https://a.hitomi.la/{dir}/{real_full_path_from_hash(image["hash"])}.{ext}', base)
    return url_from_url(url_from_hash(galleryid, image, dir, ext), base)

def url_from_file_json(galleryid, file):
    print(file)
    hash = file['hash']
    if not file['hasavif']:
        return url_from_url_from_hash(galleryid, file, 'webp', None, 'a')
    
    else:
        return url_from_url_from_hash(galleryid, file, 'avif', None, 'a')

###### Common Functions ###

def data_from_id(id):
    data = {}
    file_list = []
    if os.path.exists(os.path.join('cache',f'{id}.json')):
        with open(os.path.join('cache',f'{id}.json'),'r') as f:
            data = json.loads(f.read())
        return data
    print(f'[{id}] Fetching Hitomi.la')
    jsurl = f'https://ltn.hitomi.la/galleries/{id}.js'
    jsreq = custom_req_get(jsurl)

    if(jsreq.status_code!=200):
        print(f"[{id}] Error (ID Not exists)")
        return 0
    
    galjson = json.loads(jsreq.content.decode('utf-8').split(' = ')[1].replace('null','"null"'))

    if str(id) != galjson['id']:
        print(f"[{id}] Error (Fetch Error)")
        return 0

    data['name'] = galjson['title']
    for files in galjson['files']:
        fname = files['name']
        hash = files['hash']
        fileurl = url_from_file_json(id, files)
        file_dict = {'file':fname,'hash':hash,'url':fileurl}
        file_list.append(file_dict)

    data['id'] = id
    data['language'] = galjson['language']
    tag_list = []
    if galjson['tags']!="null":
        for tags in galjson['tags']:
            if 'female' in tags.keys():
                if tags['female']:
                    sex = "female:"
                elif tags['male']:
                    sex = "male:"
            else:
                sex = "both:"
            tag_list.append(f"{sex}{tags['tag'].replace(' ','_')}")
    data['tag'] = tag_list
    data['type'] = galjson['type']
    data['date'] = galjson['date']
    data['files'] = file_list
    with open(os.path.join('cache',f'{id}.json'),'w') as f:
        f.write(json.dumps(data))
    return data

def getKor():
    print('[*] Fetching Gallery Buffer', flush=True)
    arrBuf = custom_req_get('https://ltn.hitomi.la/index-korean.nozomi').content
    assert len(arrBuf)%4==0
    count = len(arrBuf)//4
    galList = []
    for i in range(count):
        galList.append(int.from_bytes(arrBuf[i*4:(i+1)*4], "big"))
    return galList

def getKorTop(num: int):
    print('[*] Fetching Gallery Buffer', flush=True)
    arrBuf = custom_req_get('https://ltn.hitomi.la/index-korean.nozomi').content
    print('[*] Fetch Done', flush=True)
    assert len(arrBuf)%4==0
    count = num
    galList = []
    for i in range(count):
        galList.append(int.from_bytes(arrBuf[i*4:(i+1)*4], "big"))
    return galList

def getKorRange(start: int, end:int):
    print('[*] Fetching Gallery Buffer', flush=True)
    arrBuf = custom_req_get('https://ltn.hitomi.la/index-korean.nozomi').content
    print('[*] Fetch Done', flush=True)
    assert len(arrBuf)%4==0
    galList = []
    for i in range(start,end+1):
        galList.append(int.from_bytes(arrBuf[i*4:(i+1)*4], "big"))
    return galList

def getKRwithTag(tag:str):
    print('[*] Fetching Gallery Buffer', flush=True)
    arrBuf = custom_req_get(f'https://ltn.hitomi.la/tag/{tag.replace("_"," ").replace("both:","")}-korean.nozomi').content
    print('[*] Fetch Done', flush=True)
    assert len(arrBuf)%4==0
    count = len(arrBuf)//4
    galList = []
    for i in range(count):
        galList.append(int.from_bytes(arrBuf[i*4:(i+1)*4], "big"))
    return galList

def getKRwithSeries(series:str):
    print('[*] Fetching Gallery Buffer', flush=True)
    arrBuf = custom_req_get(f'https://ltn.hitomi.la/series/{series.replace("_"," ")}-korean.nozomi').content
    assert len(arrBuf)%4==0
    count = len(arrBuf)//4
    galList = []
    for i in range(count):
        galList.append(int.from_bytes(arrBuf[i*4:(i+1)*4], "big"))
    return galList

def getFromParseTag(tags:str):
    tags = tags.split(',')
    result = getKor()
    for tag in tags:
        taglist = getKRwithTag(tag)
        result = list(set(taglist) & set(result))
    return(result)