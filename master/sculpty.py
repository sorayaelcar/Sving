# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) 2007-2009 Domino Designs Limited
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
from math import sin, cos, pi, sqrt, log, ceil

#***********************************************
# helper classes
#***********************************************

class xyz:
	def __init__( x, y, z ):
		self.x = x
		self.y = y
		self.z = z

	def __sub__( self, other ):
		return xyz(
			self.x - other.x,
			self.y - other.y,
			self.z - other.z
		)

	def __add__( self, other ):
		return xyz(
			self.x + other.x,
			self.y + other.y,
			self.z + other.z
		)

	def __mul__( self, scalar ):
		return xyz(
			self.x * scalar,
			self.y * scalar,
			self.z * scalar
		)

class bounding_box:
	def __init__( self, ob = None ):
		self.scale = xyz( 0.0, 0.0, 0.0 )
		self.center = xyz( 0.0, 0.0, 0.0 )
		if ob != None:
			bb = getBB( ob )
			self.min = xyz( bb[0] )
			self.max = xyz( bb[1] )
		else:
			self.min = xyz( 0.0, 0.0, 0.0 )
			self.max = xyz( 0.0, 0.0, 0.0 )
		self.update()

	def add( self, ob ):
		bb = getBB( ob )
		mi = xyz( bb[0] )
		ma = xyz( bb[1] )
		if self.min.x > mi.x:
			self.min.x = mi.x
		if self.min.y > mi.y:
			self.min.y = mi.y
		if self.min.z > mi.z:
			self.min.z = mi.z
		if self.max.x < ma.x:
			self.max.x = ma.x
		if self.max.y < ma.y:
			self.max.y = ma.y
		if self.max.z < ma.z:
			self.max.z = ma.z
		self.update()

	def update( self ):
		self.scale = self.max - self.min
		self.center = self.min + self.scale * 0.5

	def normalised( self ):
		s = bounding_box()
		s.min.x = s.min.y = s.min.z = min( self.min.x, self.min.y, self.min.z )
		s.max.x = s.max.y = s.max.z = max( self.max.x, self.max.y, self.max.z )
		s.update()
		return s

	def centered( self ):
		s = bounding_box()
		if -self.min.x > self.max.x:
			s.max.x = -self.min.x
			s.min.x = self.min.x
		else:
			s.max.x = self.max.x
			s.min.x = -self.max.x
		if -self.min.y > self.max.y:
			s.max.y = -self.min.y
			s.min.y = self.min.y
		else:
			s.max.y = self.max.y
			s.min.y = -self.max.y
		if -self.min.z > self.max.z:
			s.max.z = -self.min.z
			s.min.z = self.min.z
		else:
			s.max.z = self.max.z
			s.min.z = -self.max.z
		s.update()
		return s

		def xyz_to_rgb( x, y, z ):
			r = round( 255.0 * (( x - self.min.x ) / self.scale.x ) )
			g = round( 255.0 * (( y - self.min.y ) / self.scale.y ) )
			b = round( 255.0 * (( z - self.min.z ) / self.scale.z ) )
			return r, g, b

#***********************************************
# sculpty info functions
#***********************************************

def face_count( width, height, x_faces, y_faces, model = True ):
	'''
	Returns usable face count from input

	width - sculpt map width
	height - sculpt map width
	x_faces - desired x face count
	y_faces - desired y face count
	model - when true, returns 8 x 4 instead of 9 x 4 to give extra subdivision
	'''
	ratio = float(width) / float(height)
	verts = int(min( 0.25 * width * height, x_faces * y_faces ))
	if (width != height) and model:
		verts = verts & 0xfff8
	y_faces = int(sqrt( verts / ratio))
	y_faces = max( y_faces, 4 )
	x_faces = verts // y_faces
	x_faces = max( x_faces, 4 )
	y_faces = verts // x_faces
	return int(x_faces), int(y_faces)

def lod_info( width, height, format = "LOD%(lod)d:%(x_faces)dx%(y_faces)d\n" ):
	'''
	Returns a string with the lod info for a map size of width * height
	'''
	info = ""
	for i in [3,2,1,0]:
		faces = float([ 6, 8, 16, 32 ][i])
		x_faces, y_faces = lod_size( width, height, i )
		info += format%{ 'lod':i, 'x_faces':x_faces, 'y_faces':y_faces }
	return info

def lod_size( width, height, lod ):
	'''
	Returns x and y face counts for the given map size and lod
	'''
	sides = float([ 6, 8, 16, 32 ][lod])
	ratio = float(width) / float(height)
	verts = int(min( 0.25 * width * height, sides * sides))
	y_faces = int(sqrt( verts / ratio))
	y_faces = max( y_faces, 4 )
	x_faces = verts // y_faces
	x_faces = max( x_faces, 4 )
	y_faces = verts // x_faces
	return int(x_faces), int(y_faces)

def map_size( x_faces, y_faces, levels ):
	'''
	Suggests optimal sculpt map size for x_faces * y_faces * levels

	x_faces - x face count
	y_faces - y face count
	levels - subdivision levels

	returns

	s, t, w, h, cs, ct

	s - x face count
	t - y face count
	w - map width
	h - map height
	cs - True if x face count was corrected
	ct - True if y face count was corrected
	'''
	w = int(pow(2, levels + 1 + ceil( log(x_faces) / log(2))))
	h = int(pow(2, levels + 1 + ceil( log(y_faces) / log(2))))
	w, h = face_count( w, h, 32, 32 )
	s = min( w, x_faces )
	t = min( h, y_faces )
	w = int(pow(2, levels + 1 + ceil( log(w>>levels) / log(2))))
	h = int(pow(2, levels + 1 + ceil( log(h>>levels) / log(2))))
	if w == h == 8:
		# 8 x 8 won't upload
		w = 16
		h = 16
	cs = True
	ct = True
	if ( s<<(levels + 1) > w ):
		s = w>>(levels + 1)
	if ( t<<(levels +1) > h ):
		t = h>>(levels + 1)
	if ( s < x_faces ):
		cs = False
	if ( t < y_faces ):
		ct = False
	return s, t, w, h, cs, ct

def vertex_pixels( size, faces ):
	'''
	Returns a list of pixels used for vertex points on map size
	'''
	pixels = []
	for i in range( faces ):
		pixels.append( int( size * i / float(faces)) )
	pixels.append( faces - 1 )
	return pixels

def map_pixels( width, height ):
	ss = [ width - 1 ]
	ts = [ height - 1 ]
	for i in [3,2,1,0]:
		u,v = lod_size( width, height, i )
		for p in vertex_pixels( width, u ):
			if p not in ss:
				ss.append( p )
		for p in vertex_pixels( height, v ):
			if p not in ts:
				ts.append( p )
	return ss, ts

def flip_pixels( pixels ):
	m = max( pixels )
	ps = []
	for p in pixels:
		ps.append( m - p )
	return ps

#***********************************************
# sculpty object functions
#***********************************************

def getBB( obj ):
	'''
	Returns the post modifier stack bounding box for the object
	'''
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

def new_from_map( image ):
	'''
	Returns a new sculptie object created from the sculpt map image.
	'''
	Blender.Window.WaitCursor(1)
	in_editmode = Blender.Window.EditMode()
	if in_editmode:
		Blender.Window.EditMode(0)
	else:
		try:
			in_editmode = Blender.Get('add_editmode')
		except:
			pass

	sculpt_type = map_type( image )
	x_faces, y_faces = image.size
	x_faces, y_faces = face_count( x_faces, y_faces, 32, 32 )
	multires = 0
	while multires < 2 and x_faces >= 8 and y_faces >= 8 and not ( (x_faces & 1) or (y_faces & 1) ):
		x_faces = x_faces >> 1
		y_faces = y_faces >> 1
		multires += 1
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects:
		ob.sel = False
	mesh = new_mesh( image.name, sculpt_type, x_faces, y_faces )
	ob = scene.objects.new( mesh, image.name )
	ob.setLocation( Blender.Window.GetCursorPos() )
	ob.sel = True
	for f in mesh.faces:
		f.image = image
	mesh.flipNormals()
	if multires:
		mesh.multires = True
		mesh.addMultiresLevel( multires )
	mesh.sel = True
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
	mesh.addUVLayer( "UVTex")
	mesh.update()
	mesh.renderUVLayer = "UVTex"
	mesh.activeUVLayer = "UVTex"
	if in_editmode:
		Blender.Window.EditMode(1)
	Blender.Window.WaitCursor(0)
	return ob

def open( filename ):
	'''
	Creates a sculptie object from the image map file
	'''
	image = Blender.Image.Load( filename )
	image.name = Blender.sys.splitext( image.name )[0]
	image.properties["scale_x"] = 1.0
	image.properties["scale_y"] = 1.0
	image.properties["scale_z"] = 1.0
	return new_from_map( image )

def set_center ( ob, offset=( 0.0, 0.0, 0.0 ) ):
	'''
	Updates object center to middle of mesh plus offset

	ob - object to update
	offset - ( x, y, z ) offset for mesh center
	'''
	mesh=ob.getData()
	mat= ob.getmatrix()
	mesh.transform(mat)
	#mesh.update()
	mat=Blender.mathutils.matrix(
			 [1.0,0.0,0.0,0.0],
			 [0.0,1.0,0.0,0.0],
			 [0.0,0.0,1.0,0.0],
			 [0.0,0.0,0.0,1.0])
	ob.setmatrix(mat)
	bb= ob.getBoundBox()
	c=[bb[0][n]+(bb[-2][n]-bb[0][n])/2.0 for n in [0,1,2]]
	c[0] += offset[0]
	c[1] += offset[1]
	c[2] += offset[2]
	mat= ob.getmatrix()
	mat=Blender.mathutils.matrix(mat[0][:],
							mat[1][:],
							mat[2][:],
							[-c[0],-c[1],-c[2],1.0])
	mesh.transform(mat)
	#mesh.update()
	mat=Blender.mathutils.matrix(mat[0][:],
							mat[1][:],
							mat[2][:],
							[c[0],c[1],c[2],1.0])
	ob.setmatrix(mat)

#***********************************************
# sculpty mesh functions
#***********************************************

def bake_mesh( mesh, scale ):
	'''
	Bakes the mesh to the specified scale.
	'''
	currentUV = mesh.activeUVLayer
	if "sculptie" in mesh.getUVLayerNames():
		mesh.activeUVLayer = "sculptie"
	else:
		return
	for f in mesh.faces:
		if f.image != None:
			for i in range( len(f.verts) ):
				if f.uv[i][0] == 1.0:
					u = f.image.size[0] - 1
				else:
					u = round(f.uv[ i ][0] * f.image.size[0])
				if f.uv[i][1] == 1.0:
					v = f.image.size[1] - 1
				else:
					v = round(f.uv[ i ][1] * f.image.size[1])
				r,g,b = scale.xyz_to_rgb( f.verts[i].x, f.verts[i].y, f.verts[i].z )
				f.image.setPixelI( u, v, ( r, g, b, 255 ) )
	mesh.activeUVLayer = currentUV

def map_images( mesh ):
	'''
	Returns the list of images assigned to the 'sculptie' UV layer.
	'''
	images = []
	if "sculptie" in mesh.getUVLayerNames():
		currentUV = mesh.activeUVLayer
		mesh.activeUVLayer = "sculptie"
		for f in mesh.faces:
			if f.image != None:
				if f.image not in images:
					images.append( f.image )
		mesh.activeUVLayer = currentUV
	return images

def set_map( mesh, image ):
	'''
	Assigns the image to the selected 'sculptie' uv layer faces. The mesh is updated.
	'''
	currentUV = mesh.activeUVLayer
	mesh.activeUVLayer = "sculptie"
	if mesh.multires:
		levels = mesh.multiresDrawLevel
		mesh.multiresDrawLevel = 1
	for f in mesh.faces:
		if f.sel:
			f.image = image
	if mesh.multires:
		mesh.multiresDrawLevel = levels
	mesh.activeUVLayer = currentUV
	update_from_map( mesh, image )

def new_mesh( name, sculpt_type, x_faces, y_faces, levels = 0, clean_lods = True ):
	'''
	Returns a sculptie mesh created from the input

	name - the mesh name
	sculpt_type - one of "SPHERE", "TORUS", "CYLINDER", "PLANE" or "HEMI"
	x_faces - x face count
	y_faces - y face count
	levels - LOD levels
	clean_lods - aligns UV layout with power of two grid if True
	'''
	mesh = Blender.Mesh.New( name )
	uv = []
	verts = []
	seams = []
	faces = []
	wrap_x = ( sculpt_type != "PLANE" ) & ( sculpt_type != "HEMI" )
	wrap_y = ( sculpt_type == "TORUS" )
	verts_x = x_faces + 1
	verts_y = y_faces + 1
	actual_x = verts_x - wrap_x
	actual_y = verts_y - wrap_y
	uvgrid_y = []
	uvgrid_x = []
	uvgrid_s = []
	uvgrid_t = []
	s, t, w, h, clean_s, clean_t = map_size( x_faces, y_faces, levels )
	clean_s = clean_s & clean_lods
	clean_t = clean_t & clean_lods
	level_mask = 0xFFFE
	for i in range(levels):
		level_mask = level_mask<<1
	for i in range( s ):
		p = int(w * i / float(s))
		if clean_s:
			p = p & level_mask
		if p:
			p = float(p) / w
		uvgrid_s.append( p )
	uvgrid_s.append( 1.0 )
	for i in range( t ):
		p = int(h * i / float(t))
		if clean_t:
			p = p & level_mask
		if p:
			p = float(p) / h
		uvgrid_t.append( p )
	uvgrid_t.append( 1.0 )
	verts_s = s + 1 - wrap_x
	verts_t = t + 1 - wrap_y
	for i in xrange( verts_t ):
		for k in xrange( verts_s ):
			vert = Blender.Mathutils.Vector( 0.0, 0.0, 0.0 )
			mesh.verts.extend( [ vert ] )
			verts.append ( mesh.verts[-1] )
		if wrap_x:
			verts.append( mesh.verts[ -verts_s ] )
			if i:
				seams.append( ( (i - 1) * verts_s, i * verts_s ) )
				if wrap_y:
					if i == verts_t - 1:
						seams.append( ( 0, i * verts_s ) )
	if wrap_y:
		verts.extend( verts[:(s+1)] )
		for x in xrange( verts_s - 1 ):
			seams.append( ( x, x + 1 ) )
		seams.append( ( 0, verts_s - 1 ) )
	for y in xrange( t ):
		offset_y = y * (s +1)
		for x in xrange( s ):
			faces.append( ( verts[offset_y + x], verts[offset_y + s + 1 + x],
					verts[offset_y + s + x + 2], verts[offset_y + x + 1] ) )
			if wrap_x and x == verts_s - 1 and (y == 0 or y == verts_t -1):
				# blender auto alters vert order - correct uv to match
				uv.append( ( Blender.Mathutils.Vector( uvgrid_s[ x + 1 ], uvgrid_t[ y + 1 ] ),
					Blender.Mathutils.Vector( uvgrid_s[ x + 1 ], uvgrid_t[ y ] ),
					Blender.Mathutils.Vector( uvgrid_s[ x ], uvgrid_t[ y ] ),
					Blender.Mathutils.Vector( uvgrid_s[ x ], uvgrid_t[ y + 1 ] ) ) )
			else:
				uv.append( ( Blender.Mathutils.Vector( uvgrid_s[ x ], uvgrid_t[ y ] ),
					Blender.Mathutils.Vector( uvgrid_s[ x ], uvgrid_t[ y + 1 ] ),
					Blender.Mathutils.Vector( uvgrid_s[ x + 1 ], uvgrid_t[ y + 1 ] ),
					Blender.Mathutils.Vector( uvgrid_s[ x + 1 ], uvgrid_t[ y ] ) ) )
	mesh.faces.extend( faces )
	mesh.faceUV = True
	for f in xrange( len(mesh.faces) ):
		mesh.faces[ f ].uv = uv[ f ]
	mesh.renameUVLayer( mesh.activeUVLayer, "sculptie" )
	if seams != []:
		for e in mesh.findEdges( seams ):
			mesh.edges[e].flag = mesh.edges[e].flag | Blender.Mesh.EdgeFlags.SEAM
	return mesh

def update_from_map( mesh, image ):
	'''
	Updates the mesh to locations from the sculpt map image
	'''
	currentUV = mesh.activeUVLayer
	if "sculptie" in mesh.getUVLayerNames():
		mesh.activeUVLayer = "sculptie"
	verts = range( len( mesh.verts ) )
	for f in mesh.faces:
		for vi in xrange( len( f.verts) ):
			if f.verts[ vi ].index in verts:
				verts.remove( f.verts[ vi ].index )
				if f.verts[ vi ].sel:
					u, v = f.uv[ vi ]
					u = int( 2.0 / image.size[0] + u * image.size[0])
					v = int( 2.0 / image.size[1] + v * image.size[1])
					if u == image.size[0]:
						u = image.size[0] - 1
					if v == image.size[1]:
						v = image.size[1] - 1
					p  = image.getPixelF( u, v )
					f.verts[ vi ].co = Blender.Mathutils.Vector(( p[0] - 0.5),
							(p[1] - 0.5),
							(p[2] - 0.5))
	mesh.activeUVLayer = currentUV
	mesh.sel = True

#***********************************************
# sculpty image functions
#***********************************************

def bake_default( image, sculpt_type, radius = 0.25 ):
	'''
	Bakes a mathematical sculpt map to image

	sculpt_type - one of "SPHERE", "TORUS", "CYLINDER", "PLANE" or "HEMI"
	radius - inner radius value for torus
	'''
	x = image.size[0]
	y = image.size[1]
	for u in range( x ):
		path = float(u) / x
		if u == x - 1:
			path = 1.0
		for v in range( y):
			profile = float(v) / y
			if v == y - 1:
				profile = 1.0
			a = pi + 2 * pi * path
			if sculpt_type == "SPHERE":
				ps = sin( pi * profile ) / 2.0
				r = 0.5 + sin( a ) * ps
				g = 0.5 - cos( a ) * ps
				b = 0.5 -cos( pi * profile ) / 2.0
			elif sculpt_type == "CYLINDER":
				r = 0.5 + sin( a ) / 2.0
				g = 0.5 - cos( a  ) / 2.0
				b = profile
			elif sculpt_type == "TORUS":
				ps = (( 1.0 - radius ) - sin( 2.0 * pi * profile) * radius) / 2.0
				r = 0.5 + sin( a ) * ps
				g = 0.5 - cos( a ) * ps
				b = 0.5 + cos( 2 * pi * profile ) / 2.0
			elif sculpt_type == "HEMI":
				b = sqrt( 2.0 )
				z = -cos( 2 * pi * min( path, profile, 1.0 - path, 1.0 - profile) ) / 2.0
				pa = path - 0.5
				pr = profile - 0.5
				ph = sqrt(pa * pa + pr * pr)
				ps = sqrt( sin( (0.5 - z ) * pi * 0.5 ) / 2.0 )
				if ph == 0.0: ph = 1.0
				r = 0.5 + ( pa / ph * ps ) / b
				g = 0.5 + ( pr / ph * ps ) / b
				b = 0.5 + z
			else:
				r = path
				g = profile
				b= 0.0
			image.setPixelI( u, v, ( int(r * 255.0), int(g * 255.0), int(b * 255.0), 255 ) )

def bake_lod( image ):
	'''
	Bakes the sculptie LOD points for the image size.
	The brighter the blue dots, the more LODs use that pixel.
	'''
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

def bake_preview( image ):
	'''
	Bakes a pseudo 3D representation of the sculpt map image to it's alpha channel
	'''
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

def clear_alpha( image ):
	'''
	Clears the alpha channel of the sculpt map image to hide the map
	'''
	for x in xrange( image.size[0] ):
		for y in xrange( image.size[1] ):
			c1 = image.getPixelF( x, y )
			c1[3] = 0.0
			image.setPixelF( x, y, c1 )

def fill_holes( image ):
	'''
	Any pixels with alpha 0 on the image have colour interpolated from neighbours
	'''
	def getFirstX( y ):
		for x in xrange( image.size[0] ):
			c = image.getPixelF( x, y )
			if c[3] != 0:
				if x > 0: fill = True
				return c
		return None
	def getFirstY( x ):
		for y in xrange( image.size[1] ):
			c = image.getPixelF( x, y )
			if c[3] != 0:
				if y > 0: fill = True
				return c
		return None
	def fillX():
		skipx = fill = False
		for v in xrange( image.size[1] ):
			c = getFirstX( v )
			if not c :
				skipx= True
				continue
			sr = c[0]
			sg = c[1]
			sb = c[2]
			s = 0
			for u in xrange( 1, image.size[0] ):
				nc = image.getPixelF( u, v )
				if nc[3] == 0:
					if not fill:
						fill = True
				else:
					if fill:
						fill = False
						drawHLine( image, v, s, u, sr, sg, sb, nc[0], nc[1], nc[2] )
					s = u
					sr = nc[0]
					sg = nc[1]
					sb = nc[2]
			if fill:
				fill = False
				drawHLine( image, v, s, u, sr, sg, sb, sr, sg, sb )
		return skipx
	def fillY():
		fill = False
		for u in xrange( image.size[0] ):
			c = getFirstY( u )
			if not c :
				continue
			sr = c[0]
			sg = c[1]
			sb = c[2]
			s = 0
			for v in xrange( 1, image.size[1] ):
				nc = image.getPixelF( u, v )
				if nc[3] == 0:
					if not fill:
						fill = True
				else:
					if fill:
						fill = False
						drawVLine( image, u, s, v, sr, sg, sb, nc[0], nc[1], nc[2] )
					s = v
					sr = nc[0]
					sg = nc[1]
					sb = nc[2]
			if fill:
				fill = False
				drawVLine( image, u, s, v, sr, sg, sb, sr, sg, sb )
	skipx = fillX()
	fillY()
	if skipx: fillX()

def map_type( image ):
	'''
	Returns the sculpt type of the sculpt map image
	'''
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

def mirror_pixels( image ):
	'''
	Expands each pixel of the sculpt map image into a 2 x 2 block
	'''
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
