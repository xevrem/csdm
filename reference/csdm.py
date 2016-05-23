#!/usr/bin/python2

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

import shelve
import hashlib
import os
import time
from bheap import *
from os import urandom
import json

def make_node_struct():
	"""
	returns an empty node structure
	"""
	return {'name':None,
			'id': None,
			'friend': False,
			'friend_data':None,
			'pub_key': None,
			'address': None,
			'port': None}

def make_friend_struct():
	"""
	returns an empty friend structure
	"""
	return {'common':None,
			'public':None,
			'private':None,
			'secret':None}

def make_node_db_struct():
	"""
	returns a node.db structure
	"""
	return {'localhost':None,
			'nodes':[]}

class CSDM(object):
	"""
	Manages CSDM Structures and Information
	"""

	#the node structure
	nodes = None
	db_name = "nodes.db"

	#this node's info
	localhost_node = {}

	#the online Nodes
	online_nodes = {}


	def __init__(self):
		if os.path.exists(self.db_name):
			self.load_db()
		else:
			print('nodes.db not found...')
			self.create_db()

	def init_localhost(self):
		"""
		initializes the localhost node data
		"""
		self.localhost_node = make_node_struct()
		self.localhost_node['name'] = 'localhost'
		self.localhost_node['id'] = self.create_id()
		return

	def load_db(self):
		"""
		loads the nodes.db
		"""
		with open(self.db_name, 'rb') as f:
			data = f.read()
			self.nodes = json.loads(data.decode())
			self.localhost_node = self.nodes['localhost']

	def create_db(self):
		"""
		establishes a new nodes.db
		"""
		print('creating db...')
		self.init_localhost()
		db = make_node_db_struct()
		db['localhost'] = self.localhost_node

		with open('nodes.db', 'wb') as f:
			f.write(json.dumps(db))

		print('wrote nodes.db...')

	def create_id(self):
		"""
		generates a new hash id via OS urandom
		"""
		return hashlib.sha1(os.urandom(32)).hexdigest()

	def get_closest_nodes(self, hashkey):
		"""retruns a BinaryHeap of online nodes ordered by closeness to the hashkey"""
		bh = BinaryHeap()

		#use XOR method to order nodes which are closest to hashkey
		for key in self.online_nodes.keys():
			bh.add(self.online_nodes[key].long_hash ^ long(hashkey,16),key)

		return bh


	def hashcheck(self, value, hash):
		"""verify a value matches it's hash"""
		data_hash = hashlib.sha1(value).hexdigest()
		if data_hash == hash:
			return True
		else:
			return False


def make_request():
	return {'header':{'cmd':'', 'id':gen_unique_id(), 'hash':'', 'signature':''}, 'body':''}

def make_value_request(key):
	req = make_request()
	req['header']['cmd'] = 'value'
	req['body'] = key
	return req

def make_manifest_request(key):
	req = make_request()
	req['header']['cmd'] = 'manifest'
	req['body'] = key
	return req

def make_manifest_list_request():
	req = make_request()
	req['header']['cmd'] = 'manifest-list'
	return req

def make_ping_request():
	req = make_request()
	req['header']['cmd'] = 'ping'
	return req

def make_friend_request():
	req = make_request()
	req['header']['cmd'] = 'friend-request'
	req['body'] = {'stage': 0}
	return req

def make_response():
	return {'header':{'status':'', 'id':gen_unique_id(), 'hash':'', 'signature':''}, 'body':''}

def make_status_response(status):
	res = make_response()
	res['header']['status'] = status
	return res

def gen_unique_id():
	return hashlib.sha1(urandom(32)).hexdigest()

def make_base_manifest():
	return {'header':{'hash':'','signature':'', 'sym_key':''},'manifest':[] }

def make_manifest(manifest_list):
	base = make_base_manifest()
	base['manifest'] = manifest_list
	return base

def encrypt_manifest(manifest):
	return (manifest, 'something', 'anotherthing')

def main():
	csdm = CSDM()


if __name__ == '__main__':
	main()
