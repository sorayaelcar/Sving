#!BPY
"""
Name: 'Import as Sculptie'
Blender: 246
Group: 'Image'
Tooltip: 'Import this image as a new sculptie'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "1.00"
__bpydoc__ = """\

Import as Sculptie

This script imports the active image as a sculptie
"""
# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) 2009 Domino Designs Limited
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

import Blender
from primstar.sculpty import new_from_map

def main():
	in_editmode = Blender.Window.EditMode()
	# MUST leave edit mode before changing an active mesh:
	if in_editmode:
		Blender.Window.EditMode(0)
	else:
		try:
			in_editmode = Blender.Get('add_editmode')
		except:
			pass
	image = Blender.Image.GetCurrent()
	if image:
		ob = new_from_map(image, False)
	else:
		Blender.Draw.PupBlock("Can't add Sculptie", ["No current image"])
	if in_editmode:
		Blender.Window.EditMode(1)
	Blender.Redraw()

if __name__ == '__main__':
	main()