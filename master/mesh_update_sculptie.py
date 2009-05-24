#!BPY

"""
Name: 'Update from Sculptie'
Blender: 245
Group: 'Mesh'
Tooltip: 'Updates a mesh with a sculptie UV layer from a .tga map file'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.02"
__bpydoc__ = """\

Sculptie Updater

This script updates a sculptie mesh from a Second Life sculptie image map
"""
#TODO:
# Needs to work with shape keys
#0.02 Domino Marama 2009-05-22
#- Removed image to face assignments and scaling
#0.01 Domino Marama 2007-08-10
#- Initial Version

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

import Blender
from sculpty import update_from_map

#***********************************************
# Import modules
#***********************************************

def main( filename ):
	image = Blender.Image.Load( filename )
	editmode = Blender.Window.EditMode()
	if editmode: Blender.Window.EditMode(0)
	Blender.Window.WaitCursor(1)
	ob = Blender.Scene.GetCurrent().getActiveObject()
	if ob.type == 'Mesh':
		mesh = ob.getData( False, True)
		if "sculptie" in mesh.getUVLayerNames():
			update_from_map( mesh, image )
		else:
			Blender.Draw.PupBlock( "Sculptie Error", ["Mesh has no 'sculptie' UV Layer"] )
	Blender.Window.WaitCursor(0)
	Blender.Window.EditMode( editmode )

#***********************************************
# Request image file
#***********************************************

Blender.Window.FileSelector( main, 'Select Sculptie Map', '.tga' )

