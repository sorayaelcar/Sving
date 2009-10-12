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
# Inc., 59 Temple Place - Suite 330, Boston, maximum  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

class Prim:
	def __init__(self, name, ob=None):
		self.name = name
		self.children = []
		self.textures = []
		self.sculpt_maps = []
		self.size = XYZ(1.0, 1.0, 1.0)
		self.rotation = (0.0, 0.0, 0.0, 1.0)
		self.location = XYZ(0.0, 0.0, 0.0)
		if ob:
			if active(ob):
				mesh = ob.getData(False, True)
				self.sculpt_maps = map_images(mesh)
				self.textures = [Texture(i, mesh) for i in map_images(mesh, 'UVTex')]
			self.size = ob.size
			r = ob.getMatrix().rotationPart().invert().toQuat()
			self.rotation = (r[1], r[2], r[3], r[0])
			location = ob.getLocation('worldspace')
			self.location = XYZ(location.x, location.y, location.z)
			for c in obChildren(ob):
				self.children.append(Prim(c.name, c))

class Texture:
	def __init__(self, image = None, mesh = None):
		self.image = image
		if mesh:
			self.offset, self.repeat, self.rotation = uv_params(mesh)
		else:
			self.offset = XYZ(0.0, 0.0, 0.0)
			self.repeat = XYZ(1.0, 1.0, 0.0)
			self.rotation = 0.0
		self.face = 0

	def save_image(self, filename):
		oldfile = self.image.filename
		self.image.filename = filename
		self.image.save()
		self.image.filename = oldfile

def get_prims():
	prims = []
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects.selected:
		# collect prims
		if ob.parent != None:
			continue
		if active(ob):
			rootprim = Prim( ob.name, ob )
			prims.append( rootprim )
	return prims

def uv_corners(mesh):
	'''returns the four corner points of the UV layout'''
	debug(40, "primitive.uv_corners(%s)"%(mesh.name))
	max_vu = XYZ(-99999.0, -99999.0, 0.0)
	min_vu = XYZ(99999.0, 99999.0, 0.0)
	max_uv = XYZ(-99999.0, -99999.0, 0.0)
	min_uv = XYZ(99999.0, 99999.0, 0.0)
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

def uv_params(mesh, layer='UVTex'):
	'''returns the offset, scale and rotation of the UV layout'''
	debug(40, "primitive.uv_params(%s, %s)"%(mesh.name, layer))
	currentUV = mesh.activeUVLayer
	mesh.activeUVLayer = layer
	bl, tl, br, tr = uv_corners(mesh)
	mesh.activeUVLayer = currentUV
	hv = tl - bl
	wv = br - bl
	a = atan2(hv.x,hv.y)
	s = XYZ(Blender.Mathutils.Vector(wv.x, wv.y).length,
			Blender.Mathutils.Vector(hv.x, hv.y).length, 0.0)
	return bl + (tr - bl) / 2.0 - XYZ(0.5, 0.5, 0.0), s, a
