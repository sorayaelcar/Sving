#!BPY

"""
Name: 'Second Life Sculptie (.tga)'
Blender: 246
Group: 'Import'
Tooltip: 'Import from a Second Life sculptie image map (.tga)'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.36"
__bpydoc__ = """\

Sculptie Importer

This script creates an object from a Second Life sculptie image map
"""

#Changes:
#0.37 Domino Marama 2009-05-22
#- Now uses mapType to detect sculptie type. Dialog box removed.
#0.36 Domino Marama 2008-10-25
#- Wrapped edges are marked as seams
#0.35 Domino Marama 2008-10-19
#- Added face counts on multires calculation
#0.34 Domino Marama 2008-10-18
#- Jira VWR-9384 style oblong support
#- add mesh api support removed as it's now in add_mesh_sculpt_mesh.py
#0.33 Domino Marama 2008-08-27
#- added support for oblong sculpties
#0.32 Domino Marama 2008-08-05
#- corrected hemi rotation bug introduced by last "fix"
#0.31 Domino Marama 2008-07-14
#- corrected normals on hemi
#0.30 Domino Marama 2008-07-14
#- added hemi generator
#0.29 Domino Marama 2008-06-28
#- sphere poles left as small circle
#0.28 Domino Marama 2008-06-26
#- required version text updated
#- rename uv map to sculptie and assign image
#0.27 Domino Marama 2008-05-07
#- use preferences for align to view and enter editmode on add mesh
#0.26 Domino Marama 2008-04-30
#- persistant settings added
#0.25 Domino Marama 2008-04-22
#- wait cursor added
#0.24 Domino Marama 2008-03-12
#- updated for baker v0.12
#0.23 Domino Marama 2008-03-03
#- bug fix on assigning sculpt map - needed to be on multires level 1
#0.22 Domino Marama 2008-02-29
#- allows running on Blender 2.45 by converting multires to additional faces on base mesh
#0.21 Domino Marama 2008-02-12
#- seams moved to -ve x to match SL forward direction
#0.20 Domino Marama 2008-02-12
#- multires made optional on new sculpties
#- new objects now created at 3D cursor
#0.19 Domino Marama 2008-02-11
#- exposed faces_x, faces_y and multires for more general use
#- assigning sculpt map to uv faces put back
#0.18 Domino Marama 2008-02-10
#- minor bug fix, torus was prompting for radius on import
#0.17 Domino Marama 2008-02-09
#- sculpt map no longer assigned to UV faces
#- sculpt map filename now stored as property
#- script seperated into functions to expose api
#- generate default meshes for each sculptie type added
#0.16 Domino Marama 2008-02-02
#- updated for addMultiresLayer_2.patch
#- uv face rotation correction for wrapped min and max y
#0.15 Domino Marama 2008-02-01
#- used wrap_? vars in later tests
#0.14 Domino Marama 2008-01-31
#- mesh generation rewritten to support wrapping
#0.13 Domino Marama 2008-01-24
#- major rewrite to use multires
#0.12 Domino Marama 2007-12-23
#- fixed sculptie types
#0.11 Domino Marama 2007-08-29
#- minor code cleanup
#- added prim properties
#0.10 Domino Marama 2007-08-26
#- corrected name handler using blender sys to replace os
#0.09 Domino Marama 2007-08-21
#- dependancy on os module removed
#0.08 Domino Marama 2007-08-19
#- Removed storage of original uv co-ords as 0.02 baker no longer needs
#0.07 Domino Marama 2007-08-13
#- Material simplified as new sculptie baker only uses it to signal a
#- sculpted prim mesh, default verts set to map size + 1 <=33
#- uv border removed as not needed with correct verts count
#0.06 Domino Marama 2007-08-13
#- Added original mapping pixels storage in vertex paint r & g channels
#0.05 Domino Marama 2007-08-12
#- Added verts and border uv to options
#0.04 Domino Marama 2007-08-12
#- Fixed wrap bug on planes
#0.03 Domino Marama 2007-08-11
#- Settings menu added
#0.02 Domino Marama 2007-08-11
#- Main functionality completed
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
from math import sin, cos, pi, sqrt
from export_lsl import mapType

#***********************************************
# functions
#***********************************************

def adjust_size( width, height, s, t ):
	ratio = float(width) / float(height)
	verts = int(min( 0.25 * width * height, s * t ))
	if width != height:
		verts = verts & 0xfff8
	t = int(sqrt( verts / ratio))
	t = max( t, 4 )
	s = verts // t
	s = max( s, 4 )
	t = verts // s
	return int(s), int(t)

#***********************************************
# update vertex positions in sculptie mesh
#***********************************************

def update_sculptie_from_map(mesh, image, sculpt_type):
	wrap_x = ( sculpt_type != "PLANE" )
	wrap_y = ( sculpt_type == "TORUS" )
	verts = range( len( mesh.verts ) )
	for f in mesh.faces:
		f.image = image
		for vi in xrange( len( f.verts) ):
			if f.verts[ vi ].index in verts:
				verts.remove( f.verts[ vi ].index )
				u, v = f.uv[ vi ]
				u = int( u * image.size[0])
				v = int( v * image.size[1])
				if u == image.size[0]:
					if wrap_x:
						u = 0
					else:
						u = image.size[0] - 1
				if v == 0:
					if ( sculpt_type == "SPHERE" ):
						u = image.size[0] / 2
				if v == image.size[1]:
					if wrap_y:
						v = 0
					else:
						v = image.size[1] - 1
						if ( sculpt_type == "SPHERE" ):
							u = image.size[0] / 2
				p  = image.getPixelF( u, v )
				f.verts[ vi ].co = Blender.Mathutils.Vector(( p[0] - 0.5),
						(p[1] - 0.5),
						(p[2] - 0.5))
	mesh.update()
	mesh.sel = True
	mesh.recalcNormals( 0 )

#***********************************************
# generate sculptie mesh
#***********************************************

def new_sculptie( filename ):
	Blender.Window.WaitCursor(1)
	filebase = Blender.sys.basename(filename)
	basename = Blender.sys.splitext(filebase)[0]
	image = Blender.Image.Load( filename )
	sculpt_type = mapType( image )
	faces_x, faces_y = image.size
	faces_x, faces_y = adjust_size( faces_x, faces_y, 32, 32 )
	multires = 0
	while multires < 2 and faces_x >= 8 and faces_y >= 8 and not ( (faces_x & 1) or (faces_y & 1) ):
		faces_x = faces_x >> 1
		faces_y = faces_y >> 1
		multires += 1
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects:
		ob.sel = False
	mesh = generate_base_mesh( basename, sculpt_type, faces_x + 1, faces_y + 1 )
	ob = scene.objects.new( mesh, basename )
	ob.setLocation( Blender.Window.GetCursorPos() )
	ob.sel = True
	for f in mesh.faces:
		f.image = image
	mesh.flipNormals()
	if multires:
		mesh.multires = True
		mesh.addMultiresLevel( multires )
	update_sculptie_from_map( mesh, image, sculpt_type )
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

def generate_base_mesh( name, sculpt_type, verts_x, verts_y ):
	mesh = Blender.Mesh.New("%s.mesh"%name)
	uv = []
	verts = []
	seams = []
	faces = []
	wrap_x = ( sculpt_type != "PLANE" ) & ( sculpt_type != "HEMI" )
	wrap_y = ( sculpt_type == "TORUS" )
	actual_x = verts_x - wrap_x
	actual_y = verts_y - wrap_y
	uvgrid_y = []
	uvgrid_x = []
	for x in xrange( verts_x ):
		uvgrid_x.append( float( x ) / ( verts_x - 1 ) )
	for y in xrange( verts_y ):
		uvgrid_y.append( float( y ) / ( verts_y - 1 ) )
	for y in xrange( actual_y ):
		for x in xrange( actual_x ):
			mesh.verts.extend([ ( 0.0, 0.0, 0.0 )])
			verts.append( mesh.verts[-1] )
		if wrap_x:
			verts.append( mesh.verts[ -actual_x ] )
			if y:
				seams.append( ( (y - 1) * actual_x, y * actual_x ) )
				if wrap_y:
					if y == actual_y - 1:
						seams.append( ( 0, y * actual_x ) )
	if wrap_y:
		verts.extend( verts[:verts_x] )
		for x in xrange( actual_x - 1 ):
			seams.append( ( x, x + 1 ) )
		seams.append( ( 0, actual_x - 1 ) )
	for y in xrange( verts_y - 1 ):
		offset_y = y * verts_x
		for x in xrange( verts_x - 1 ):
			faces.append( ( verts[offset_y + x], verts[offset_y + verts_x + x],
					verts[offset_y + verts_x + x + 1], verts[offset_y + x + 1] ) )
			if wrap_x and x == actual_x - 1 and (y == 0 or y == actual_y -1):
				# blender auto alters vert order - correct uv to match
				uv.append( ( Blender.Mathutils.Vector( uvgrid_x[ x + 1 ], uvgrid_y[ y + 1 ] ),
					Blender.Mathutils.Vector( uvgrid_x[ x + 1 ], uvgrid_y[ y ] ),
					Blender.Mathutils.Vector( uvgrid_x[ x ], uvgrid_y[ y ] ),
					Blender.Mathutils.Vector( uvgrid_x[ x ], uvgrid_y[ y + 1 ] ) ) )
			else:
				uv.append( ( Blender.Mathutils.Vector( uvgrid_x[ x ], uvgrid_y[ y ] ),
					Blender.Mathutils.Vector( uvgrid_x[ x ], uvgrid_y[ y + 1 ] ),
					Blender.Mathutils.Vector( uvgrid_x[ x + 1 ], uvgrid_y[ y + 1 ] ),
					Blender.Mathutils.Vector( uvgrid_x[ x + 1 ], uvgrid_y[ y ] ) ) )
	mesh.faces.extend( faces )
	mesh.faceUV = True
	for f in xrange( len(mesh.faces) ):
		mesh.faces[ f ].uv = uv[ f ]
	mesh.renameUVLayer( mesh.activeUVLayer, "sculptie" );
	if seams != []:
		for e in mesh.findEdges( seams ):
			mesh.edges[e].flag = mesh.edges[e].flag | Blender.Mesh.EdgeFlags.SEAM
	return mesh	

#***********************************************
# load sculptie file
#***********************************************

def load_sculptie(filename):
	print "--------------------------------"
	print 'Importing "%s"' % filename
	in_editmode = Blender.Window.EditMode()
	# MUST leave edit mode before changing an active mesh:
	if in_editmode:
		Blender.Window.EditMode(0)
	else:
		try:
			in_editmode = Blender.Get('add_editmode')
		except:
			pass
	time1 = Blender.sys.time()  #for timing purposes
	ob = new_sculptie( filename )
	if in_editmode:
		Blender.Window.EditMode(1)
	Blender.Redraw()
	print 'finished importing: "%s" in %.4f sec.' % (filename, (Blender.sys.time()-time1))

#***********************************************
# register callback
#***********************************************
def my_callback(filename):
	load_sculptie(filename)

if __name__ == '__main__':
	Blender.Window.FileSelector(my_callback, "Import Sculptie", '.tga')
