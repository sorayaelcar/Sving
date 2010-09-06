#!BPY
"""
Name: 'Align to Sculpt Map'
Blender: 249
Group: 'UV'
Tooltip: 'Align UV points to sculpt map'
"""

__author__ = ["Domino Marama"]
__url__ = ("Online Help, http://dominodesigns.info/manuals/primstar/align-to-sculpt-map")
__version__ = "1.0.0"
__bpydoc__ = """\

Align sculpt map

This script aligns the current meshes UV points on the current sculpt map
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
from primstar.uv_tools import snap_to_pixels


def main():
    scene = Blender.Scene.GetCurrent()
    ob = scene.objects.active
    image = Blender.Image.GetCurrent()
    if image:
        snap_to_pixels(ob.getData(mesh=1), True, image)
    else:
        Blender.Draw.PupBlock("Align map error", ["No current image"])
    Blender.Redraw()

if __name__ == '__main__':
    main()
