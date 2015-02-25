#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005  Michiel Brentjens
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import os
from numpy import *
from string import *
import struct
import glob


class FontMetrics:
    """
    Class to store character widths from AFM files. Can compute width
    of strings in print.
    """
    def __init__(self, directory='.'):
        self.dir = directory
        fontfiles = glob.glob1(directory, '*.[aA][fF][mM]')
        self.metrics = {}
        for ff in fontfiles:
            name, ext = ff.split('.')
            self.metrics[name] = self.read_metrics(ff)
            pass
        pass


    def read_metrics(self, afm_name):
        widths = zeros(256)

        f = file(self.dir+os.sep+afm_name, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            split_up  = line.split()
            if 'WX' in split_up and ';' in split_up and 'C' in split_up:
                index = atoi(split_up[1])
                w = atoi(split_up[4])
                if index >= 0:
                    widths[index] = w
                    pass
                pass
            pass # for...

        return widths


    def string_width(self, fontname, fontsize, text):
        size = 0.0
        try:
            N = len(text)
            if N > 0:
                fmt = 'B'*N
                chars = struct.unpack(fmt, text)
                for c in chars:
                    size += self.metrics[fontname][c]
                    pass
                size *= fontsize/1000.0
                pass
            pass
        except KeyError:
            print 'Unknown font: '+fontname
            size = -1
            pass
        return size

    pass


__all__ = ['FontMetrics']
