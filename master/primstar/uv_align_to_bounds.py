#!BPY
"""
Name: 'Align to Bounds'
Blender: 249
Group: 'UV'
Tooltip: 'Align UV points to bounds'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "1.00"
__bpydoc__ = """\

Align to bounds

This script scales the current meshes UV points to a 0.0 to 1.0 range
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
from primstar.uv_tools import scale_map_uv


def main():
    scene = Blender.Scene.GetCurrent()
    ob = scene.objects.active
    Blender.Window.EditMode(0)
    scale_map_uv(ob, False)
    Blender.Window.EditMode(1)
    Blender.Redraw()

if __name__ == '__main__':
    main()
