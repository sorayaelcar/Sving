#!BPY

"""
Name: 'EAC from View'
Blender: 245
Group: 'UVCalculation'
Tooltip: 'Equal area cylindrical projection unwrap from object centre and view'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.03"
__bpydoc__ = """\
This script uses an equal area cylindrical projection to unwrap the
selected meshes.

see http://mathworld.wolfram.com/CylindricalEqual-AreaProjection.html
"""


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

#***********************************************
# Import modules
#***********************************************

try:
    import psyco
    psyco.full()
except:
    pass

import Blender
import bpy
from primstar.uv_tools import eac_unwrap


def main():
    time1 = Blender.sys.time()
    objects = bpy.data.scenes.active.objects
    obList = [ob for ob in objects.context if ob.type == 'Mesh']
    ob = objects.active
    if ob and ob.sel == 0 and ob.type == 'Mesh':
        obList += [ob]
    del objects
    if not obList:
        Blender.Draw.PupMenu('Error: no selected mesh objects')
        return
    editmode = Blender.Window.EditMode()
    if editmode:
        Blender.Window.EditMode(0)
    for ob in obList:
        if ob.type == 'Mesh':
            eac_unwrap(ob)
    print 'EAC Projection time: %.4f' % ((Blender.sys.time() - time1))
    Blender.Window.RedrawAll()
    Blender.Window.EditMode(editmode)

if __name__ == '__main__':
    main()
