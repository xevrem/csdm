#!/usr/bin/python3

"""
    This file is part of CSDM.

    Copyright (C) 2014  Thomas H. Jonell <@Net_Gnome>

    CryptDistMail is free software: you can redistribute it and/or modify
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

from multiprocessing import Pool, Process
import zmq
import json
from csdm import make_value_request, make_manifest_request
from os import urandom
from binascii import hexlify
import base64

class TestClient(object):
    def run(self):
        context = zmq.Context.instance()
        req = context.socket(zmq.REQ)
        req.connect('tcp://127.0.0.1:8080')

        for i in range(100):
            msg = json.dumps(make_value_request(hexlify(urandom(32)).decode()))
            req.send(msg.encode())
            print("C: received: {}".format(req.recv()))

        req.close()
        context.term()

class RetrieveTest(object):
    def run(self):
        context = zmq.Context.instance()
        req = context.socket(zmq.REQ)
        req.connect('tcp://127.0.0.1:8080')

        #man_file = '7e725dae613062ae5dd26799c9baa8a6d19e3126'
        man_file = '69f4075cbceb77d49cf643422884b0ed96e3af39'
        msg = json.dumps(make_manifest_request(man_file))
        req.send(msg.encode())

        res = req.recv().decode()
        #print('C: received: {}'.format(res))

        js = json.loads(res)
        manifest = js['body']

        data = b''

        #get each chunk described in the manifest
        for line in manifest.split('\n'):
            if len(line) < 1:
                continue
            msg = json.dumps(make_value_request(line))
            req.send(msg.encode())

            res = req.recv().decode()
            js = json.loads(res)
            #print('C: received: {}'.format(js['header']))

            data += base64.b64decode(js['body'].encode())

        print('C: writing file...')
        with open('video.mp4', 'wb') as w:
            w.write(data)

        req.close()
        context.term()



def test1():
    #start test client
    client = TestClient()
    client.run()

def test2():
    client = RetrieveTest()
    client.run()

def main():
    #test1()
    test2()

if __name__ == '__main__':
    main()