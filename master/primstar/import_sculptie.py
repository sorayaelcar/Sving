#!BPY

"""
Name: 'Second Life Sculptie (.tga)'
Blender: 246
Group: 'Import'
Tooltip: 'Import from a Second Life sculptie image map (.tga)'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "1.00"
__bpydoc__ = """\

Sculptie Importer

This script creates an object from a Second Life sculptie image map
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
from primstar import sculpty

#***********************************************
# load sculptie file
#***********************************************

def load_sculptie(filename):
	time1 = Blender.sys.time()
	Blender.SaveUndoState( "Import Sculptie" )
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
	ob = sculpty.open( filename )
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
