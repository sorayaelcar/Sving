#!BPY

"""
Name: 'Bake Second Life Sculpties'
Blender: 245
Group: 'Render'
Tooltip: 'Bake Sculptie Maps on Active objects'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.22"
__bpydoc__ = """\

Bake Sculptie Map

This script requires a square planar mapping. It bakes the local vertex
positions to the prim's sculptie map image.
"""

#Changes
#0.22 Domino Marama 2008-07-06
#- added compressible option requested by Aminom Marvin
#0.21 Domino Marama 2008-06-29
#- save meshscale for exporters
#0.20 Domino Marama 2008-06-27
#- bug fix for updateSculptieMap when imported by another module
#0.19 Domino Marama 2008-06-27
#- added support for "sculptie" uv map
#- removed LL_SCULPT_IMAGE property
#0.18 Gaia Clary 2008-05-24
#- round r, g, b to avoid rounding errors in triangle fill
#0.17 Domino Marama 2008-05-24
#- normalising the sculptie map made optional
#0.16 Domino Marama 2008-05-07
#- added rotation to print out
#0.15 Domino Marama 2008-04-22
#- added sorted() function for python 2.3 builds
#0.14 Domino Marama 2008-04-17
#- added error catch for uv map positions < 0
#0.13 Domino Marama 2008-04-05
#- now works on post modifier stack data
#0.12 Domino Marama 2008-03-12
#- reorganised to allow for prim export
#- sculptie map no longer needs to be assigned to UV faces
#0.11 Domino Marama 2008-02-28
#- now adds new 64 x 64 image if no image assigned to mesh
#- colvert renamed to pixel
#0.10 Domino Marama 2008-02-21
#- plane type ends now handled cleanly
#0.09 Domino Marama 2008-02-19
#- pixel __sub_, _add__ and __mul__ methods added and used
#0.08 Domino Marama 2008-02-17
#- Hole Fill changed to off by default
#0.07 Domino Marama 2008-02-10
#- Bake routine rewritten
#0.06 Domino Marama 2007-12-23
#- fixed sculptie type
#0.05 Domino Marama 2007-08-29
#- code cleanup
#- added prim properties
#- changed console print out to LSL
#0.04 Domino Marama 2007-08-26
#- Fixed fill routine and added options for faces & fill
#0.03 Domino Marama 2007-08-19
#- Various fixes to triangle fill routines
#0.02 Domino Marama 2007-08-18
#- Converted to triangle fill routines
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
from sys import version_info

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
	def __init__ ( self, objects, normalised ):
		self.minx = None
		for ob in objects:
			if ob.type == 'Mesh':
				mesh = Blender.Mesh.New()
				mesh.getFromObject( ob, 0, 1 )
				if self.minx == None:
					self.minx = mesh.verts[0].co.x
					self.maxx = self.minx
					self.miny = mesh.verts[0].co.y
					self.maxy = self.miny
					self.minz = mesh.verts[0].co.z
					self.maxz = self.minz
				for v in mesh.verts[1:-1]:
					if v.co.x < self.minx :
						self.minx = v.co.x
					elif v.co.x > self.maxx :
						self.maxx = v.co.x
					if v.co.y < self.miny :
						self.miny = v.co.y
					elif v.co.y > self.maxy :
						self.maxy = v.co.y
					if v.co.z < self.minz :
						self.minz = v.co.z
					elif v.co.z > self.maxz :
						self.maxz = v.co.z
			if normalised == 0:
				self.minx = self.miny = self.minz = min( self.minx, self.miny, self.minz )
				self.maxx = self.maxy = self.maxz = max( self.maxx, self.maxy, self.maxz )
			self.x = self.maxx - self.minx
			self.y = self.maxy - self.miny
			self.z = self.maxz - self.minz
			# avoid divide by zero errors
			if self.x == 0.0: self.x = 1.0
			if self.y == 0.0: self.y = 1.0
			if self.z == 0.0: self.z = 1.0
	def normalise( self, co ):
		return ( co[0] - self.minx ) / self.x, ( co[1] - self.miny ) / self.y, ( co[2] - self.minz ) / self.z
		
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
		x = float(int(s1.x))
		ex = float(int(e1.x))
		while x <= ex and x <= image.size[0]:
			s = ( x - s1.x ) / r1.x
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
	for u in xrange( s, e + 1 ):
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

def expandPixels( image ):
	dx = image.size[0] / 32
	if ( dx != int(dx) ):
		print "Unable to make " + image.name + "' compressible as X size is not a multiple of 32"
		return
	dy = image.size[1] / 32
	if ( dy != int(dy) ):
		print "Unable to make '" + image.name + "' compressible as Y size is not a multiple of 32"
		return
	for y in xrange( 0, image.size[1], dy ):
		for x in xrange( 0, image.size[0] - 1):
			if x % dx:
				image.setPixelF( x, y, c )
			else:
				c = image.getPixelF( x, y )
	y = image.size[1] - 1
	for x in xrange( 0, image.size[0] - 1):
			if x % dx:
				image.setPixelF( x, y, c )
			else:
				c = image.getPixelF( x, y )
	for x in xrange( 0, image.size[0] ):
		for y in xrange( 0, image.size[1] -1 ):
			if y % dy:
				image.setPixelF( x, y, c )
			else:
				c = image.getPixelF( x, y )

#***********************************************
# bake UV map from XYZ
#***********************************************

def updateSculptieMap( ob, scale = None, fill = False, normalised = True, expand = True ):
	if scale == None:
		scale = scaleRange( [ob], normalised )
	if ob.type == 'Mesh':
		try:
			primtype = ob.getProperty( 'LL_PRIM_TYPE' ).getData()
			if primtype != 7:
				print "Skipping:", ob.name,"prim type is not a sculptie"
				return
			else:
				sculptie_type = ob.getProperty( 'LL_SCULPT_TYPE' ).getData()
		except:
			sculptie_type = Blender.Draw.PupMenu( "Sculpt Type?%t|Sphere|Torus|Plane|Cylinder" )
			ob.addProperty( 'LL_PRIM_TYPE', 7 )
			ob.addProperty( 'LL_SCULPT_TYPE', sculptie_type )
			ob.addProperty( 'X_SCALE', scale.x )
			ob.addProperty( 'Y_SCALE', scale.y )
			ob.addProperty( 'Z_SCALE', scale.z )
		if sculptie_type < 1:
			print "Skipping:", ob.name, " - sculptie type is 'NONE'"
			return
		mesh = ob.getData( False, True)
		if "sculptie" in mesh.getUVLayerNames():
			mesh.activeUVLayer = "sculptie"
			mesh.update()
		sculptimage = mesh.faces[0].image
		if sculptimage == None:
			sculptimage = Blender.Image.New( ob.name, 64, 64, 32 )
			if mesh.multires:
				mr = mesh.multiresDrawLevel
				mesh.multiresDrawLevel = 1
			for f in mesh.faces:
				f.image = sculptimage
			if mesh.multires:
				mesh.multiresDrawLevel = mr
			mesh.update()
		mesh = Blender.Mesh.New()
		mesh.getFromObject( ob, 0, 1 )
		for u in xrange( sculptimage.size[0] ):
			for v in xrange( sculptimage.size[1] ):
				sculptimage.setPixelI(u, v, (0, 0, 0, 0))
		try:
			for f in mesh.faces:
				for t in Blender.Geometry.PolyFill([ f.uv ]):
					nf = []
					for i in t:
						r, g, b = scale.normalise( f.verts[ i ].co )
						nf.append(
							pixel(
								f.uv[ i ][0] * sculptimage.size[0],
								f.uv[ i ][1] * sculptimage.size[1],
								round( r * 255.0 ) / 255.0, round( g * 255.0 ) / 255.0, round( b * 255.0 ) / 255.0
							)
						)
					drawTri( sculptimage, sorted( nf ) )
		except ValueError:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["The UV map is outside","the image area"] )
			return
		if fill:
			def getFirstX( y ):
				for x in xrange( sculptimage.size[0] ):
					c = sculptimage.getPixelF( x, y )
					if c[3] != 0:
						if x > 0: fill = True
						return c
				return None
			def getFirstY( x ):
				for y in xrange( sculptimage.size[1] ):
					c = sculptimage.getPixelF( x, y )
					if c[3] != 0:
						if y > 0: fill = True
						return c
				return None
			def fillX():
				skipx = fill = False
				for v in xrange( sculptimage.size[1] ):
					c = getFirstX( v )
					if not c : 
						skipx= True
						continue
					sr = c[0]
					sg = c[1]
					sb = c[2]
					s = 0
					for u in xrange( 1, sculptimage.size[0] ):
						nc = sculptimage.getPixelF( u, v )
						if nc[3] == 0:
							if not fill:
								fill = True
						else:
							if fill:
								fill = False
								drawHLine( sculptimage, v, s, u, sr, sg, sb, nc[0], nc[1], nc[2] )
							s = u
							sr = nc[0]
							sg = nc[1]
							sb = nc[2]
					if fill:
						fill = False
						drawHLine( sculptimage, v, s, u, sr, sg, sb, sr, sg, sb )
				return skipx
			def fillY():
				fill = False
				for u in xrange( sculptimage.size[0] ):
					c = getFirstY( u )
					if not c :
						continue
					sr = c[0]
					sg = c[1]
					sb = c[2]
					s = 0
					for v in xrange( 1, sculptimage.size[1] ):
						nc = sculptimage.getPixelF( u, v )
						if nc[3] == 0:
							if not fill:
								fill = True
						else:
							if fill:
								fill = False
								drawVLine( sculptimage, u, s, v, sr, sg, sb, nc[0], nc[1], nc[2] )
							s = v
							sr = nc[0]
							sg = nc[1]
							sb = nc[2]
					if fill:
						fill = False
						drawVLine( sculptimage, u, s, v, sr, sg, sb, sr, sg, sb )
			skipx = fillX()
			fillY()
			if skipx: fillX()
		if expand:
			expandPixels ( sculptimage )
		sculptimage.makeCurrent()
		return Blender.sys.splitext( sculptimage.name )[0]
	else:
		return None

#***********************************************
# main
#***********************************************

def main():
	block = []
	doFill = Blender.Draw.Create( False )
	doNorm = Blender.Draw.Create( True )
	doExpand = Blender.Draw.Create( True )
	block.append (( "Fill Holes", doFill ))
	block.append (( "Normalise", doNorm ))
	block.append (( "Compressible", doExpand ))

	if Blender.Draw.PupBlock( "Sculptie Bake Options", block ):
		print "--------------------------------"
		time1 = Blender.sys.time()  #for timing purposes
		scene = Blender.Scene.GetCurrent()
		editmode = Blender.Window.EditMode()
		if editmode: Blender.Window.EditMode(0)
		Blender.Window.WaitCursor(1)
		meshscale = scaleRange( scene.objects.selected , doNorm )
		if meshscale.minx == None:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["No objects selected"] )
		else:
			for ob in scene.objects.selected:			
				if ob.type == 'Mesh':
					sculptie_map = updateSculptieMap( ob , meshscale, doFill.val, doNorm.val, doExpand.val )
					try:
						scale = ob.getSize()
						primtype = ob.getProperty( 'LL_PRIM_TYPE' ).getData()
						if primtype == 7:
							sculptie_type = ob.getProperty( 'LL_SCULPT_TYPE' ).getData()
							rotation = ob.getMatrix().rotationPart().invert().toQuat()
							priminfo = ( sculptie_map,
								["NONE", "SPHERE", "TORUS", "PLANE", "CYLINDER"][sculptie_type],
								meshscale.x * scale[0],
								meshscale.y * scale[1],
								meshscale.z * scale[2],
								rotation[1],
								rotation[2],
								rotation[3],
								rotation[0]
							)
							print "llSetPrimitiveParams( [ PRIM_TYPE, PRIM_TYPE_SCULPT, \"%s\", PRIM_SCULPT_TYPE_%s, PRIM_SIZE, < %.5f, %.5f, %.5f >, PRIM_ROTATION, < %.5f, %.5f, %.5f, %.5f > ] );"%priminfo
					except:
						pass

		print "--------------------------------"
		print 'finished baking: in %.4f sec.' % ((Blender.sys.time()-time1))
		Blender.Redraw()
		if editmode: Blender.Window.EditMode(1)
		Blender.Window.WaitCursor(0)

if __name__ == '__main__':
	main()
