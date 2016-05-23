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

from Crypto.Hash import HMAC, SHA256
from Crypto.PublicKey import RSA
from Crypto.Protocol import KDF
from Crypto import Random
from Crypto.Util.number import bytes_to_long, long_to_bytes
import seccure
import scrypt
import hashlib
import os

class SQRL(object):
    """
    An implementation of the Secure Quick Reliabe Login protocol (SQRL)
    tailored for CSDM
    """
    def __init__(self):
        pass

    def makesecret(self):
        pass

    def makekeypair(self, secret):
        pass

    def scrypthash(self, secret, password):
        pass

    def scryptstore(self, data, password, maxtime=60):
        pass

    def scryptrestore(self, data, password, maxtime=60):
        pass

    def sign(self, private, message):
        pass

    def verify(self, public, signature, message):
        pass

if __name__ == '__main__':
    #secret = Random.new().read(32)
    secret = os.urandom(32)#long_to_bytes(int('22a5986c8cb3d18a9cc383494151ba2cabeefa53e841d1603cc0265a6a624a82',16))
    print ('SECRET: \t{}'.format(hex(bytes_to_long(secret))))

    #build the key for hmac using scrypt
    skey = scrypt.hash('password_goes_here', hashlib.sha256(secret).hexdigest())[:32]
    #skey = scrypt.encrypt('password', secret,  maxtime=0.5)
    print ('SCRYPT: \t{}'.format(hex(bytes_to_long(skey))))

    #XOR the scrypt key with the secret to create the hmac key
    hashkey = bytes_to_long(secret) ^ bytes_to_long(skey)
    print ('HASHKEY: \t{}'.format(hex(hashkey)))

    #build the hmac hash from the msg using sha256
    hmac = HMAC.new(long_to_bytes(hashkey), msg='foo'.encode(), digestmod=SHA256.new())
    hash = hmac.hexdigest()
    print ('HMAC: \t\t{}'.format(hash))

    #create the ECC private key from the hmac hash
    newprv = hash.encode()
    newpub = str(seccure.passphrase_to_pubkey(newprv))
    print ('ECC PRIVATE: \t{}'.format(newprv))
    print ('ECC PUBLIC:  \t{}'.format(newpub))

    #sign the message
    sig = seccure.sign('bar'.encode(), newprv)
    print ('ECC SIG: \t{}'.format(sig))

    #attempt verification
    if seccure.verify('bar'.encode(), sig, newpub):
        print('GOOD SIGNATURE')
    else    :
        print('BAD SIGNATURE')
