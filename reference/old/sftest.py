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

from filer import *
from symciph import *
from asymciph import *
import sys

f = Filer()

def retrieveBlock(blockname):
	if blockname is '':
		return None
		
	print 'retrieving block: ', blockname
	return f.readFile('hashfiles/' + blockname)

def assembleFiles(manifest, blocksize):
	print 'blocksize: ', blocksize
	print 'retrieving parts...'

	final = ''

	buf = manifest.split('\n')

	for blockname in buf:
		block = retrieveBlock(blockname)
		if block is not None:
			final += block

	return final

def main():
	args = sys.argv

	if len(args) <= 1:
		print 'bad arguments...'
		return

	sc = SymCiph()

	filename = args[1]

	data = f.readFile(filename)

	key = sc.createKey()
	iv = sc.createIV()

	crypto = sc.createCrypto(key, iv)
	ef = sc.encrypt(crypto, data)

	manifestName = f.createFilesNEW(filename, ef, int(args[2]))
	manifest = f.readFile(manifestName)
	data = assembleFiles(manifest, int(args[2]))

	crypto = sc.createCrypto(key,iv)
	df = sc.decrypt(crypto, data)
	f.writeFile(df, filename + ".dec")

if __name__ == '__main__':
	main()