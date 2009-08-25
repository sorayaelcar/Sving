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
# Inc., 59 Temple Place - Suite 330, Boston, maximum  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

#***********************************************
# Import modules
#***********************************************

import Blender
import bpy
import os
from math import sin, cos, pi, sqrt, log, ceil, atan2, radians

lib_dir = os.path.join(bpy.config.userScriptsDir, 'primstar', 'library')

#***********************************************
# constants
#***********************************************
DRAW_ADJUST = 1.0 / 512.0

#***********************************************
# helper functions
#***********************************************

def clip(value, minimum=0, maximum=255):
	result = min(maximum, max(minimum, value))
	if value != result:
		debug(90, str(value) + "clipped to" + str(result))
	return result

def debug(num,msg):
	if Blender.Get('rt') >= num:
		print 'debug:', (' '*num), msg

def obChildren(ob):
    return [ob_child for ob_child in Blender.Object.Get() if ob_child.parent == ob]

#***********************************************
# helper classes
#***********************************************

class XYZ:
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x = x
		self.y = y
		self.z = z

	def __cmp__(self, other):
		try:
			if self.x == other.x:
				if self.y == other.y:
					return cmp(self.z, other.z)
				else:
					return cmp(self.y, other.y)
			else:
				return cmp(self.x, other.x)
		except:
			return False

	def __sub__(self, other):
		return XYZ(
			self.x - other.x,
			self.y - other.y,
			self.z - other.z
		)

	def __add__(self, other):
		return XYZ(
			self.x + other.x,
			self.y + other.y,
			self.z + other.z
		)

	def __mul__(self, scalar):
		return XYZ(
			self.x * scalar,
			self.y * scalar,
			self.z * scalar
		)

	def __div__(self, scalar):
		return XYZ(
			float(self.x) / scalar,
			float(self.y) / scalar,
			float(self.z) / scalar
		)

	def __repr__(self):
		return "XYZ(" + str(self.x) + ", " +\
			str(self.y) + ", " +\
			str(self.z) + ")"

class RGBRange:
	def __init__(self, minimum=XYZ(0, 0, 0), maximum=XYZ(255, 255, 255)):
		self.min = minimum
		self.max = maximum
		self.update()

	def convert(self, rgb):
		'''converts float rgb to integers from the range'''
		return XYZ(int(self.min.x + self.range.x * rgb.x),
				int(self.min.y + self.range.y * rgb.y),
				int(self.min.z + self.range.z * rgb.z))

	def update(self):
		'''Call after setting min and max to refresh the scale and center.'''
		self.range = self.max - self.min
		self.scale = self.range / 255.0
		self.center = (self.min + self.max * 0.5) / 255.0 - XYZ(0.5, 0.5, 0.5)

	def __repr__(self):
		return "RGBRange(" + repr(self.min) + ", " + repr(self.max) + ")"

#***********************************************
# classes
#***********************************************

class BoundingBox:
	'''class for calculating the bounding box for post modifier stack meshes'''
	def __init__(self, ob = None):
		self.rgb = RGBRange()
		self._dmin = XYZ(0.0, 0.0, 0.0)
		self._dmax = XYZ(0.0, 0.0, 0.0)
		if ob != None:
			self.min, self.max = get_bounding_box(ob)
			self._default = XYZ(False, False, False)
			self._dirty = XYZ(False, False, False)
		else:
			self._dirty = XYZ(True, True, True)
			self._default = XYZ(True, True, True)
			self.min = XYZ(0.0, 0.0, 0.0)
			self.max = XYZ(0.0, 0.0, 0.0)
		self.update()

	def __repr__(self):
		return "bb{ min=" + repr(self.min) +", max=" + repr(self.max) + ", scale=" +\
			repr(self.scale) + ", center" + repr(self.center) + "}"

	def add(self, ob):
		'''Expands box to contain object (if neccessary).'''
		minimum, maximum = get_bounding_box(ob)
		if self._dirty.x:
			if self._default.x:
				self._default.x = False
				self.min.x = minimum.x
				self.max.x = maximum.x
			else:
				self.min.x = self._dmin.x
				self.max.x = self._dmax.x
		if self._dirty.y:
			if self._default.y:
				self._default.y = False
				self.min.y = minimum.y
				self.max.y = maximum.y
			else:
				self.min.y = self._dmin.y
				self.max.y = self._dmax.y
		if self._dirty.z:
			if self._default.z:
				self._default.z = False
				self.min.z = minimum.z
				self.max.z = maximum.z
			else:
				self.min.z = self._dmin.z
				self.max.z = self._dmax.z
		if self.min.x > minimum.x:
			self.min.x = minimum.x
		if self.min.y > minimum.y:
			self.min.y = minimum.y
		if self.min.z > minimum.z:
			self.min.z = minimum.z
		if self.max.x < maximum.x:
			self.max.x = maximum.x
		if self.max.y < maximum.y:
			self.max.y = maximum.y
		if self.max.z < maximum.z:
			self.max.z = maximum.z
		self.update()

	def update(self):
		'''Call after adding objects to refresh the scale and center.'''
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

	def normalised(self):
		'''Returns a normalised version of the bounding box'''
		s = BoundingBox()
		s.min.x = s.min.y = s.min.z = min(self.min.x, self.min.y, self.min.z)
		s.max.x = s.max.y = s.max.z = max(self.max.x, self.max.y, self.max.z)
		s.update()
		return s

	def centered(self):
		'''Returns a centered version of the bounding box'''
		s = BoundingBox()
		s.min.x = min(-self.max.x, self.min.x)
		s.max.x = max(self.max.x, -self.min.x)
		s.min.y = min(-self.max.y, self.min.y)
		s.max.y = max(self.max.y, -self.min.y)
		s.min.z = min(-self.max.z, self.min.z)
		s.max.z = max(self.max.z, -self.min.z)
		s.update()
		return s

	def xyz_to_rgb(self, loc):
		'''converts a location in the bounding box to rgb sculpt map values'''
		return self.rgb.convert(self.xyz_to_float(loc))

	def xyz_to_float(self, loc):
		'''converts a location in the bounding box to float rgb sculpt map values'''
		x = (loc.x - self.min.x) / self.scale.x
		y = (loc.y - self.min.y) / self.scale.y
		z = (loc.z - self.min.z) / self.scale.z
		return XYZ(x, y ,z)

class PlotPoint:
	def __init__(self):
		self.seam = False
		self.values = []

	def add(self, value, seam):
		if self.seam:
			return
		if seam:
			self.seam = seam
			self.values = [value]
		else:
			self.values.append(value)

	def __repr__(self):
		return "(%s, %s)"%(repr(self.values), repr(self.seam))

class BakeMap:
	def __init__(self, image):
		self.map = []
		self.image = image
		self.bb_min = None
		self.bb_max = None
		self.scale = None
		self.center = None
		self.edges = {}
		self.map = [[PlotPoint() for x in range(image.size[0])] for y in range(image.size[1])]

	def plot_line(self, v1, v2, col1, col2, seam):
		c1 = XYZ(col1.co.x, col1.co.y, col1.co.z)
		c2 = XYZ(col2.co.x, col2.co.y, col2.co.z)
		x1 = int(v1.x * self.image.size[0])
		y1 = int(v1.y * self.image.size[1])
		x2 = int(v2.x * self.image.size[0])
		y2 = int(v2.y * self.image.size[1])
		steep = abs(y2 - y1) > abs(x2 - x1)
		if steep:
			x1, y1 = y1, x1
			x2, y2 = y2, x2
		if x1 > x2:
			x1, x2 = x2, x1
			y1, y2 = y2, y1
			c1, c2 = c2, c1
		mix = c2 - c1
		deltax = x2 - x1
		deltay = abs(y2 - y1)
		error = deltax / 2
		y = y1
		if y1 < y2:
			ystep = 1
		else:
			ystep = -1
		for x in range(x1, x2 + 1):
			d = x - x1
			if d:
				colour = c1 + mix * (float(d) / deltax)
			else:
				colour = c1
			if steep:
				self.plot_point(y, x, colour, seam)
			else:
				self.plot_point(x, y, colour, seam)
			error = error - deltay
			if error < 0:
				y = y + ystep
				error = error + deltax

	def plot_point(self, x, y, colour, seam):
		if x < 0:
			return
		if y < 0:
			return
		if x > self.image.size[0]:
			return
		if y > self.image.size[1]:
			return
		if x == self.image.size[0] - 1:
			seam = False
		if y == self.image.size[1] - 1:
			seam = False
		if x == self.image.size[0]:
			x = self.image.size[0] - 1
		if y == self.image.size[1]:
			y = self.image.size[1] - 1
		self.map[x][y].add(colour, seam)

	def update_map(self):
		for key, line in self.edges.iteritems():
			seam = line['seam'] or line['count'] == 1
			self.plot_line(line['uv1'][0], line['uv2'][0], line['v1'], line['v2'], seam)
			if line['count'] == 2:
				if (line['uv1'][0] != line['uv1'][1]) or (line['uv2'][0] != line['uv2'][1]):
					self.plot_line(line['uv1'][1], line['uv2'][1], line['v1'], line['v2'], seam)
			if line['count'] >= 3:
				print "Skipping extra edges: %d not drawn"%(line['count'] - 2)
		for u in range(self.image.size[0]):
			for v in range(self.image.size[1]):
				if len(self.map[u][v].values) > 1:
					value = XYZ()
					for val in self.map[u][v].values:
						value += val
					self.map[u][v].values = [value / len(self.map[u][v].values)]
				if self.map[u][v].values != []:
					if self.bb_min:
						self.bb_min.x = min(self.bb_min.x, self.map[u][v].values[0].x)
						self.bb_min.y = min(self.bb_min.y, self.map[u][v].values[0].y)
						self.bb_min.z = min(self.bb_min.z, self.map[u][v].values[0].z)
						self.bb_max.x = max(self.bb_max.x, self.map[u][v].values[0].x)
						self.bb_max.y = max(self.bb_max.y, self.map[u][v].values[0].y)
						self.bb_max.z = max(self.bb_max.z, self.map[u][v].values[0].z)
					else:
						self.bb_min = XYZ() + self.map[u][v].values[0]
						self.bb_max = XYZ() + self.map[u][v].values[0]
		self.update()

	def update(self):
		self.scale = self.bb_max - self.bb_min
		self.center = self.bb_min + self.scale * 0.5

	def bake(self, rgb=RGBRange()):
		for u in range(self.image.size[0]):
			for v in range(self.image.size[1]):
				if self.map[u][v].values:
					c = self.map[u][v].values[0] - self.bb_min
					if self.scale.x:
						c.x = c.x / self.scale.x + DRAW_ADJUST
					else:
						c.x = 0.5
					if self.scale.y:
						c.y = c.y / self.scale.y + DRAW_ADJUST
					else:
						c.y = 0.5
					if self.scale.z:
						c.z = c.z / self.scale.z + DRAW_ADJUST
					else:
						c.z = 0.5
					c = rgb.convert( c )
					self.image.setPixelI(u, v, (c.x, c.y, c.z, 255))

class LibPath:
	def __init__(self, path, root=None):
		self.path = path
		if root:
			self.local_path = path[len(root):]
		else:
			self.local_path = path
		self.name = Blender.sys.makename( path, strip=1 )

	def __lt__(self, other):
		return self.path < other.path

class LibDir(LibPath):
	def __init__(self, path, root=None):
		LibPath.__init__(self, path, root)
		self.files = []
		self.dirs = []

class LibFile(LibPath):
	pass

def build_lib(path=None, LibDir=LibDir, LibFile=LibFile):
	if not path:
		path = lib_dir
	top = LibDir(path)
	path2dir = {path: top}
	for root, dirs, files in os.walk(path):
		dirobj = path2dir[root]
		for name in dirs:
			subdirobj = LibDir(os.path.join(root, name), top.path)
			path2dir[subdirobj.path] = subdirobj
			dirobj.dirs.append(subdirobj)
		for name in files:
			if name[-4:] == '.png':
				dirobj.files.append(LibFile(os.path.join(root, name), top.path))
				dirobj.files[-1].local_path = dirobj.files[-1].local_path[:-4]
	return top

class Pixel:
	def __init__(self, u, v, rgb):
		self.u = u
		self.v = v
		self.rgb = rgb

	def __cmp__(self, other):
		if self.u == other.u:
			return cmp(self.v, other.v)
		else:
			return cmp(self.u, other.u)

	def __sub__(self, other):
		return Pixel(
			self.u - other.u,
			self.v - other.v,
			self.rgb - other.rgb
		)

	def __add__(self, other):
		return Pixel(
			self.u + other.u,
			self.v + other.v,
			self.rgb + other.rgb
		)

	def __mul__(self, scalar):
		return Pixel(
			self.u * scalar,
			self.v * scalar,
			self.rgb * scalar
		)

	def __div__(self, scalar):
		return Pixel(
			self.u / scalar,
			self.v / scalar,
			self.rgb / scalar
		)

	def __repr__(self):
		return "Pixel(" + str(self.u) + ", " +\
			str(self.v) + ", " +\
			str(self.rgb) + ")"

class Prim:
	def __init__(self, name, ob=None):
		self.name = name
		self.children = []
		self.textures = []
		self.sculpt_maps = []
		self.size = (1.0, 1.0, 1.0)
		self.rotation = (0.0, 0.0, 0.0, 1.0)
		self.location = (0.0, 0.0, 0.0)
		if ob:
			if active(ob):
				mesh = ob.getData(False, True)
				self.sculpt_maps = map_images(mesh)
				self.textures = [Texture( i ) for i in map_images(mesh, 'UVTex')]
			self.size = ob.size
			r = ob.getMatrix().rotationPart().invert().toQuat()
			self.rotation = ( r[1], r[2], r[3], r[0] )
			self.location = ob.getLocation( 'worldspace' )
			for c in obChildren(ob):
				self.children.append(Prim(c.name, c))

class Texture:
	def __init__( self, image = None ):
		self.image = image
		self.offset = ( 0.0, 0.0 )
		self.repeat = ( 1.0, 1.0 )
		self.rotation = 0.0
		self.face = 0

	def save_image( self, filename ):
		oldfile = self.image.filename
		self.image.filename = filename
		self.image.save()
		self.image.filename = oldfile

#***********************************************
# functions
#***********************************************

def active(ob):
	'''Returns True if object is an active sculptie.
	An active sculptie is a mesh with a 'sculptie' uv layer with an image assigned
	'''
	debug(50, "sculpty.active(%s)"%(ob.name))
	if ob.type == 'Mesh':
		mesh = ob.getData(False, True)
		if 'sculptie' in mesh.getUVLayerNames():
			currentUV = mesh.activeUVLayer
			mesh.activeUVLayer = "sculptie"
			for f in mesh.faces:
				if f.image != None:
					mesh.activeUVLayer = currentUV
					return True
			mesh.activeUVLayer = currentUV
	return False

def bake_default(image, sculpt_type, radius = 0.25):
	'''Bakes a mathematical sculpt map to image

	sculpt_type - one of "SPHERE", "TORUS Z", "TORUS X", "CYLINDER", "PLANE" or "HEMI"
	radius - inner radius value for torus
	'''
	debug(30, "sculpty.bake_default(%s, %s, %f)"%(image.name, sculpt_type, radius))
	x = image.size[0]
	y = image.size[1]
	for u in range(x):
		path = float(u) / x
		if u == x - 1:
			path = 1.0
		for v in range(y):
			profile = float(v) / y
			if v == y - 1:
				profile = 1.0
			rgb = uv_to_rgb(sculpt_type, path, profile, radius)
			image.setPixelF(u, v, (rgb.x, rgb.y, rgb.z , 1.0))

def bake_lod(image):
	'''Bakes the sculptie LOD points for the image size.
	The brighter the blue dots, the more LODs use that pixel.
	'''
	debug(30, "sculpty.bake_lod(%s)"%(image.name))
	x = image.size[0]
	y = image.size[1]
	for u in range(x):
		for v in range(y):
			image.setPixelF(u, v, (float(u) / x, float(v) / y, 0.0, 1.0))
	for l in range(4):
		sides = [ 6, 8, 16, 32 ][l]
		s, t = face_count(x , y, sides, sides, False)
		ss = [ int(x * k / float(s)) for k in range(s) ]
		ss.append(x - 1)
		ts = [ int(y * k / float(t)) for k in range(t) ]
		ts.append(y - 1)
		for s in ss:
			for t in ts:
				c = image.getPixelF(s, t)
				c[2] += 0.25
				image.setPixelF(s, t, c)

def bake_object(ob, bb, clear=True):
	'''Bakes the object's mesh to the specified bounding box.
	Returns False if object is not an active sculptie.
	'''
	debug(20, "sculpty.bake_object(%s, %d)"%(ob.name, clear))
	if not active(ob):
		return False
	mesh = Blender.Mesh.New()
	mesh.getFromObject(ob, 0, 1)
	images = map_images(mesh)
	maps = {}
	for i in images:
		maps[i.name] = BakeMap(i)
		if clear:
			clear_image(i)
	currentUV = mesh.activeUVLayer
	mesh.activeUVLayer = "sculptie"
	edges = dict([(ed.key, {'count':0,
		'seam':bool(ed.flag & Blender.Mesh.EdgeFlags.SEAM),
		'v1':ed.v1,
		'v2':ed.v2
		}) for ed in mesh.edges])
	for f in mesh.faces:
		if f.image:
			for key in f.edge_keys:
				if key not in maps[f.image.name].edges:
					maps[f.image.name].edges[key] = edges[key].copy()
					maps[f.image.name].edges[key]['uv1'] = []
					maps[f.image.name].edges[key]['uv2'] = []
				maps[f.image.name].edges[key]['count'] += 1
				i = f.v.index(edges[key]['v1'])
				maps[f.image.name].edges[key]['uv1'].append(XYZ(f.uv[i].x, f.uv[i].y, 0.0))
				i = f.v.index(edges[key]['v2'])
				maps[f.image.name].edges[key]['uv2'].append(XYZ(f.uv[i].x, f.uv[i].y, 0.0))
	for m in maps:
		maps[m].update_map()
		if len(maps) == 1:
			maps[m].bb_min = bb.min
			maps[m].bb_max = bb.max
			maps[m].update()
	if len(maps) > 1:
		#todo handle updating bb_min & bb_max to give common scale on joined meshes
		pass
	for m in maps:
		maps[m].image.properties['ps_scale_x'] = bb.scale.x / maps[m].scale.x
		maps[m].image.properties['ps_scale_y'] = bb.scale.y / maps[m].scale.y
		maps[m].image.properties['ps_scale_z'] = bb.scale.z / maps[m].scale.z
		maps[m].image.properties['ps_size_x'] = bb.scale.x * ob.size[0]
		maps[m].image.properties['ps_size_y'] =  bb.scale.y * ob.size[1]
		maps[m].image.properties['ps_size_z'] = bb.scale.z * ob.size[2]
		maps[m].bake(bb.rgb)
	mesh.activeUVLayer = currentUV
	return True

def bake_preview(image):
	'''Bakes a pseudo 3D representation of the sculpt map image to it's alpha channel'''
	debug(30, "sculpty.bake_preview(%s)"%(image.name))
	clear_alpha(image)
	for x in xrange(image.size[0]):
		for y in xrange(image.size[1]):
			c1 = image.getPixelF(x, y)
			f = (c1[1] * 0.35) + 0.65
			s = int((image.size[0] - 1) * (0.5 - (0.5 - c1[0]) * f))
			t = int((image.size[1] - 1) * (0.5 - (0.5 - c1[2]) * f))
			c2 = image.getPixelF(s, t)
			if c2[3] < c1[1]:
				c2[3] = c1[1]
				image.setPixelF(s, t, c2)
def check(ob):
	'''Returns true if the object is a mesh with a sculptie uv layer'''
	debug(50, "sculpty.check(%s)"%(ob.name))
	if ob.type == 'Mesh':
		mesh = ob.getData(False, True)
		if 'sculptie' in mesh.getUVLayerNames():
			return True
	return False

def clear_image(image):
	'''Clears the image to black with alpha 0'''
	debug(30, "sculpty.clear_image(%s)"%(image.name))
	for x in xrange(image.size[0]):
		for y in xrange(image.size[1]):
			image.setPixelI(x, y, (0, 0, 0, 0))

def clear_alpha(image):
	'''Clears the alpha channel of the sculpt map image to hide the map'''
	debug(30, "sculpty.clear_alpha(%s)"%(image.name))
	for x in xrange(image.size[0]):
		for y in xrange(image.size[1]):
			c1 = image.getPixelI(x, y)
			c1[3] = 0
			image.setPixelI(x, y, c1)

def draw_line(image, v1, v2, c1, c2, ends = False):
	'''Draws a gradient line on a sculpt map image'''
	x1 = v1.x
	if x1 == image.size[0] - 1:
		x1 = image.size[0]
	x2 = v2.x
	if x2 == image.size[0] - 1:
		x2 = image.size[0]
	y1 = v1.y
	if y1 == image.size[1] - 1:
		y1 = image.size[1]
	y2 = v2.y
	if y2 == image.size[1] - 1:
		y2 = image.size[1]
	steep = abs(y2 - y1) > abs(x2 - x1)
	if steep:
		x1, y1 = y1, x1
		x2, y2 = y2, x2
	if x1 > x2:
		x1, x2 = x2, x1
		y1, y2 = y2, y1
		c1, c2 = c2, c1
	mix = c2 - c1
	deltax = x2 - x1
	deltay = abs(y2 - y1)
	error = deltax / 2
	y = y1
	if y1 < y2:
		ystep = 1
	else:
		ystep = -1
	for x in range(x1, x2 + 1):
		if ends:
			draw = True
		else:
			draw = (x != x1 and x != x2)
		if draw:
			d = x - x1
			if d:
				if d == deltax:
					colour = c2
				else:
					colour = c1 + mix * (DRAW_ADJUST + float(d) / deltax)
			else:
				colour = c1
			if steep:
				draw_point(image, y, x, colour)
			else:
				draw_point(image, x, y, colour)
		error = error - deltay
		if error < 0:
			y = y + ystep
			error = error + deltax

def draw_point(image, u, v, colour):
	'''Set pixel colour for given u,v on a sculpt map'''
	if u == image.size[0] - 1:
		return
	if v == image.size[1] - 1:
		return
	if u == image.size[0]:
		u = image.size[0] - 1
	if v == image.size[1]:
		v = image.size[1] - 1
	image.setPixelF(u, v, (colour.x, colour.y, colour.z, 1.0))

def face_count(width, height, x_faces, y_faces, model = True):
	'''Returns usable face count from input

	width - sculpt map width
	height - sculpt map width
	x_faces - desired x face count
	y_faces - desired y face count
	model - when true, returns 8 x 4 instead of 9 x 4 to give extra subdivision
	'''
	debug(40, "sculpty.face_count(%d, %d, %d, %d, %d)"%(
			width, height, x_faces, y_faces, model))
	ratio = float(width) / float(height)
	verts = int(min(0.25 * width * height, x_faces * y_faces))
	if (width != height) and model:
		verts = verts & 0xfff8
	y_faces = int(sqrt(verts / ratio))
	y_faces = max(y_faces, 4)
	x_faces = verts // y_faces
	x_faces = max(x_faces, 4)
	y_faces = verts // x_faces
	return int(x_faces), int(y_faces)

def fill_holes(image):
	'''Any pixels with alpha 0 on the image have colour interpolated from neighbours'''
	debug( 30, "sculpty.fill_holes(%s)"%(image.name))
	def getFirstX(y):
		for x in xrange(image.size[0]):
			c = image.getPixelF(x, y)
			if c[3] != 0:
				if x > 0: fill = True
				return c
		return None
	def getFirstY(x):
		for y in xrange(image.size[1]):
			c = image.getPixelF(x, y)
			if c[3] != 0:
				if y > 0: fill = True
				return c
		return None
	def fillX():
		skipx = fill = False
		for v in xrange(image.size[1]):
			c = getFirstX(v)
			if not c :
				skipx= True
				continue
			sr = c[0]
			sg = c[1]
			sb = c[2]
			s = 0
			for u in xrange(1, image.size[0]):
				nc = image.getPixelF(u, v)
				if nc[3] == 0:
					if not fill:
						fill = True
				else:
					if fill:
						fill = False
						draw_line(image, XYZ(s, v, 0),
								XYZ(u, v, 0),
								XYZ(sr, sg, sb),
								XYZ(nc[0], nc[1], nc[2]))
					s = u
					sr = nc[0]
					sg = nc[1]
					sb = nc[2]
			if fill:
				fill = False
				draw_line(image, XYZ(s, v, 0),
						XYZ(u, v, 0),
						XYZ(sr, sg, sb),
						XYZ(sr, sg, sb))
		return skipx
	def fillY():
		fill = False
		for u in xrange(image.size[0]):
			c = getFirstY(u)
			if not c :
				continue
			sr = c[0]
			sg = c[1]
			sb = c[2]
			s = 0
			for v in xrange(1, image.size[1]):
				nc = image.getPixelF(u, v)
				if nc[3] == 0:
					if not fill:
						fill = True
				else:
					if fill:
						fill = False
						draw_line(image, XYZ(u, s, 0),
								XYZ(u, v, 0),
								XYZ(sr, sg, sb),
								XYZ(nc[0], nc[1], nc[2]))
					s = v
					sr = nc[0]
					sg = nc[1]
					sb = nc[2]
			if fill:
				fill = False
				draw_line(image, XYZ(u, s, 0),
						XYZ(u, v, 0),
						XYZ(sr, sg, sb),
						XYZ(sr, sg, sb))
	skipx = fillX()
	fillY()
	if skipx: fillX()

def finalise(image):
	'''Expands each active pixel of the sculpt map image'''
	debug(30, "sculpty.finalise(%s)"%(image.name))
	u_pixels, v_pixels = map_pixels(image.size[0], image.size[1])
	u_pixels.append(image.size[0])
	v_pixels.append(image.size[1])
	for x in u_pixels[:-1]:
		for y in v_pixels[:-1]:
			c = image.getPixelI(x, y)
			if x + 1 not in u_pixels:
				image.setPixelI(x + 1, y, c)
				if y + 1 not in v_pixels:
					image.setPixelI(x + 1, y + 1, c)
			if y + 1 not in v_pixels:
				image.setPixelI(x, y + 1, c)

def flip_pixels(pixels):
	'''Converts a list of pixels on a sculptie map to their mirror positions.'''
	m = max(pixels)
	return [ m - p for p in pixels ]

def get_bounding_box(obj):
	'''Returns the post modifier stack bounding box for the object'''
	debug(40, "sculpty.get_bounding_box(%s)"%(obj.name))
	mesh = Blender.Mesh.New()
	mesh.getFromObject(obj, 0, 1)
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
	return XYZ(min_x, min_y, min_z), XYZ(max_x, max_y, max_z)

def lod_info(width, height, format = "LOD%(lod)d: %(x_faces)d x %(y_faces)d\n"):
	'''Returns a string with the lod info for a map size of width * height'''
	debug(40, "sculpty.lod_info(%d, %d, %s)"%(width, height, format))
	info = ""
	for i in [3,2,1,0]:
		faces = float([ 6, 8, 16, 32 ][i])
		x_faces, y_faces = lod_size(width, height, i)
		info += format%{ 'lod':i, 'x_faces':x_faces, 'y_faces':y_faces }
	return info

def lod_size(width, height, lod):
	'''Returns x and y face counts for the given map size and lod'''
	debug(40, "sculpty.lod_size(%d, %d, %d)"%(width, height, lod))
	sides = float([ 6, 8, 16, 32 ][lod])
	ratio = float(width) / float(height)
	verts = int(min(0.25 * width * height, sides * sides))
	y_faces = int(sqrt(verts / ratio))
	y_faces = max(y_faces, 4)
	x_faces = verts // y_faces
	x_faces = max(x_faces, 4)
	y_faces = verts // x_faces
	return int(x_faces), int(y_faces)

def map_images(mesh, layer='sculptie'):
	'''Returns the list of images assigned to the 'sculptie' UV layer.'''
	debug(40, "sculpty.map_images(%s, %s)"%(mesh.name, layer))
	images = []
	if layer in mesh.getUVLayerNames():
		currentUV = mesh.activeUVLayer
		mesh.activeUVLayer = layer
		for f in mesh.faces:
			if f.image != None:
				if f.image not in images:
					images.append(f.image)
		mesh.activeUVLayer = currentUV
	return images

def map_pixels(width, height):
	'''Returns ss and ts as lists of used pixels for the given map size.'''
	debug(40, "sculpty.map_pixels(%d, %d)"%(width, height))
	ss = [ width - 1 ]
	ts = [ height - 1 ]
	for i in [3,2,1,0]:
		u,v = lod_size(width, height, i)
		for p in vertex_pixels(width, u):
			if p not in ss:
				ss.append(p)
		for p in vertex_pixels(height, v):
			if p not in ts:
				ts.append(p)
	ss.sort()
	ts.sort()
	return ss, ts

def map_size(x_faces, y_faces, levels):
	'''Suggests optimal sculpt map size for x_faces * y_faces * levels

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
	debug(30, "sculpty.map_size(%d, %d, %d)"%(x_faces, y_faces, levels))
	if ( (( x_faces == 9 and y_faces == 4) or ( x_faces == 4 and y_faces == 9))
		and levels == 0):
		s = x_faces
		t = y_faces
		w = (x_faces - x_faces % 2) * 2
		h = (y_faces - y_faces % 2) * 2
		cs = ct = False
	else:
		w = int(pow(2, levels + 1 + ceil(log(x_faces) / log(2))))
		h = int(pow(2, levels + 1 + ceil(log(y_faces) / log(2))))
		w, h = face_count(w, h, 32, 32)
		s = min(w, x_faces)
		t = min(h, y_faces)
		w = int(pow(2, levels + 1 + ceil(log(w>>levels) / log(2))))
		h = int(pow(2, levels + 1 + ceil(log(h>>levels) / log(2))))
		if w == h == 8:
			# 8 x 8 won't upload
			w = 16
			h = 16
		cs = True
		ct = True
		if (s<<(levels + 1) > w):
			s = w>>(levels + 1)
		if (t<<(levels +1) > h):
			t = h>>(levels + 1)
		if (s < x_faces):
			cs = False
		if (t < y_faces):
			ct = False
	return s, t, w, h, cs, ct

def map_type(image):
	'''Returns the sculpt type of the sculpt map image'''
	debug(20, "sculpty.map_type(%s)"%(image.name))
	poles = True
	xseam = True
	yseam = True
	p1 = image.getPixelI(0, 0)[:3]
	p2 = image.getPixelI(0, image.size[1] - 1)[:3]
	if p1 != p2:
		yseam = False
	for x in xrange(1, image.size[0] ):
		p3 = image.getPixelI(x, 0)[:3]
		p4 = image.getPixelI(x, image.size[1] - 1)[:3]
		if p1 != p3 or p2 != p4:
			poles = False
		if p3 != p4:
			yseam = False
		p1 = p3
		p2 = p4
	for y in xrange(image.size[1] ):
		p1 = image.getPixelI(0, y)[:3]
		p2 = image.getPixelI(image.size[0] - 1, y)[:3]
		if p1 != p2:
			xseam = False
	if xseam:
		if poles:
			return "SPHERE"
		if yseam:
			return "TORUS"
		return "CYLINDER"
	return "PLANE"

def new_from_map(image):
	'''Returns a new sculptie object created from the sculpt map image.'''
	debug(10, "sculpty.new_from_map(%s)"%(image.name))
	Blender.Window.WaitCursor(1)
	in_editmode = Blender.Window.EditMode()
	if in_editmode:
		Blender.Window.EditMode(0)
	else:
		try:
			in_editmode = Blender.Get('add_editmode')
		except:
			pass

	sculpt_type = map_type(image)
	x_faces, y_faces = image.size
	x_faces, y_faces = face_count(x_faces, y_faces, 32, 32)
	multires = 0
	while multires < 2 and x_faces >= 8 and y_faces >= 8 and not ((x_faces & 1) or (y_faces & 1)):
		x_faces = x_faces >> 1
		y_faces = y_faces >> 1
		multires += 1
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects:
		ob.sel = False
	mesh = new_mesh(image.name, sculpt_type, x_faces, y_faces, clean_lods=False)
	ob = scene.objects.new(mesh, image.name)
	ob.setLocation(Blender.Window.GetCursorPos())
	ob.sel = True
	for f in mesh.faces:
		f.image = image
	mesh.flipNormals()
	if multires:
		mesh.multires = True
		mesh.addMultiresLevel(multires)
	mesh.sel = True
	update_from_map(mesh, image)
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
	try:
		x = image.properties['ps_size_x']
		y = image.properties['ps_size_y']
		z = image.properties['ps_size_z']
		ob.setSize( x, y, z )
	except:
		pass
	if in_editmode:
		Blender.Window.EditMode(1)
	Blender.Window.WaitCursor(0)
	return ob

def new_mesh(name, sculpt_type, x_faces, y_faces, levels = 0, clean_lods = True, radius=0.25):
	'''Returns a sculptie mesh created from the input

	name - the mesh name
	sculpt_type - one of "SPHERE", "TORUS Z", "TORUS X", "CYLINDER", "PLANE" or "HEMI"
	x_faces - x face count
	y_faces - y face count
	levels - LOD levels
	clean_lods - aligns UV layout with power of two grid if True
	'''
	debug(10, "sculpty.new_mesh( %s, %s,%d, %d, %d, %d, %f)"%(
			name,
			sculpt_type,
			x_faces,
			y_faces,
			levels,
			clean_lods,
			radius))
	mesh = Blender.Mesh.New(name)
	uv = []
	verts = []
	seams = []
	faces = []
	wrap_x = (sculpt_type != "PLANE") and (sculpt_type != "HEMI")
	wrap_y = (sculpt_type[:5] == "TORUS")
	verts_x = x_faces + 1
	verts_y = y_faces + 1
	actual_x = verts_x - wrap_x
	actual_y = verts_y - wrap_y
	uvgrid_y = []
	uvgrid_x = []
	uvgrid_s = []
	uvgrid_t = []
	s, t, w, h, clean_s, clean_t = map_size(x_faces, y_faces, levels)
	clean_s = clean_s & clean_lods
	clean_t = clean_t & clean_lods
	level_mask = 0xFFFE
	for i in range(levels):
		level_mask = level_mask<<1
	for i in range(s):
		p = int(w * i / float(s))
		if clean_s:
			p = p & level_mask
		if p:
			p = float(p) / w
		uvgrid_s.append(p)
	uvgrid_s.append(1.0)
	for i in range(t):
		p = int(h * i / float(t))
		if clean_t:
			p = p & level_mask
		if p:
			p = float(p) / h
		uvgrid_t.append(p)
	uvgrid_t.append(1.0)
	verts_s = s + 1 - wrap_x
	verts_t = t + 1 - wrap_y
	for i in xrange(verts_t):
		profile = float(i)/t
		for k in xrange(verts_s):
			path = float(k)/s
			pos = uv_to_rgb(sculpt_type, path, profile, radius)
			vert = Blender.Mathutils.Vector(pos.x - 0.5, pos.y - 0.5, pos.z - 0.5)
			mesh.verts.extend([ vert ])
			verts.append (mesh.verts[-1])
		if wrap_x:
			verts.append(mesh.verts[ -verts_s ])
			if i:
				seams.append(((i - 1) * verts_s, i * verts_s))
				if wrap_y:
					if i == verts_t - 1:
						seams.append((0, i * verts_s))
	if wrap_y:
		verts.extend(verts[:(s+1)])
		for x in xrange(verts_s - 1):
			seams.append((x, x + 1))
		seams.append((0, verts_s - 1))
	for y in xrange(t):
		offset_y = y * (s +1)
		for x in xrange(s):
			faces.append((verts[offset_y + x], verts[offset_y + s + 1 + x],
					verts[offset_y + s + x + 2], verts[offset_y + x + 1]))
			if wrap_x and x == verts_s - 1 and (y == 0 or y == verts_t -1):
				# blender auto alters vert order - correct uv to match
				uv.append((Blender.Mathutils.Vector(uvgrid_s[ x + 1 ], uvgrid_t[ y + 1 ]),
					Blender.Mathutils.Vector(uvgrid_s[ x + 1 ], uvgrid_t[ y ]),
					Blender.Mathutils.Vector(uvgrid_s[ x ], uvgrid_t[ y ]),
					Blender.Mathutils.Vector(uvgrid_s[ x ], uvgrid_t[ y + 1 ])))
			else:
				uv.append((Blender.Mathutils.Vector(uvgrid_s[ x ], uvgrid_t[ y ]),
					Blender.Mathutils.Vector(uvgrid_s[ x ], uvgrid_t[ y + 1 ]),
					Blender.Mathutils.Vector(uvgrid_s[ x + 1 ], uvgrid_t[ y + 1 ]),
					Blender.Mathutils.Vector(uvgrid_s[ x + 1 ], uvgrid_t[ y ])))
	mesh.faces.extend(faces)
	mesh.faceUV = True
	for f in xrange(len(mesh.faces)):
		mesh.faces[ f ].uv = uv[ f ]
	mesh.renameUVLayer(mesh.activeUVLayer, "sculptie")
	if seams != []:
		for e in mesh.findEdges(seams):
			mesh.edges[e].flag = mesh.edges[e].flag | Blender.Mesh.EdgeFlags.SEAM
	return mesh

def open(filename):
	'''Creates a sculptie object from the image map file'''
	debug(10, "sculpty.open(%s)"%(filename))
	image = Blender.Image.Load(filename)
	image.name = Blender.sys.splitext(image.name)[0]
	image.properties["scale_x"] = 1.0
	image.properties["scale_y"] = 1.0
	image.properties["scale_z"] = 1.0
	return new_from_map(image)

def set_alpha(image, alpha):
	'''Sets the alpha channel of the sculpt map image to the alpha image'''
	debug(30, "sculpty.set_alpha(%s, %s)"%(image.name, alpha.name))
	for x in xrange(image.size[0]):
		for y in xrange(image.size[1]):
			c1 = image.getPixelI (x, y)
			c2 = pimage.getPixelI(x, y)
			c1[3]= c2[1]
			image.setPixelI(x, y, c1)

def set_center(ob, offset=XYZ(0.0, 0.0, 0.0)):
	'''Updates object center to middle of mesh plus offset

	ob - object to update
	offset - (x, y, z) offset for mesh center
	'''
	debug(30, "sculpty.set_center(%s, %s)"%(ob.name, str(offset)))
	children = obChildren(ob)
	for c in children:
		c.clrParent(2,1)
	bb = BoundingBox(ob)
	offset += bb.center
	mesh = ob.getData()
	mat = ob.getMatrix()
	rot_quat = mat.toQuat()
	rot = rot_quat.toMatrix().resize4x4().invert()
	trans_mat = Blender.Mathutils.TranslationMatrix(
			Blender.Mathutils.Vector(offset.x, offset.y, offset.z) * -1.0) * rot
	mesh.transform(trans_mat)
	rot.invert()
	mesh.transform(rot)
	mesh.update()
	loc_mat = Blender.Mathutils.TranslationMatrix(
			Blender.Mathutils.Vector(offset.x, offset.y, offset.z)) * rot
	moved = loc_mat.translationPart()
	scale = mat.scalePart()
	ob.loc = (ob.loc[0] + moved[0] * scale[0],
			ob.loc[1] + moved[1] * scale[1],
			ob.loc[2] + moved[2] * scale[2])
	ob.makeParent(children)
	for c in children:
		c.loc = (c.loc[0] - moved[0] * scale[0],
			c.loc[1] - moved[1] * scale[1],
			c.loc[2] - moved[2] * scale[2])

def set_map(mesh, image):
	'''Assigns the image to the selected 'sculptie' uv layer faces.'''
	debug(30, "sculpty.set_map(%s, %s)"%(mesh.name, image.name))
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

def update_from_map(mesh, image):
	'''Updates the mesh to locations from the sculpt map image'''
	debug(30, "sculpty.update_from_map(%s, %s)"%(mesh.name, image.name))
	currentUV = mesh.activeUVLayer
	if "sculptie" in mesh.getUVLayerNames():
		mesh.activeUVLayer = "sculptie"
	verts = range(len(mesh.verts))
	for f in mesh.faces:
		for vi in xrange(len(f.verts)):
			if f.verts[ vi ].index in verts:
				verts.remove(f.verts[ vi ].index)
				if f.verts[ vi ].sel:
					u, v = f.uv[ vi ]
					u = int(round(u * image.size[0]))
					v = int(round(v * image.size[1]))
					if u == image.size[0]:
						u = image.size[0] - 1
					if v == image.size[1]:
						v = image.size[1] - 1
					p  = image.getPixelF(u, v)
					#adjust = 256.0 / 255.0
					#x = min( p[0]  * adjust, 1.0 ) - 0.5
					#y = min( p[1]  * adjust, 1.0 ) - 0.5
					#z = min( p[2]  * adjust, 1.0 ) - 0.5
					x = p[0] - 0.5
					y = p[1] - 0.5
					z = p[2] - 0.5
					f.verts[ vi ].co = Blender.Mathutils.Vector(x, y, z)
	mesh.activeUVLayer = currentUV
	mesh.sel = True

def uv_corners(mesh):
	'''returns the four corner points of the UV layout'''
	debug(40, "sculpty.uv_corners(%s)"%(mesh.name))
	max_vu = XYZ(-99999.0, -99999.0, 0.0 )
	min_vu = XYZ(99999.0, 99999.0, 0.0 )
	max_uv = XYZ(-99999.0, -99999.0, 0.0 )
	min_uv = XYZ(99999.0, 99999.0, 0.0 )
	for f in mesh.faces:
		for i in range(len(f.verts)):
			v = XYZ(f.uv[i][0], f.uv[i][1], 0.0)
			max_uv = max(max_uv, v)
			min_uv = min(min_uv, v)
			v = XYZ(f.uv[i][1], f.uv[i][0], 0.0)
			max_vu = max(max_vu, v)
			min_vu = min(min_vu, v)
	min_vu = XYZ(min_vu.y, min_vu.x, 0.0)
	max_vu = XYZ(max_vu.y, max_vu.x, 0.0)
	if min_vu == min_uv:
		min_uv.y = max_uv.y
	if max_vu == max_uv:
		max_vu.y = min_vu.y
	return min_vu, min_uv, max_vu, max_uv

def uv_params(mesh):
	'''returns the offset, scale and rotation of the UV layout'''
	debug(40, "sculpty.uv_params(%s)"%(mesh.name))
	bl, tl, br, tr = uv_corners(mesh)
	hv = tl - bl
	wv = br - bl
	a = atan2(hv.x,hv.y)
	s = XYZ( Blender.Mathutils.Vector( wv.x, wv.y ).length,
			Blender.Mathutils.Vector( hv.x, hv.y ).length, 0.0 )
	return bl + (tr - bl) / 2.0 - XYZ(0.5, 0.5, 0.0), s, a

def uv_to_rgb(sculpt_type, u, v, radius=0.25):
	'''Returns 3D location for the given UV co-ordinates on a default sculpt type'''
	debug(90, "sculpty.uv_to_rgb(%s, %f, %f, %f)"%(sculpt_type, u, v, radius))
	a = pi + 2 * pi * u
	if sculpt_type == "SPHERE":
		ps = sin(pi * v) / 2.0
		r = 0.5 + sin(a) * ps
		g = 0.5 - cos(a) * ps
		b = 0.5 -cos(pi * v) / 2.0
	elif sculpt_type == "CYLINDER":
		r = 0.5 + sin(a) / 2.0
		g = 0.5 - cos(a) / 2.0
		b = v
	elif sculpt_type == "TORUS Z":
		v += 0.25
		ps = ((1.0 - radius) - sin(2.0 * pi * v) * radius) / 2.0
		r = 0.5 + sin(a) * ps
		g = 0.5 - cos(a) * ps
		b = 0.5 + cos(2 * pi * v) / 2.0
	elif sculpt_type == "TORUS X":
		a = pi + 2 * pi * v
		u += 0.25
		ps = ((1.0 - radius) - sin(2.0 * pi * u) * radius) / 2.0
		r = 0.5 + cos(2 * pi * u) / 2.0
		g = 0.5 - cos(a) * ps
		b = 0.5 + sin(a) * ps
	elif sculpt_type == "HEMI":
		z = -cos(2 * pi * min(u, v, 1.0 - u, 1.0 - v)) / 2.0
		pa = u - 0.5
		pr = v - 0.5
		ph = sqrt(pa * pa + pr * pr)
		ps = sqrt(sin((0.5 - z) * pi * 0.5) / 2.0)
		if ph == 0.0: ph = 1.0
		sr2 = sqrt(2.0)
		r = 0.5 + (pa / ph * ps) / sr2
		g = 0.5 + (pr / ph * ps) / sr2
		b= 0.5 + z
	else:
		r = u
		g = v
		b = 0.5
	return XYZ(r, g, b)

def vertex_pixels(size, faces):
	'''Returns a list of pixels used for vertex points on map size'''
	debug(50, "sculpty.vertex_pixels(%d, %d)"%(size, faces))
	pixels = [ int(size * i / float(faces)) for i in range(faces) ]
	pixels.append(faces - 1)
	return pixels
