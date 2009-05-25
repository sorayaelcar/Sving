#!BPY
"""
Name: 'Sculpt Mesh'
Blender: 246
Group: 'AddMesh'
Tooltip: 'Add a Second Life sculptie compatible mesh'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.12"
__bpydoc__ = """\

Sculpt Mesh

This script creates an object with a gridded UV map suitable for Second Life sculpties.
"""
#0.12 Domino Marama 2009-05-24
#- Image based sculptie generation added
#0.11 Domino Marama 2008-10-27
#- Use getBB from render_sculptie.py
#0.10 Domino Marama 2008-10-25
#- Wrapped edges are marked as seams
#0.09 Domino Marama 2008-10-17
#- Added subsurf modifer for lod levels
#0.08 Domino Marama 2008-10-17
#- Added clean LODs option and proper oblong support
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
from math import log, ceil, sqrt, pi, sin, cos
import sculpty

#***********************************************
# constants
#***********************************************

SPHERE = 1
TORUS = 2
PLANE = 3
CYLINDER = 4
HEMI = 5

settings = {'x_faces':8,'y_faces':8,'type':1,'multires':2, 'clean_lod':True, 'radius':0.25, 'subsurf':True}

def add_sculptie( sculpt_type, faces_x=8, faces_y=8, multires=2, clean_lods = True, subsurf = False ):
	Blender.Window.WaitCursor(1)
	basename = ("Sphere", "Torus", "Plane", "Cylinder", "Hemi")[sculpt_type -1]
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects:
		ob.sel = False
	rdict = Blender.Registry.GetKey('ImportSculptie', True) # True to check on disk also
	if rdict: # if found, get the values saved there
		try:
			settings['radius'] = rdict['radius']
		except:
			settings['radius'] = 0.25
	if sculpt_type == TORUS:
		radius = Blender.Draw.Create( settings['radius'] )
		Blender.Window.WaitCursor(0)
		retval = Blender.Draw.PupBlock( "Torus Options", [( "Radius: ", radius, 0.05, 0.5 )] )
		Blender.Window.WaitCursor(1)
		settings['radius'] = radius.val
		Blender.Registry.SetKey('ImportSculptie', settings, True) # save latest settings
	mesh = sculpty.new_mesh( basename, ["none","SPHERE","TORUS","PLANE","CYLINDER","HEMI"][sculpt_type], faces_x, faces_y, multires, clean_lods )
	s, t, w, h, clean_s, clean_t = sculpty.map_size( faces_x, faces_y, multires )
	image = Blender.Image.New( basename, w, h, 32 )
	sculpty.bake_default( image, ["none","SPHERE","TORUS","PLANE","CYLINDER","HEMI"][sculpt_type], settings['radius'] )
	ob = scene.objects.new( mesh, basename )
	if sculpt_type != PLANE:
		mesh.flipNormals()
	ob.sel = True
	ob.setLocation( Blender.Window.GetCursorPos() )
	if sculpt_type == PLANE:
		mesh.flipNormals()
	sculpty.set_map( mesh, image )
	if multires:
		if subsurf:
			mods = ob.modifiers
			mod = mods.append(Blender.Modifier.Types.SUBSURF)
			mod[Blender.Modifier.Settings.LEVELS] = multires
			mod[Blender.Modifier.Settings.UV] = False
		else:
			mesh.multires = True
			mesh.addMultiresLevel( multires )
			mesh.sel = True
			sculpty.update_from_map( mesh, image )
	# adjust scale for subdivision
	bb = sculpty.getBB( ob )
	x = 1.0 / (bb[1][0] - bb[0][0])
	y = 1.0 / (bb[1][1] - bb[0][1])
	try:
		z = 1.0 / (bb[1][2] - bb[0][2])
	except:
		z = 0.0
	if sculpt_type == TORUS:
		z = settings['radius'] * z
	elif sculpt_type == HEMI:
		z = 0.5 * z
	tran = Blender.Mathutils.Matrix( [ x, 0.0, 0.0 ], [0.0, y, 0.0], [0.0, 0.0, z] ).resize4x4()
	mesh.transform( tran )
	# align to view
	try:
		quat = None
		if Blender.Get('add_view_align'):
			quat = Blender.Mathutils.Quaternion(Blender.Window.GetViewQuat())
			if quat:
				mat = quat.toMatrix()
				mat.invert()
				mat.resize4x4()
				ob.setMatrix(mat)
	except:
		pass
	Blender.Window.WaitCursor(0)
	return ob

def main():
	rdict = Blender.Registry.GetKey('AddMeshSculptMesh', True) # True to check on disk also
	if rdict: # if found, get the values saved there
		try:
			settings['x_faces'] = rdict['x_faces']
			settings['y_faces'] = rdict['y_faces']
			settings['multires'] = rdict['multires']
			settings['type'] = rdict['type']
			settings['clean_lod'] = rdict['clean_lod']
			settings['subsurf'] = rdict['subsurf']
		except:
			pass
	block = []
	sculpt_type = Blender.Draw.Create ( settings['type'] )
	faces_x = Blender.Draw.Create( settings['x_faces'] )
	faces_y = Blender.Draw.Create( settings['y_faces'] )
	multires_levels = Blender.Draw.Create( settings['multires'] )
	clean_lod = Blender.Draw.Create( settings['clean_lod'] )
	subsurf = Blender.Draw.Create( settings['subsurf'] )
	block.append (( "Mesh Type: ", sculpt_type, 1, 5 ))
	block.append (( "  1 Sphere  2 Torus  3 Plane" ))
	block.append (( "      4 Cylinder  5 Hemi" ))
	block.append (( "X Faces", faces_x, 2, 256 ))
	block.append (( "Y Faces", faces_y, 2, 256 ))
	block.append (( "Subdivision Levels", multires_levels, 0, 16 ))
	block.append (( "Use Subsurf", subsurf ))
	block.append (( "Clean LODs", clean_lod ))
	if Blender.Draw.PupBlock( "Sculpt Mesh Options", block ):
		settings['x_faces'] = faces_x.val
		settings['y_faces'] = faces_y.val
		settings['multires'] = multires_levels.val
		settings['type'] = sculpt_type.val
		settings['clean_lod'] = clean_lod.val
		settings['subsurf'] = subsurf.val
		Blender.Registry.SetKey('AddMeshSculptMesh', settings, True)
		in_editmode = Blender.Window.EditMode()
		# MUST leave edit mode before changing an active mesh:
		if in_editmode:
			Blender.Window.EditMode(0)
		else:
			try:
				in_editmode = Blender.Get('add_editmode')
			except:
				pass
		ob = add_sculptie( sculpt_type.val, faces_x.val, faces_y.val, multires_levels.val, clean_lod.val, subsurf.val )
		if in_editmode:
			Blender.Window.EditMode(1)

if __name__ == '__main__':
	main()
