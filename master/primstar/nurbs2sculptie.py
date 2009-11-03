#!BPY

"""
Name: 'Nurbs to Sculptie (1.5)'
Blender: 248
Group: 'Object'
Tooltip: 'Bake Sculptie Maps from a NURBS'
"""

__author__ = ["Gaia Clary"]
__url__ = ("http://blog.machinimatrix.org")
__version__ = "0.7"
__bpydoc__ = """\

Bake Sculptie Map from NURBS

Note: This script requires primstar-0.9.23 or newer from Domino Designs!
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

import Blender, bpy, BPyMesh
from Blender import *
from primstar.nurbs import convertNurbs2Sculptie

#***********************************************
# main
#***********************************************

def main():

    #keep current edit-mode and temporary leave it
    in_editmode = Window.EditMode()
    Window.EditMode(0)

    # get the current scene
    scn = bpy.data.scenes.active
    activeObject = scn.objects.active

    ob = convertNurbs2Sculptie(scn, activeObject)


    #restore original edit_mode
    Window.EditMode(in_editmode)

    #Redraw all windows
    Blender.Redraw

if __name__ == '__main__':
    main()
