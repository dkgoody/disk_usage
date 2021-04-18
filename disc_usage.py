#disc_usage.py

import os
import numpy as np
from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, Quad
from bokeh.palettes import Turbo256 as palette
from bokeh.models import CategoricalColorMapper
from bokeh.plotting import figure
import time
from random import sample
from pandas import DataFrame
from ScanDirSize import Tree, Box

'''
Argument parser
'''
import argparse
parser = argparse.ArgumentParser("Disk Usage Visualizer")
parser.add_argument('-w', '--wide',  type=int, default=1200, help='Result width in pixels')
parser.add_argument('-t', '--tall',  type=int, default=800, help='Result height in pixels')
parser.add_argument('-d', '--depth', type=int, default=4, help='Folder summary at this depth')
parser.add_argument('-s', '--scan',  type=str, default=None, help='Scan this folder. Default is current folder')
args  = parser.parse_args()

if not args.scan:
    args.scan = os.getcwd()

'''
Make a ScanDirSize.Tree
Measure time it takes
Make a title
'''
start_time = time.time()
result = Tree.make(args.scan)
title = f'Disk Usage for {args.scan} looking {args.depth} folders deep. Time used: {time.time() - start_time}'


'''
Make an original ScanDirSize.Box
Assign it to the tree 
'''
result.boxit(Box(result.size, 0, 0, args.wide, args.tall), depth=args.depth)


'''
Convert ScanDirSize.Tree to pandas.DataFrame
Then convert it to bokeh.ColumnDataSource 
'''
df = DataFrame(data=[(p.type, p.name, p.pretty_size, p.box.x0, p.box.y0, p.box.x0 + p.box.dx, p.box.y0 + p.box.dy) for p in result.get_boxes()], 
               columns=['type', 'name', 'size', 'left', 'bottom', 'right', 'top'])
source = ColumnDataSource(df)


'''
Get most common file types
Create a color mapper based on color types
Create a Quad glyph with this color mapper
'''

types = df.type.value_counts()[:len(palette)].index
color_mapper = CategoricalColorMapper(palette=sample(palette, len(types)), factors=list(types))
glyph = Quad(fill_color={'field': 'type', 'transform': color_mapper})


'''
Make a boker.figure of requested size
Add data/glyph
Show the figure 
'''

plot = figure(
    title=title, 
    plot_width=args.wide, 
    plot_height=args.tall,
    toolbar_location=None,
    x_axis_location=None,
    y_axis_location=None,
    tooltips=[
        ("Location", "@name"), ("Size", "@size")
    ])

plot.add_glyph(source, glyph)
curdoc().add_root(plot)
show(plot)