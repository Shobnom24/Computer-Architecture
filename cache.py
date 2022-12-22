"""
Cache simulation
"""
import sys
from collections import deque

import configuration ##import cache configurations

#n in 2^n-way set associative cache (number of block is 2^n)
#n = 0, 1, 2, ...
#n = 0 => direct-mapped cache
n = configuration.n
#cache size = 2^x
x = configuration.x
#block size 2 ^ y
y = configuration.y
 #apply LRU
LRU = configuration.LRU

# number of sets is 2^s
s = x - y - n
num_of_ways = 2**n


#################################
# tag  |  set index   |  offset
################################

#Block Offset = Memory Address mod 2^y
def get_block_offset(address):
    return address % (2**y)

#Block Address = Memory Address / 2^y
def get_block_address(address):
    return address // (2**y)

#Set Index = Block Address mod 2^s
def get_set_index(address):
    return address % (2**s)

def get_tag(address): #extract tag (m-s-n) bits
    return address >> (s + y) # use y instead on 'n'
 
#update cache's set and block entry with new block entry (empty block/ victim block)
def update_cache_set_and_block(cache, block,set_index, tag):
    #print("miss: ",set_index, tag)
    cache.sets[set_index].queue.append(tag) ##tag append at the end of queue. Most recent reference to this block
    block.valid = True ##valid cache entry
    block.tag = tag ##tag info
    block.LRU = 1  ##For LRU replacement policy

class Block: #define block in set in cache, each block contains 2^y bytes
    
    #constructor
    def __init__(self, y):
        #tag
        self.tag = 0
        #valid flag
        self.valid = False
        #LRU
        self.LRU = 0
        
class CacheSet: #set in cache (append 2^n number of 2^y sized blocks in one set)
    
    #constructor
    def __init__(self, n, y):
        self.blocks = []
        self.queue = deque()
        for i in range(2**n):
            self.blocks.append(Block(y))
            
class Cache: #define Cache
            
    #constructor
    def __init__(self, s, n, y):
        self.sets = []
        for i in range(2**s):
            self.sets.append(CacheSet(n, y))
            
        self.num_hits = 0
        self.num_misses = 0

        
def process(cache, address):
        
    block_offset = get_block_offset(address)
    block_address = get_block_address(address)
    set_index = get_set_index(block_address)
    
    #tag
    tag =  get_tag(address)
    
    #search for the block in the cache
    for block in cache.sets[set_index].blocks:
        if block.valid == True and block.tag == tag: #block is in the cache            
            try:
                cache.sets[set_index].queue.remove(tag)
            except ValueError:
                pass

            cache.sets[set_index].queue.append(tag)
            block.LRU = block.LRU + 1 #increase access                
            cache.num_hits = cache.num_hits + 1
            return
    
    #cache miss and find an empty slot in cache to load the current block 
    for block in cache.sets[set_index].blocks:
        if block.valid == False and block.tag != tag:
            update_cache_set_and_block(cache, block, set_index, tag)
            cache.num_misses = cache.num_misses + 1  
            return
    
    
    #no empty slot in cache, so find the victim block to be replaced with the current block using LRU 
    tag_popped=""        
    victimLRU = 0 #index of block with least recently referenced
    try: 
        tag_popped = cache.sets[set_index].queue.popleft()
    except IndexError:
        pass

    if LRU:
        i = 1
        while i < 2**n:
            if cache.sets[set_index].blocks[i].tag == tag_popped:
                victimLRU = i
            i = i + 1   
    #print(victimLRU)

    block = cache.sets[set_index].blocks[victimLRU] #choose this block to replace
    update_cache_set_and_block(cache, block, set_index, tag)
    cache.num_misses = cache.num_misses + 1  
    return       
    
    
    
  
#read file and process
def main(filename):
    cache = Cache(s, n, y)
    lines = open(filename).readlines()
    for line in lines:
        data = line.split()
        #print(data)
        if (len(data) == 3):
            process(cache, int(data[2], 16)) #process virtual memory address one at a time

    #print result
    print("Cache miss rate: %.2f%%" % ((cache.num_misses * 100.0) / (cache.num_hits + cache.num_misses)))
    pass

if __name__ == "__main__":
    main(sys.argv[1])
