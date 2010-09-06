#!BPY

"""
Name: 'JASS Basic Lib of Sculpts'
Blender: 248
Group: 'AddMesh'
Tooltip: 'Select Sculptie from library'
"""

__author__ = ["Gaia Clary"]
__url__ = ("http://blog.machinimatrix.org")
__version__ = "1.3"
__bpydoc__ = """\

Select a sculptie from the JASS Basic sculptie library

This script can be used stand alone, but it is highly recommended to 
also instal the scripts from Domino Marama!

Version history:
2009-05-19: gaia.clary: Now the library can also be installed in the blender scripts folder
2009-04-18: gaia.clary: started integration into Domino Scripts

"""

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) Machinimatrix
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

import Blender, bpy, BPyMesh
from Blender import *

LibraryName = "JASS Library of Basic Sculpties"
LibraryRelativePath = "/jass/lib/lib-basic.blend"

#***********************************************
# main
#***********************************************

def main():

	#keep current edit-mode and temporary leave it
	in_editmode = Window.EditMode()
	Window.EditMode(0)

	# get the current scene
	scene = bpy.data.scenes.active
	

	# Get the script location
	scriptLocation = bpy.config.userScriptsDir
	libraryIsOpen = False
	library = ""
	if scriptLocation:
		print "uscriptsdir=", scriptLocation
	
		# Load and open the basic sculpties library
		library  = scriptLocation + LibraryRelativePath
		try:
			Library.Open(library)
			libraryIsOpen = True
		except:
			print "JASSLibrary not installed in user scripts dir"
			pass
	
	if libraryIsOpen == False:
		scriptLocation = Blender.Get(r"scriptsdir") 
		print "scriptsdir=", scriptLocation
		# Load and open the basic sculpties library
		library  = scriptLocation + LibraryRelativePath
		try:
			Library.Open(library)
			libraryIsOpen = True
		except:
			print "JASSLibrary not installed in scripts dir"
			pass
	
	if libraryIsOpen == False:
		Blender.Draw.PupBlock( "Library open Error", ["JASSLibrary not installed"] )
		return
	else:
		print "JASSLibrary loaded from ", library

	# Create the selection menu
	menuText=LibraryName + "%t"
	libContent = []
	for obname in Library.Datablocks("Object"):
		libContent.append(obname)
		menuText += "|"+obname
	menuText += "|"

	# Select and res the selected object
	itemId = Blender.Draw.PupMenu(menuText)
	if (itemId != -1):
		for ob in scene.objects:
			ob.sel = False
		libraryObjectName = libContent[itemId-1]
		print "selected ", libraryObjectName
		lib = bpy.libraries.load(library)
		pseudoOb = lib.objects.append(libraryObjectName)
		ob = scene.objects.link(pseudoOb)
		ob.setLocation(Window.GetCursorPos())
		ob.sel = True
		
	#restore original edit_mode
	Window.EditMode(in_editmode)

	#Redraw all windows
	Blender.Redraw


if __name__ == '__main__':
	main()

