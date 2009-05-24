#!BPY

"""
Name: 'Second Life Sculptie (.tga)'
Blender: 246
Group: 'Import'
Tooltip: 'Import from a Second Life sculptie image map (.tga)'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.38"
__bpydoc__ = """\

Sculptie Importer

This script creates an object from a Second Life sculptie image map
"""

#Changes:
#0.38 Domino Marama 2009-05-24
#- split fuctionality into sculpty.py
#0.37 Domino Marama 2009-05-22
#- Now uses mapType to detect sculptie type. Dialog box removed.
#0.36 Domino Marama 2008-10-25
#- Wrapped edges are marked as seams
#0.35 Domino Marama 2008-10-19
#- Added face counts on multires calculation
#0.34 Domino Marama 2008-10-18
#- Jira VWR-9384 style oblong support
#- add mesh api support removed as it's now in add_mesh_sculpt_mesh.py
#0.33 Domino Marama 2008-08-27
#- added support for oblong sculpties
#0.32 Domino Marama 2008-08-05
#- corrected hemi rotation bug introduced by last "fix"
#0.31 Domino Marama 2008-07-14
#- corrected normals on hemi
#0.30 Domino Marama 2008-07-14
#- added hemi generator
#0.29 Domino Marama 2008-06-28
#- sphere poles left as small circle
#0.28 Domino Marama 2008-06-26
#- required version text updated
#- rename uv map to sculptie and assign image
#0.27 Domino Marama 2008-05-07
#- use preferences for align to view and enter editmode on add mesh
#0.26 Domino Marama 2008-04-30
#- persistant settings added
#0.25 Domino Marama 2008-04-22
#- wait cursor added
#0.24 Domino Marama 2008-03-12
#- updated for baker v0.12
#0.23 Domino Marama 2008-03-03
#- bug fix on assigning sculpt map - needed to be on multires level 1
#0.22 Domino Marama 2008-02-29
#- allows running on Blender 2.45 by converting multires to additional faces on base mesh
#0.21 Domino Marama 2008-02-12
#- seams moved to -ve x to match SL forward direction
#0.20 Domino Marama 2008-02-12
#- multires made optional on new sculpties
#- new objects now created at 3D cursor
#0.19 Domino Marama 2008-02-11
#- exposed faces_x, faces_y and multires for more general use
#- assigning sculpt map to uv faces put back
#0.18 Domino Marama 2008-02-10
#- minor bug fix, torus was prompting for radius on import
#0.17 Domino Marama 2008-02-09
#- sculpt map no longer assigned to UV faces
#- sculpt map filename now stored as property
#- script seperated into functions to expose api
#- generate default meshes for each sculptie type added
#0.16 Domino Marama 2008-02-02
#- updated for addMultiresLayer_2.patch
#- uv face rotation correction for wrapped min and max y
#0.15 Domino Marama 2008-02-01
#- used wrap_? vars in later tests
#0.14 Domino Marama 2008-01-31
#- mesh generation rewritten to support wrapping
#0.13 Domino Marama 2008-01-24
#- major rewrite to use multires
#0.12 Domino Marama 2007-12-23
#- fixed sculptie types
#0.11 Domino Marama 2007-08-29
#- minor code cleanup
#- added prim properties
#0.10 Domino Marama 2007-08-26
#- corrected name handler using blender sys to replace os
#0.09 Domino Marama 2007-08-21
#- dependancy on os module removed
#0.08 Domino Marama 2007-08-19
#- Removed storage of original uv co-ords as 0.02 baker no longer needs
#0.07 Domino Marama 2007-08-13
#- Material simplified as new sculptie baker only uses it to signal a
#- sculpted prim mesh, default verts set to map size + 1 <=33
#- uv border removed as not needed with correct verts count
#0.06 Domino Marama 2007-08-13
#- Added original mapping pixels storage in vertex paint r & g channels
#0.05 Domino Marama 2007-08-12
#- Added verts and border uv to options
#0.04 Domino Marama 2007-08-12
#- Fixed wrap bug on planes
#0.03 Domino Marama 2007-08-11
#- Settings menu added
#0.02 Domino Marama 2007-08-11
#- Main functionality completed
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
import sculpty

#***********************************************
# load sculptie file
#***********************************************

def load_sculptie(filename):
	print "--------------------------------"
	print 'Importing "%s"' % filename
	in_editmode = Blender.Window.EditMode()
	# MUST leave edit mode before changing an active mesh:
	if in_editmode:
		Blender.Window.EditMode(0)
	else:
		try:
			in_editmode = Blender.Get('add_editmode')
		except:
			pass
	time1 = Blender.sys.time()  #for timing purposes
	Blender.SaveUndoState( "Import Sculptie" )
	image = Blender.Image.Load( filename )
	image.name = Blender.sys.splitext( image.name )[0]
	image.properties["scale_x"] = 1.0
	image.properties["scale_y"] = 1.0
	image.properties["scale_z"] = 1.0
	ob = sculpty.new_from_map( image )
	if in_editmode:
		Blender.Window.EditMode(1)
	Blender.Redraw()
	print 'finished importing: "%s" in %.4f sec.' % (filename, (Blender.sys.time()-time1))

#***********************************************
# register callback
#***********************************************
def my_callback(filename):
	load_sculptie(filename)

if __name__ == '__main__':
	Blender.Window.FileSelector(my_callback, "Import Sculptie", '.tga')
