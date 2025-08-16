import memory_graph as mg
import random
random.seed(0) # use same random numbers each run

class BinTree:

    def __init__(self, value=None, smaller=None, larger=None):
        self.smaller = smaller
        self.value = value
        self.larger = larger

    def add(self, value):
        if self.value is None:
            self.value = value
        elif value < self.value:
            if self.smaller is None:
                self.smaller = BinTree(value)
            else:
                self.smaller.add(value)
        else:
            if self.larger is None:
                self.larger = BinTree(value)
            else:
                self.larger.add(value)
        mg.block(mg.show, mg.stack())

tree = BinTree()
n = 100
for i in range(n):
    value = random.randrange(n)
    tree.add(value)
