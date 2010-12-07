#!BPY

"""
Name: ' Quick bake Sculpt Meshes'
Blender: 245
Group: 'Render'
Tooltip: 'Rebake Sculptie Maps on Active objects'
"""

__author__ = ["Gaia Clary"]
__url__ = ("Online Help, http://dominodesigns.info/manuals/primstar/bake-sculptie")
__version__ = "1.0.0"
__bpydoc__ = """\

Bake Sculptie Map

This script requires a square planar mapping. It bakes the local vertex
positions to the image assigned to the 'sculptie' UV layer.
"""

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) 2007-2009 Domino Designs Limited
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


try:
    import psyco
    psyco.full()
except:
    pass

import Blender

from primstar.bake_sculpt_mesh_util import BakeApp


#***********************************************
# main
#***********************************************


def main():
    app = BakeApp()
    app.bake()

if __name__ == '__main__':
    main()
