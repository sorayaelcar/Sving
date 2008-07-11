#!BPY

"""
Name: 'Update from Sculptie'
Blender: 245
Group: 'Mesh'
Tooltip: 'Updates a mesh with a sculptie UV layer from a .tga map file'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.01"
__bpydoc__ = """\

Sculptie Updater

This script updates a sculptie mesh from a Second Life sculptie image map
"""
#TODO:
# Needs to work with shape keys

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
from import_sculptie import update_sculptie_from_map

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
		try:
			primtype = ob.getProperty( 'LL_PRIM_TYPE' ).getData()
			if primtype != 7:
				print "Skipping:", ob.name,"prim type is not a sculptie"
				return
			else:
				sculpt_type = ob.getProperty( 'LL_SCULPT_TYPE' ).getData()
		except:
				print "Skipping:", ob.name," is not a sculptie"
				return
		mesh = ob.getData( False, True)
		if "sculptie" in mesh.getUVLayerNames():
			mesh.activeUVLayer = "sculptie"
			mesh.update()
		if mesh.multires:
			mr = mesh.multiresDrawLevel
			mesh.multiresDrawLevel = 1
		for f in mesh.faces:
			f.image = image
		if mesh.multires:
			mesh.multiresDrawLevel = mr
		mesh.update()
		update_sculptie_from_map( mesh, image, sculpt_type )
		mesh.update()
	Blender.Window.WaitCursor(0)
	Blender.Window.EditMode( editmode )

#***********************************************
# Request image file
#***********************************************

Blender.Window.ImageSelector( main, 'Select Sculptie Map', '.tga' )

