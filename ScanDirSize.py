#ScanDirSize.py

'''
ScanDirSize extends os.scandir output with size and visualization information
 
 How Size Extension works:
 - os.scandir is used recursively to create a tree representing directories structure 
 - Each node of the tree, either sub-tree (directory) or leaf (file) has a size in bytes attached 
 - Tree size is calculated as a sum of all sub-trees and files under it.
  
How Visualization works:
 - The goal is to represent each file in proportion to its size
 - Given dimentions of the box (glyph) for the whole tree structure, each node (either sub-tree or file) gets a inner box assigned to it.  
    - when depth of the visualization is unlimited (=very large) - only leafs (files) are assigned to boxes.
    - when the depth is limited, directories at the maximum depth are assigned to boxes and their content is not get visualized
 - After the assigment, the boxes can be plotted to visualize the whole tree content. 
 - Each box represents a file/directory and its size is proportional to file/directory size on the disk.
'''


import os
from pathlib import Path, PurePosixPath
from collections import namedtuple

Box = namedtuple('Box', ('size', 'x0', 'y0', 'dx', 'dy'))
Box.__doc__ = '''\
    rectangular coordinates representing object of size\
    (x0, y0) - low left corner
    (dx, dy) - (width, height)
'''


class Node():
    '''
    Common base class for Leaf and Tree 
    '''
    def __init__(self, name, size=0):
        self._size = size
        self._name = name
        self.box = None

    def __str__(self):
        return f'{self.__class__.__name__}("{self.name}", {self.size})'

    @property
    def size(self):
        return self._size

    @property
    def pretty_size(self):
    
        if (self.size < 1024):
            return '{:d} Bytes'.format(self.size)
    
        if (self.size < 1024*1024):
            return '{:.3f} KB'.format(self.size/1024)

        if (self.size < 1024*1024*1024):
            return '{:.3f} MB'.format(self.size/(1024*1024))
    
        return '{:.3f} GB'.format(self.size/(1024*1024*1024))
    

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return None

    def boxit(self, box : Box, depth = 0, box_ratio = 0.5) :

        '''
        Assign box inside the input box to the node.
        Return the rest  
        '''
        if not box.size :
            return box
        ratio = self.size/box.size
        if (box.dx > box_ratio*box.dy):
            self.box = Box(self.size, box.x0, box.y0, int(round(box.dx*ratio)), box.dy)
            return Box(box.size - self.size, box.x0 + self.box.dx, box.y0,  box.dx - self.box.dx, box.dy)
        else:
            self.box = Box(self.size, box.x0, box.y0, box.dx, int(round(box.dy*ratio)))
            return Box(box.size - self.size, box.x0, box.y0 + self.box.dy, box.dx,  box.dy - self.box.dy)


    

class Leaf(Node):
    '''
    Leaf is a Node of a tree with no sub-nodes. 
    '''
    def __init__(self, name, size=0):
        Node.__init__(self, name, size)
        self._type = PurePosixPath(self._name).suffix[1:4]

    @property           
    def type(self):
        return self._type


class Tree(Node):
    '''
    Tree is a Node with sub-nodes
    '''
    def __init__(self, name, size, nodes):
        Node.__init__(self, name, size)
        self.nodes = nodes

    @property
    def type(self):
        return 'directory'

    @classmethod
    def make(cls, path : str): 
        '''
        return a Tree representing directory structure with root = path 
        '''

        nodes=[]
        size=0
        try:
            for it in os.scandir(path):                
                name = os.path.join(path, it.name)
                if it.is_dir():
                    node = cls.make(name)
                else:
                    node = Leaf(name, it.stat().st_size)
                size += node.size         
                nodes.append(node)

        except OSError:
            pass

        return Tree(path, size, nodes)


    def boxit(self, box : Box, depth) :
        '''
        Assign nodes in the Tree to boxes inside the input box:  
        - when depth is unlimited (=very large) - only leafs (files) are assigned to boxes.
        - when the depth is limited, directories at the maximum depth are assigned to boxes.
        '''
        left = Node.boxit(self, box)
    
        if depth and self.box:
            use_box = self.box
            for it in sorted(self.nodes, key=lambda  it : it.size, reverse=True) :
                use_box = it.boxit(use_box, depth - 1)
            self.box = None

        return left


    def get_boxes(self): 
        '''
        Return all boxes in the Tree 
        '''
        if self.box:
            yield(self)
        for it in self.nodes:
            if type(it) == type(self):
                yield from it.get_boxes()
            elif it.box:
                yield(it)