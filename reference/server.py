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

opts = """CSDM Server

Usage:
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
import zmq
import json
from multiprocessing import Process
from filer import Filer, check_dirs
import base64
import os
from diffie import DiffieHash

class Server:
    cdm = None
    url = None
    nickname = None
    hashname = None
    fi = Filer()
    ADDRESS = '127.0.0.1'
    PORT = '8080'
    PROTOCOL = 'tcp://'

    def __init__(self, args):
        pass

    def interupt_signal(self, signum, frame):
        """
        process an interrupt signal
        """
        print('\nS: Shutting Down...')
        self.cleanup()

    def cleanup(self):
        """
        perform any cleanup
        """
        self.running = False
        self.router.close()
        self.context.term()

    def setup(self):
        """
        perform any needed setup
        """
        signal.signal(signal.SIGINT, self.interupt_signal)
        self.cache_manifest_names()

    def cache_manifest_names(self):
        tups = os.walk('manifests')
        tup = tups.__next__()
        self.manifests = tup[2]
        print(self.manifests)

    def run(self):
        """
        Run ZMQ server and handle connections
        """
        self.setup()

        self.context = zmq.Context.instance()
        self.router = self.context.socket(zmq.ROUTER)
        #self.router.bind('tcp://127.0.0.1:8080')
        self.router.bind(self.PROTOCOL + self.ADDRESS + ':' + self.PORT)

        self.poller = zmq.Poller()
        self.poller.register(self.router, zmq.POLLIN)

        self.running = True

        while self.running:
            try:
                #poll and timeout every 60th of a second to do other processing
                socks = dict(self.poller.poll(timeout=1000))
            except Exception as e:
                if e is zmq.error.Again or zmq.error.ZMQError:
                    self.cleanup()
                    break
                print('S: something else: ' + str(Exception))
                self.cleanup()
                break

            if socks.get(self.router) == zmq.POLLIN:
                id, null, data = self.router.recv_multipart()
                if data is not None:
                    print("S: received: " + data.decode())

                    j = json.loads(data.decode())

                    response = self.process(j)
                else:
                    response = json.dumps(csdm.make_status_response('BAD'))

                self.router.send_multipart([id,null,response.encode()])
            else:
                #print('S: doing other...')
                self.do_other()

        print('S: Exiting...')

    def process(self, js):
        if 'manifest' == js['header']['cmd']:
            key = js['body']

            if not self.fi.manifest_exists(key):
                #dont have manifest, need to search network for manifest
                return json.dumps(csdm.make_status_response('NO_FILE'))

            manifest = self.fi.read_manifest_file(key)
            response = csdm.make_status_response('OK')
            response['body'] = manifest
            return json.dumps(response)
        elif 'value' == js['header']['cmd']:
            key = js['body']

            if not self.fi.chunk_exists(key):
                #dont have chunk, need to search network for chunk
                return json.dumps(csdm.make_status_response('NO_FILE'))

            chunk = self.fi.read_chunk(key)
            response = csdm.make_status_response('OK')
            response['body'] = base64.b64encode(chunk).decode()
            return json.dumps(response)
        elif 'manifest-list' == js['header']['cmd']:
            response = csdm.make_status_response('OK')
            #print('manifests {}'.format(self.manifests))
            response['body'] = self.manifests
            return json.dumps(response)
        elif 'ping' == js['header']['cmd']:
            response = csdm.make_status_response('OK')
            response['body'] = 'pong'
            return json.dumps(response)
        elif 'friend-request' == js['header']['cmd']:
            response = csdm.make_status_response('OK')

            common = self.process_friend_reqest(js)
            response['body'] = {'status':'received',
                                'stage':0,
                                'common':common }
            return json.dumps(response)
        else:
            return json.dumps(csdm.make_status_response('OK'))

    def do_other(self):
        #print("S: processing other...")
        pass

    def process_friend_reqest(self, request):
        print("S: received friend request...")

        if request['body']['stage'] == 0:

            #create new diffie object for this friend and gen the common
            dif = DiffieHash()
            common = dif.gen_key()

            friend = csdm.make_friend_struct()
            friend['private'] = dif.private
            friend['common'] = common
            friend['public'] = dif.make_public(common)
            return common
        elif request['body']['stage'] == 1:
            return None


if __name__ == '__main__':
    args = docopt(opts)
    #print(args)

    check_dirs()

    #start the server
    server = Server(args)
    server.ADDRESS = args['-a']
    server.PORT = args['-p']
    server.run()
