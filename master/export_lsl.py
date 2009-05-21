#!BPY

"""
Name: 'Second Life LSL (to dir)'
Blender: 245
Group: 'Export'
Tooltip: 'Export lsl and tga files for Second Life (to dir)'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.09"
__bpydoc__ = """\

LSL Exporter

This script exports Second Life sculpties in lsl + tga files
"""

#Changes:
#0.09 Domino Marama 2009-05-19
#- replaced sculpttype with automatic map detection in mapType function
#- added support for multiple sculpt maps
#- new single LSL script export with linkset support via parenting
#0.08 Domino Marama 2008-12-19
#- refactor to allow better linkset support
# 0.07 BETLOG Hax 2008-10-22
#- added PRIM_POSITION and altered output LSL  to include offsets when in a linkset
#0.06 Domino Marama 2008-07-09
#- minor bug fixes
#0.05 Domino Marama 2008-06-29
#- LSL now removes used items from prim contents
#0.04 Domino Marama 2008-06-29
#- ALL_FACES bug in lsl fixed
#0.03 Domino Marama 2008-06-28
#- missed quotes in lsl for texture
#0.02 Domino Marama 2008-06-28
#- refactored
#- added basic texture support
#0.01 Domino Marama 2008-06-27
#- initial version

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
from render_sculptie import updateSculptieMap, scaleRange

#***********************************************
# Templates
#***********************************************

MAIN_LSL = """string base = "Prim";
list textures = %(textures)s;
vector myPos;

integer isKey(key in)
{
	if(in) return 2;
	return (in == NULL_KEY);
}

addPrim()
{
	llRezObject(base, myPos, ZERO_VECTOR, ZERO_ROTATION, 0 );
}

state default
{
	state_entry()
	{
		if ( llGetInventoryType( base ) != INVENTORY_OBJECT )
		{
			llOwnerSay( "Please add a prim called \\"" + base + "\\" to my contents" );
			state needs_something;
		}
		tI = llGetListLength( textures );
		while ( tI ):
			if ( isKey( tS = llList2String( textures, tI = ~-tI ) ) == 0 )
			{
				if ( llGetInventoryType( tS ) != INVENTORY_TEXTURE )
				{
					llOwnerSay( "Please add texture \\"" + tS + "\\" to my contents" );
					state needs_something;
				}
			}
		}
		llRequestPermissions( llGetOwner(), PERMISSION_CHANGE_LINKS );
	}

	run_time_permissions( integer perm )
	{
		if ( perm & PERMISSION_CHANGE_LINKS )
		{
			state ready;
		}
		else
		{
			llOwnerSay( "You must give link permissions for the build to work. Click to try again." );
			state needs_something;
		}
	}
}

state ready
{
	state_entry()
	{
		llOwnerSay( "Ready to build. Click to start." );
	}

	touch_start( integer num )
	{
		if ( llDetectedKey ( 0 ) == llGetOwner() )
		{
			state build;
		}
	}
}

state_build
{
	state_entry()
	{
		myPos = llGetPos();
		llSetRot( ZERO_ROTATION );
		addPrim();
	}

	object_rez( key id )
	{
		llCreateLink(id, FALSE );
	}

	changed( integer change )
	{
		if ( change & CHANGED_LINK )
		{
			tI = ~-llGetNumberOfPrims();
			%(builder)sif (tI > 0 ) {
				llSetLinkPrimitiveParams( 1, [ %(rootParams)s ] );
				llBreakLink( llGetNumberOfPrims() );
			}
			else
			{
				llOwnerSay( "Finished!" );
				state ready;
			}
		}
	}
}

state needs_something
{
	on_rez( integer num)
	{
		state default;
	}

	changed( integer change )
	{
		if ( change & CHANGED_INVENTORY )
		{
			state default;
		}
	}

	touch_start( integer num )
	{
		if ( llDetectedKey ( 0 ) == llGetOwner() )
		{
			state default;
		}
	}
}
"""
LINK_LSL = """if ( tI == %(linkNum)i )
			{
				llSetLinkPrimitiveParams( 1, [ %(linkParams)s ] );
				addPrim();
			}
			else """

#***********************************************
# classes
#***********************************************
class prim:
	def __init__( self, name ):
		self.name = name
		self.children = []
		self.textures = []
		self.primtype = 0
		self.sculptimage = None
		self.meshscale = ( 1.0, 1.0, 1.0 )
		self.scale = ( 1.0, 1.0, 1.0 )
		self.rotation = ( 0.0, 0.0, 0.0, 1.0 )
		self.location = ( 0.0, 0.0, 0.0 )

	def fromOb( self, ob ):
		r = ob.getMatrix().rotationPart().invert().toQuat()
		self.rotation = ( r[1], r[2], r[3], r[0] )
		mesh = ob.getData( False, True )
		ms = scaleRange( [ ob ], True )
		self.scale = ( ms.x * ob.size[0], ms.y * ob.size[1], ms.z * ob.size[2] )
		if "sculptie" in mesh.getUVLayerNames():
			self.primtype = 7
			if "UVTex" in mesh.getUVLayerNames():
				currentUV = mesh.activeUVLayer
				mesh.activeUVLayer = "UVTex"
				mesh.update()
				image = mesh.faces[0].image
				if image:
					filebase = Blender.sys.basename( image.filename )
					if filebase[-4:] in [ ".tga", ".TGA" ]:
						newtex = texture( Blender.sys.splitext(filebase)[0], image )
					else:
						newtex = texture( filebase, image )
						self.textures.append( newtex )
				mesh.activeUVLayer = currentUV
				mesh.update()
		self.location = ob.getLocation( 'worldspace' )

	def toLSLParams( self ):
		pt = ["missing","missing","missing","missing","missing","missing","missing","SCULPT"][ self.primtype ]
		lsl = "PRIM_TYPE, PRIM_TYPE_%s, "%( pt )
		if self.primtype == 7:
			lsl += "\"%s\", PRIM_SCULPT_TYPE_%s, "%( self.sculptimage.name, mapType( self.sculptimage.image ) )
		lsl += "PRIM_SIZE, < %.5f, %.5f, %.5f >, "%( self.scale )
		lsl += "PRIM_ROTATION, < %.5f, %.5f, %.5f, %.5f >, "%( self.rotation )
		lsl += "PRIM_LOCATION, myPos + < %.5f, %.5f, %.5f >"%( self.location )
		for t in self.textures:
			lsl += ", " + t.toLSLParams()
		return lsl

class texture:
	def __init__( self, name, image = None ):
		self.name = name
		self.image = image
		self.offset = ( 0.0, 0.0 )
		self.repeat = ( 1.0, 1.0 )
		self.rotation = 0.0
		if name == "UVTex":
			self.face = 0
		elif name[:5] == "UVTex":
			self.face = int( name[6:] )
		else:
			self.face = -1

	def toLSLParams( self ):
		lsl = "PRIM_TEXTURE, "
		if self.face == -1:
			lsl += "ALL_SIDES, "
			f = "0"
		else:
			lsl += str( self.face ) + ", "
			f = str( self.face )
		lsl += "tK" + f + ", "
		lsl += "<" + str( self.repeat[0] ) + ", " + str( self.repeat[1] ) + ", 0.0>, "
		lsl += "<" + str( self.offset[0] ) + ", " + str( self.offset[1] ) + ", 0.0>, "
		lsl += str( self.rotation )
		return lsl

	def saveImageAs( self, filename ):
		oldfile = self.image.filename
		self.image.filename = filename
		self.image.save()
		self.image.filename = oldfile

#***********************************************
# functions
#***********************************************

def obChildren(ob):
    return [ob_child for ob_child in Blender.Object.Get() if ob_child.parent == ob]

def mapImages( mesh ):
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

def mapType( image ):
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

#***********************************************
# simple export to .lsl files + .tga images
#***********************************************

def mesh2Prim( ob, rootprim = None ):
	mesh = ob.getData( False, True )
	images = mapImages( mesh )
	if images != []:
		newprim = prim( images[0].name )
		newprim.fromOb( ob )
		newprim.sculptimage = texture( images[0].name , images[0] )
		newprim.scale = ( newprim.scale[0] / images[0].properties['scale_x'],
						newprim.scale[1] / images[0].properties['scale_y'],
						newprim.scale[2] / images[0].properties['scale_z'] )
		if rootprim == None:
			rootprim = newprim
		else:
			rootprim.children.append( newprim )
		for image in images[1:]:
			newprim = prim( image.name )
			newprim.fromOb( ob )
			newprim.sculptimage = texture( image.name , image )
			newprim.scale = ( newprim.scale[0] / images[0].properties['scale_x'],
						newprim.scale[1] / images[0].properties['scale_y'],
						newprim.scale[2] / images[0].properties['scale_z'] )
			rootprim.children.append( newprim )
	return rootprim

def ob2Prim( ob, rootprim = None ):
	if ob.type == 'Mesh':
		rootprim = mesh2Prim( ob, rootprim )
	for c in obChildren( ob ):
		rootprim = ob2Prim( c, rootprim )
	return rootprim

def export_lsl( filename ):
	Blender.Window.WaitCursor(1)
	prims = []
	basepath = Blender.sys.dirname( filename )
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects.selected:
		# collect prims
		if ob.parent != None:
			continue
		rootprim = ob2Prim( ob )
		if rootprim != None:
			prims.append( rootprim )
	if prims == []:
		Blender.Draw.PupBlock( "Nothing to do", ["No root prims are selected", " for export"] )
		return
	textures = []
	builder = ""
	for r in prims:
		tk = 1
		if r.sculptimage:
			if not ( r.sculptimage.name in textures ):
				textures.append( r.sculptimage.name )
				r.sculptimage.saveImageAs( Blender.sys.join( basepath, r.sculptimage.name + ".tga" ) )
			for t in r.textures:
				if not ( t.name in textures ):
					t.saveImageAs( Blender.sys.join( basepath, t.name + ".tga" ) )
					textures.append( t.name )
		for c in r.children:
			if c.sculptimage:
				builder += LINK_LSL%{ "linkNum": tk, "linkParams":c.toLSLParams() }
				tk += 1
				if not ( c.sculptimage.name in textures ):
					c.sculptimage.saveImageAs( Blender.sys.join( basepath, c.sculptimage.name + ".tga" ) )
					textures.append( c.sculptimage.name )
			for t in c.textures:
				if not ( t.name in textures ):
					t.saveImageAs( Blender.sys.join( basepath, t.name + ".tga" ) )
					textures.append( t.name )
		f = open( Blender.sys.join( basepath, r.name + ".lsl" ), 'w' )
		t = str( textures )
		f.write( MAIN_LSL%{ "textures": t.replace(", ",",\n\t\t\t"), "builder":builder, "rootParams": r.toLSLParams() } )
		f.close()

	Blender.Window.WaitCursor(0)

#***********************************************
# register callback
#***********************************************
def my_callback(filename):
	export_lsl(filename)

if __name__ == '__main__':
	Blender.Window.FileSelector(my_callback, "Export LSL", '.')
