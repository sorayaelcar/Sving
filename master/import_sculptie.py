#!BPY

"""
Name: 'Second Life Sculptie (.tga)'
Blender: 245
Group: 'Import'
Tooltip: 'Import from a Second Life sculptie image map (.tga)'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.30"
__bpydoc__ = """\

Sculptie Importer

This script creates an object from a Second Life sculptie image map
"""

#Changes:
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

#***********************************************
# constants
#***********************************************

SPHERE = 1
TORUS = 2
PLANE = 3
CYLINDER = 4
HEMI = 5
FACES_X = 8
FACES_Y = 8

settings = {'radius':0.25}

#***********************************************
# update vertex positions in sculptie mesh
#***********************************************

def update_sculptie_from_map(mesh, image, sculpt_type):
	wrap_x = ( sculpt_type != PLANE )
	wrap_y = ( sculpt_type == TORUS )
	verts = range( len( mesh.verts ) )
	for f in mesh.faces:
		f.image = image
		for vi in xrange( 4 ):
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
					if ( sculpt_type == SPHERE ):
						u = image.size[0] / 2
				if v == image.size[1]:
					if wrap_y:
						v = 0
					else:
						v = image.size[1] - 1
						if ( sculpt_type == SPHERE ):
							u = image.size[0] / 2
				p  = image.getPixelF( u, v )
				f.verts[ vi ].co = Blender.Mathutils.Vector(( p[0] - 0.5),
						(p[1] - 0.5),
						(p[2] - 0.5))
	mesh.update()
	mesh.sel = True
	mesh.recalcNormals( 0 )

def default_sculptie( mesh, sculptie_type, radius = 0.2 ):
	verts = range( len( mesh.verts ) )
	halfpi = pi * 0.5
	twopi = pi * 2.0
	for f in mesh.faces:
		for vi in xrange( 4 ):
			if f.verts[ vi ].index in verts:
				verts.remove( f.verts[ vi ].index )
				u, v = f.uv[ vi ]
				if sculptie_type == PLANE:
					f.verts[ vi ].co = Blender.Mathutils.Vector( u - 0.5, v -0.5, 0.0 )

				elif sculptie_type == CYLINDER:
					a = pi + twopi * u
					f.verts[ vi ].co = Blender.Mathutils.Vector( cos( a )/2.0,
										sin( a )/2.0,
										v - 0.5 )
				elif sculptie_type == SPHERE:
					if v == 1.0: v = 0.9995
					elif v == 0.0: v = 0.0005
					a = pi + twopi * u
					s = sin( pi * v ) / 2.0
					f.verts[ vi ].co = Blender.Mathutils.Vector( cos( a ) * s,
										sin( a ) * s,
										-cos( pi * v ) / 2.0 )

				elif sculptie_type == TORUS:
					a = pi + twopi * u
					s = (( 1.0 - radius ) - sin( 2.0 * pi * v) * radius) / 2.0
					f.verts[ vi ].co = Blender.Mathutils.Vector( cos( a ) * s,
										sin( a ) * s,
										cos( twopi * v ) / 2.0 * radius )

				elif sculptie_type == HEMI:
					b = sqrt( 2.0 )
					z = -cos( twopi * min( u, v, 1.0 - u, 1.0 - v) ) / 2.0
					u -= 0.5
					v -= 0.5
					h = sqrt(u * u + v * v)
					a = pi + twopi * h
					s = sqrt( sin( ( 0.5 - z ) * halfpi ) / 2.0 )
					if h == 0.0: h = 1.0
					x = u / h * s
					y = v / h * s
					f.verts[ vi ].co = Blender.Mathutils.Vector( x / b,
										y / b ,
										( 0.5 + z ) / 2.0 )

	mesh.update()
	mesh.sel = True
	mesh.recalcNormals( 0 )

#***********************************************
# generate sculptie mesh
#***********************************************

def new_sculptie( sculpt_type, faces_x=FACES_X, faces_y=FACES_Y, multires=2, filename=None ):
	Blender.Window.WaitCursor(1)
	if filename:
		filebase = Blender.sys.basename(filename)
		basename = Blender.sys.splitext(filebase)[0]
	else:
		basename = ("Sphere", "Torus", "Plane", "Cylinder", "Hemi")[sculpt_type -1]
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects:
		ob.sel = False
	mesh = generate_base_mesh( basename, sculpt_type, faces_x + 1, faces_y + 1 )
	if multires and 'addMultiresLevel' not in dir( mesh ):
		print "Warning: this version of Blender does not support addMultiresLevel, get 2.46 or later from http://www.blender.org for full functionality"
		for i in range(multires):
			faces_x *= 2
			faces_y *= 2
		multires = 0
		del( mesh )
		mesh = generate_base_mesh( basename, sculpt_type, faces_x + 1, faces_y + 1 )
	ob = scene.objects.new( mesh, basename )
	ob.setLocation( Blender.Window.GetCursorPos() )
	ob.sel = True
	ob.addProperty( 'LL_PRIM_TYPE', 7 )
	if sculpt_type == HEMI:
		ob.addProperty( 'LL_SCULPT_TYPE', PLANE )
	else:
		ob.addProperty( 'LL_SCULPT_TYPE', sculpt_type )
	if filename:
		image = Blender.Image.Load( filename )
		for f in mesh.faces:
			f.image = image
	elif sculpt_type == TORUS:
		rdict = Blender.Registry.GetKey('Import-Sculptie', True) # True to check on disk also
		if rdict: # if found, get the values saved there
			try:
				settings['radius'] = rdict['radius']
			except:
				pass
		radius = Blender.Draw.Create( settings['radius'] )
		Blender.Window.WaitCursor(0)
		retval = Blender.Draw.PupBlock( "Torus Options", [( "Radius: ", radius, 0.05, 0.5 )] )
		Blender.Window.WaitCursor(1)
		settings['radius'] = radius.val
		Blender.Registry.SetKey('Import-Sculptie', settings, True) # save latest settings
		ob.addProperty( 'LL_HOLE_SIZE_Y', settings['radius'] )
	mesh.flipNormals()
	if multires:
		mesh.multires = True
		mesh.addMultiresLevel( multires )
	if filename:
		update_sculptie_from_map( mesh, image, sculpt_type )
	else:
		default_sculptie( mesh, sculpt_type, settings['radius'] )
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
	faces = []
	wrap_x = ( sculpt_type != PLANE ) & ( sculpt_type != HEMI )
	wrap_y = ( sculpt_type == TORUS )
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
	if wrap_y:
		verts.extend( verts[:verts_x] )
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
	block = []
	scale_x = Blender.Draw.Create( 1.0 )
	scale_y = Blender.Draw.Create( 1.0 )
	scale_z = Blender.Draw.Create( 1.0 )
	sculpt_type = Blender.Draw.Create ( 1 )
	block.append (( "Mesh Type: ", sculpt_type, 1, 4 ))
	block.append (( "      1 Sphere  2 Torus" ))
	block.append (( "      3 Plane   4 Cylinder" ))
	block.append (( "" ))
	block.append (( "Scale X: ", scale_x, 0.01, 100.0 ))
	block.append (( "Scale Y: ", scale_y, 0.01, 100.0 ))
	block.append (( "Scale Z: ", scale_z, 0.01, 100.0 ))
	retval = Blender.Draw.PupBlock( "Sculptie Options", block )
	time1 = Blender.sys.time()  #for timing purposes
	ob = new_sculptie( sculpt_type.val, filename=filename )
	ob.setSize( scale_x.val, scale_y.val, scale_z.val )
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
