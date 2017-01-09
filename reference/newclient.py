#!/usr/bin/env python3
"""
    This file is part of CSDM.

    Copyright (C) 2013, 2014, 2015, 2016  Erika V. Jonell <@xevrem>

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

opts = """CSDM Client

Usage:
    client.py -h | --help
    client.py get-file <manifest> <passphrase> [-a <address> -p <port>]
    client.py list-manifests [-a <address -p <port>]
    client.py get-manifest <manifest> [-a <address -p <port>]
    client.py get-value <key> [-a <address> -p <port>]
    client.py process-file <file>
    client.py ping [-a <address> -p <port>]
    client.py status
    client.py gen-key <passphrase>
    client.py store-file <manifest> [-a <address> -p <port>]
    client.py assemble-file <manifest> <passphrase>
    client.py friend-request [-a <address> -p <port>]

Options:
    -h --help          Show this screen.
    -a=<address>        CSDM node address to query [default: 127.0.0.1]
    -p=<port>           CSDM node port to use in query [default: 8080]
    -d=<database>       Database to use [default: nodes.db]
    -m=<manifest-key>   Key for manifest of file to retrieve
"""

from docopt import docopt
import sys
import base64
import json
from csdm import make_value_request, make_manifest_request, make_manifest_list_request, make_ping_request, make_friend_request
import os
from filer import Filer, MANIFESTDIR, CHUNKDIR, ASSEMBLEDIR, check_dirs, CHUNKSIZE
from eccpgp import ECCPGP, b64enc, b64dec
from diffie import DiffieHash

import asyncio
import uvloop
from paws.paws import get
from paws.pahttp import HttpRequest

fi = Filer()

async def do_get_manifest(host, port, key):
    print('C: requesting manifest for {}'.format(key))
    msg = json.dumps(make_manifest_request(key))
    data = await get(url=f'http://{host}/manifest', port=port, body=msg)
    req = HttpRequest(data)
    print('C: manifest retrieved...')
    #print('\n{}'.format(req.body))
    return req.body

async def do_get_manifest_list(host, port):
    print('C: requesting manifest list...')
    data = await get(url=f'http://{host}/manifest_list', port=port)
    req = HttpRequest(data)
    print('C: manifest list retrieved...')
    js = json.loads(req.body)
    for manifest in js['body']:
        print(manifest)

async def do_get_value(host, port, key):
    #print('C: requesting value...')
    msg = json.dumps(make_value_request(key))
    data = await get(url=f'http://{host}/value', port=port, body=msg)
    req = HttpRequest(data)
    #print('C: value retrieved:')
    #print('{}'.format(req.body))
    return req.body

def execute_async_cmd(coro, *args):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(coro(*args))
    loop.run_until_complete(future)
    #loop.run_forever()

async def get_file(host, port, manifest_key, passphrase):
    data = await do_get_manifest(host, port, manifest_key)
    js = json.loads(data)
    manifest = json.loads(js['body'])

    print('C: manifest retrieved...')

    #setup epgp object
    epgp = ECCPGP()
    epgp.generate(passphrase)

    #dectrypt the manifest
    manenc = manifest['manifest']
    mandec = epgp.raw_dec(b64dec(manenc), passphrase.encode())
    manifest['manifest'] = json.loads(mandec.decode())

    print(manifest['manifest'])

    data = b''

    #retrieve each chunk and store it...
    for chunk in manifest['manifest']:
        cdata = await do_get_value(host, port, chunk)
        jdata = json.loads(cdata)
        data = b64dec(jdata['body'])

        fi.write_chunk(data, chunk)

    print('C: got chunks...')

def main(args):
    #print(args)

    if args['list-manifests']:
        execute_async_cmd(do_get_manifest_list, args['-a'], args['-p'])
    elif args['get-manifest']:
        if args['<manifest>'] is not None:
            execute_async_cmd(do_get_manifest, args['-a'], args['-p'], args['<manifest>'])
        else:
            print('usage: ./client.py get-manifest <manifest>')
    elif args['get-file']:
        if args['<manifest>'] is not None:
            execute_async_cmd(get_file, args['-a'], args['-p'], args['<manifest>'], args['<passphrase>'])
        else:
            print('usage: ./clinet.py get-file <manifest> <passphrase>')
    elif args['get-value']:
        if args['<key>'] is not None:
            execute_async_cmd(do_get_value, args['-a'], args['-p'], args['<key>'])
        else:
            print('usage: ./client.py get-value <key>')
    else:
        print('you done sumfin wrong...')

if __name__ == '__main__':
    args = docopt(opts)
    #asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    main(args)
