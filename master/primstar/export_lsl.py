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
from primstar.sculpty import map_type

#***********************************************
# Globals
#***********************************************

PRIM_NAME = "Primstar"

#***********************************************
# Classes
#***********************************************

class UniqueList(list):
	def __init__(self, items=None):
		list.__init__(self, [])
		if items:
			self.extend(items)

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
		addPrim( "%(prim)s" );
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
				llSetLinkPrimitiveParams( 2, [ %(root_params)s ] );
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

LINK_LSL = """if ( tI == %(link_num)i )
			{
				llSetLinkPrimitiveParams( 2, [ PRIM_TYPE, PRIM_TYPE_SCULPT, "%(sculpt_map)s", PRIM_SCULPT_TYPE_%(sculpt_type)s, PRIM_SIZE, %(size)s, PRIM_ROTATION, %(rotation)s, PRIM_POSITION, %(position)s ] );
				addPrim( "%(prim)s" );
			}
			else """

PRIM_REZ = """addPrim( prim )
{
	llRezObject(prim, myPos, ZERO_VECTOR, ZERO_ROTATION, 0 );
}
"""

PRIM_TEST = """		if ( llGetInventoryType( "%(prim)s" ) != INVENTORY_OBJECT )
		{
			llOwnerSay( "Please add a prim called \\"%(prim)s\\" to my contents" );
			state needs_something;
		}
"""

PRIM_PARAMS = """PRIM_TYPE, PRIM_TYPE_SCULPT, "%(sculpt_map)s", PRIM_SCULPT_TYPE_%(sculpt_type)s, PRIM_SIZE, %(size)s, PRIM_ROTATION, %(rotation)s"""

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
		save_linkset( p, basepath )
	Blender.Window.WaitCursor(0)

def prim2dict(prim, link=0):
	return {'prim':PRIM_NAME,
		'name':prim.name,
		'position':"< %(x).5f, %(y).5f, %(z).5f >"%prim.location,
		'rotation':"< %.5f, %.5f, %.5f, %.5f >"%prim.rotation,
		'size':"< %(x).5f, %(y).5f, %(z).5f >"%prim.size,
		'sculpt_map':prim.sculpt_map.name,
		'link_num':link,
		'sculpt_type':map_type(prim.sculpt_map)}

def texture2dict(texture):
	d= {'name':texture.image.name,
		'offset':"< %(x).5f, %(y).5f, %(z).5f >"%texture.offset,
		'repeat':"< %(x).5f, %(y).5f, %(z).5f >"%texture.repeat,
		'rotation':"%.5f"%texture.rotation}
	if texture.face == -1:
		d['face'] = "ALL_SIDES"
	else:
		d['face'] = str(texture.face)
	return d

def link_lsl(prim, link = 0):
	link += 1
	if link > 1:
		t = LINK_LSL%prim2dict(prim, link)
	else:
		t = ''
	for c in prim.children:
		tc, link = link_lsl(c, link)
		t += tc
	return t, link

def save_linkset(prim, basepath):
	d={'prim':PRIM_NAME}
	root = prim2dict(prim)
	if prim.children:
		d['multi'] = 'TRUE'
		d['functions'] = PRIM_REZ
		d['setup'] = PRIM_TEST%d
		builder, link = link_lsl(prim)
		d['states'] = STATE_MULTI%{'prim':PRIM_NAME, 'builder':builder, 'root_params':PRIM_PARAMS%root + ", " + PRIM_LOCATION%root}
	else:
		d['multi'] = 'FALSE'
		d['functions'] = ''
		d['setup'] = ''
		d['builder'] = ''
	d['textures'] = str(collect_textures(prim)).replace("'", "\"")

	print MAIN_LSL%d

#***********************************************
# register callback
#***********************************************
def my_callback(filename):
	export_lsl(filename)

if __name__ == '__main__':
	Blender.Window.FileSelector(my_callback, "Export LSL", '.')
