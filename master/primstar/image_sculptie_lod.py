#!BPY
"""
Name: 'Bake Sculptie LOD'
Blender: 246
Group: 'Image'
Tooltip: 'Bake a sculptie LOD to image'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "1.00"
__bpydoc__ = """\

Bake Sculptie LOD

This script bakes a sculptie LOD helper to the active image
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

try:
    import psyco
    psyco.full()
except:
    pass

import Blender
from primstar.sculpty import bake_lod


def main():
    image = Blender.Image.GetCurrent()
    if image:
        bake_lod(image)
    else:
        Blender.Draw.PupBlock("Sculptie Bake Error", ["No current image"])

if __name__ == '__main__':
    main()
