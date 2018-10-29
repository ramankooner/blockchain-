# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 18:04:56 2018

@author: Raman Kooner
"""

# Module 1: Create a Blockchain

# To be Installed: 
# Flask == 1.0.2: pip install Flask==1.0.2
# Postman HTTP client: https://www.getpostman.com/

# Importing the libraries

import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain

class Blockchain:
    
    def __init__(self): 
        self.chain = [] # this is the chain containing the blocks. this is a list
        self.create_block(proof = 1, previous_hash = '0' ) # this is the genesis block so it is the first block of the chain so its prevhash is 0
        
        # the block we mine will give us the proof from solving the proof of work 
        # previous_hash links two blocks 
        # this defines the new block that is mined
    def create_block(self, proof, previous_hash):            # this creates a dictionary with 4 essential keys
        block = {'index': len(self.chain) + 1,               # index will take the length of the chain and add 1 to it
                 'timeStamp': str(datetime.datetime.now()),  # this gives us the exact time the block is mined
                 'proof': proof,                             # this comes from the proof of work function
                 'previous_hash': previous_hash }            # this gives us the previous_hash
        
        self.chain.append(block)                             # this will append the block to our chain list
        return block                                         # return the block so we can display this info in postman
    
    def get_previous_block(self):                            # returns the last block of the current chain we are dealing with at any time
        return self.chain[-1]                                # -1 gives us the last index of the chain
    
    # proof of work is the piece of data the miners have to find in order to mine the new block
    # we will make a problem and to solve the problem they will need to find a specific number that is the proof of work
    # we need a problem that has a number that is hard to find but easy to verify 
    # we need it hard to get bc if it is easy then they can easily get it and the cyrpto loses its value
    
    def proof_of_work(self, previous_proof):
        new_proof = 1 # we initialize this to 1 bc to solve the problem we will increment this variable at each iteration of the while loop until we get the right proof
        check_proof = False # this will get set to true when we find the proof 
        
        while check_proof is False:
            # sha256 hash function
            # four leading zeros, the more leading zeros the harder it will be for the miners to solve the problem
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            # check to see if the first four characters are zeros
            if hash_operation[:4] == '0000': # checks to see if the first four characters of the string are four zeros
                check_proof = True           # miner wins
            else:
                new_proof += 1               # this will increment new proof again to try with a new value
                
        return new_proof # this is the proof that gave us the hash with four leading zeros 
    
    def hash(self, block): # takes block as input and returns the sha256 cryptographic hash of the block
        encoded_block = json.dumps(block, sort_keys = True).encode() # sort_keys makes sure our block dictionary is sorted by keys, this will turn our block into a string
        return hashlib.sha256(encoded_block).hexdigest()             # returns the cryptographic hash of our block
    
    # checks to see if our blockchain is valid
    def is_chain_valid(self, chain):
        previous_block = chain[0] # gives us the first block of the chain
        block_index = 1
        while block_index < len(chain): # we increment block index by 1 until it reaches the lenght of the chain
            block = chain[block_index]  # this is the current block we are dealing with in the loop
            # check to see if the previous_hash of the block we are dealing with is equal to the hash of the previous block
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof'] # proof of our previous block, gets the proof key of our previous block
            proof = block['proof']# gets proof of our current block
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000': # checks to see if the hash operation contains four leading zeros
                return False # if it doesnt we return false
            previous_block = block # we update it so that the previous_block becomes the current block at the current iteration 
            block_index += 1       # we increment the looping variable 
        return True  # we return true if everything is good and we didnt get false anywhere else 

# Part 2 - Mining our Blockchain 
        
# Creating a Web app
app = Flask(__name__)


# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block() # gives us the last block of the chain  
    previous_proof = previous_block['proof']         # gives us the proof of the previous block
    proof = blockchain.proof_of_work(previous_proof) # gives us the proof of our future new block that will be added to the blockchain
    
    # we need to get the previous_hash 
    previous_hash = blockchain.hash(previous_block)
    
    block = blockchain.create_block(proof, previous_hash) # this will create the block
    # making a new dictionary and taking the values of the block dictionary
    response = {'message': 'Congratulations, you just mined a block!', # will contian the info of the block and a message congratulating the miner for mining the block
                'index': block['index'],
                'timeStamp': block['timeStamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    
    return jsonify(response), 200 

# Getting the full Blockchain 
    
@app.route('/get_chain', methods = ['GET'])

# displays the full chain in our block chain
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return jsonify(response), 200

#Check if blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston we have a problem. The Blockchain is not valid.'}
    
    return jsonify(response), 200


# Running the App
    
app.run(host = '0.0.0.0', port = 5000)
    





