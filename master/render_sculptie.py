#!BPY

"""
Name: 'Bake Second Life Sculpties'
Blender: 245
Group: 'Render'
Tooltip: 'Bake Sculptie Maps on Active objects'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.31"
__bpydoc__ = """\

Bake Sculptie Map

This script requires a square planar mapping. It bakes the local vertex
positions to the prim's sculptie map image.
"""

#Changes
#0.31 Domino Marama 2008-11-28
#- RGB range adjustment added
#- Preview improved & made optional
#- Map name updated on bake if appropriate
#0.30 Domino Marama 2008-11-01
#- bug fix to getBB
#0.29 Domino Marama 2008-10-30
#- Alpha channel preview protection added
#0.28 Domino Marama 2008-10-26
#- scaleRange uses calculation when modifiers involved
#0.27 Domino Marama 2008-09-14
#- Fixed overshoot on triangle fill
#0.26 Domino Marama 2008-08-27
#- added support for oblong sculpties
#0.25 Domino Marama 2008-07-25
#- fixed centering with normalise off
#- scaleRange now uses bounding box
#- WIP: bake updates object scale (under rt:55)
#0.24 Domino Marama 2008-07-13
#- fixed centering of flat planes
#0.23 Gaia Clary 2008-07-12
#- round uv for triangle fill
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
				bb = getBB( ob )
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

def expandPixels( image ):
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

def protectMap( image, preview ):
	for x in xrange( image.size[0] ):
		for y in xrange( image.size[1] ):
			c1 = image.getPixelF( x, y )
			c1[3] = 0.0
			image.setPixelF( x, y, c1 )
	if preview:
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

#***********************************************
# bake UV map from XYZ
#***********************************************

def updateSculptieMap( ob, scale = None, fill = False, normalised = True, expand = True, centered = False, clear = True, scaleRGB = True ):
	rt = Blender.Get( 'rt' )
	if scale == None:
		scale = scaleRange( [ob], normalised, centered )
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
		if clear:
			for u in xrange( sculptimage.size[0] ):
				for v in xrange( sculptimage.size[1] ):
					sculptimage.setPixelI(u, v, (0, 0, 0, 0))
		try:
			for f in mesh.faces:
				for t in Blender.Geometry.PolyFill([ f.uv ]):
					nf = []
					for i in t:
						r, g, b = scale.adjusted( f.verts[ i ].co )
						if f.uv[i][0] == 1.0:
							u = sculptimage.size[0] - 1
						else:
							u = round(f.uv[ i ][0] * sculptimage.size[0])
						if f.uv[i][1] == 1.0:
							v = sculptimage.size[1] - 1
						else:
							v = round(f.uv[ i ][1] * sculptimage.size[1])
						nf.append(
							pixel(
								u,
								v,
								round( r * 255.0 ) / 255.0, round( g * 255.0 ) / 255.0, round( b * 255.0 ) / 255.0
							)
						)
					drawTri( sculptimage, sorted( nf ) )
		except ValueError:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["The UV map is outside","the image area"] )
			return
		offset = ( 0.0, 0.0, 0.0 )
		if not centered:
			mesh = ob.getData()
			loc = ob.getLocation()
			x = scale.minx + ( scale.x * 0.5 )
			y = scale.miny + ( scale.y * 0.5 )
			z = scale.minz + ( scale.z * 0.5 )
			if (x, y, z) != offset:
				offset = Blender.Mathutils.Vector( x, y, z )
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
		bb = getBB( ob )
		if scaleRGB:
			sf = ( scale.r / 255.0, scale.g / 255.0, scale.b / 255.0 )
		else:
			sf = ( 1.0, 1.0, 1.0 )
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
		n = Blender.sys.splitext( sculptimage.name )
		n = n[:-1]
		if n[0] in ["Untitled", "Sphere_map", "Torus_map", "Cylinder_map", "Plane_map", "Hemi_map", "Sphere", "Torus","Cylinder","Plane","Hemi" ]:
			sculptimage.name = ob.name + "_map"
			return sculptimage.name
		return ".".join( n )
	else:
		return None

#***********************************************
# main
#***********************************************

def main():
	block = []
	doFill = Blender.Draw.Create( False )
	doScale = Blender.Draw.Create( False )
	doExpand = Blender.Draw.Create( False )
	doCentre = Blender.Draw.Create( False )
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
	block.append (( "Fill Holes", doFill ))
	block.append (( "Keep Scale", doScale ))
	block.append (( "Keep Center", doCentre ))
	block.append (( "True Mirror", doExpand ))
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
		meshscale = scaleRange( scene.objects.selected , not doScale.val, doCentre.val, (minR.val,maxR.val,minG.val,maxG.val,minB.val,maxB.val) )
		if meshscale.minx == None:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["No objects selected"] )
		else:
			for ob in scene.objects.selected:			
				if ob.type == 'Mesh':
					sculptie_map = updateSculptieMap( ob , meshscale, doFill.val, not doScale.val, doExpand.val, doCentre.val, doClear.val )
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
							if doProtect.val:
								mesh = ob.getData( False, True)
								if "sculptie" in mesh.getUVLayerNames():
									mesh.activeUVLayer = "sculptie"
									mesh.update()
								image = mesh.faces[0].image
								protectMap( image, doPreview.val )
					except:
						pass

		print "--------------------------------"
		print 'finished baking: in %.4f sec.' % ((Blender.sys.time()-time1))
		Blender.Redraw()
		if editmode: Blender.Window.EditMode(1)
		Blender.Window.WaitCursor(0)

if __name__ == '__main__':
	main()
