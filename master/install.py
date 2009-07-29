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
from distutils import dir_util

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
		'uvcalc_eac.py',
		'add_mesh_sculpt_mesh.pyc',
		'add_mesh_gui_test.pyc',
		'export_lsl.pyc',
		'image_sculptie_finalise.pyc',
		'image_sculptie_lod.pyc',
		'import_sculptie.pyc',
		'mesh_update_sculptie.pyc',
		'render_sculptie.pyc',
		'sculpty.pyc',
		'uvcalc_eac.pyc']

script_path = bpy.config.userScriptsDir

message = ["Primstar has been", "successfully installed."]

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
bpydata_path = os.path.join(script_path,"bpydata")
if not os.path.exists(bpydata_path):
	os.mkdir(bpydata_path)
dir_util.copy_tree('primstar', os.path.join(script_path, 'primstar'), update=1)
Blender.Draw.PupBlock( "Installation Complete", message )