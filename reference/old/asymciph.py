#!/usr/bin/python3
"""
    This file is part of CSDM.

    Copyright (C) 2013, 2014  Thomas H. Jonell <@Net_Gnome>

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


from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_PSS
from filer import *
import math
import sys

class AsymCiph(object):
    _BLOCK_SIZE = 32

    def __init__(self):
        pass

    def pad(self, data):
        num = len(data) % self._BLOCK_SIZE
        ch = chr(self._BLOCK_SIZE - num)
        return data + (self._BLOCK_SIZE - num) * ch.encode()

    def unpad(self, bfile):
        return bfile[0:-bfile[-1]]
        #return bfile[0:-ord(bfile[-1].decode())]

    def create_private(self, size):
        private = RSA.generate(size)
        return private

    def create_public(self, private):
        public = private.publickey()
        return public

    def create_crypto(self, key):
        return PKCS1_OAEP.new(key)

    def encrypt(self, data, crypto, modulusSize):
        #create the cipher and calculate block size
        dSize = crypto._hashObj.digest_size
        blockSize = modulusSize - 2 - 2 * dSize
        print('blocksize: {}'.format(blockSize))

        #determine file size and blocks according to modulus size
        pdata = self.pad(data)
        size = len(pdata)
        print('data size: {}'.format(size))

        blocks = int(math.ceil(float(size) / float(blockSize)))
        print('blocks: {}'.format(blocks))

        fullCipher = b''
        for i in range(blocks):
            block = pdata[i*blockSize:i*blockSize+blockSize]
            cipher =   crypto.encrypt(block)
            fullCipher += cipher

        return fullCipher

    def decrypt(self, data, crypto, modulusSize):
        dSize = crypto._hashObj.digest_size
        blockSize = modulusSize#modulusSize - 2 - 2 * dSize
        print('blocksize: {}'.format(blockSize))

        #determine file size and blocks according to modulus size
        size = len(data)
        print('data size: {}'.format(size))

        blocks = int(math.ceil(float(size) / float(blockSize)))
        print('blocks: {}'.format(blocks))

        fullMessage = b''
        
        for i in range(blocks):
            block = data[i*blockSize:i*blockSize+blockSize]
            message = crypto.decrypt(block)
            fullMessage += message

        return self.unpad(fullMessage)

    def sign(self, key, message):
        h = SHA256.new()
        h.update(message)
        
        signer = PKCS1_PSS.new(key)
        return signer.sign(h)

    def verify(self, key, message, signature):
        h = SHA256.new()
        h.update(message)

        verifier = PKCS1_PSS.new(key)
        return verifier.verify(h, signature)

    def createKeyPair(self, seed):
        
        return {"public": None, "private": None}

    def write_key(self, filename, key):
        with open(filename, 'wb') as w:
            w.write(key.exportKey('PEM'))

    def read_key(self, filename):
        with open(filename, 'rb') as f:
            data = f.read()
            return RSA.importKey(data)


def main():
    args = sys.argv

    if(len(args) <= 1):
        print('usage is: ./asymciph.py FILENAME')
        return

    filename = args[1]

    ac = AsymCiph()

    private = ac.create_private(2048)
    public = ac.create_public(private)

    with open(filename, 'rb') as f:
        data = f.read()
    
    print("encrypting...")
    crypto = ac.create_crypto(public)
    enc = ac.encrypt(data, crypto, 256)
    
    with open(filename+'.enc', 'wb') as w:
        w.write(enc)

    #f.write_file(enc,filename + ".enc")
    
    print("decrypting...")
    crypto = ac.create_crypto(private)
    dec = ac.decrypt(enc, crypto, 256)
    
    with open(filename+'.dec', 'wb') as w:
        w.write(dec)
    
    signature = ac.sign(private,data)

    print("signature: {}".format(signature))

    if ac.verify(public, data, signature):
        print("authentic")
    else:
        print("not authentic")

if __name__ == '__main__':
    main()