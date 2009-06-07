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
#0.13 Gaia Clary 2009-06-07
#- Enhanced GUI added
#0.12 Domino Marama 2009-05-24
#- Image based sculptie generation added
#0.11 Domino Marama 2008-10-27
#- Use get_bounding_box from render_sculptie.py
#0.10 Domino Marama 2008-10-25
#- Wrapped edges are marked as seams
#0.09 Domino Marama 2008-10-17
#- Added subsurf modifer for lod levels
#0.08 Domino Marama 2008-10-17
#- Added clean LODs option and proper oblong support
#0.07 Domino Marama 2008-08-27
#- Increased max faces for oblong sculpties
#0.06 Domino Marama 2008-07-13
#- Added hemi sculpt type
#0.05 Domino Marama 2008-06-28
#- settings ranges reduced to be mostly sensible
#0.04 Domino Marama 2008-06-26
#- space removed from registry key name
#0.03 Domino Marama 2008-05-07
#- use preferences for entering edit mode on add mesh
#0.02 Domino Marama 2008-04-30
#- Added versioning info and persistant settings
#0.01 Domino Marama
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

def addLodRow(label, xpos, ypos, width, height, lod, levels, tooltip ):
	Blender.Draw.Button(label, EVENT_NONE, xpos, ypos, 55, 20, tooltip)
	factor = 2**levels
	x_faces = width  * factor
	y_faces = height * factor
	lx,ly = sculpty.lod_size( x_faces , y_faces, lod )
	print "(",x_faces,",",y_faces,") --> (",lx,",",ly,") lod:",lod, " levels:",levels, "factor:",factor 
	Blender.Draw.Button(str(lx),  EVENT_NONE, xpos+55, ypos , 35, 20)
	Blender.Draw.Button(str(ly) , EVENT_NONE, xpos+90, ypos, 35, 20)
	Blender.Draw.Button(str(ly*lx) , EVENT_NONE, xpos+125, ypos, 50, 20)

def addLodLabelRow(xpos, ypos):
	Blender.Draw.Button("faces:", EVENT_NONE, xpos, ypos, 55, 20)
	Blender.Draw.Button("X",   EVENT_NONE, xpos+55, ypos , 35, 20)
	Blender.Draw.Button("Y" ,  EVENT_NONE, xpos+90, ypos, 35, 20)
	Blender.Draw.Button("X*Y", EVENT_NONE, xpos+125, ypos, 50, 20)

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
	x,y = mouseCoords
	x-=260
	y+=200

	row  = [x + 0, x + 190, x + 305]

	GLOBALS['event'] = EVENT_EXIT

	block = []
		
	title = "Sculpt Mesh Options " + sculpty.RELEASE
	# Left Popup Block
			
	Blender.Draw.Label(title, row[0], y, 335, 20)

			
	# ==========================================================
	# MESH GEOMETRY
	# ==========================================================
	Blender.Draw.Label("Mesh Geometry:", row[0], y-30, 150, 20)

	Blender.Draw.BeginAlign()
	GLOBALS['faces_x'] = Blender.Draw.Number("X Faces", EVENT_MESH_CHANGE, row[0], y-50, 175, 20, GLOBALS['faces_x'].val, 0, 256, "Number of faces along the X-axis", toggle_button)
	GLOBALS['faces_y'] = Blender.Draw.Number("Y Faces", EVENT_MESH_CHANGE, row[0], y-70, 175, 20, GLOBALS['faces_y'].val, 0, 256, "Number of faces along the Y-axis", toggle_button)
   
	Blender.Draw.EndAlign()
	Blender.Draw.BeginAlign()

	GLOBALS['multires_levels'] = Blender.Draw.Number("subdivision levels", EVENT_MESH_CHANGE, row[0], y-100, 175, 20, GLOBALS['multires_levels'].val, 0, 256, "Number of mesh subdivisions (Corresponds to SL LOD)", toggle_button)

	GLOBALS['subdiv_type_catmull_clark'] = Blender.Draw.Toggle("Catmull-Clark", EVENT_SUBDIV_CATMULL, row[0], y-121, 100, 20, GLOBALS['subdiv_type_catmull_clark'].val,"Catmull-Clark", do_subdiv_type_sel)
	GLOBALS['subdiv_type_simple']        = Blender.Draw.Toggle("Simple",        EVENT_SUBDIV_SIMPLE, row[0]+100, y-121, 75, 20, GLOBALS['subdiv_type_simple'].val, "Simple", do_subdiv_type_sel)

	Blender.Draw.BeginAlign()
	addLodLabelRow(row[0], y-150)
	addLodRow("LOD3", row[0], y-170, GLOBALS['faces_x'].val, GLOBALS['faces_y'].val, 3, GLOBALS['multires_levels'].val+1, "Maximum Number of rendered faces (when object is close to camera)" )
	addLodRow("LOD2", row[0], y-190, GLOBALS['faces_x'].val, GLOBALS['faces_y'].val, 2, GLOBALS['multires_levels'].val+1, "First reduction of rendered faces (when object is near to camera)")
	addLodRow("LOD1", row[0], y-210, GLOBALS['faces_x'].val, GLOBALS['faces_y'].val, 1, GLOBALS['multires_levels'].val+1, "Secnd reduction of rendered faces (when object is further away from camera")
	addLodRow("LOD0", row[0], y-230, GLOBALS['faces_x'].val, GLOBALS['faces_y'].val, 0, GLOBALS['multires_levels'].val+1, "Minimum Number of rendered faces (when object is far away from camera")

	GLOBALS['clean_lod'] = Blender.Draw.Toggle("Clean LODs", EVENT_CLEAN_LOD, row[0], y-250, 175, 20, GLOBALS['clean_lod'].val,   "For non power of 2 facecounts: Ensure the object will use good LOD settings", toggle_button)

	Blender.Draw.EndAlign()
	
	# ==========================================================
	# MESH TYPE
	# ==========================================================
	Blender.Draw.Label("Mesh type:", row[1], y-30, 100, 20)			

	Blender.Draw.BeginAlign()
	GLOBALS['sculpt_type_sphere']   = Blender.Draw.Toggle("Sphere",   EVENT_SCULPT_TYPE_SPHERE,   row[1], y-50,  100, 18, GLOBALS['sculpt_type_sphere'].val,  "Spherical shaped object", do_sculpt_type_sel)
	GLOBALS['sculpt_type_torus']    = Blender.Draw.Toggle("Torus",    EVENT_SCULPT_TYPE_TORUS,    row[1], y-68,  100, 18, GLOBALS['sculpt_type_torus'].val,   "Torus shaped object",     do_sculpt_type_sel)
	GLOBALS['sculpt_type_plane']    = Blender.Draw.Toggle("Plane",    EVENT_SCULPT_TYPE_PLANE,    row[1], y-86,  100, 18, GLOBALS['sculpt_type_plane'].val,   "Plane object",            do_sculpt_type_sel)
	GLOBALS['sculpt_type_cylinder'] = Blender.Draw.Toggle("Cylinder", EVENT_SCULPT_TYPE_CYLINDER, row[1], y-104, 100, 18, GLOBALS['sculpt_type_cylinder'].val,"Cylinder shaped object",  do_sculpt_type_sel)
	GLOBALS['sculpt_type_hemi']     = Blender.Draw.Toggle("Hemi",     EVENT_SCULPT_TYPE_HEMI,     row[1], y-122, 100, 18, GLOBALS['sculpt_type_hemi'].val,    "Hemi shaped object",      do_sculpt_type_sel)
	Blender.Draw.EndAlign()

	# ==========================================================
	# BUILD STYLE
	# ==========================================================
	Blender.Draw.Label("Build style:", row[1], y-200, 100, 20)			
	Blender.Draw.BeginAlign()
	GLOBALS['build_mode_subsurf']  = Blender.Draw.Toggle("Subsurf",  EVENT_BUILD_MODE_SUBSURF , row[1], y-226, 100, 20, GLOBALS['build_mode_subsurf'].val, "subsurf (beginners, easy LOD)", do_build_mode_sel)
	GLOBALS['build_mode_multires'] = Blender.Draw.Toggle("Multires", EVENT_BUILD_MODE_MULTIRES, row[1], y-250, 100, 20, GLOBALS['build_mode_multires'].val,"multires (experts, high flexibility)", do_build_mode_sel)
	Blender.Draw.EndAlign()
	
	GLOBALS['button_ok']    = Blender.Draw.Button("OK", EVENT_OK, row[2], y-250, 25, 220,  "Create object", do_ok_sel)

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
