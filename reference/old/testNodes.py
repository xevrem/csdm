#!/usr/bin/python2
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

import hashlib
import argparse
from cdm import CDM, CDMNode

c = CDM()

def buildNodes(exceptionPort):

	for i in range(100):
		if i+8080 == exceptionPort:
			continue
		else:
			n = CDMNode()
			n.Name = "localhost"+str(i)
			n.IP = "127.0.0.1"
			n.Port = 8080 + i
			n.Hash = hashlib.sha1(n.Name.encode('utf-8')).hexdigest()
			n.LongHash = int(n.Hash,16)
			n.Trusted = True
			if n.Hash not in c.Nodes.keys():
				c.Nodes[n.Hash] = n

def main():
	
	parser = argparse.ArgumentParser(description="Hosts a PyCDM node")
	parser.add_argument("-p","--port", type=int, default=8080,
						help="create a node.db excluding the given port")
	parser.add_argument("-n","--name", default="nodes0.db",
						help="create the node database with the given name")

	args = parser.parse_args()


	n = CDMNode()

	c.DBName = args.name
	c.loadNodes()

	buildNodes(args.port)

	c.syncNodes()
	c.closeNodes()


if __name__ == '__main__':
	main()