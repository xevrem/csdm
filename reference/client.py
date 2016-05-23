#!/usr/bin/python3

"""
    This file is part of CSDM.

    Copyright (C) 2013, 2014, 2015  Erika V. Jonell <@xevrem>

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
import zmq
import sys
import base64
import json
from csdm import make_value_request, make_manifest_request, make_manifest_list_request, make_ping_request, make_friend_request
import os
from filer import Filer, MANIFESTDIR, CHUNKDIR, ASSEMBLEDIR, check_dirs, CHUNKSIZE
from eccpgp import ECCPGP, b64enc, b64dec
from diffie import DiffieHash

class Client(object):
    PROTOCOL = 'tcp://'
    ADDRESS = '127.0.0.1'
    PORT = '8080'

    def __init__(self):
        pass

    def retrieve(self, key, passphrase):
        """
        attempts to retrieve and re-assemble a file with a given manifest key
        """
        #setup zmq connection
        context = zmq.Context.instance()
        req = context.socket(zmq.REQ)
        req.connect(self.PROTOCOL + self.ADDRESS + ':' + self.PORT)

        #if manifest doesnt exist locally, request it
        if not os.path.exists(MANIFESTDIR+key):
            print('C: requesting manifest for {}'.format(key))
            msg = json.dumps(make_manifest_request(key))
            req.send(msg.encode())

            res = req.recv().decode()
            js = json.loads(res)

            #read in the manifest
            manifest = json.loads(js['body'])

            #store manifest locally
            with open(MANIFESTDIR+key, 'wb') as f:
                f.write(js['body'].encode())
        else:
            with open(MANIFESTDIR+key,'r') as f:
                manifest = json.loads(f.read())

        print('C: manifest retrieved...')

        #print(manifest)

        #setup the eccpgp object
        epgp = ECCPGP()
        epgp.generate(passphrase)

        #decrypt the manifest
        manenc = manifest['manifest']
        mandec = epgp.raw_dec(b64dec(manenc), passphrase.encode())
        manifest['manifest'] = json.loads(mandec.decode())

        data = b''

        #get each chunk described in the manifest
        print('C: retrieving chunks...')
        fi = Filer()
        for chunk in manifest['manifest']:
            msg = json.dumps(make_value_request(chunk))
            req.send(msg.encode())

            res = req.recv().decode()
            js = json.loads(res)

            data = b64dec(js['body'])

            fi.write_chunk(data, chunk)
            #with open(CHUNKDIR+chunk, 'wb') as w:
            #    w.write(data)

        print('C: chunks saved...')

        #terminate connection
        req.close()
        context.term()

    def list_manifests(self):
        """
        attempts to get the known manifests from a node
        """
        #setup zmq connetion
        context = zmq.Context.instance()
        req = context.socket(zmq.REQ)
        req.connect(self.PROTOCOL + self.ADDRESS + ':' + self.PORT)

        #issue request
        print('C: geting manifests...')
        msg = json.dumps(make_manifest_list_request())
        req.send(msg.encode())

        res = req.recv().decode()

        print('C: manifest-list retrieved...')

        js = json.loads(res)

        #print manifest keys to screen
        for manifest in js['body']:
            print(manifest)

        #terminate connection
        req.close()
        context.term()


    def get_value(self, key):
        """
        attempts to retrieve a chunk with the specified key value
        """
        #setup zmq connection
        context = zmq.Context.instance()
        req = context.socket(zmq.REQ)
        req.connect(self.PROTOCOL + self.ADDRESS + ':' + self.PORT)

        print('C: geting chunk...')
        msg = json.dumps(make_value_request(key))
        req.send(msg.encode())

        res = req.recv().decode()

        print('C: chunk retrieved...')

        js = json.loads(res)

        data = b64dec(js['body'])

        #check to make sure there was content
        if data is not b'':
            fi = Filer()
            fi.write_chunk(data, key)
            print('C: wrote chunk...')
        else:
            print('C: chunk has no data...')

        #terminate connection
        req.close()
        context.term()

    def ping_node(self):
        """
        attempts to ping a node
        """
        #setup zmq connection
        context = zmq.Context.instance()
        req = context.socket(zmq.REQ)
        req.connect(self.PROTOCOL + self.ADDRESS + ':' + self.PORT)

        print('C: pinging node...')
        msg = json.dumps(make_ping_request())
        req.send(msg.encode())

        res = req.recv().decode()

        print('C: pong received:\n{}'.format(res))

        #terminate connection
        req.close()
        context.term()

    def process_file(self, filename):
        """
        attempts to store a file into CSDM
        """
        #attempt to open file
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = f.read()
        else:
            print('C: file does not exist...')
            return

        print('C: checking for public key...')

        #make sure public key exists
        if os.path.exists('public.ecc'):
            with open('public.ecc', 'rb') as f:
                epub = f.read()
        else:
            print('C: public ecc key does not exist...')
            print('C: please run: client.py gen-key <passphrase>')
            return

        #setup ecc object
        print('C: encrypting...')
        epgp = ECCPGP()
        epgp._epub = epub
        pack = epgp.encrypt(data, filename)

        #process the file into an eccpgp pack
        print('C: processing file...')
        fi = Filer()
        manifest = fi.process_data(pack['payload'].encode())
        manifest['header'] = pack['header']

        #encrypt the manifest
        manstr = json.dumps(manifest['manifest'])
        manenc = b64enc(epgp.raw_enc(manstr.encode(), epub))
        manifest['manifest'] = manenc

        #write manifest to disk
        with open(MANIFESTDIR+manifest['hash'], 'wb') as f:
            f.write(json.dumps(manifest).encode())

        print('C: chunks and manifest created...')


    def get_status(self):
        """
        gets the status of the client
        """
        print('C: status...')


    def gen_key(self, passphrase):
        """
        generates the ecc public key of the given passphrase
        """
        print('C: generating public key...')
        epgp = ECCPGP()
        epgp.generate(passphrase)

        with open('public.ecc', 'wb') as f:
            f.write(epgp._epub)

    def store_file(self, key):
        """
        attempts to store a locally processed file with a given manifest key into the CSDM network
        """
        pass

    def assemble_file(self, key, passphrase):
        """
        attempts to decrypt and assemble the local file defined by the passed manifest key
        """
        #attempt to load the manifest
        print('assembling....')
        with open(MANIFESTDIR+key, 'rb') as f:
            manifest = json.loads(f.read().decode())

        #create eccpgp object
        epgp = ECCPGP()
        epgp.generate(passphrase)

        #attempt to decrypt manifest
        manenc = manifest['manifest']
        mandec = epgp.raw_dec(b64dec(manenc), passphrase.encode())
        manifest['manifest'] = json.loads(mandec.decode())

        data = b''

        #assemble all the blocks
        fi = Filer()
        #size = len(manifest['manifest'])
        #i = 0
        for chunk in manifest['manifest']:
            data += fi.read_chunk(chunk)
            #print('{}% complete'.format(int((i/size)*100)))
            #i += 1

        #create eccpgp structure and assign data
        struct = epgp.make_eccpgp_structure()
        struct['header'] = manifest['header']
        struct['payload'] = data.decode()

        #decrypt the structure into a pgp package
        pack = epgp.decrypt(struct, passphrase)

        #write the decrypted package to assembly directory
        with open(ASSEMBLEDIR+pack['header']['filename'], 'wb') as f:
            f.write(pack['payload'])

        print('file assembled:\t'+ASSEMBLEDIR+pack['header']['filename'])

    def make_friend_request(self):
        #setup zmq connection
        context = zmq.Context.instance()
        req = context.socket(zmq.REQ)
        req.connect(self.PROTOCOL + self.ADDRESS + ':' + self.PORT)

        print('C: making friend request...')
        msg = json.dumps(make_friend_request())
        req.send(msg.encode())

        res = req.recv().decode()

        js = json.loads(res)
        print(js)
        if js['body']['status'] == 'received':
            print('C: request reply received...')
            common = js['body']['common']
            print('C: common code: {}'.format(hex(common)))

            dif = DiffieHash()
            public = dif.make_public(common)
            print('C: public key: {}'.format(hex(public)))

            freq = make_friend_request()
            freq['body'] = {'stage':1,'public':public}
            msg = json.dumps(freq)

            req.send(msg.encode())
            res = req.recv().decode()
            print('C: res:{}'.format(res))

        else:
            print('C: request failed...')


def main(args):
    check_dirs()

    client = Client()
    client.ADDRESS = args['-a']
    client.PORT = args['-p']

    if args['get-file']:
        if args['<manifest>'] is not None:
            client.retrieve(args['<manifest>'], args['<passphrase>'])
        else:
            print('usage: ./client.py get-file <manifest>')
    elif args['list-manifests']:
        client.list_manifests()
    elif args['get-value']:
        if args['<key>'] is not None:
            client.get_value(args['<key>'])
        else:
            print('usage: ./client.py get-value <key>')
    elif args['ping']:
        client.ping_node()
    elif args['process-file']:
        if args['<file>'] is not None:
            client.process_file(args['<file>'])
        else:
            print('usage: client.py process-file <file>')
    elif args['status']:
        client.get_status()
    elif args['gen-key']:
        if args['<passphrase>'] is not None:
            client.gen_key(args['<passphrase>'])
    elif args['store-file']:
        if args['<manifest>'] is not None:
            client.store_file(args['<manifest>'])
    elif args['assemble-file']:
        if args['<manifest>'] is not None:
            client.assemble_file(args['<manifest>'], args['<passphrase>'])
    elif args['friend-request']:
        client.make_friend_request()


if __name__ == '__main__':
    args = docopt(opts)
    #print(args)

    main(args)
