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
# helper functions
#***********************************************

def clip( v ):
			return min( 0, max( 255, v ) )

#***********************************************
# helper classes
#***********************************************

class xyz:
	def __init__( self, x, y, z ):
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
	'''
	class for calculating the bounding box for post modifier stack meshes
	'''
	def __init__( self, ob = None ):
		self.rgb = rgb_range()
		self._dirty = xyz( True, True, True )
		self._dmin = None
		self._dmax = None
		if ob != None:
			bb = getBB( ob )
			self.min = xyz( bb[0][0], bb[0][1], bb[0][2] )
			self.max = xyz( bb[1][0], bb[1][1], bb[1][2] )
			self._default = xyz( False, False, False )
		else:
			self._default = xyz( True, True, True )
			self.min = xyz( 0.0, 0.0, 0.0 )
			self.max = xyz( 0.0, 0.0, 0.0 )
		self.update()

	def add( self, ob ):
		'''
		Expands box to contain object (if neccessary).
		'''
		bb = getBB( ob )
		mi = xyz( bb[0] )
		ma = xyz( bb[1] )
		if self._dirty.x:
			if self._default.x:
				self._default.x = False
				self.min.x = mi.x
				self.max.x = ma.x
			else:
				self.min.x = self._dmin.x
				self.max.x = self._dmax.x
		if self._dirty.y:
			if self._default.y:
				self._default.y = False
				self.min.y = mi.y
				self.max.y = ma.y
			else:
				self.min.y = self._dmin.y
				self.max.y = self._dmax.y
		if self._dirty.z:
			if self._default.z:
				self._default.z = False
				self.min.z = mi.z
				self.max.z = ma.z
			else:
				self.min.z = self._dmin.z
				self.max.z = self._dmax.z
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
		'''
		Call after adding objects to refresh the scale and center.
		'''
		self.scale = self.max - self.min
		if self.scale.x == 0.0:
			self._dmin.x = self.min.x
			self._dmax.x = self.max.x
			self.min.x = -0.5
			self.max.x = 0.5
			self.scale.x = 1.0
			self._dirty.x = True
		else:
			self._dirty.x = False
		if self.scale.y == 0.0:
			self._dmin.y = self.min.y
			self._dmax.y = self.max.y
			self.min.y = -0.5
			self.max.y = 0.5
			self.scale.y = 1.0
			self._dirty.y = True
		else:
			self._dirty.y = False
		if self.scale.z == 0.0:
			self._dmin.z = self.min.z
			self._dmax.z = self.max.z
			self.min.z = -0.5
			self.max.z = 0.5
			self.scale.z = 1.0
			self._dirty.z = True
		else:
			self._dirty.z = False
		self.center = self.min + self.scale * 0.5

	def normalised( self ):
		'''
		Returns a normalised version of the bounding box
		'''
		s = bounding_box()
		s.min.x = s.min.y = s.min.z = min( self.min.x, self.min.y, self.min.z )
		s.max.x = s.max.y = s.max.z = max( self.max.x, self.max.y, self.max.z )
		s.update()
		return s

	def centered( self ):
		'''
		Returns a centered version of the bounding box
		'''
		s = bounding_box()
		s.min.x = min( -self.max.x, self.min.x )
		s.max.x = max( self.max.x, -self.min.x )
		s.min.y = min( -self.max.y, self.min.y )
		s.max.y = max( self.max.y, -self.min.y )
		s.min.z = min( -self.max.z, self.min.z )
		s.max.z = max( self.max.z, -self.min.z )
		s.update()
		return s

	def xyz_to_rgb( self, loc ):
		'''
		converts a location in the bounding box to rgb sculpt map values
		'''
		x = ( loc.x - self.min.x ) / self.scale.x
		y = ( loc.y - self.min.y ) / self.scale.y
		z = ( loc.z - self.min.z ) / self.scale.z
		return self.rgb.convert( xyz( x, y, z) )

class rgb_range:
	def __init__( self, min_r = 0, max_r = 255, min_g = 0, max_g = 255, min_b = 0, max_b = 255 ):
		self.min = xyz( min_r, min_g, min_b )
		self.max = xyz( max_r, max_g, max_b )
		self.update()

	def convert( self, rgb ):
		'''
		converts float rgb to integers from the range
		'''
		return xyz( clip( self.min.x + int( self.max.x * rgb.x ) ),
				clip( self.min.y + int( self.max.y * rgb.y ) ),
				clip( self.min.z + int( self.max.z * rgb.z ) ) )

	def update( self ):
		'''
		Call after setting min and max to refresh the scale and center.
		'''
		self.scale = xyz( ( self.max.x - self.min.x ) / 255.0,
				( self.max.y - self.min.y ) / 255.0,
				( self.max.z - self.min.z ) / 255.0 )
		self.center = xyz( (( self.min.x + ( self.max.x * 0.5 )) / 255.0 ) - 0.5,
				(( self.min.y + ( self.max.y * 0.5 )) / 255.0 ) - 0.5,
				(( self.min.z + ( self.max.z * 0.5 )) / 255.0 ) - 0.5 )

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
	pixels = [ int( size * i / float(faces)) for i in range( faces ) ]
	pixels.append( faces - 1 )
	return pixels

def map_pixels( width, height ):
	'''
	Returns ss and ts as lists of used pixels for the given map size.
	'''
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
	ss.sort()
	ts.sort()
	return ss, ts

def flip_pixels( pixels ):
	'''
	Converts a list of pixels on a sculptie map to their mirror positions.
	'''
	m = max( pixels )
	return [ m - p for p in pixels ]

#***********************************************
# sculpty object functions
#***********************************************

def active( ob ):
	'''
	Returns True if object is an active sculptie.
	An active sculptie is a mesh with a 'sculptie' uv layer with an image assigned
	'''
	if ob.type == 'Mesh':
		mesh = ob.getData( False, True)
		if 'sculptie' in mesh.getUVLayerNames():
			currentUV = mesh.activeUVLayer
			mesh.activeUVLayer = "sculptie"
			for f in mesh.faces:
				if f.image != None:
					mesh.activeUVLayer = currentUV
					return True
			mesh.activeUVLayer = currentUV
	return False

def bake_object( ob, bb, clear = True, fill = True ):
	'''
	Bakes the object's mesh to the specified bounding box.
	'''
	mesh = Blender.Mesh.New()
	mesh.getFromObject( ob, 0, 1 )
	images = map_images( mesh )
	if images == []:
		# skip bounding boxes - meshes with sculptie uv but no image
		return
	for i in images:
		i.properties['scale_x'] = bb.scale.x
		i.properties['scale_y'] = bb.scale.y
		i.properties['scale_z'] = bb.scale.z
		if clear:
			clear_image( i )
	currentUV = mesh.activeUVLayer
	mesh.activeUVLayer = "sculptie"
	for f in mesh.faces:
		if f.image != None:
			uvmap = []
			for i in range( len(f.verts) ):
				if f.uv[i][0] == 1.0:
					u = f.image.size[0] - 1
				else:
					u = int(f.uv[ i ][0] * f.image.size[0])
				if f.uv[i][1] == 1.0:
					v = f.image.size[1] - 1
				else:
					v = int(f.uv[ i ][1] * f.image.size[1])
				rgb = bb.xyz_to_rgb( f.verts[i].co )
				uvmap.append( (u, v, rgb) )
			for i in range( len(uvmap) - 1 ):
				drawn = False
				v1 = uvmap[ i ]
				for v2 in uvmap[ i + 1: ]:
					if v1[0] == v2[0]:
						drawVLineI( f.image, v1[0], v1[1], v2[1],
								v1[2].x, v1[2].y, v1[2].z,
								v2[2].x, v2[2].y, v2[2].z )
						drawn = True
					elif v1[1] == v2[1]:
						drawHLineI( f.image, v1[1], v1[0], v2[0],
								v1[2].x, v1[2].y, v1[2].z,
								v2[2].x, v2[2].y, v2[2].z )
						drawn = True
					else:
						u ,v, rgb = v2
						f.image.setPixelI( u, v, ( rgb.x, rgb.y, rgb.z, 255 ) )
				if not drawn:
					u ,v, rgb = v1
					f.image.setPixelI( u, v, ( rgb.x, rgb.y, rgb.z, 255 ) )

	mesh.activeUVLayer = currentUV
	if fill:
		for i in images:
			fill_holes( i )
			expand_pixels( i )

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

def set_center( ob, offset=( 0.0, 0.0, 0.0 ) ):
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
	wrap_x = ( sculpt_type != "PLANE" ) and ( sculpt_type != "HEMI" )
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
	expand_pixels( image )

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
		ss = [ int(x * k / float(s)) for k in range( s ) ]
		ss.append( x - 1 )
		ts = [ int(y * k / float(t)) for k in range( t ) ]
		ts.append( y - 1)
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

def clear_image( image ):
	'''
	Clears the image to black with alpha 0
	'''
	for x in xrange( image.size[0] ):
		for y in xrange( image.size[1] ):
			image.setPixelI( x, y, (0, 0, 0, 0 ))

def clear_alpha( image ):
	'''
	Clears the alpha channel of the sculpt map image to hide the map
	'''
	for x in xrange( image.size[0] ):
		for y in xrange( image.size[1] ):
			c1 = image.getPixelI( x, y )
			c1[3] = 0
			image.setPixelI( x, y, c1 )

def set_alpha( image, alpha ):
	'''
	Sets the alpha channel of the sculpt map image to the alpha image
	'''
	for x in xrange( image.size[0] ):
		for y in xrange( image.size[1] ):
			c1 = image.getPixelI ( x, y )
			c2 = pimage.getPixelI( x, y )
			c1[3]= c2[1]
			image.setPixelI( x, y, c1 )

def drawHLineI( image, y, s, e, sr, sg, sb, er, eg, eb ):
	'''
	Draws a horizontal line on the image on row y, from column s to e.

	image - where to draw
	y - v co-ordinate
	s - start u co-ordinate
	e - end u co-ordinate
	sr - start red
	sg - start green
	sb - start blue
	er - end red
	eg - end green
	eb - end blue
	'''
	if s - e == 0:
		image.setPixelI( s, y, ( (sr + er) // 2, (sg +eg) // 2, (sb +eb) // 2, 255 ) )
		return
	dr = ( er - sr ) / ( e - s )
	dg = ( eg - sg ) / ( e - s )
	db = ( eb - sb ) / ( e - s )
	for u in xrange( s, e ):
		if u == image.size[0]:
			image.setPixelI( u - 1, y, ( clip(int(sr)), clip(int(sg)), clip(int(sb)), 255 ) )
		else:
			image.setPixelI( u, y, ( clip(int(sr)), clip(int(sg)), clip(int(sb)), 255 ) )
		sr += dr
		sg += dg
		sb += db

def drawVLineI( image, x, s, e, sr, sg, sb, er, eg, eb ):
	'''
	Draws a vertical line on the image on column x, from row s to e.

	image - where to draw
	x - u co-ordinate
	s - start v co-ordinate
	e - end v co-ordinate
	sr - start red
	sg - start green
	sb - start blue
	er - end red
	eg - end green
	eb - end blue
	'''
	if x < 0 or s < 0 or x > image.size[0] or e > image.size[1]:
		raise ValueError
	if x == image.size[0]:
		x -= 1
	if s - e == 0:
		if s == image.size[1]:
			s -= 1
		image.setPixelI( x, s, ( clip((sr + er) // 2), clip((sg +eg) // 2), clip((sb +eb)//2), 255 ) )
		return
	dr = ( er - sr ) / ( e - s )
	dg = ( eg - sg ) / ( e - s )
	db = ( eb - sb ) / ( e - s )
	for v in xrange( s, e + 1 ):
		if v == image.size[1]:
			image.setPixelI( x, v - 1, ( clip(int(sr)), clip(int(sg)), clip(int(sb)), 255 ) )
		else:
			image.setPixelI( x, v, ( clip(int(sr)), clip(int(sg)), clip(int(sb)), 255 ) )
		sr += dr
		sg += dg
		sb += db

def expand_pixels( image ):
	'''
	Expands each active pixel of the sculpt map image
	'''
	ss, ts = map_pixels( image.size[0], image.size[1] )
	d = 2
	for y in xrange( 0, image.size[1], d ):
		for x in xrange( 0, image.size[0] - 1):
			if x in ss:
				c = image.getPixelI( x, y )
			else:
				image.setPixelI( x, y, c )
	y = image.size[1] - 1
	for x in xrange( 0, image.size[0] - 1):
			if x in ss:
				c = image.getPixelI( x, y )
			else:
				image.setPixelI( x, y, c )
	for x in xrange( 0, image.size[0] ):
		for y in xrange( 0, image.size[1] -1 ):
			if y in ts:
				c = image.getPixelI( x, y )
			else:
				image.setPixelI( x, y, c )

def fill_holes( image ):
	'''
	Any pixels with alpha 0 on the image have colour interpolated from neighbours
	'''
	def getFirstX( y ):
		for x in xrange( image.size[0] ):
			c = image.getPixelI( x, y )
			if c[3] != 0:
				if x > 0: fill = True
				return c
		return None
	def getFirstY( x ):
		for y in xrange( image.size[1] ):
			c = image.getPixelI( x, y )
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
				nc = image.getPixelI( u, v )
				if nc[3] == 0:
					if not fill:
						fill = True
				else:
					if fill:
						fill = False
						drawHLineI( image, v, s, u, sr, sg, sb, nc[0], nc[1], nc[2] )
					s = u
					sr = nc[0]
					sg = nc[1]
					sb = nc[2]
			if fill:
				fill = False
				drawHLineI( image, v, s, u, sr, sg, sb, sr, sg, sb )
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
				nc = image.getPixelI( u, v )
				if nc[3] == 0:
					if not fill:
						fill = True
				else:
					if fill:
						fill = False
						drawVLineI( image, u, s, v, sr, sg, sb, nc[0], nc[1], nc[2] )
					s = v
					sr = nc[0]
					sg = nc[1]
					sb = nc[2]
			if fill:
				fill = False
				drawVLineI( image, u, s, v, sr, sg, sb, sr, sg, sb )
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
