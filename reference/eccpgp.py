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

from symciph import SymCiph
import json
import seccure
from hashlib import sha1
import base64

class ECCPGP(object):
    _iv = None
    _skey = None
    _eprv = None
    _epub = None
    _passphrase = None

    def __init__(self, passphrase=''):
        self.generate(passphrase)

    def generate(self, passphrase):
        self._eprv = passphrase.encode()
        self._epub = str(seccure.passphrase_to_pubkey(self._eprv)).encode()

    def make_eccpgp_structure(self):
        return {'header':{'filename':None,
                           'hash':None,
                           'key':None,
                           'iv': None},
                'payload':None}

    def encrypt(self, data, filename='no_name.file'):
        struct = self.make_eccpgp_structure()
        struct['header']['filename'] = filename

        struct['header']['hash'] = sha1(data).hexdigest()

        sc = SymCiph()
        self._skey = sc.create_key()
        self._iv = sc.create_iv()
        struct['header']['key'] = b64enc(self._skey)
        struct['header']['iv'] = b64enc(self._iv)
        crypto = sc.create_crypto(self._skey, self._iv)

        struct['payload'] = b64enc(sc.encrypt(crypto, data))

        header = json.dumps(struct['header'])
        enc_header = seccure.encrypt(header.encode(),self._epub)
        struct['header'] = b64enc(enc_header)

        return struct

    def decrypt(self, eccpgp_struct, passphrase=''):
        struct = self.make_eccpgp_structure()

        header = seccure.decrypt(b64dec(eccpgp_struct['header']), passphrase.encode())
        struct['header'] = json.loads(header.decode())

        sc = SymCiph()
        self._skey = b64dec(struct['header']['key'])
        self._iv = b64dec(struct['header']['iv'])
        crypto = sc.create_crypto(self._skey, self._iv)

        payload = sc.decrypt(crypto, b64dec(eccpgp_struct['payload']))
        struct['payload'] = payload

        return struct

    def raw_enc(self, data, pubkey=''):
        return seccure.encrypt(data, pubkey)

    def raw_dec(self, data, prvkey=''):
        return seccure.decrypt(data, prvkey)


def b64enc(data):
    return base64.b64encode(data).decode()

def b64dec(data):
    return base64.b64decode(data.encode())

def main():
    epgp = ECCPGP()
    print(epgp.make_eccpgp_structure())

    epgp.generate('this is a private key')
    print('private key: {}\n public key: {}'.format(epgp._eprv, epgp._epub))

    with open('lorem.txt','rb') as f:
        data = f.read()

    #pack = epgp.encrypt(b'fjord!!!','message.txt')
    pack = epgp.encrypt(data, 'lorem.txt')
    print(pack)
    print(json.dumps(pack))

    print(epgp.decrypt(pack,'this is a private key'))

if __name__ == '__main__':
    main()
