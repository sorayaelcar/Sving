#!BPY

"""
Name: 'Bake Second Life Sculpties'
Blender: 245
Group: 'Render'
Tooltip: 'Bake Sculptie Maps on Active objects'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.34"
__bpydoc__ = """\

Bake Sculptie Map

This script requires a square planar mapping. It bakes the local vertex
positions to the prim's sculptie map image.
"""

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
from sys import version_info
import sculpty

#***********************************************
# Classes
#***********************************************

class pixel:
	def __init__(self, x, y, r, g, b):
		self.x = x
		self.y = y
		self.r = r
		self.g = g
		self.b = b

	def __cmp__(self, other):
		if self.x == other.x:
			return cmp(self.y, other.y)
		else:
			return cmp(self.x, other.x)

	def __sub__(self, other):
		return pixel(
			self.x - other.x,
			self.y - other.y,
			self.r - other.r,
			self.g - other.g,
			self.b - other.b
		)

	def __add__(self, other):
		return pixel(
			self.x + other.x,
			self.y + other.y,
			self.r + other.r,
			self.g + other.g,
			self.b + other.b
		)

	def __mul__(self, scalar):
		return pixel(
			self.x * scalar,
			self.y * scalar,
			self.r * scalar,
			self.g * scalar,
			self.b * scalar,
		)

	def __repr__(self):
		return "pixel(" + str(self.x) + ", " +\
			str(self.y) + ", " +\
			str(self.r) + ", " +\
			str(self.g) + ", " +\
			str(self.b) + ")"

class scaleRange:
	def __init__ ( self, objects, normalised, centered = 0, colourRange= ( 0,255,0,255,0,255 )):
		self.minx = None
		self.minr = colourRange[0]
		self.r = colourRange[1] - self.minr
		self.ming = colourRange[2]
		self.g = colourRange[3] - self.ming
		self.minb = colourRange[4]
		self.b = colourRange[5] - self.minb
		for ob in objects:
			if ob.type == 'Mesh':
				bb = sculpty.getBB( ob )
				if self.minx == None:
					self.minx, self.miny, self.minz = bb[0]
					self.maxx, self.maxy, self.maxz = bb[1]
				else:
					if bb[0][0] < self.minx:
						self.minx = bb[0][0]
					if bb[0][1] < self.miny:
						self.miny = bb[0][1]
					if bb[0][2] < self.minz:
						self.minz = bb[0][2]
					if bb[1][0] > self.maxx:
						self.maxx = bb[1][0]
					if bb[1][1] > self.maxy:
						self.maxy = bb[1][1]
					if bb[1][2] > self.maxz:
						self.maxz = bb[1][2]
				if normalised == 0:
					self.minx = self.miny = self.minz = min( self.minx, self.miny, self.minz )
					self.maxx = self.maxy = self.maxz = max( self.maxx, self.maxy, self.maxz )
				if centered == 1:
					if -self.minx > self.maxx:
						self.maxx = -self.minx
					else:
						self.minx = -self.maxx
					if -self.miny > self.maxy:
						self.maxy = -self.miny
					else:
						self.miny = -self.maxy
					if -self.minz > self.maxz:
						self.maxz = -self.minz
					else:
						self.minz = -self.maxz
				self.x = self.maxx - self.minx
				self.y = self.maxy - self.miny
				self.z = self.maxz - self.minz
				# avoid divide by zero errors
				if self.x == 0.0:
					self.minx -= 0.5
					self.maxx += 0.5
					self.x = 1.0
				if self.y == 0.0:
					self.y = 1.0
					self.miny -= 0.5
					self.maxy += 0.5
				if self.z == 0.0:
					self.minz -= 0.5
					self.maxz += 0.5
					self.z = 1.0

	def normalise( self, co ):
		r = ( co[0] - self.minx ) / self.x
		g = ( co[1] - self.miny ) / self.y
		b = ( co[2] - self.minz ) / self.z
		if r > 1.0: r = 1.0
		if g > 1.0: g = 1.0
		if b > 1.0: b = 1.0
		return r, g, b
		
	def adjusted( self, co ):
		r, g, b = self.normalise( co )
		r = (self.minr + ( r * self.r )) / 255.0
		g = (self.ming + ( g * self.g )) / 255.0
		b = (self.minb + ( b * self.b )) / 255.0
		return r, g, b

#***********************************************
# Functions
#***********************************************

if version_info[0] == 2 and version_info[1] < 4:
	# sorted function for python 2.3
	def sorted(seq):
		newseq = seq[:]
		newseq.sort()
		return newseq

def drawTri( image, verts ):
	scanlines = [ verts[0] ]
	if int(verts[0].x) != int(verts[1].x):
		scanlines.extend( [ verts[0] ])
		if int(verts[1].x) == int(verts[2].x):
			scanlines.extend( [ verts[1], verts[2] ] )
		else:
			n = verts[0] + (( verts[2] - verts[0] ) * (( verts[1].x - verts[0].x ) / ( verts[2].x - verts[0].x )))
			if verts[1].y < verts[2].y:
				scanlines.extend( [ verts[1], n, verts[1], n, verts[2], verts[2] ] )
			else:
				scanlines.extend( [ n, verts[1], n, verts[1], verts[2], verts[2] ] )
	else:
		scanlines.extend( [ verts[1], verts[2], verts[2] ] )
	while scanlines:
		s1 = scanlines[ 0 ]
		s2 = scanlines[ 1 ]
		e1 = scanlines[ 2 ]
		e2 = scanlines[ 3 ]
		scanlines = scanlines[4:]
		r1 = e1 - s1
		r2 = e2 - s2
		x = xs = float(int(s1.x))
		ex = float(int(e1.x))
		while x <= ex and x <= image.size[0]:
			if r1.x == 0:
				s = ( x - xs )
			else:
				s = ( x - xs ) / r1.x
			if s < 0.0:
				x += 1.0
				continue
			drawVLine( image, int(x),
				int( s1.y + r1.y * s ),
				int( s2.y + r2.y * s ),
				s1.r + r1.r * s,
				s1.g + r1.g * s,
				s1.b + r1.b * s,
				s2.r + r2.r * s,
				s2.g + r2.g * s,
				s2.b + r2.b * s
			)
			x += 1.0
			
def drawHLine( image, y, s, e, sr, sg, sb, er, eg, eb ):
	if s - e == 0:
		image.setPixelF( s, y, ( sr, sg, sb, 1.0 ) )
		return
	dr = ( er - sr ) / ( e - s )
	dg = ( eg - sg ) / ( e - s )
	db = ( eb - sb ) / ( e - s )
	for u in xrange( s, e ):
		if u == image.size[0]:
			image.setPixelF( u - 1, y, ( sr, sg, sb, 1.0 ) )
		else:
			image.setPixelF( u, y, ( sr, sg, sb, 1.0 ) )
		sr += dr
		sg += dg
		sb += db
		if sr < 0:
			sr = 0
		if sg < 0:
			sg = 0
		if sb < 0:
			sb = 0
		if sr > 1.0:
			sr = 1.0
		if sg > 1.0:
			sg = 1.0
		if sb > 1.0:
			sb = 1.0

def drawVLine( image, x, s, e, sr, sg, sb, er, eg, eb ):
	if x < 0 or s < 0 or x > image.size[0] or e > image.size[1]:
		raise ValueError
	if x == image.size[0]:
		x -= 1
	if s - e == 0:
		if s == image.size[1]:
			s -= 1
		if sr < 0:
			sr = 0
		if sg < 0:
			sg = 0
		if sb < 0:
			sb = 0
		if sr > 1.0:
			sr = 1.0
		if sg > 1.0:
			sg = 1.0
		if sb > 1.0:
			sb = 1.0
		image.setPixelF( x, s, ( sr, sg, sb, 1.0 ) )
		return
	dr = ( er - sr ) / ( e - s )
	dg = ( eg - sg ) / ( e - s )
	db = ( eb - sb ) / ( e - s )
	for v in xrange( s, e + 1 ):
		if v == image.size[1]:
			image.setPixelF( x, v - 1, ( sr, sg, sb, 1.0 ) )
		else:
			image.setPixelF( x, v, ( sr, sg, sb, 1.0 ) )
		sr += dr
		sg += dg
		sb += db
		if sr < 0:
			sr = 0
		if sg < 0:
			sg = 0
		if sb < 0:
			sb = 0
		if sr > 1.0:
			sr = 1.0
		if sg > 1.0:
			sg = 1.0
		if sb > 1.0:
			sb = 1.0

#***********************************************
# bake UV map from XYZ
#***********************************************

def updateSculptieMap( ob, scale = None, normalised = True, centered = False, clear = True, scaleRGB = True):
	rt = Blender.Get( 'rt' )
	if scale == None:
		scale = scaleRange( [ob], normalised, centered )
	if ob.type == 'Mesh':
		mesh = ob.getData( False, True)
		currentUV = mesh.activeUVLayer
		if "sculptie" in mesh.getUVLayerNames():
			mesh.activeUVLayer = "sculptie"
			mesh.update()
		mesh = Blender.Mesh.New()
		mesh.getFromObject( ob, 0, 1 )
		images = []
		for f in mesh.faces:
			if f.image != None:
				if f.image not in images:
					images.append( f.image )
		if clear:
			for i in images:
				for u in xrange( i.size[0] ):
					for v in xrange( i.size[1] ):
						i.setPixelI(u, v, (0, 0, 0, 0))
		try:
			for f in mesh.faces:
				if f.image != None:
					for t in Blender.Geometry.PolyFill([ f.uv ]):
						nf = []
						for i in t:
							r, g, b = scale.adjusted( f.verts[ i ].co )
							if f.uv[i][0] == 1.0:
								u = f.image.size[0] - 1
							else:
								u = round(f.uv[ i ][0] * f.image.size[0])
							if f.uv[i][1] == 1.0:
								v = f.image.size[1] - 1
							else:
								v = round(f.uv[ i ][1] * f.image.size[1])
							nf.append(
								pixel(
									u,
									v,
									round( r * 255.0 ) / 255.0, round( g * 255.0 ) / 255.0, round( b * 255.0 ) / 255.0
								)
							)
						drawTri( f.image, sorted( nf ) )
		except ValueError:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["The UV map is outside","the image area"] )
			return
		bb = sculpty.getBB( ob )
		if scaleRGB:
			sf = ( scale.r / 255.0, scale.g / 255.0, scale.b / 255.0 )
		else:
			sf = ( 1.0, 1.0, 1.0 )
		for sculptimage in images:
			try:
				sculptimage.properties['scale_x'] = scale.x / (( bb[1][0] - bb[0][0] ) * sf[0])
			except:
				sculptimage.properties['scale_x'] = scale.x * sf[0]
			try:
				sculptimage.properties['scale_y'] = scale.y / (( bb[1][1] - bb[0][1] ) * sf[1])
			except:
				sculptimage.properties['scale_y'] = scale.y * sf[1]
			try:
				sculptimage.properties['scale_z'] = scale.z / (( bb[1][2] - bb[0][2] ) * sf[2])
			except:
				sculptimage.properties['scale_z'] = scale.z * sf[2]
			n = Blender.sys.splitext( sculptimage.name )
			if n[0] in ["Untitled", "Sphere_map", "Torus_map", "Cylinder_map", "Plane_map", "Hemi_map", "Sphere", "Torus","Cylinder","Plane","Hemi" ]:
				sculptimage.name = ob.name
	return images

#***********************************************
# main
#***********************************************

def main():
	block = []
	doFinal = Blender.Draw.Create( True )
	keepScale = Blender.Draw.Create( False )
	doExpand = Blender.Draw.Create( False )
	keepCentre = Blender.Draw.Create( False )
	doClear = Blender.Draw.Create( True )
	doProtect = Blender.Draw.Create( True )
	doPreview = Blender.Draw.Create( True )
	minR = Blender.Draw.Create( 0 )
	maxR = Blender.Draw.Create( 255 )
	minG = Blender.Draw.Create( 0 )
	maxG = Blender.Draw.Create( 255 )
	minB = Blender.Draw.Create( 0 )
	maxB = Blender.Draw.Create( 255 )
	doScaleRGB = Blender.Draw.Create( True )
	block.append (( "Clear", doClear ))
	block.append (( "Keep Scale", keepScale ))
	block.append (( "Keep Center", keepCentre ))
	block.append (( "Finalise", doFinal ))
	block.append (( "Protect Map", doProtect ))
	block.append (( "With Preview", doPreview ))
	block.append (( " " ))
	block.append (( "   Color Range Adjustment" ))
	block.append (( "Min R:", minR, 0, 255 ))
	block.append (( "Max R:", maxR, 0, 255 ))
	block.append (( "Min G:", minG, 0, 255 ))
	block.append (( "Max G:", maxG, 0, 255 ))
	block.append (( "Min B:", minB, 0, 255 ))
	block.append (( "Max B:", maxB, 0, 255 ))
	block.append (( "Include in Size", doScaleRGB ))

	if Blender.Draw.PupBlock( "Sculptie Bake Options", block ):
		print "--------------------------------"
		time1 = Blender.sys.time()  #for timing purposes
		scene = Blender.Scene.GetCurrent()
		editmode = Blender.Window.EditMode()
		if editmode: Blender.Window.EditMode(0)
		Blender.Window.WaitCursor(1)
		meshscale = scaleRange( scene.objects.selected , not keepScale.val, keepCentre.val, (minR.val,maxR.val,minG.val,maxG.val,minB.val,maxB.val) )
		if meshscale.minx == None:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["No objects selected"] )
		else:
			if not keepCentre.val:
				offset = ( 0.0, 0.0, 0.0 )
				for ob in scene.objects.selected:
					if ob.type == 'Mesh':
						mesh = ob.getData( False, True)
						if 'sculptie' in mesh.getUVLayerNames():
							loc = ob.getLocation( 'worldspace' )
							x = meshscale.minx + ( meshscale.x * 0.5 )
							y = meshscale.miny + ( meshscale.y * 0.5 )
							z = meshscale.minz + ( meshscale.z * 0.5 )
							if (x, y, z) != offset:
								offset = Blender.Mathutils.Vector( x,y,z )
								print offset, (loc[0],loc[1],loc[2])
								x += loc[0]
								y += loc[1]
								z += loc[2]
								mat = ob.getMatrix()
								tran = Blender.Mathutils.TranslationMatrix( Blender.Mathutils.Vector( loc ) )
								mesh.transform( tran )
								mesh.update()
								mat[3] = [0.0, 0.0, 0.0, 1.0]
								ob.setMatrix( mat )
								tran = Blender.Mathutils.TranslationMatrix( Blender.Mathutils.Vector( x, y, z ) * -1.0 )
								mesh.transform( tran )
								mesh.update()
								mat[3] = [x, y, z , 1.0]
								ob.setMatrix( mat )
				meshscale = scaleRange( scene.objects.selected , not keepScale.val, True, (minR.val,maxR.val,minG.val,maxG.val,minB.val,maxB.val) )

			for ob in scene.objects.selected:
				if ob.type == 'Mesh':
					images = updateSculptieMap( ob , meshscale, not keepScale.val, keepCentre.val, doClear.val )
					for image in images:
						if doFinal.val:
							sculpty.fill_holes( image )
							sculpty.expand_pixels( image )
							if doProtect.val:
									if doPreview.val:
										sculpty.bake_preview( image )
									else:
										sculpty.clear_alpha( image )

		print "--------------------------------"
		print 'finished baking: in %.4f sec.' % ((Blender.sys.time()-time1))
		Blender.Redraw()
		if editmode: Blender.Window.EditMode(1)
		Blender.Window.WaitCursor(0)

if __name__ == '__main__':
	main()
