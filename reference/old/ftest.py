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
import argparse
import requests
from filer import Filer


class FGet(object):

	URL = None

	def retrieveBlock(self, blockname):
		if blockname is '':
			return None
		if blockname is None:
			return None
			
		print 'retrieving block: ', blockname
		req = requests.get(self.URL+'value/'+blockname)
		return req.content

	def assembleFiles(self, manifest, blocksize):
		print 'blocksize: ', blocksize
		print 'retrieving parts...'

		final = ''

		buf = manifest.split('\n')

		for blockname in buf:
			if blockname == '':
				continue
			block = self.retrieveBlock(blockname)
			if block is not None:
				final += block

		return final

def main():
	parser = argparse.ArgumentParser(description="Retrieves a file from a PyCDM node")

	parser.add_argument("filename", help="name of file to retrieve")
	parser.add_argument("-a", "--address", default="127.0.0.1",
						help="ip address of host")
	parser.add_argument("-p", "--port", default="8080",
						help="port of host")

	args = parser.parse_args()

	filename = args.filename
	URL = "http://" + args.address + ":" + args.port + "/"

	print 'retrieving manifest for {} from {}'.format(filename,URL)

	resp = requests.get(URL + 'manifest/' + filename)

	manifest = resp.content

	fget = FGet()
	fget.URL = URL

	rfile = fget.assembleFiles(manifest, 512)
	
	f = Filer()
	f.writeFile(rfile,filename + '.ret')
	
	



if __name__ == '__main__':
	main()