[IN-WORK: section descriptions and methodologies may change]

Cryptographically Segmented & Distributed Messaging (CSDM)
==========================================================
CSDM is an experimental take on combating modern insecurity in internet communications and problems regarding centralized messaging hubs such as web-mail services. CSDM aims to devise a strategem by which it no longer matters if an adversary has access to the content of a given network as that content in and of itself will be useless. CSDM also aims to abandon concepts such as hierchy of trust or web of trust for a non-trust model or web of distrust, in which no node is trusted unless it proves otherwise.

CSDM attempts to accomplish these goals by employing layered cryptography against segmented messages over a distributed network. 

Distributed Network
-------------------
CSDM distributes all message segements over an overlay network. This overlay network follows a simple, yet proven model: Kademlia. While CSDM doesnt follow the Kademlia protocl 1 to 1, it employs many of its characteristics, but with a twist. Each node in CSDM is a zmq server following a simple protocol implemented in JSON. Messages are stored in chunks with a requisite hash id. These ids are aligned to key-spaces which also align to the requisite nodes in the distributed network. This in-turn, causes the distributed network itself to act as a distributed hashtable, where data is stored progressively closer to the closest id available in the network. In this way, due to progressive replication of data, the data becomes anonymous and almost untraceable as you have no way to tell if the data is an initial store or a replication request.

Cryptography & Segmentation
---------------------------
CSDM utilizes several layers of cryptography employing reliable forms such as AES and newcomers such as Elliptic Curve and Scrypt to create a PGP-like, node-to-node key-unique encryption. To send a message to a known node address, first a "friend request" is made, establishing a shared secret Diffie-Hellmen key between the two nodes. This key, plus a combined sender-receiver address hash and a guessable piece of data such as a day's date combine when hashed to create a unique manifest identifer for a message (i.e., this is what a receiver looks for when checking for messages from a friend). The message itself is hashed (integrity check), then stream ciphered (AES), sgemented with each segment hashed with the hash being added to the message manifest. This manifest is then hashed, ECC encrypted with the destinations shared "public" key and then given the unique manifest identifer as specified earlier. Each hashed segment is given its hash as its filename, binary 64 encoded into text and then stored within the distributed network. After all segments have been successfully stored, then the manifest is also stored into the network for retrieval, decryption, and assembly of the message by its requisite friendly node.

Dependencies
------------
[Python 3.4+](https://python.org)

[docopt](https://pypi.python.org/pypi/docopt)

[seccure](https://pypi.python.org/pypi/seccure)

[pyzmq](https://pypi.python.org/pypi/pyzmq)

[pycrypto](https://pypi.python.org/pypi/pycrypto)