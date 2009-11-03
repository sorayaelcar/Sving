#!BPY

"""
Name: 'Nurbs to Sculpt Mesh'
Blender: 248
Group: 'Object'
Tooltip: 'Convert a nurbs surface to a sculpt mesh'
"""

__author__ = ["Gaia Clary", "Domino Marama"]
__url__ = ("http://blog.machinimatrix.org", "http://dominodesigns.info")
__version__ = "0.7"
__bpydoc__ = """\

Convert a nurbs surface to a sculpt mesh

"""

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) Machinimatrix
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

import Blender
from primstar.nurbs import uvcalc
from primstar.sculpty import sculptify

#***********************************************
# temp functions, move to sculptie.py when done
#***********************************************


def convert_from_nurbs(ob):
    if ob.type != "Surf":
        return False
    scene = Blender.Scene.GetCurrent()

    # get selected and thus the active object
    objectName = ob.getName()

    # make new mesh (reuse the objectName)
    me = Blender.Mesh.New(objectName)

    # fill new mesh with raw data from the active object
    me.getFromObject(ob)

    #Select all vertices in the active object
    me.sel = 1

    # Add a new UV Texture.
    # The texture should be equivalent to "Mesh -> UV-unwrap -> Reset"
    me.addUVLayer("sculptie")

    #Set the first face as the active face.
    me.activeFace = 0

    # make a new object, fill it with the just created mesh data
    # and and link it to current scene
    location = ob.loc
    rotation = ob.rot
    size = ob.size
    scene.objects.unlink(ob)
    new_ob = scene.objects.new(me, objectName)
    new_ob.loc = location
    new_ob.rot = rotation
    new_ob.size = size

    #Make the new object the active object
    new_ob.select(1)

    #Unwrap follow active (quads)
    uvcalc(new_ob) # This replaces call to uvcalc_follow_active_coords.extend()

    return sculptify(new_ob)

#***********************************************
# main
#***********************************************


def main():

    scene = Blender.Scene.GetCurrent()
    success = False
    Blender.Window.WaitCursor(1)
    for ob in scene.objects.selected:
        if convert_from_nurbs(ob):
            success = True
    Blender.Window.WaitCursor(0)
    if not success:
        Blender.Draw.PupBlock("Conversion Error",
                ["No NURBS surfaces", "are selected"])
    Blender.Redraw()

if __name__ == '__main__':
    main()
