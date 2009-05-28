#!BPY
"""
Name: 'Finalise Sculptie'
Blender: 246
Group: 'Image'
Tooltip: 'Tweak sculpt map for mirroring'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "1.00"
__bpydoc__ = """\

Finalise sculptie

This script applies final polish to a sculptie. It makes the map mirrorable and allows
better compression of the image.
"""
# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) 2008-2009 Domino Designs Limited
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
from sculpty import expand_pixels

def main():
	image = Blender.Image.GetCurrent()
	if image:
		expand_pixels( image )
	else:
		Blender.Draw.PupBlock( "Sculptie Bake Error", ["No current image"] )

if __name__ == '__main__':
	main()