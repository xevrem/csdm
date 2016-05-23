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

import io
import sys
import math
import binascii

from Crypto import Random
from Crypto.Cipher import AES
from filer import *


class SymCiph(object):
    _BLOCK_SIZE=32

    def __init__(self):
        pass

    def create_key(self):
        return Random.new().read(32)

    def create_iv(self):
        return Random.new().read(AES.block_size)

    def pad(self, data):
        num = len(data) % self._BLOCK_SIZE
        ch = chr(self._BLOCK_SIZE - num)
        return data + (self._BLOCK_SIZE - num) * ch.encode()

    def unpad(self, bfile):
        return bfile[0:-bfile[-1]]

    def encrypt(self, crypto, data):
        #print('encrypting...')
        pfile = self.pad(data)
        cdata = crypto.encrypt(pfile)
        return cdata

    def decrypt(self, crypto, data):
        #print('decrypting...')
        ddata = self.unpad(crypto.decrypt(data))
        return ddata

    def create_crypto(self, key, iv):
        return AES.new(key, AES.MODE_CBC, iv)

def main():
    args = sys.argv

    if(len(args) <= 1):
        print('usage is: ./symciph.py FILENAME')
        return

    filename = args[1]

    sc = SymCiph()
    f = Filer()

    key = sc.create_key()
    iv = sc.create_iv()

    crypto = sc.create_crypto(key,iv)

    with open(filename, 'rb') as f:
        data = f.read()

    ef = sc.encrypt(crypto, data)

    with open(filename + '.enc', 'wb') as w:
        w.write(ef)

    #f.writeFile(ef, filename + '.enc')

    #reset crypto
    crypto = sc.create_crypto(key,iv)

    with open(filename + '.enc', 'rb') as f:
        data = f.read()

    df = sc.decrypt(crypto, data)

    with open(filename + '.dec', 'wb') as w:
        w.write(df)
    #f.writeFile(df, filename + '.dec')


if __name__ == '__main__':
    main()
