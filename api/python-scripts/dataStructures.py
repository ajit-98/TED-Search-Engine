import sys
from bson.objectid import ObjectId
#minHeap to merge a list of tuples based on the param index
class MinHeap:
    def __init__(self,maxsize,param=0,type='ObjectId'):
        self.maxsize=maxsize
        self.param = param
        self.size=0
        self.type = type
        if self.type == 'ObjectId':
            self.Heap=[(-1,ObjectId("FFFFFFFFFFFFFFFFFFFFFFFF")) for i in range(maxsize+1)]
            self.Heap[0] = (-1,ObjectId("000000000000000000000000"))
        elif self.type == 'int':
            self.Heap=[(-1,sys.maxsize) for i in range(maxsize+1)]
            self.Heap[0] = (-1,-sys.maxsize)
        self.FRONT = 1
    
    def parent(self,pos):
        return pos//2
    
    def leftChild(self,pos):
        return 2*pos
    def rightChild(self,pos):
        return (2*pos) + 1
    def isLeaf(self,pos):
        if pos > self.size//2 and pos<=self.size and pos>self.maxsize//2:
            return True
        return False
    def swap(self,fpos,spos):
        temp = self.Heap[fpos]
        self.Heap[fpos] = self.Heap[spos]
        self.Heap[spos] = temp
    def minHeapify(self,pos):
        if pos != self.maxsize and not self.isLeaf(pos):
            if self.leftChild(pos)<=self.maxsize and self.rightChild(pos) <=self.maxsize:
                if(self.Heap[pos][self.param]>self.Heap[self.leftChild(pos)][self.param]) or (self.Heap[pos][self.param]>self.Heap[self.rightChild(pos)][self.param]):
                    if self.Heap[self.rightChild(pos)][self.param]<self.Heap[self.leftChild(pos)][self.param]:
                        smallest = self.rightChild(pos)
                    else:
                        smallest = self.leftChild(pos)
                    self.swap(pos,smallest)
                    self.minHeapify(smallest)
            elif self.leftChild(pos) ==self.maxsize:
                if self.Heap[pos][self.param] >self.Heap[self.leftChild(pos)][self.param]:
                    smallest = self.leftChild(pos)
                    self.swap(pos,smallest) 

    def insert(self,element):
        if self.size >=self.maxsize:
            return 0
        self.size+=1
        self.Heap[self.size] = element
        current = self.size
        while self.Heap[current][self.param] < self.Heap[self.parent(current)][self.param]:
            self.swap(current,self.parent(current))
            current = self.parent(current)
    
    def minHeap(self):
        for pos in range(self.size//2,0,-1):
            self.minHeapify(pos)
    def remove(self):
        popped = self.Heap[self.FRONT]
        if self.type == 'ObjectId':
            self.Heap[self.FRONT] = (-1,ObjectId("FFFFFFFFFFFFFFFFFFFFFFFF"))
            self.minHeapify(self.FRONT)
        elif self.type == 'int':
            self.Heap[self.FRONT] = (-1,sys.maxsize)
            self.minHeapify(self.FRONT)
        self.size = self.size-1
        return popped
    def min(self):
        return self.Heap[self.FRONT]
        
    def removeandreplace(self,element):
        popped = self.Heap[self.FRONT]
        self.Heap[self.FRONT] = element
        self.minHeapify(self.FRONT)
        return popped
            
            

if __name__ == "__main__":
    minHeap = MinHeap(3,param=1)
    minHeap.insert((1, ObjectId('5f2114f80bb6905a48349805'))) 
    minHeap.insert((0, ObjectId('5f2114f70bb6905a4834901e'))) 
    minHeap.removeandreplace((0,ObjectId('5f2114f80bb6905a48349815')))
    minHeap.minHeapify(minHeap.FRONT)
    print(minHeap.size)
    print(minHeap.isLeaf(minHeap.FRONT))
    print(minHeap.Heap)