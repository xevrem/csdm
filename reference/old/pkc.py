#!/usr/bin/python2
"""
    This file is part of CSDM.

    Copyright (C) 2013  Thomas H. Jonell <@Net_Gnome> 

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

import io
import math
from cryptlib import createKey, createPublicKey, encrypt, decrypt, createCypherObject
from filer import getFileSize

#encrypts a file
def fileCrypt(filename, key, modulusSize):
	print('encrypting file...')
	f = io.open(filename, 'rb')
		
	#create the cipher and calculate block size
	co = createCypherObject(key)
	dSize = co._hashObj.digest_size
	blockSize = modulusSize - 2 - 2 * dSize
	print('blocksize: ',blockSize)

	#determine file size and blocks according to modulus size
	fsize = getFileSize(f)
	print('file size: ', fsize)
	blocks = int(math.ceil(float(fsize) / float(blockSize)))
	print('blocks: ', blocks)

	fullCipher = ''
	for i in range(0, blocks):
		block = f.read(blockSize)
		cipher = co.encrypt(block)
		fullCipher += cipher

	f = io.open(filename + '.cipher', 'wb')
	f.write(fullCipher)

def fileDecrypt(filename, key, modulusSize):
	print('decrypting file...')
	f = io.open(filename + '.cipher', 'rb')

	#create decrypter
	co = createCypherObject(key)
	dSize = co._hashObj.digest_size
	blockSize = modulusSize#modulusSize - 2 - 2 * dSize
	print('blocksize: ',blockSize)

	#determine file size and blocks according to modulus size
	fsize = getFileSize(f)
	print('file size: ', fsize)
	blocks = int(math.ceil(float(fsize) / float(blockSize)))
	print('blocks: ', blocks)

	fullMessage = ''
	for i in range(0, blocks):
		#print i
		block = f.read(blockSize)
		message = co.decrypt(block)
		fullMessage += message

	f = io.open(filename + '.decipher', 'wb')
	f.write(fullMessage)

		

def main():
	private = createKey('private.pem',2048)
	public = createPublicKey('public.pem', private)
	message = 'hello world'
	co = createCypherObject(public)

	print('message: ' + message)
	#cipher = encrypt(message,public,0)
	cipher = co.encrypt(message)
	print('cipher: ' , cipher)
	co = createCypherObject(private)
	#message = decrypt(cipher, private)
	message = co.decrypt(cipher)
	print('deciphered message: ' + message)
	fileCrypt('out.mp4.manifest',public,256)
	fileDecrypt('out.mp4.manifest', private, 256)
	
if __name__ == '__main__':
	main()
