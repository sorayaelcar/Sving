#!BPY

"""
Name: 'Second Life LSL (to dir)'
Blender: 245
Group: 'Export'
Tooltip: 'Export lsl and tga files for Second Life (to dir)'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.06"
__bpydoc__ = """\

LSL Exporter

This script exports Second Life sculpties in lsl + tga files
"""

#Changes:
#0.07 Domino Marama 2008-07-10
#- added linkset support
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
list textures = [ %(textures)s ];
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
			llOwnerSay( "Please add a prim called \"" + base + "\" to my contents" );
			state needs_something;
		}
		tI = llGetListLength( textures );
		while ( tI ):
			if ( isKey( tS = llList2String( textures, tI = ~-tI ) ) == 0 )
			{
				if ( llGetInventoryType( tS ) != INVENTORY_TEXTURE )
				{
					llOwnerSay( "Please add texture \"" + tS + "\" to my contents" );
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
			%(builder)s
			{
				llSetLinkPrimitiveParams( 1, [ %(rootParams)s ] );
		                llBreakLink( llGetNumberOfPrims() );
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
		self.sculpttype = 0
		self.sculptimage = None
		self.meshscale = ( 1.0, 1.0, 1.0 )
		self.scale = ( 1.0, 1.0, 1.0 )
		self.rotation = ( 0.0, 0.0, 0.0, 1.0 )
		self.location = ( 0.0, 0.0, 0.0 )

	def fromOb( self, ob ):
		self.primtype = ob.getProperty( 'LL_PRIM_TYPE' ).getData()
		r = ob.getMatrix().rotationPart().invert().toQuat()
		self.rotation = ( r[1], r[2], r[3], r[0] )
		if self.primtype == 7:
			self.sculpttype = ob.getProperty( 'LL_SCULPT_TYPE' ).getData()
			mesh = ob.getData( False, True )
			try:
				ms = ( ob.getProperty( 'SCALE_X' ).getData(),
						ob.getProperty( 'SCALE_Y' ).getData(),
						ob.getProperty( 'SCALE_Z' ).getData() )
			except:
				ms = scaleRange( [ ob ], True )
				ms = ( ms.x, ms.y, ms.z )
			self.location = ( ob.loc[0], ob.loc[1], ob.loc[2] )
			self.scale = ( ob.SizeX * ms[0], ob.SizeY * ms[1], ob.SizeZ * ms[2] )
			currentUV = mesh.activeUVLayer
			if "sculptie" in mesh.getUVLayerNames():					
				mesh.activeUVLayer = "sculptie"
				mesh.update()
				image = mesh.faces[0].image
				if image:
					filebase = Blender.sys.basename( image.filename )
					if filebase[-4:] in [ ".tga", ".TGA" ]:
						si = Blender.sys.splitext(filebase)[0]
					else:
						si = filebase
					self.sculptimage = texture( si, image )
				else:
					self.sculptimage = None
			if "UVTex" in mesh.getUVLayerNames():
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

	def toLSL( self, prefix = "" ):
		pt = ["missing","missing","missing","missing","missing","missing","missing","SCULPT"][ self.primtype ]
		lsl = prefix + "llSetPrimitiveParams( [ " + self.toLSLParams() + " ] );\n"
		lsl += prefix + "llSetObjectName( \"%s\" );\n"%( self.name )
		return lsl

	def toLSLParams( self ):
		pt = ["missing","missing","missing","missing","missing","missing","missing","SCULPT"][ self.primtype ]
		lsl = "PRIM_TYPE, PRIM_TYPE_%s, "%( pt )
		if self.primtype == 7:
			st = ["NONE", "SPHERE", "TORUS", "PLANE", "CYLINDER"][self.sculpttype]
			lsl += "\"%s\", PRIM_SCULPT_TYPE_%s, "%( self.sculptimage.name, st )
		lsl += "PRIM_SIZE, < %.5f, %.5f, %.5f >, "%( self.scale )
		lsl += "PRIM_ROTATION, < %.5f, %.5f, %.5f, %.5f >"%( self.rotation )
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
		else:
			lsl += str( self.face ) + ", "
		lsl += "tK" + str( self.face ) + ", "
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
# simple export to .lsl files + .tga images
#***********************************************

def export_lsl( filename ):
	Blender.Window.WaitCursor(1)
	prims = []
	basepath = Blender.sys.dirname( filename )
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects.selected:
		# collect prims
		if ob.type == 'Mesh':
			try:				
				primtype = ob.getProperty( 'LL_PRIM_TYPE' ).getData()
			except:
				continue
			newprim = prim( ob.name )
			newprim.fromOb( ob )
			if newprim.primtype == 7 and newprim.sculpttype > 0:
				if newprim.sculptimage == None:
					sn = updateSculptieMap( ob , None, True )
					newprim.sculptimage = texture( sn , Blender.Image.Get( sn ) )
			prims.append( newprim )

	# save prims
	for p in prims:
		lsl_t_h = ""
		if p.sculptimage:
			p.sculptimage.saveImageAs( Blender.sys.join( basepath, p.sculptimage.name + ".tga" ) )
		i = 0
		for t in p.textures:
			t.saveImageAs( Blender.sys.join( basepath, t.name + ".tga" ) )
			lsl_t_h += "\t\tkey tK" + str( t.face ) + " = llGetInventoryKey( \"" + t.name + "\" );"
			lsl_t_h += "\t\tllRemoveInventory( \"" + t.name + "\" );"
		lsl =  "string tS;\n\ndefault\n{\n\tstate_entry()\n\t{\n" 
		lsl += lsl_t_h + p.toLSL( "\t\t" )
		if p.sculptimage:
			lsl += "\t\tllRemoveInventory( \"" + p.sculptimage.name +"\" );"
		lsl += "\t\tllRemoveInventory( tS = llGetScriptName() );\n\t\tllSetScriptState( tS, FALSE );\t}\n}\n" 
		f = open( Blender.sys.join( basepath, p.name + ".lsl" ), 'w' )
		f.write( lsl )
		f.close()

	Blender.Window.WaitCursor(0)

#***********************************************
# register callback
#***********************************************
def my_callback(filename):
	export_lsl(filename)

if __name__ == '__main__':
	Blender.Window.FileSelector(my_callback, "Export LSL", '.')
