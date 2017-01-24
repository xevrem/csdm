#!/usr/bin/env python3
"""
    This file is part of CSDM.

    Copyright (C) 2013, 2014, 2015, 2016, 2017  Erika V. Jonell <@xevrem>

    CSDM is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

opts = """CSDM Server

Usage:paws
    server.py -h | --help
    server.py [-a <address> -p <port> -d <database>]

Options:
    -h --help      Show this screen.
    -a=<addres>     Host address to use [default: 127.0.0.1]
    -p=<port>       Port to use [default: 8080]
    -d=<database>   Database to use [default: nodes.db]
"""

from docopt import docopt
import hashlib
import csdm
#from csdm import CSDM, make_status_response
import signal
import json
from filer import Filer, check_dirs
import base64
import os
from diffie import DiffieHash
import asyncio

from paws.paws import run_server
from paws import pahttp
from paws.palog import AsyncLogger


fi = Filer()
global log, manifest
manifests = None
log = None

def cache_manifest_names():
    global manifests

    tups = os.walk('manifests')
    tup = tups.__next__()
    manifests = tup[2]
    print(manifests)

def package(js):
    return dumps(js)

async def root(req, res):
    return res

async def manifest(req, res):
    global log

    if req.body is not None:
        #js = json.loads(req.body)
        #log.log('S: manifest request received:\n{}'.format(js))
        #key = js['body']
        key = req.wildcards['key']
        log.log(f'S: manifest request received: {key}')

        if not fi.manifest_exists(key):
            res.body = json.dumps(csdm.make_status_response('NO_FILE'))
            return res

        manifest = fi.read_manifest_file(key)
        resjs = csdm.make_status_response('OK')
        resjs['body'] = manifest
        res.body = json.dumps(resjs)

        return res
    else:
        res.body = json.dumps(csdm.make_status_response('BAD'))
        return res

async def value(req, res):
    global log

    if req.body is not None:
        #js = json.loads(req.body)
        #log.log('S: value request received:\n{}'.format(js))
        #key = js['body']
        key = req.wildcards['key']
        log.log(f'S: value request received: {key}')

        if not fi.chunk_exists(key):
            res.body = json.dumps(csdm.make_status_response('NO_FILE'))
            return res

        chunk = fi.read_chunk(key)
        rdata = csdm.make_status_response('OK')
        rdata['body'] = base64.b64encode(chunk).decode()
        res.body = json.dumps(rdata)

        log.log('S: sending value...')

        return res
    else:
        res.body = json.dumps(csdm.make_status_response('BAD'))
        return res

async def manifest_list(req, res):
    global manifests
    global log

    resjs = csdm.make_status_response('OK')
    resjs['body'] = manifests
    res.body = json.dumps(resjs)
    log.log('S: sending manifest list...')
    return res

async def ping(req, res):
    return res

async def friend_request(req, res):
    return res

def routes(app):
    app.add_route('/', root)
    app.add_route('/manifest/{key}', manifest)
    app.add_route('/value/{key}', value)
    app.add_route('/manifest_list', manifest_list)
    app.add_route('/ping', ping)
    app.add_route('/friend_request', friend_request)

def main():
    global log

    #determine command line arguments
    args = docopt(opts)

    #ensure all the directories are properly setup
    check_dirs()

    #cache manifest IDs
    cache_manifest_names()

    log = AsyncLogger(loop=asyncio.get_event_loop(), debug=True)

    #start the server
    run_server(routing_cb=routes, host=args['-a'], port=int(args['-p']), processes=8, use_uvloop=True, debug=False)


if __name__ == '__main__':
    main()
