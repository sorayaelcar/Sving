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
from primstar.nurbs import convertNurbs2Sculptie

#***********************************************
# main
#***********************************************

def main():

    scene = Blender.Scene.GetCurrent()
    success = False
    Blender.Window.WaitCursor(1)
    for ob in scene.objects.selected:
        if active_object.type == "Surf":
            ob = convertNurbs2Sculptie(scene, active_object)
            success = True
    Blender.Window.WaitCursor(0)
    if not success:
        Blender.Draw.PupBlock("Conversion Error",
                ["No NURBS surfaces","are selected"])
    Blender.Redraw()

if __name__ == '__main__':
    main()
