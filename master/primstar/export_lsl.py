#!BPY

"""
Name: 'Second Life LSL (to dir)'
Blender: 245
Group: 'Export'
Tooltip: 'Export lsl and tga files for Second Life (to dir)'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.90"
__bpydoc__ = """\

LSL Exporter

This script exports Second Life sculpties in lsl + tga files
"""

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) 2008-2009 Domino Designs Limited
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
from primstar.primitive import get_prims

#***********************************************
# Globals
#***********************************************

PRIM_NAME = "Primstar"

#***********************************************
# Classes
#***********************************************

class UniqueList(list):
	def append(self, item):
		if item not in self:
			list.append(self, item)
	def extend(self, items):
		for item in items:
			self.append(item)

#***********************************************
# Templates
#***********************************************

MAIN_LSL = """multi = %(multi)s;
list textures = %(textures)s;
vector myPos;
integer tI;
string tS;

integer isKey(key in)
{
	if(in) return 2;
	return (in == NULL_KEY);
}

%(functions)s

default
{
	state_entry()
	{
%(setup)s
		tI = llGetListLength( textures );
		while ( tI ){
			if ( isKey( tS = llList2String( textures, tI = ~-tI ) ) == 0 )
			{
				if ( llGetInventoryType( tS ) != INVENTORY_TEXTURE )
				{
					llOwnerSay( "Please add texture \\"" + tS + "\\" to my contents" );
					state needs_something;
				}
			}
		}
		if ( multi ):
		{
			llRequestPermissions( llGetOwner(), PERMISSION_CHANGE_LINKS );
		}
		else:
		{
			state ready;
		}
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

%(states)s

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

STATE_MULTI = """state ready
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

state build
{
	state_entry()
	{
		myPos = llGetPos();
		llSetRot( ZERO_ROTATION );
		addPrim( %(prim)s );
	}

	object_rez( key id )
	{
		llCreateLink(id, TRUE );
	}

	changed( integer change )
	{
		if ( change & CHANGED_LINK )
		{
			tI = ~-llGetNumberOfPrims();
			%(builder)sif (tI > 0 )
			{
				llSetLinkPrimitiveParams( 2, [ %(rootParams)s ] );
				llBreakLink( 1 );
			}
			else
			{
				llOwnerSay( "Finished!" );
				state ready;
			}
		}
	}
}
"""

LINK_LSL = """if ( tI == %(linkNum)i )
			{
				llSetLinkPrimitiveParams( 2, [ %(linkParams)s ] );
				addPrim( %(prim)s );
			}
			else """

PRIM_REZ = """addPrim( prim )
{
	llRezObject(prim, myPos, ZERO_VECTOR, ZERO_ROTATION, 0 );
}
"""

PRIM_TEST = """		if ( llGetInventoryType( "%(prim)s" ) != INVENTORY_OBJECT )
		{
			llOwnerSay( "Please add a prim called "%(prim)s" to my contents" );
			state needs_something;
		}
"""

LINK_PARAMS = """PRIM_TYPE, PRIM_TYPE_SCULPT, "%(sculpt_map)s", PRIM_SCULPT_TYPE_%(sculpt_type)s, PRIM_SIZE, %(size)s, PRIM_ROTATION, %(rotation)s"""

PRIM_LOCATION = """PRIM_POSITION, %(position)s"""

TEXTURE = """PRIM_TEXTURE, %(face)s, "%(name)s", %(repeat)s, %(offset)s, %(rotation)s"""


def collect_textures(prim):
	textures = UniqueList([prim.sculpt_map.name])
	for t in prim.textures:
		textures.append(t.image.name)
	for c in prim.children:
		textures.extend(collect_textures(c))
	return textures

def export_lsl( filename ):
	Blender.Window.WaitCursor(1)
	prims = get_prims()
	if prims == []:
		Blender.Window.WaitCursor(0)
		Blender.Draw.PupBlock( "Nothing to do", ["No root prims are selected", " for export"] )
		return
	basepath = Blender.sys.dirname( filename )
	for p in prims:
		save_prim( p, basepath )
	Blender.Window.WaitCursor(0)

def prim2dict(prim):
	d = {}
	d['prim'] = PRIM_NAME
	d['name'] = prim.name
	d['position'] = "< %(x).5f, %(y).5f, %(z).5f >"%prim.location
	d['rotation'] = "< %.5f, %.5f, %.5f, %.5f >"%prim.rotation
	d['size'] = "< %(x).5f, %(y).5f, %(z).5f >"%prim.size
	d['sculpt_map'] = prim.sculpt_map.name
	return d

def texture2dict(texture):
	d= {}
	d['name'] = texture.image.name
	d['offset'] = "< %(x).5f, %(y).5f, %(z).5f >"%texture.offset
	d['repeat'] = "< %(x).5f, %(y).5f, %(z).5f >"%texture.repeat
	d['rotation'] = "%.5f"%texture.rotation
	if texture.face == -1:
		d['face'] = "ALL_SIDES"
	else:
		d['face'] = str(texture.face)
	return d

def save_prim(prim, basepath):
	d={}
	if prim.children:
		d['multi'] = 'TRUE'
	else:
		d['multi'] = 'FALSE'
	d['textures'] = str(collect_textures(prim)).replace("'", "\"")
	print prim2dict(prim)
	for t in prim.textures:
		print TEXTURE%texture2dict(t)
	print d

#***********************************************
# register callback
#***********************************************
def my_callback(filename):
	export_lsl(filename)

if __name__ == '__main__':
	Blender.Window.FileSelector(my_callback, "Export LSL", '.')
