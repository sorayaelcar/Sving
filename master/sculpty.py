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
# functions
#***********************************************

def face_count( width, height, s, t, model = True ):
	ratio = float(width) / float(height)
	verts = int(min( 0.25 * width * height, s * t ))
	if (width != height) and model:
		verts = verts & 0xfff8
	t = int(sqrt( verts / ratio))
	t = max( t, 4 )
	s = verts // t
	s = max( s, 4 )
	t = verts // s
	return int(s), int(t)

def map_images( mesh ):
	images = []
	if "sculptie" in mesh.getUVLayerNames():
		currentUV = mesh.activeUVLayer
		mesh.activeUVLayer = "sculptie"
		mesh.update()
		for f in mesh.faces:
			if f.image != None:
				if f.image not in images:
					images.append( f.image )
		mesh.activeUVLayer = currentUV
		mesh.update()
	return images

def map_type( image ):
	poles = True
	xseam = True
	yseam = True
	p1 = image.getPixelI( 0, 0 )[:3]
	p2 = image.getPixelI( 0, image.size[1] - 1 )[:3]
	if p1 != p2:
		yseam = False
	for x in xrange( 1, image.size[0]  ):
		p3 = image.getPixelI( x, 0 )[:3]
		p4 = image.getPixelI( x, image.size[1] - 1 )[:3]
		if p1 != p3 or p2 != p4:
			poles = False
		if p3 != p4:
			yseam = False
		p1 = p3
		p2 = p4
	for y in xrange( image.size[1]  ):
		p1 = image.getPixelI( 0, y )[:3]
		p2 = image.getPixelI( image.size[0] - 1, y )[:3]
		if p1 != p2:
			xseam = False
	if xseam:
		if poles:
			return "SPHERE"
		if yseam:
			return "TORUS"
		return "CYLINDER"
	return "PLANE"

def update_from_map( mesh, image ):
	currentUV = mesh.activeUVLayer
	if "sculptie" in mesh.getUVLayerNames():
		mesh.activeUVLayer = "sculptie"
		mesh.update()
	verts = range( len( mesh.verts ) )
	for f in mesh.faces:
		for vi in xrange( len( f.verts) ):
			if f.verts[ vi ].index in verts:
				verts.remove( f.verts[ vi ].index )
				if f.verts[ vi ].sel:
					u, v = f.uv[ vi ]
					u = int( u * image.size[0])
					v = int( v * image.size[1])
					if u == image.size[0]:
						u = image.size[0] - 1
					if v == image.size[1]:
						v = image.size[1] - 1
					p  = image.getPixelF( u, v )
					f.verts[ vi ].co = Blender.Mathutils.Vector(( p[0] - 0.5),
							(p[1] - 0.5),
							(p[2] - 0.5))
	mesh.activeUVLayer = currentUV
	mesh.update()
	mesh.sel = True
	mesh.recalcNormals( 0 )

def new_from_map( image ):
	Blender.Window.WaitCursor(1)
	sculpt_type = map_type( image )
	faces_x, faces_y = image.size
	faces_x, faces_y = face_count( faces_x, faces_y, 32, 32 )
	multires = 0
	while multires < 2 and faces_x >= 8 and faces_y >= 8 and not ( (faces_x & 1) or (faces_y & 1) ):
		faces_x = faces_x >> 1
		faces_y = faces_y >> 1
		multires += 1
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects:
		ob.sel = False
	mesh = new_mesh( image.name, sculpt_type, faces_x + 1, faces_y + 1 )
	ob = scene.objects.new( mesh, image.name )
	ob.setLocation( Blender.Window.GetCursorPos() )
	ob.sel = True
	for f in mesh.faces:
		f.image = image
	mesh.flipNormals()
	if multires:
		mesh.multires = True
		mesh.addMultiresLevel( multires )
	for v in mesh.verts:
		v.sel = True
	update_from_map( mesh, image )
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

def new_mesh( name, sculpt_type, verts_x, verts_y ):
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
	mesh.addUVLayer( "UVTex" )
	mesh.activeUVLayer = "UVTex"
	if seams != []:
		for e in mesh.findEdges( seams ):
			mesh.edges[e].flag = mesh.edges[e].flag | Blender.Mesh.EdgeFlags.SEAM
	return mesh

def bake_lod( image ):
	x = image.size[0]
	y = image.size[1]
	for u in range(x):
		for v in range(y):
			image.setPixelF( u, v, ( float(u) / x, float(v) / y, 0.0, 1.0 ) )
	for l in range(4):
		sides = [ 6, 8, 16, 32 ][l]
		s, t = face_count( x , y, sides, sides, False )
		ts = []
		ss = []
		for k in range( s ):
			ss.append( int(x * k / float(s)) )
		for k in range( t ):
			ts.append( int(y * k / float(t)) )
		ts.append( y - 1)
		ss.append( x - 1 )
		for s in ss:
			for t in ts:
				c = image.getPixelF( s, t )
				c[2] += 0.25
				image.setPixelF( s, t, c )

def clear_alpha( image ):
	for x in xrange( image.size[0] ):
		for y in xrange( image.size[1] ):
			c1 = image.getPixelF( x, y )
			c1[3] = 0.0
			image.setPixelF( x, y, c1 )

def bake_preview( image ):
	clear_alpha( image )
	for x in xrange( image.size[0] ):
		for y in xrange( image.size[1] ):
			c1 = image.getPixelF( x, y )
			f = (c1[1] * 0.35) + 0.65
			s = int( (image.size[0] - 1) * (0.5 - (0.5 - c1[0]) * f))
			t = int( (image.size[1] - 1) * (0.5 - (0.5 - c1[2]) * f))
			c2 = image.getPixelF( s, t )
			if c2[3] < c1[1]:
				c2[3] = c1[1]
				image.setPixelF( s, t, c2 )

def mirror_pixels( image ):
	d = 2
	for y in xrange( 0, image.size[1], d ):
		for x in xrange( 0, image.size[0] - 1):
			if x % d:
				image.setPixelF( x, y, c )
			else:
				c = image.getPixelF( x, y )
	y = image.size[1] - 1
	for x in xrange( 0, image.size[0] - 1):
			if x % d:
				image.setPixelF( x, y, c )
			else:
				c = image.getPixelF( x, y )
	for x in xrange( 0, image.size[0] ):
		for y in xrange( 0, image.size[1] -1 ):
			if y % d:
				image.setPixelF( x, y, c )
			else:
				c = image.getPixelF( x, y )

def getBB( obj ):
	mesh = Blender.Mesh.New()
	mesh.getFromObject( obj, 0, 1 )
	min_x = mesh.verts[0].co.x
	max_x = min_x
	min_y = mesh.verts[0].co.y
	max_y = min_y
	min_z = mesh.verts[0].co.z
	max_z = min_z
	for v in mesh.verts[1:-1]:
		if v.co.x < min_x :
			min_x = v.co.x
		elif v.co.x > max_x :
			max_x = v.co.x
		if v.co.y < min_y :
			min_y = v.co.y
		elif v.co.y > max_y :
			max_y = v.co.y
		if v.co.z < min_z :
			min_z = v.co.z
		elif v.co.z > max_z :
			max_z = v.co.z
	return ( min_x, min_y, min_z ), ( max_x, max_y, max_z )
