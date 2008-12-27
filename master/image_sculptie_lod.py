#!BPY
"""
Name: 'Bake Sculptie LOD'
Blender: 246
Group: 'Image'
Tooltip: 'Bake a sculptie LOD to image'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.02"
__bpydoc__ = """\

Bake Sculptie LOD

This script bakes a sculptie LOD helper to the active image
"""

#0.02 Domino Marama 2008-11-29
#- Adjust size used to match other scripts
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

def adjust_size( width, height, s, t ):
	ratio = float(width) / float(height)
	verts = int(min( 0.25 * width * height, s * t ))
	#if width != height:
	#	verts = verts & 0xfff8
	t = int(sqrt( verts / ratio))
	t = max( t, 4 )
	s = verts // t
	s = max( s, 4 )
	t = verts // s
	return int(s), int(t)

def main():
	image = Blender.Image.GetCurrent()
	if image:
		x = image.size[0]
		y = image.size[1]
		for u in range(x):
			for v in range(y):
				image.setPixelF( u, v, ( float(u) / x, float(v) / y, 0.0, 1.0 ) )
		for l in range(4):
			sides = [ 6, 8, 16, 32 ][l]
			s, t = adjust_size( x , y, sides, sides )
			ts = []
			ss = []
			for k in range( s ):
				ss.append( int(x * k / float(s)) )
			for k in range( t ):
				ts.append( int(y * k / float(t)) )
			ts.append( y - 1)
			ss.append( x - 1 )
			for s in ss:
				for t in ts:
					c = image.getPixelF( s, t )
					c[2] += 0.25
					image.setPixelF( s, t, c )
	else:
		Blender.Draw.PupBlock( "Sculptie Bake Error", ["No current image"] )

if __name__ == '__main__':
	main()