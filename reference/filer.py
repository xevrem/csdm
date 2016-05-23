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

import hashlib
import io
import sys
import math
import os

CHUNKDIR = 'chunkfiles/'
MANIFESTDIR = 'manifests/'
ASSEMBLEDIR = 'assemblies/'
CHUNKSIZE = 16000

class Chunk(object):
    data = None
    hash = None

    def __init__(self):
        pass

class HashFile(object):
    hash = None
    chunks = []
    chunk_size = None

    def __init__(self):
        pass

def check_dirs():
    if not os.path.exists(CHUNKDIR):
        os.makedirs(CHUNKDIR)

    for i in range(256):
        if i < 16:
            if not os.path.exists(CHUNKDIR+'0'+hex(i)[2:]):
                os.makedirs(CHUNKDIR + '0' + hex(i)[2:])
        else:
            if not os.path.exists(CHUNKDIR+hex(i)[2:]):
                os.makedirs(CHUNKDIR+hex(i)[2:])


    if not os.path.exists(MANIFESTDIR):
        os.makedirs(MANIFESTDIR)

    if not os.path.exists(ASSEMBLEDIR):
        os.makedirs(ASSEMBLEDIR)


class Filer(object):

    def __init__(self):
        pass

    def hash_value(self, data):
        """
        returns the hash value of a piece of binary data
        """
        return hashlib.sha1(data).hexdigest()

    def make_chunks(self, data, chunk_size):
        """
        turns data into a Chunk array
        """
        size = len(data)
        num_chunks = math.ceil(size / chunk_size)
        chunks = []

        for i in range(num_chunks):
            chunk = Chunk()
            chunk.data = data[i*chunk_size:i*chunk_size+chunk_size]
            chunk.hash = self.hash_value(chunk.data)
            chunks.append(chunk)

        return chunks

    def write_chunks(self, chunks):
        """
        writes a chunk to the chunkfiles directory with its hash as its name
        """
        if not os.path.exists('chunkfiles'):
            os.mkdir('chunkfiles')

        for chunk in chunks:
            with open(CHUNKDIR+'/'+chunk.hash[:2]+'/'+chunk.hash, 'wb') as f:
                f.write(chunk.data)

    def read_chunk(self, chunkname):
        """
        reads a chunk
        """
        with open(CHUNKDIR+'/'+chunkname[:2]+'/'+chunkname, 'rb') as f:
            return f.read()

    def create_hashfile(self, data, chunk_size):
        """
        creates a HashFile from a piece of data with chunks of chunk_size
        """
        hashfile = HashFile()
        hashfile.hash = self.hash_value(data)
        hashfile.chunk_size = chunk_size
        hashfile.chunks = self.make_chunks(data, chunk_size)

        return hashfile

    def chunks_from_manifest(self, manifest):
        """
        returns a chunk array from a given manifest string
        """
        chunks = []
        for line in manifest.split('\n'):
            if len(line) == 0:
                continue

            if not os.path.exists(CHUNKDIR+'/'+line[:2]+'/'+line):
                print('missing chunk: '+line)
                return None

            data = self.read_chunk(line)
            chunk = Chunk()
            chunk.hash = line
            chunk.data = data
            chunks.append(chunk)

        return chunks

    def process_file(self, file, chunk_size=CHUNKSIZE):
        """
        makes chunks from a file and creates requisite manifest by reading file in pieces of chunksize
        """
        chunknames = []
        with open(file, 'rb') as f:
            data = f.read()
            size = len(data)
            num_chunks = math.ceil(size / chunk_size)
            fhash = self.hash_value(data)

            for i in range(num_chunks):
                chunk = data[i*chunk_size:i*chunk_size+chunk_size]
                hash = self.hash_value(chunk)
                chunknames.append(hash)
                self.write_chunk(chunk, hash)

        manifest = ''

        for chunkname in chunknames:
            manifest += chunkname + '\n'

        self.write_manifest_file(manifest, fhash)

    def process_data(self, data, chunk_size=CHUNKSIZE):
        """
        makes chunks from data and creates requisite manifest by reading file in pieces of chunksize
        """

        chunknames = []
        size = len(data)
        num_chunks = math.ceil(size / chunk_size)
        fhash = self.hash_value(data)

        for i in range(num_chunks):
            chunk = data[i*chunk_size:i*chunk_size+chunk_size]
            hash = self.hash_value(chunk)
            chunknames.append(hash)
            self.write_chunk(chunk, hash)

        manifest = {'header': None, 'hash':fhash, 'manifest': []}

        for chunkname in chunknames:
            manifest['manifest'].append(chunkname)

        #self.write_manifest_file(manifest, fhash)
        return manifest


    def write_chunk(self, data, name):
        with open(CHUNKDIR+'/'+name[:2]+'/'+name, 'wb') as w:
            w.write(data)

    def chunks_to_file(self, chunks):
        """
        assembles a chunk array, returning the reassembled data file
        """
        data = b''
        for chunk in chunks:
            data += chunk.data

        return data

    def make_manifest(self, hashfile):
        """
        makes a manifest string from a HashFile
        """
        manifest = ''
        for chunk in hashfile.chunks:
            manifest += chunk.hash + '\n'

        return manifest

    def write_manifest_file(self, manifest, filename):
        """
        writes the manifest string to a file
        """
        if not os.path.exists(MANIFESTDIR):
            os.mkdir(MANIFESTDIR)

        with open(MANIFESTDIR+filename, 'w') as f:
            f.write(manifest)

    def read_manifest_file(self, filename):
        """
        reads a manifest file and returns the manifest string
        """
        with open(MANIFESTDIR+filename, 'r') as f:
            manifest = f.read()

        return manifest

    def manifest_exists(self, key):
        return os.path.exists(MANIFESTDIR+key)

    def chunk_exists(self, key):
        return os.path.exists(CHUNKDIR+'/'+key[:2]+'/'+key)


def main():
    args = sys.argv

    if len(args) <= 2:
        print('usage is filer.py FILE_LOCATION BLOCK_SIZE')
        return

    fi = Filer()
    fi.process_file(args[1], int(args[2]))


if __name__ == '__main__':
    main()
