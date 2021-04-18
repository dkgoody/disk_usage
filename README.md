

ScanDirSize extends os.scandir output with size and visualization information
 
 How Size Extension works:
 ========================
 - os.scandir is used recursively to create a tree representing directories structure 
 - Each node of the tree, either sub-tree (directory) or leaf (file) has a size in bytes attached 
 - Tree size is calculated as a sum of all sub-trees and files under it.


 
  
How Visualization works:
======================
 - The goal is to represent each file in proportion to its size
 - Given dimentions of the box (glyph) for the whole tree structure, each node (either sub-tree or file) gets a inner box assigned to it.  
    - when depth of the visualization is unlimited (=very large) - only leafs (files) are assigned to boxes.
    - when the depth is limited, directories at the maximum depth are assigned to boxes and their content is not get visualized
 - After the assigment, the boxes can be plotted to visualize the whole tree content. 
 - Each box represents a file/directory and its size is proportional to file/directory size on the disk.