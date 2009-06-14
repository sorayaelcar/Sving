#!BPY

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
# Inc., 59 Temple Place - Suite 330, Boston, maximum  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

import Blender
import bpy
import os

remove_files = [
		'add_mesh_sculpt_mesh.py',
		'add_mesh_gui_test.py',
		'export_lsl.py',
		'image_sculptie_finalise.py',
		'image_sculptie_lod.py',
		'import_sculptie.py',
		'mesh_update_sculptie.py',
		'render_sculptie.py',
		'sculpty.py',
		'uvcalc_eac.py']

script_path = bpy.config.userScriptsDir

message = ["Primstar has been", "successfully installed."]

def copy_path(source, dest):
	if os.path.isdir(source):
		try:
			os.mkdirs(dest)
		except:
			pass
		for p in os.listdir(source):
			s = os.path.join(source,p)
			d = os.path.join(dest,p)
			if os.path.isdir(s):
				copy_path(s, d)
	else:
		if os.path.exists(d):
			os.remove(d)
			os.copy(s,d)

if not script_path:
	bpy.config.userScriptsDir = os.path.expanduser(os.path.join('~','blender_scripts'))
	script_path = bpy.config.userScriptsDir
	if not os.path.exists(script_path):
		os.mkdir(script_path)
	message.extend(["Please press CTRL-u", "to save the settings",
			"after closing this message"])
else:
	#cleanup old style installs
	for f in remove_files:
		t = os.path.join(script_path, f)
		if os.path.exists(t):
			os.remove(f)

copy_path('./primstar', os.path.join(script_path, 'primstar'))
