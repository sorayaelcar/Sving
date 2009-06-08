#!BPY
"""
Name: 'Sculpt Mesh'
Blender: 246
Group: 'AddMesh'
Tooltip: 'Add a Second Life sculptie compatible mesh'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.13"
__bpydoc__ = """\

Sculpt Mesh

This script creates an object with a gridded UV map suitable for Second Life sculpties.
"""

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
# Inc., 59 Temple Place - Suite 330, Boston, maximum  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

import Blender
from math import log, ceil, sqrt, pi, sin, cos
import sculpty

#***********************************************
# constants
#***********************************************

SPHERE   = 1
TORUS    = 2
PLANE    = 3
CYLINDER = 4
HEMI     = 5

BUILD_MODE_SUBSURF  = 1
BUILD_MODE_MULTIRES = 2

SUBDIV_MODE_CATMULL_CLARK = 1
SUBDIV_MODE_SIMPLE = 2

EVENT_NONE = 0
EVENT_EXIT = 1
EVENT_REDRAW = 2
EVENT_MESH_CHANGE = 3

EVENT_SUBDIV_CATMULL = 10
EVENT_SUBDIV_SIMPLE  = 11

EVENT_SCULPT_TYPE_SPHERE   = 21
EVENT_SCULPT_TYPE_TORUS    = 22
EVENT_SCULPT_TYPE_PLANE    = 23
EVENT_SCULPT_TYPE_CYLINDER = 24
EVENT_SCULPT_TYPE_HEMI     = 25

EVENT_BUILD_MODE_SUBSURF  = 31
EVENT_BUILD_MODE_MULTIRES = 32

EVENT_CLEAN_LOD = 41

EVENT_OK = 51

MESH_REGISTRY = 'AddMeshSculptMesh'

settings = {'x_faces':8,
			'y_faces':8, 
			'sculpt_type':1,
			'multires_levels':2,
			'subdiv_type':1,
			'clean_lod':True,
			'radius':0.25,
			'build_mode':1
		   }

GLOBALS = {}

def add_sculptie( sculpt_type, faces_x=8, faces_y=8, multires=2, clean_lods=True, subsurf=False, catmull=True ):
	Blender.Window.WaitCursor(1)
	basename = ("Sphere", "Torus", "Plane", "Cylinder", "Hemi")[sculpt_type -1]
	scene = Blender.Scene.GetCurrent()
	for ob in scene.objects:
		ob.sel = False
	rdict = Blender.Registry.GetKey('ImportSculptie', True) # True to check on disk also
	if rdict: # if found, get the values saved there
		try:
			settings['radius'] = rdict['radius']
		except:
			settings['radius'] = 0.25
	if sculpt_type == TORUS:
		radius = Blender.Draw.Create( settings['radius'] )
		Blender.Window.WaitCursor(0)
		retval = Blender.Draw.PupBlock( "Torus Options", [( "Radius: ", radius, 0.05, 0.5 )] )
		Blender.Window.WaitCursor(1)
		settings['radius'] = radius.val
		Blender.Registry.SetKey('ImportSculptie', settings, True) # save latest settings
	mesh = sculpty.new_mesh( basename,
			["none","SPHERE","TORUS","PLANE","CYLINDER","HEMI"][sculpt_type],
			faces_x, faces_y, multires, clean_lods, settings['radius'])
	s, t, w, h, clean_s, clean_t = sculpty.map_size( faces_x, faces_y, multires )
	image = Blender.Image.New( basename, w, h, 32 )
	sculpty.bake_lod(image)
	ob = scene.objects.new( mesh, basename )
	if sculpt_type != PLANE:
		mesh.flipNormals()
	ob.sel = True
	ob.setLocation( Blender.Window.GetCursorPos() )
	if sculpt_type == PLANE:
		mesh.flipNormals()
	sculpty.set_map( mesh, image )
	if multires:
		if subsurf:
			mods = ob.modifiers
			mod = mods.append(Blender.Modifier.Types.SUBSURF)
			mod[Blender.Modifier.Settings.LEVELS] = multires
			mod[Blender.Modifier.Settings.RENDLEVELS] = multires
			mod[Blender.Modifier.Settings.UV] = False
			if not catmull:
				mod[Blender.Modifier.Settings.TYPES] = 1
		else:
			mesh.multires = True
			mesh.addMultiresLevel(multires, ('simple', 'catmull-clark')[catmull])
			mesh.sel = True
	# adjust scale for subdivision
	minimum, maximum = sculpty.get_bounding_box( ob )
	x = 1.0 / (maximum.x - minimum.x)
	y = 1.0 / (maximum.y - minimum.y)
	try:
		z = 1.0 / (maximum.z - minimum.z)
	except:
		z = 0.0
	if sculpt_type == TORUS:
		z = settings['radius'] * z
	elif sculpt_type == HEMI:
		z = 0.5 * z
	tran = Blender.Mathutils.Matrix( [ x, 0.0, 0.0 ], [0.0, y, 0.0], [0.0, 0.0, z] ).resize4x4()
	mesh.transform( tran )
	# align to view
	try:
		quat = None
		if Blender.Get('add_view_align'):
			quat = Blender.Mathutils.Quaternion(Blender.Window.GetViewQuat())
			if quat:
				mat = quat.toMatrix()
				mat.invert()
				mat.resize4x4()
				ob.setMatrix(mat)
	except:
		pass
	Blender.Window.WaitCursor(0)
	return ob

# ============================================
# Event handler for the Sculpt Mesh selection
# ============================================
def do_sculpt_type_sel(event, val):
	GLOBALS['event'] = event
	GLOBALS['sculpt_type_sphere'].val   =  (event == EVENT_SCULPT_TYPE_SPHERE)
	GLOBALS['sculpt_type_torus'].val    =  (event == EVENT_SCULPT_TYPE_TORUS)
	GLOBALS['sculpt_type_plane'].val    =  (event == EVENT_SCULPT_TYPE_PLANE)
	GLOBALS['sculpt_type_cylinder'].val =  (event == EVENT_SCULPT_TYPE_CYLINDER)
	GLOBALS['sculpt_type_hemi'].val     =  (event == EVENT_SCULPT_TYPE_HEMI)
	GLOBALS['sculpt_type']              =   event - EVENT_SCULPT_TYPE_SPHERE + 1

# ============================================
# Event handler for the build mode
# ============================================
def do_build_mode_sel(event, val):
	GLOBALS['event'] = event
	GLOBALS['build_mode_subsurf'].val  = (event == EVENT_BUILD_MODE_SUBSURF)
	GLOBALS['build_mode_multires'].val = (event == EVENT_BUILD_MODE_MULTIRES)
	GLOBALS['build_mode']              = event - EVENT_BUILD_MODE_SUBSURF + 1

# =============================================
# Event handler for subdivision type selection
# =============================================
def do_subdiv_type_sel(event, val):
	GLOBALS['event'] = event
	GLOBALS['subdiv_type_catmull_clark'].val  = (event == EVENT_SUBDIV_CATMULL)
	GLOBALS['subdiv_type_simple'].val         = (event == EVENT_SUBDIV_SIMPLE)
	GLOBALS['subdiv_type']                    = event - EVENT_SUBDIV_CATMULL + 1

# =============================================
# Event handler for the Clean LODs button
# =============================================
def toggle_button(event, val):
	GLOBALS['event'] = event

# ===============================================================
# Event handler for the Clean LODs button if build mode is NURBS
# ===============================================================
def do_force_clean_lod_sel(event, val):
	GLOBALS['clean_lod'].val = 0

# ===============================================================
# Event handler for the OK button
# ===============================================================
def do_ok_sel(event, val):
	GLOBALS['event'] = event

def addLodRow(label, x, y, width, height, lod, levels, tooltip ):
	Blender.Draw.Button(label, EVENT_NONE, x, y, 55, 20, tooltip)
	factor = 2**levels
	x_faces = width  * factor
	y_faces = height * factor
	lx,ly = sculpty.lod_size( x_faces , y_faces, lod )
	print "(",x_faces,",",y_faces,") --> (",lx,",",ly,") lod:",lod, " levels:",levels, "factor:",factor 
	Blender.Draw.Button(str(lx),     EVENT_NONE, x+55,  y, 35, 20)
	Blender.Draw.Button(str(ly) ,    EVENT_NONE, x+90,  y, 35, 20)
	Blender.Draw.Button(str(ly*lx) , EVENT_NONE, x+125, y, 50, 20)

def addLodLabelRow(x, y):
	Blender.Draw.Button("faces:", EVENT_NONE, x,  y, 55, 20)
	Blender.Draw.Button("X",      EVENT_NONE, x+ 55, y, 35, 20)
	Blender.Draw.Button("Y" ,     EVENT_NONE, x+ 90, y, 35, 20)
	Blender.Draw.Button("X*Y",    EVENT_NONE, x+125, y, 50, 20)

# ===================================================================
# This method presets the GLOBAL map from where the UIBlock and the 
# event handlers read the data
# ===================================================================
def create_gui_globals():

	# ====================================================
	# Preset the Window element values from the registry
	# ====================================================
	
	registry = MESH_REGISTRY
	try:
		rdict = Blender.Registry.GetKey(registry, True) # True to check on disk also
	except:
		print "No registry entry found for key", registry
		
	if rdict: # if found, get the values saved there
		try:
			settings['x_faces']          = rdict['x_faces']
			settings['y_faces']          = rdict['y_faces']
			settings['multires_levels']  = rdict['multires_levels']
			settings['subdiv_type']      = rdict['subdiv_type']
			settings['sculpt_type']      = rdict['sculpt_type']
			settings['clean_lod']        = rdict['clean_lod']
			settings['build_mode']       = rdict['build_mode']
			settings['radius']           = rdict['radius']
		except:
			pass

	# ===========================================================
	# Create the drawing elements
	# ===========================================================
	
	GLOBALS['sculpt_type']     = settings['sculpt_type']
	GLOBALS['subdiv_type']     = settings['subdiv_type']
	GLOBALS['build_mode']      = settings['build_mode']
	GLOBALS['faces_x']         = Blender.Draw.Create( settings['x_faces'] )
	GLOBALS['faces_y']         = Blender.Draw.Create( settings['y_faces'] )
	GLOBALS['multires_levels'] = Blender.Draw.Create( settings['multires_levels'] )
	GLOBALS['clean_lod']       = Blender.Draw.Create( settings['clean_lod'] )
	
	GLOBALS['subdiv_type_catmull_clark']  = Blender.Draw.Create( settings['subdiv_type'] == SUBDIV_MODE_CATMULL_CLARK )
	GLOBALS['subdiv_type_simple']         = Blender.Draw.Create( settings['subdiv_type'] == SUBDIV_MODE_SIMPLE )
	
	GLOBALS['sculpt_type_sphere']   = Blender.Draw.Create(settings['sculpt_type'] == SPHERE)
	GLOBALS['sculpt_type_torus']    = Blender.Draw.Create(settings['sculpt_type'] == TORUS)
	GLOBALS['sculpt_type_plane']    = Blender.Draw.Create(settings['sculpt_type'] == PLANE)
	GLOBALS['sculpt_type_cylinder'] = Blender.Draw.Create(settings['sculpt_type'] == CYLINDER)
	GLOBALS['sculpt_type_hemi']     = Blender.Draw.Create(settings['sculpt_type'] == HEMI)
	
	GLOBALS['build_mode_subsurf']  = Blender.Draw.Create(settings['build_mode'] == BUILD_MODE_SUBSURF)
	GLOBALS['build_mode_multires'] = Blender.Draw.Create(settings['build_mode'] == BUILD_MODE_MULTIRES)
	
	GLOBALS['mouseCoords'] = Blender.Window.GetMouseCoords()
	GLOBALS['event'] = EVENT_NONE
	

# ===============================================================
# The main drawing routine
# ===============================================================
def drawCreateBox():
	
	mouseCoords = GLOBALS['mouseCoords']
	mouse_x, mouse_y = mouseCoords
	mouse_x-=260
	mouse_y+=200

	row  = [mouse_x + 0, mouse_x + 190, mouse_x + 305]

	GLOBALS['event'] = EVENT_EXIT

	block = []
		
	title = "Sculpt Mesh Options"
	# Left Popup Block

	x = row[0]
	y = mouse_y	
	
	Blender.Draw.Label(title, x, y, 335, 20)
			
	# ==========================================================
	# MESH GEOMETRY
	# ==========================================================
	y -= 30
	Blender.Draw.Label("Mesh Geometry:", x, y, 150, 20); y -= 20

	Blender.Draw.BeginAlign()
	GLOBALS['faces_x']   = Blender.Draw.Number("X Faces", EVENT_MESH_CHANGE, x,y, 175, 20, GLOBALS['faces_x'].val, 0, 256, "Number of faces along the X-axis", toggle_button); y -=20
	GLOBALS['faces_y']   = Blender.Draw.Number("Y Faces", EVENT_MESH_CHANGE, x,y, 175, 20, GLOBALS['faces_y'].val, 0, 256, "Number of faces along the Y-axis", toggle_button); y -=20
	GLOBALS['clean_lod'] = Blender.Draw.Toggle("Clean LODs", EVENT_CLEAN_LOD, x,y, 175, 20, GLOBALS['clean_lod'].val,   "For non power of 2 facecounts: Ensure the object will use good LOD settings", toggle_button); y -=20
	Blender.Draw.EndAlign()

	y -= 10
	Blender.Draw.BeginAlign()
	GLOBALS['multires_levels'] = Blender.Draw.Number("subdivision levels", EVENT_MESH_CHANGE, x,y, 175, 20, GLOBALS['multires_levels'].val, 0, 256, "Number of mesh subdivisions (Corresponds to SL LOD)", toggle_button); y -=20
	GLOBALS['subdiv_type_catmull_clark'] = Blender.Draw.Toggle("Catmull-Clark", EVENT_SUBDIV_CATMULL, x,y, 100, 20, GLOBALS['subdiv_type_catmull_clark'].val,"Catmull-Clark", do_subdiv_type_sel) 
	GLOBALS['subdiv_type_simple']        = Blender.Draw.Toggle("Simple",        EVENT_SUBDIV_SIMPLE, x+100, y, 75, 20, GLOBALS['subdiv_type_simple'].val, "Simple", do_subdiv_type_sel); y -=20
	Blender.Draw.EndAlign()

	y -=10
	Blender.Draw.BeginAlign()
	addLodLabelRow(x,y); y -=20
	addLodRow("LOD3", x,y, GLOBALS['faces_x'].val, GLOBALS['faces_y'].val, 3, GLOBALS['multires_levels'].val+1, "Maximum Number of rendered faces (when object is close to camera)" ); y -=20
	addLodRow("LOD2", x,y, GLOBALS['faces_x'].val, GLOBALS['faces_y'].val, 2, GLOBALS['multires_levels'].val+1, "First reduction of rendered faces (when object is near to camera)"); y -=20
	addLodRow("LOD1", x,y, GLOBALS['faces_x'].val, GLOBALS['faces_y'].val, 1, GLOBALS['multires_levels'].val+1, "Secnd reduction of rendered faces (when object is further away from camera"); y -=20
	addLodRow("LOD0", x,y, GLOBALS['faces_x'].val, GLOBALS['faces_y'].val, 0, GLOBALS['multires_levels'].val+1, "Minimum Number of rendered faces (when object is far away from camera"); y -=20
	Blender.Draw.EndAlign()
	
	# ==========================================================
	# MESH TYPE
	# ==========================================================
	x = row[1]
	y = mouse_y - 30
	
	Blender.Draw.Label("Mesh type:", x,y, 100, 20); y -=20

	Blender.Draw.BeginAlign()
	GLOBALS['sculpt_type_sphere']   = Blender.Draw.Toggle("Sphere",   EVENT_SCULPT_TYPE_SPHERE,  x, y, 100, 18, GLOBALS['sculpt_type_sphere'].val,  "Spherical shaped object", do_sculpt_type_sel); y -=20
	GLOBALS['sculpt_type_torus']    = Blender.Draw.Toggle("Torus",    EVENT_SCULPT_TYPE_TORUS,   x, y, 100, 18, GLOBALS['sculpt_type_torus'].val,   "Torus shaped object",     do_sculpt_type_sel);	y -=20
	GLOBALS['sculpt_type_plane']    = Blender.Draw.Toggle("Plane",    EVENT_SCULPT_TYPE_PLANE,   x, y, 100, 18, GLOBALS['sculpt_type_plane'].val,   "Plane object",            do_sculpt_type_sel);	y -=20
	GLOBALS['sculpt_type_cylinder'] = Blender.Draw.Toggle("Cylinder", EVENT_SCULPT_TYPE_CYLINDER,x, y, 100, 18, GLOBALS['sculpt_type_cylinder'].val,"Cylinder shaped object",  do_sculpt_type_sel);	y -=20
	GLOBALS['sculpt_type_hemi']     = Blender.Draw.Toggle("Hemi",     EVENT_SCULPT_TYPE_HEMI,    x, y, 100, 18, GLOBALS['sculpt_type_hemi'].val,    "Hemi shaped object",      do_sculpt_type_sel);	y -=20
	Blender.Draw.EndAlign()

	# ==========================================================
	# BUILD STYLE
	# ==========================================================
	y -=60

	Blender.Draw.Label("Build style:", x, y, 100, 20); y -=20			
	Blender.Draw.BeginAlign()
	GLOBALS['build_mode_subsurf']  = Blender.Draw.Toggle("Subsurf",  EVENT_BUILD_MODE_SUBSURF , x, y, 100, 20, GLOBALS['build_mode_subsurf'].val, "subsurf (beginners, easy LOD)", do_build_mode_sel); y -= 20
	GLOBALS['build_mode_multires'] = Blender.Draw.Toggle("Multires", EVENT_BUILD_MODE_MULTIRES, x, y, 100, 20, GLOBALS['build_mode_multires'].val,"multires (experts, high flexibility)", do_build_mode_sel); y -= 20
	Blender.Draw.EndAlign()

	x = row[2]
	y = mouse_y - 250	
	GLOBALS['button_ok']    = Blender.Draw.Button("OK", EVENT_OK, x, y, 25, 220,  "Create object", do_ok_sel)

def create_sculpty():

	settings['x_faces']          = GLOBALS['faces_x'].val
	settings['y_faces']          = GLOBALS['faces_y'].val
	settings['multires_levels']  = GLOBALS['multires_levels'].val
	settings['subdiv_type']      = GLOBALS['subdiv_type']
	settings['sculpt_type']      = GLOBALS['sculpt_type']
	settings['build_mode']       = GLOBALS['build_mode']
	settings['clean_lod']        = GLOBALS['clean_lod'].val
		
	Blender.Registry.SetKey(MESH_REGISTRY, settings, True)
	in_editmode = Blender.Window.EditMode()
	# MUST leave edit mode before changing an active mesh:
	if in_editmode:
		Blender.Window.EditMode(0)
	else:
		try:
			in_editmode = Blender.Get('add_editmode')
		except:
			pass
	try:
		ob = add_sculptie(
			GLOBALS['sculpt_type'], 
			GLOBALS['faces_x'].val, 
			GLOBALS['faces_y'].val, 
			GLOBALS['multires_levels'].val, 
			GLOBALS['clean_lod'].val, 
			GLOBALS['build_mode']==BUILD_MODE_SUBSURF,
			GLOBALS['subdiv_type']==SUBDIV_MODE_CATMULL_CLARK )
	except RuntimeError:
		Blender.Draw.PupBlock( "Unable to create sculptie", ["Please decrease face counts","or subdivision levels"] )

	if in_editmode:
		Blender.Window.EditMode(1)

# ===============================================================
# Main loop.
# Note: The UIBlock is redrawn with every mouse click, so that
# Toggle buttons are refreshed or made visible/invisible epending
# on the mesh type and build mode etc...
#
# The main loop terminates when the mouse clicks outside of the
# Window or when the mouse clicks on the OK button. If the OK
# button is clicked, a new sculptie will be created.
# ===============================================================
def main():

	create_gui_globals()
	GLOBALS['event'] = EVENT_REDRAW
	while GLOBALS['event'] != EVENT_EXIT and GLOBALS['event'] != EVENT_OK:
		Blender.Draw.UIBlock( drawCreateBox, 0 )
	if GLOBALS['event'] == EVENT_OK:
		create_sculpty()

if __name__ == '__main__':
	main()
