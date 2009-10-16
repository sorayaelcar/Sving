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

import Blender
from primstar.sculpty import XYZ, map_images, obChildren, active, map_type
from primstar.gui import debug
from math import atan2

class Prim:
	def __init__(self, name):
		self.name = name
		self.children = []
		self.textures = []
		self.sculpt_map = None
		self.size = XYZ(1.0, 1.0, 1.0)
		self.rotation = (0.0, 0.0, 0.0, 1.0)
		self.location = XYZ(0.0, 0.0, 0.0)

class Texture:
	def __init__(self, image):
		self.image = image
		self.offset = XYZ(0.0, 0.0, 0.0)
		self.repeat = XYZ(1.0, 1.0, 0.0)
		self.rotation = 0.0
		self.face = 0

	def save_image(self, filename):
		oldfile = self.image.filename
		self.image.filename = filename
		self.image.save()
		self.image.filename = oldfile

def mesh2Prim(ob, rootprim = None):
	mesh = ob.getData(False, True)
	images, textures = map_images(mesh, 'sculptie', 'UVTex')
	size = XYZ(ob.size[0], ob.size[1], ob.size[2])
	r = ob.getMatrix().rotationPart().invert().toQuat()
	rotation = (r[1], r[2], r[3], r[0])
	l = ob.getLocation('worldspace')
	location = XYZ(l[0], l[1], l[2])
	for i in range(len(images)):
		image = images[i]
		texture = textures[i]
		newprim = Prim(image.name)
		newprim.sculpt_map = image
		if texture:
			newtex = Texture(texture)
			newtex.offset, newtex.repeat, newtex.rotation = uv_params(mesh, image)
			newprim.textures.append(newtex)
		newprim.rotation = rotation
		newprim.size = XYZ(
				image.properties['primstar']['scale_x'] * size.x,
				image.properties['primstar']['scale_y'] * size.y,
				image.properties['primstar']['scale_z'] * size.z)
		newprim.location = XYZ(
			image.properties['primstar']['loc_x'],
			image.properties['primstar']['loc_y'],
			image.properties['primstar']['loc_z'])
		if rootprim == None:
			rootprim = newprim
		else:
			newprim.location -= rootprim.location
			rootprim.children.append(newprim)
	return rootprim

def ob2Prim(ob, rootprim = None):
	if active(ob):
		rootprim = mesh2Prim(ob, rootprim)
	for c in obChildren(ob):
		rootprim = ob2Prim(c, rootprim)
	return rootprim

def get_prims():
	prims = []
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects.selected:
		# collect prims
		if ob.parent != None:
			continue
		rootprim = ob2Prim(ob)
		if rootprim != None:
			prims.append(rootprim)
	return prims

def uv_corners(mesh, image=None):
	'''returns the four corner points of the UVTex layout for the sculpt map image'''
	debug(40, "primitive.uv_corners(%s, %s)"%(mesh.name, image.name))
	max_vu = XYZ(-99999.0, -99999.0, 0.0)
	min_vu = XYZ(99999.0, 99999.0, 0.0)
	max_uv = XYZ(-99999.0, -99999.0, 0.0)
	min_uv = XYZ(99999.0, 99999.0, 0.0)
	current_uv = mesh.activeUVLayer
	mesh.activeUVLayer = 'sculptie'
	if image:
		faces = [f for f in mesh.faces if f.image == image]
	else:
		faces = mesh.faces
	mesh.activeUVLayer = 'UVTex'
	for f in faces:
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
	mesh.activeUVLayer = current_uv
	return min_vu, min_uv, max_vu, max_uv

def uv_params(mesh, image=None):
	'''returns the offset, scale and rotation of the UVTex layout for the sculpt map image'''
	debug(40, "primitive.uv_params(%s, %s)"%(mesh.name, image.name))
	bl, tl, br, tr = uv_corners(mesh, image)
	hv = tl - bl
	wv = br - bl
	a = atan2(hv.x,hv.y)
	s = XYZ(Blender.Mathutils.Vector(wv.x, wv.y).length,
			Blender.Mathutils.Vector(hv.x, hv.y).length, 0.0)
	return bl + (tr - bl) / 2.0 - XYZ(0.5, 0.5, 0.0), s, a
