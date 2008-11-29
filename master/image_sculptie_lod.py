#!BPY
"""
Name: 'Bake Sculptie LOD'
Blender: 246
Group: 'Image'
Tooltip: 'Bake a sculptie LOD to image'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.01"
__bpydoc__ = """\

Bake Sculptie LOD

This script bakes a sculptie LOD helper to the active image
"""

#0.01 Domino Marama 2008-11-29
#- Initial Version

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) Domino Designs Limited
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

import Blender
from math import sqrt

def fixed_size( width, height, detail ):
	sides = float([ 6, 8, 16, 32 ][detail])
	ratio = float(width) / float(height)
	verts = int(min( 0.25 * width * height, sides * sides))
	#if width != height:
	#	verts = verts & 0xfff8
	s = int(sqrt( verts / ratio))
	s = max( s, 4.0 )
	t = verts // s
	t = max( t, 4.0 )
	s = verts // t
	return int(t), int(s)

def main():
	image = Blender.Image.GetCurrent()
	if image:
		x = image.size[0]
		y = image.size[1]
		for u in range(x):
			for v in range(y):
				image.setPixelF( u, v, ( float(u) / x, float(v) / y, 0.0, 1.0 ) )
		for l in range(4):
			t, s = fixed_size( x, y, l )
			ts = []
			ss = []
			for k in range( t ):
				ts.append( int(x * k / float(t)) )
			for k in range( s ):
				ss.append( int(y * k / float(s)) )
			ts.append( x - 1 )
			ss.append( y - 1)
			for u in ts:
				for v in ss:
					c = image.getPixelF( u, v )
					c[2] += 0.25
					image.setPixelF( u, v, c )

if __name__ == '__main__':
	main()