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

import sys
import requests
import argparse
import hashlib
from cdm import CDMNode, CDM
from flask import Flask, request, make_response
from filer import Filer

#globals
app = Flask(__name__)
port = None
address = None
url = None
nickname = None
hashname = None
f = Filer()	
cdm = CDM()
	
def respond(html, status_code, data=None):
	"""wraps the make_response function"""
	
	return make_response(html,status_code,data=data)

#return about
@app.route('/')
def index():
	return about()

#about server
@app.route('/about')
def about():
	html = """
			<h2>PyCDM</h2>
			<p>This is a reference implementation of a Cryptographic Distributed Mail (CDM) protocol server</p>
			<p>Visit <a href="http://%s/api">API</a> to see the API</p>""" % url
	return make_response(html,200)

#api reference
@app.route('/api')
def api():
	return """
			<h2>API:</h2>
		   	<p>http://servername:port/about - about PyCDM</p>
		   	<p>http://servername:port/api - this web page</P>
		   	<p>http://servername:port/value/[hashkey] - retrieve a value with a hash key</p>
		   	<p>http://servername:port/manifest/[hashkey] - retrieve a manifest with hash</p>
		   	"""

#specific value
@app.route('/lookup/value/<hashkey>')
def value_lookup(hashkey):
	return f.readFile("hashfiles/"+hashkey)

@app.route('/lookup/node/<hashkey>')
def node_lookup(hashkey):
	return "node..."

#specific manifest 
@app.route('/manifest/<hashkey>')
def manifest(hashkey):
	return f.readFile(hashkey+".manifest")

#all known manifests
@app.route('/manifest/')
def manifests():
	return "files..."

#used to accept submission of messages
@app.route('/store/<hashkey>', methods=["GET", "POST"])
def store(hashkey):
	if request.method == "POST":
		#grab the form data
		senthash = request.form['hash']
		ttl = int(request.form['ttl']) - 1
		data = request.form['data']

		print("POSTing store: {} {} {}".format(senthash,ttl,data))

		#check the data hash
		datahash = hashlib.sha1(data).hexdigest()

		if cdm.hashcheck(data,senthash): #senthash == datahash:
			print('message match... make sure to implement store...')
			
			#TODO: try to store locally and propigate according to TTL
			cdm.storeValue(senthash,data,ttl)

			#return positive result
			return make_response("<p>Successful POST of {}".format(hashkey),200)
		else:
			return make_response("<h1>BAD HASH</h1>", 404)
	else:
		#someone trying a GET on resource
		return make_response("<p>GET of {}, not supported...".format(hashkey),200)

#used to submit messages
@app.route('/message/', methods=["GET","POST"])
def message():
	if request.method == "POST":
		to = request.form['to']
		message = request.form['message']
		datahash = hashlib.sha1(message).hexdigest()

		print("POSTing message: {} {} {}".format(to,message,datahash))

		#TODO: need to create the message here...
		data = message

		#attempt to store data 6 deep
		if cdm.storeValue(datahash, data, 6):
			return make_response("<p>all good", 200)
		else:
			return make_response("<h1>failed to store message</h1>", 401)
	else:
		return '''
			<form action="" method="post">
				<h3>To:</h3>
				<p><input type=text name=to>
				<h3>Message:</h3>
				<p><textarea name=message rows=10 cols=40></textarea>
				<p><input type=submit value=Submit>
			</form>
				'''

@app.route('/pingby/<hashkey>')
def ping(hashkey):
	hash = str(hashkey)
	if hash in cdm.Nodes.keys():
		cdm.OnlineNodes[hash] = cdm.Nodes[hash]
		print( "{} IS ONLINE".format(hashkey))
	else:
		print( "ADDING NEW NODE {}".format(hashkey))

	return make_response("<h3>hello {}</h3>".format(hashkey),200)

@app.route('/challenge/')
def challenge():
	if not request.form.has_key("nonce"):
		return make_response("", 403)
		
	nonce = request.form["nonce"]
	foo = nonce
	headers = {"signature": foo}
	return make_response("",200,headers)

@app.route('/friendrequest/<hashkey>')
def friendrequest(hashkey):
	return make_response("foo",200)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Hosts a PyCDM node")
	parser.add_argument("-a","--address", default="127.0.0.1",
						help="Host's IP Address")
	parser.add_argument("-p","--port", type=int, default=8080,
						help="Host's Listening Port")
	parser.add_argument("-db", "--database", default="nodes.db",
						help="Nodes database to use")
	parser.add_argument("-dbg", "--debug", action="store_true",
						help="Enable debugging")

	args = parser.parse_args()

	url = args['--host'] + ":" + str(args['--port'])

	cdm.DBName = args.database
	cdm.load_nodes()


	nickname = "localhost" + str(args['--port'] - 8080)
	hashname = hashlib.sha1(nickname.encode('utf-8')).hexdigest()
	print ("Nickname: {}\nHashname: {}".format(nickname,hashname))


	cdm.self_hash = hashname
	cdm.recurring_ping(30)


	app.debug = args.debug
	app.run(host=args.address, port=args.port)