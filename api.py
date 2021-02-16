import flask
import urllib.request
import requests
import json
import sqlite3
import ocr
import shortuuid
import pytesseract
import argparse
import cv2
import os
import shortuuid
import time
import datetime
from pathlib import Path
from flask import request, jsonify, render_template, redirect, url_for
from bs4 import BeautifulSoup
from PIL import Image
app = flask.Flask(__name__)
app.config["DEBUG"] = True


# Our datafolders

cwd = Path.cwd()
staticpath = Path.joinpath(cwd, 'static')
imgs = Path.joinpath(staticpath, 'img')
textpath = Path.joinpath(cwd, 'text')
dbpath = os.path.join(cwd, "databass.db")

# Database
def setup_db():
    try:
        conn = sqlite3.connect(dbpath)
        print("Created database file. Good")
        cur = conn.cursor()
        print("Connected successfully to {}.".format(dbpath))
        cur.execute("""CREATE TABLE IF NOT EXISTS ocr (
                image_url text, ip text, time text, output text, uuid text
                )""")
        conn.commit()
        print("Created database structure. Good")
        conn.close()
        
    except sqlite3.Error as e: 
        print("Info: {}".format(e.args[0]))

def connect_db():
    try:
        conn = sqlite3.connect(dbpath)
        return conn
    except sqlite3.Error as e:
        print("Error connecting: {}".format(e.args[0]))

def write_to_db(inputdict):
    with connect_db() as conn:
        cur = conn.cursor()
        #print("Writing {} to database".format(inputdict))
        cur.execute("INSERT INTO ocr VALUES (?,?,?,?,?)", [inputdict['image_url'],\
            inputdict['ip'], inputdict['time'], inputdict['output'], inputdict['uuid']])
        conn.commit()


setup_db()
connect_db()
print("DB loc is {}".format(dbpath))
# Homepage
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', status='home')

@app.route('/ocr', methods=['GET'])
def api():
    
    uuid = str(shortuuid.uuid()[:7])
    status = ''
    ip = flask.request.remote_addr
    now = datetime.datetime.now() # get current time of request
    if 'img' in request.args:
        img = str(request.args['img'])
        status = 'ok'
    else:
        status = 'noimg'
        return render_template('index.html', status=status)

    print(img)
    filename = img.split('/')[-1]
    # download linked image
    tic = time.perf_counter() # start timer for calculating how long download takes
    print("Fetching image from {}...".format(img))
    imgdata = requests.get(img, allow_redirects=True)
    with open(Path.joinpath(imgs, filename), 'wb') as savedimg:
        savedimg.write(imgdata.content)
    print("Saved image!")
    toc = time.perf_counter()
    print(f"Downloaded image in {toc - tic:0.4f} seconds")
    imgfile = str(Path.joinpath(imgs, filename))
    print(imgfile)
    arg = "threshold"
    tic = time.perf_counter() # let's time the OCR function

    text, uuidback = ocr.gettext(imgfile, arg, uuid) #run ocr

    toc = time.perf_counter()
    print(f"{uuidback}: {text}")
    print(f"Generating text took {toc - tic:0.4f} seconds")
    print("Saving to DB")
    tic = time.perf_counter() # let's time the db save function
    inputdict = {}
    inputdict['image_url'] = str(img)
    inputdict['ip'] = str(ip)
    inputdict['time'] = str(now)
    inputdict['output'] = str(text)
    inputdict['uuid'] = str(uuidback)
    write_to_db(inputdict)
    toc = time.perf_counter()
    print(f"Saved to DB. Took {toc - tic:0.4f} seconds")
    #return render_template('index.html', status=cwd, uuid=uuidback, text=text, imgfile=filename)
    return render_template('index.html', status='home', text=text, imgfile=filename, uuid=uuidback)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5999)
