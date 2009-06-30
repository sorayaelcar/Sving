#!BPY

"""
Name: 'Collada 1.4 as Sculptie (.dae)'
Blender: 246
Group: 'Import'
Tooltip: 'Import a Collada file and prepare as sculpties'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "1.00"
__bpydoc__ = """\

Sculptie Importer

This script creates sculptie compatible objects from a Collada 1.4 file
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
from colladaImEx.translator import Translator

#***********************************************
# load sculptie file
#***********************************************

def import_collada_sculptie(filename):
	time1 = Blender.sys.time()
	Blender.SaveUndoState( "Import Collada Sculptie" )
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
	t = Translator(True, '0.3.161', False, filename, False, False, False, False, True,
			False, False, True, False, False, False, False, True, False)
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects:
		if ob.type == 'Mesh':
			mesh = ob.getData(False, True)
			if "sculptie" not in mesh.getUVLayerNames():
				mesh.renameUVLayer(mesh.activeUVLayer, "sculptie")
			else:
				mesh.activeUVLayer = "sculptie"
			mesh.update()
			x_verts = 0
			y_verts = 0
			for f in mesh.faces:
				f.sel = True
				for v in f.uv:
					if v[1] == 0.0:
						x_verts += 1
					if v[0] == 0.0:
						y_verts += 1
			s,t,w,h,cs,ct = sculpty.map_size(x_verts / 2, y_verts / 2, 0)
			image = Blender.Image.New(mesh.name, w, h, 32)
			sculpty.set_map(mesh, image)

	if in_editmode:
		Blender.Window.EditMode(1)
	Blender.Redraw()
	print 'finished importing: "%s" in %.4f sec.' % (filename, (Blender.sys.time()-time1))

#***********************************************
# register callback
#***********************************************
def my_callback(filename):
	import_collada_sculptie(filename)

if __name__ == '__main__':
	Blender.Window.FileSelector(my_callback, "Import as Sculptie", '.dae')
