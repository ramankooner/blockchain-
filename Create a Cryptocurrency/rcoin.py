# Module 2: Create a Cryptocurrency

# To be Installed: 
# Flask == 1.0.2: pip install Flask==1.0.2
# Postman HTTP client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4    in anaconda prompt

# Importing the libraries

import datetime
import hashlib #for cyrptographic hash functions (sha256)
import json
from flask import Flask, jsonify, request  #used for routes (postman). request is for connecting nodes in our decentralized network
import requests #used to catch the right nodes to make sure all the nodes in the network have the same chains
from uuid import uuid4
from urllib.parse import urlparse 

#consensus - make sure all the nodes in the network contain the same blockchain

# Part 1 - Building a Blockchain

class Blockchain:
    
    def __init__(self): 
        self.chain = []
        self.transactions = [] # this contains the transactions before they are added to the block
        # transactions have to go before createBlock so the create block can get the transactions
        self.create_block(proof = 1, previous_hash = '0' ) 
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):           
        block = {'index': len(self.chain) + 1,            
                 'timeStamp': str(datetime.datetime.now()),  
                 'proof': proof,                           
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}

        self.transactions = [] # we empty the list after we add the transactions into our block. we only add the transactions once bc we cant have the same trans twice
        self.chain.append(block)                          
        return block         
                                       
    
    def get_previous_block(self):                           
        return self.chain[-1]                              
 
    def proof_of_work(self, previous_proof):
        new_proof = 1 
        check_proof = False 
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:4] == '0000': 
                check_proof = True        
            else:
                new_proof += 1          
                
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode() 
        return hashlib.sha256(encoded_block).hexdigest()             
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain): 
            block = chain[block_index] 
      
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof'] 
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000': 
                return False 
            previous_block = block
            block_index += 1      
        return True  


    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount })
            
        #index of new block which will get the transaction
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        #address is the address of the node 
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) #netloc is 127.0.0.1:5000. We are adding the url including the port into our nodes set
        
    #finds the longest chain and replaces the rest of the node with the longest chain
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain) # this is the length of our chain rn. If we find one bigger than this then we will update this variable
        
        for node in network:
            # node = 127.0.0.1:5000 
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length'] # this is the length of the chain
                chain = response.json()['chain'] 
                if length > max_length and self.is_chain_valid(chain): # checks to see if the length is larger than the max legnth and chain is valid
                    # we update the max_length variable bc we found a chain larger than the max length
                    # we also update the longest chain to this chain
                    max_length = length
                    longest_chain = chain
       
        if longest_chain: 
             # if the longest chain was replaced we return true bc the longest chain was replaced 
             self.chain = longest_chain
             return True
         
        return False # return false bc the longest chain was not replaced if we get here
        
        
# Part 2 - Mining our Blockchain 
        

app = Flask(__name__)

# Creating an address for the node on Port 5000
# we need to create this address bc whenever a miner mines a block they get some crypto 
# whenever we mine a block, there is a transaction from this node to yourself(miner)

node_address = str(uuid4()).replace('-','') # this creates our node address 

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block() 
    previous_proof = previous_block['proof']    
    proof = blockchain.proof_of_work(previous_proof) 
    previous_hash = blockchain.hash(previous_block)
    
    blockchain.add_transaction(sender = node_address, receiver = 'Raman', amount = 1)
    
    block = blockchain.create_block(proof, previous_hash)

    response = {'message': 'Congratulations, you just mined a block!', 
                'index': block['index'],
                'timeStamp': block['timeStamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200 

    
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston we have a problem. The Blockchain is not valid.'}
    
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    
    return jsonify(response), 201  # this is 201 bc for POSTs we are using the created http status code

# Part 3 - Decentralizing our Blockchain

# Connecting new Nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    # connect new node to all the other nodes
    nodes = json.get('nodes')
    
    if nodes is None:
        return "No node", 400
    
    # add the nodes
    for node in nodes:
        blockchain.add_node(node)
        
    response = {'message': 'All the nodes are now connected. The Rcoin blockchain now contains the following nodes: ',
                'total_nodes': list(blockchain.nodes)}
    
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest chain',
                    'new_chain': blockchain.chain }
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain }
    
    return jsonify(response), 200


# Running the App
    
app.run(host = '0.0.0.0', port = 5000)
    





