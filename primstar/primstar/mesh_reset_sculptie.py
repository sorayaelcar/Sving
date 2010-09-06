#!BPY

"""
Name: 'Reset Sculpt Mesh'
Blender: 245
Group: 'Object'
Tooltip: 'Updates object mesh from it's sculpt map'
"""

__author__ = ["Domino Marama"]
__url__ = ("Online Help, http://dominodesigns.info/manuals/primstar/mesh-reset-sculptie")
__version__ = "1.0.0"
__bpydoc__ = """\

Reset Sculpt Mesh

This script resets a sculpt mesh from it's assigned sculpt map
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
from primstar import sculpty

#***********************************************
# Import modules
#***********************************************


def main():
    editmode = Blender.Window.EditMode()
    if editmode:
        Blender.Window.EditMode(0)
    Blender.Window.WaitCursor(1)
    scene = Blender.Scene.GetCurrent()
    Blender.Window.WaitCursor(1)
    for ob in scene.objects.selected:
        if sculpty.active(ob):
            mesh = ob.getData(False, True)
            maps = sculpty.map_images(mesh)
            if len(maps) == 1:
                mesh.sel = True
                sculpty.update_from_map(mesh, maps[0])
                mesh.update()
            else:
                Blender.Draw.PupBlock("Sculptie Reset Error",
                ["Can't reset joined sculpt mesh", ob.name])
    Blender.Window.WaitCursor(0)
    Blender.Window.EditMode(editmode)
    Blender.Redraw()

if __name__ == '__main__':
    main()