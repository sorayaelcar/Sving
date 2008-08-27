#!BPY
"""
Name: 'Sculpt Mesh'
Blender: 245
Group: 'AddMesh'
Tooltip: 'Add a plane/torus/cylinder or sphere with square tiled UV map and multires'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.07"
__bpydoc__ = """\

Sculpt Mesh

This script creates an object with a gridded UV map suitable for Second Life sculptie image maps.
"""
#0.07 Domino Marama 2008-08-27
#- Increased max faces for oblong sculpties
#0.06 Domino Marama 2008-07-13
#- Added hemi sculpt type
#0.05 Domino Marama 2008-06-28
#- settings ranges reduced to be mostly sensible
#0.04 Domino Marama 2008-06-26
#- space removed from registry key name
#0.03 Domino Marama 2008-05-07
#- use preferences for entering edit mode on add mesh
#0.02 Domino Marama 2008-04-30
#- Added versioning info and persistant settings
#0.01 Domino Marama
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

import Blender
from import_sculptie import new_sculptie

settings = {'x_faces':8,'y_faces':8,'type':1,'multires':2}

def main():
	rdict = Blender.Registry.GetKey('AddMesh-SculptMesh', True) # True to check on disk also
	if rdict: # if found, get the values saved there
		try:
			settings['x_faces'] = rdict['x_faces']
			settings['y_faces'] = rdict['y_faces']
			settings['multires'] = rdict['multires']
			settings['type'] = rdict['type']
		except:
			pass
	block = []
	sculpt_type = Blender.Draw.Create ( settings['type'] )
	faces_x = Blender.Draw.Create( settings['x_faces'] )
	faces_y = Blender.Draw.Create( settings['y_faces'] )
	multires_levels = Blender.Draw.Create( settings['multires'] )
	block.append (( "Mesh Type: ", sculpt_type, 1, 5 ))
	block.append (( "      1 Sphere  2 Torus" ))
	block.append (( "      3 Plane   4 Cylinder" ))
	block.append (( "      5 Hemi" ))
	block.append (( "" ))
	block.append (( "X Faces", faces_x, 2, 256 ))
	block.append (( "Y Faces", faces_y, 2, 256 ))
	block.append (( "Multires Levels", multires_levels, 0, 16 ))
	if Blender.Draw.PupBlock( "Sculpt Mesh Options", block ):
		settings['x_faces'] = faces_x.val
		settings['y_faces'] = faces_y.val
		settings['multires'] = multires_levels.val
		settings['type'] = sculpt_type.val
		Blender.Registry.SetKey('AddMesh-SculptMesh', settings, True)
		in_editmode = Blender.Window.EditMode()
		# MUST leave edit mode before changing an active mesh:
		if in_editmode:
			Blender.Window.EditMode(0)
		else:
			try:
				in_editmode = Blender.Get('add_editmode')
			except:
				pass
		ob = new_sculptie( sculpt_type.val, faces_x.val, faces_y.val, multires_levels.val )
		if in_editmode:
			Blender.Window.EditMode(1)

main()
