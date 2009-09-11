#!BPY

"""
Name: 'Bake Second Life Sculpties'
Blender: 245
Group: 'Render'
Tooltip: 'Bake Sculptie Maps on Active objects'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.36"
__bpydoc__ = """\

Bake Sculptie Map

This script requires a square planar mapping. It bakes the local vertex
positions to the prim's sculptie map image.
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

#***********************************************
# Import modules
#***********************************************

import Blender
from primstar import sculpty

#***********************************************
# constants
#***********************************************

PROTECTION_NONE       = 0
PROTECTION_SIMPLE     = 1
PROTECTION_SILHOUETTE = 2
PROTECTION_IMAGE      = 3

EVENT_NONE = 0
EVENT_EXIT = 1
EVENT_REDRAW = 2

EVENT_INCLUDE_IN_SIZE = 10
EVENT_DO_SCALE        = 11
EVENT_KEEP_CENTER     = 12
EVENT_MAKE_FLIPABLE   = 13
EVENT_DO_CLEAR        = 14
EVENT_DO_FILL         = 15

EVENT_MAP_PROTECT              = 20
EVENT_PROTECT_TYPE_INVISIBLE   = 21
EVENT_PROTECT_TYPE_SILHOUETTE  = 22
EVENT_PROTECT_TYPE_IMAGE       = 23

EVENT_OK = 51
GLOBALS = {}

settings = {
			'doFinal':True,
			'doFill':True,
			'doCentre':False,
			'doClear':True,
			'doProtect':True,
			'doPreview':True,
			'minR':0,
			'maxR':255,
			'minG':0,
			'maxG':255,
			'minB':0,
			'maxB':255,
			'doScaleRGB':True
}


# ===================================================================
# This method presets the GLOBAL map from where the UIBlock and the 
# event handlers read the data
# ===================================================================
def create_gui_globals():

	# ====================================================
	# Preset the Window element values from the active object
	# ====================================================

	scene = Blender.Scene.GetCurrent()
	try:
		settings['doFinal']    = scene.objects.active.properties["ps_bake_final"]
		settings['doFill']     = scene.objects.active.properties["ps_bake_fill"]
		settings['keepScale']  = scene.objects.active.properties["ps_bake_scale"]
		settings['keepCenter'] = scene.objects.active.properties["ps_bake_center"]
		settings['doClear']    = scene.objects.active.properties["ps_bake_clear"]
		settings['doProtect']  = scene.objects.active.properties["ps_bake_protect"]
		settings['doPreview']  = scene.objects.active.properties["ps_bake_preview"]
		settings['minR']       = scene.objects.active.properties["ps_bake_min_r"]
		settings['minG']       = scene.objects.active.properties["ps_bake_min_g"]
		settings['minB']       = scene.objects.active.properties["ps_bake_min_b"]
		settings['maxR']       = scene.objects.active.properties["ps_bake_max_r"]
		settings['maxG']       = scene.objects.active.properties["ps_bake_max_g"]
		settings['maxB']       = scene.objects.active.properties["ps_bake_max_b"]
		settings['doScaleRGB'] = scene.objects.active.properties["ps_bake_scale_rgb"]
	except:
		settings['doFinal']    = True
		settings['doFill']     = True
		settings['keepScale']  = False
		settings['keepCenter'] = False
		settings['doClear']    = True
		settings['doProtect']  = True
		settings['doPreview']  = True
		settings['minR']       = 0
		settings['minG']       = 0
		settings['minB']       = 0
		settings['maxR']       = 255
		settings['maxG']       = 255
		settings['maxB']       = 255
		settings['doScaleRGB'] = True

	# ===========================================================
	# Create the drawing elements
	# ===========================================================

	GLOBALS['doFinal']       = Blender.Draw.Create( settings['doFinal'] )
	GLOBALS['doFill']        = Blender.Draw.Create( settings['doFill'] )
	GLOBALS['keepScale']     = Blender.Draw.Create( settings['keepScale'] )
	GLOBALS['keepCenter']    = Blender.Draw.Create( settings['keepCenter'] )
	GLOBALS['doClear']       = Blender.Draw.Create( settings['doClear'] )
	GLOBALS['doProtect']     = Blender.Draw.Create( settings['doProtect'] )
	
	GLOBALS['protect_type_simple']     = Blender.Draw.Create( settings['doPreview'] == False  )
	GLOBALS['protect_type_silhouette'] = Blender.Draw.Create( settings['doPreview'] == True   )

	GLOBALS['minR']        = Blender.Draw.Create( settings['minR'] )
	GLOBALS['maxR']        = Blender.Draw.Create( settings['maxR'] )
	GLOBALS['minG']        = Blender.Draw.Create( settings['minG'] )
	GLOBALS['maxG']        = Blender.Draw.Create( settings['maxG'] )
	GLOBALS['minB']        = Blender.Draw.Create( settings['minB'] )
	GLOBALS['maxB']        = Blender.Draw.Create( settings['maxB'] )
	GLOBALS['doScaleRGB']  = Blender.Draw.Create( settings['doScaleRGB'] )

	GLOBALS['mouseCoords'] = Blender.Window.GetMouseCoords()
	GLOBALS['event'] = EVENT_NONE


# =============================================
# Event handler for the toggle buttons
# =============================================
def do_toggle_button(event, val):
	GLOBALS['event'] = event

# =============================================
# Event handler for subdivision type selection
# =============================================
def do_protection_type_sel(event, val):
	GLOBALS['event'] = event
	GLOBALS['protect_type_simple'].val     = (event == EVENT_PROTECT_TYPE_INVISIBLE)
	GLOBALS['protect_type_silhouette'].val = (event == EVENT_PROTECT_TYPE_SILHOUETTE)

# ===============================================================
# The main drawing routine
# ===============================================================
def drawCreateBox():
	
	mouseCoords = GLOBALS['mouseCoords']
	x,y = mouseCoords
	x-=175

	row  = [x + 0, x + 165, x + 320, x+490]

	GLOBALS['event'] = EVENT_EXIT
	
	selectState=False;
	title = ""

	block = []
	title = "Sculptie Bake Options"
	Blender.Draw.Label(title, row[0], y, 345, 20)


	# =======================================================
	# Left popup block
	# =======================================================

	Blender.Draw.Label("Color Range Adjustment:", row[0], y-30, 150, 20)

	Blender.Draw.BeginAlign()

	x = Blender.Draw.Button("",    EVENT_NONE, row[0],    y-50, 30, 20)
	x = Blender.Draw.Button("Min", EVENT_NONE, row[0]+35, y-50, 55, 20)
	x = Blender.Draw.Button("Max", EVENT_NONE, row[0]+90, y-50, 55, 20)

	x = Blender.Draw.Button("R:", EVENT_NONE, row[0], y-70, 30, 20)
	GLOBALS['minR'] = Blender.Draw.Number("", EVENT_NONE, row[0]+35, y-70, 55, 20, GLOBALS['minR'].val, 0, 255)
	GLOBALS['maxR'] = Blender.Draw.Number("", EVENT_NONE, row[0]+90, y-70, 55, 20, GLOBALS['maxR'].val, 0, 255)

	x = Blender.Draw.Button("G:", EVENT_NONE, row[0], y-90, 30, 20)
	GLOBALS['minG'] = Blender.Draw.Number("", EVENT_NONE, row[0]+35, y-90, 55, 20, GLOBALS['minG'].val, 0, 255)
	GLOBALS['maxG'] = Blender.Draw.Number("", EVENT_NONE, row[0]+90, y-90, 55, 20, GLOBALS['maxG'].val, 0, 255)

	x = Blender.Draw.Button("B:", EVENT_NONE, row[0], y-110, 30, 20)
	GLOBALS['minB'] = Blender.Draw.Number("", EVENT_NONE, row[0]+35, y-110, 55, 20, GLOBALS['minB'].val, 0, 255)
	GLOBALS['maxB'] = Blender.Draw.Number("", EVENT_NONE, row[0]+90, y-110, 55, 20, GLOBALS['maxB'].val, 0, 255)

	GLOBALS['doScaleRGB'] = Blender.Draw.Toggle("Include in size",
						    EVENT_INCLUDE_IN_SIZE,
						    row[0], y-130,
						    145, 20,
						    GLOBALS['doScaleRGB'].val,
						    "in LSL script: correct rescaling due to color adjustment",
						    do_toggle_button)
	Blender.Draw.EndAlign()

	Blender.Draw.Label("UV-Map options", row[0], y-155, 150, 20)
	Blender.Draw.BeginAlign()
	GLOBALS['doClear'] = Blender.Draw.Toggle( "Clear map",
						   EVENT_DO_CLEAR,
						   row[0], y-175,
						   145, 20,
						   GLOBALS['doClear'].val,
						   "Remove all data from map before baking.",
						   do_toggle_button)

	GLOBALS['doFill'] = Blender.Draw.Toggle( "Fill holes",
						   EVENT_DO_FILL,
						   row[0], y-195,
						   145, 20,
						   GLOBALS['doFill'].val,
						   "Add missing faces otherwise rendered as pure black.",
						   do_toggle_button)
	Blender.Draw.EndAlign()


	# =======================================================
	# Right popup block
	# =======================================================

	Blender.Draw.Label("Map protection (alpha)", row[1], y-30, 150, 20)
	Blender.Draw.BeginAlign()

	GLOBALS['doProtect'] = Blender.Draw.Toggle( "Protect map",
			       EVENT_MAP_PROTECT,
			       row[1], y-50,
			       140, 20,
			       GLOBALS['doProtect'].val,
			       "Enable alpha mask protection of your sculptie. Hint enable F10 -> Format -> RGBA !",
			       do_toggle_button)

	if GLOBALS['doProtect'].val:
		GLOBALS['protect_type_simple'] = Blender.Draw.Toggle( "Transparent",
			       EVENT_PROTECT_TYPE_INVISIBLE,
			       row[1], y-70,
			       80,20,
			       GLOBALS['protect_type_simple'].val,
			       "Make image fully transparent. Hint: enable 'draw image with alpha' in UV-editor",
			       do_protection_type_sel)

		GLOBALS['protect_type_silhouette'] = Blender.Draw.Toggle( "Preview",
			       EVENT_PROTECT_TYPE_SILHOUETTE,
			       row[1]+80, y-70,
			       60,20,
			       GLOBALS['protect_type_silhouette'].val,
			       "Use front view silhouette as alpha mask.",
			       do_protection_type_sel)
	Blender.Draw.EndAlign()

	Blender.Draw.Label("Transformation", row[1], y-135, 120, 20)
	Blender.Draw.BeginAlign()
	GLOBALS['keepScale'] = Blender.Draw.Toggle("Keep Scale",
						 EVENT_DO_SCALE,
						 row[1], y-155,
						 140, 20,
						 GLOBALS['keepScale'].val,
						 "Maintain aspect ration. No rescale necessary (but reduces resolution)",
						 do_toggle_button)

	GLOBALS['keepCenter'] = Blender.Draw.Toggle( "Keep Center",
						    EVENT_KEEP_CENTER,
						    row[1], y-175,
						    140, 20,
						    GLOBALS['keepCenter'].val,
						    "With Keep Scale: ensure, that object center is preserved",
						    do_toggle_button)

	GLOBALS['doFinal'] = Blender.Draw.Toggle( "Finalize",
						   EVENT_MAKE_FLIPABLE,
						   row[1], y-195,
						   140, 20,
						   GLOBALS['doFinal'].val,
						   "Optimize sculpt-map for precise mirroring (caution with odd face numbers!)",
						   do_toggle_button)

	Blender.Draw.EndAlign()

	# =======================================================
	# OK block
	# =======================================================

	GLOBALS['button_ok']    = Blender.Draw.Button("OK", EVENT_OK, row[2], y-195, 25, 165,  "Create object", do_toggle_button)

def bake_sculptie():
		print "--------------------------------"
		startTime = Blender.sys.time()  #for timing purposes
		editmode  = Blender.Window.EditMode()
		if editmode: Blender.Window.EditMode(0)
		Blender.Window.WaitCursor(1)
		# prepare for bake, set centers and create bounding box
		bb = sculpty.BoundingBox()
		bb.rgb.min = sculpty.XYZ( GLOBALS['minR'].val, GLOBALS['minG'].val, GLOBALS['minB'].val )
		bb.rgb.max = sculpty.XYZ( GLOBALS['maxR'].val, GLOBALS['maxG'].val, GLOBALS['maxB'].val )
		bb.rgb.update()

		scene = Blender.Scene.GetCurrent()
		for ob in scene.objects.selected:
			if sculpty.check( ob ):
				ob.properties["ps_bake_final"]     = GLOBALS['doFinal'].val
				ob.properties["ps_bake_fill"]      = GLOBALS['doFill'].val
				ob.properties["ps_bake_scale"]     = GLOBALS['keepScale'].val
				ob.properties["ps_bake_center"]    = GLOBALS['keepCenter'].val
				ob.properties["ps_bake_clear"]     = GLOBALS['doClear'].val
				ob.properties["ps_bake_protect"]   = GLOBALS['doProtect'].val
				ob.properties["ps_bake_preview"]   = GLOBALS['protect_type_silhouette'].val == True
				ob.properties["ps_bake_min_r"]     = GLOBALS['minR'].val
				ob.properties["ps_bake_min_g"]     = GLOBALS['minG'].val
				ob.properties["ps_bake_min_b"]     = GLOBALS['minB'].val
				ob.properties["ps_bake_max_r"]     = GLOBALS['maxR'].val
				ob.properties["ps_bake_max_g"]     = GLOBALS['maxG'].val
				ob.properties["ps_bake_max_b"]     = GLOBALS['maxB'].val
				ob.properties["ps_bake_scale_rgb"] = GLOBALS['doScaleRGB'].val
				if not ob.properties["ps_bake_center"]:
					#center new
					sculpty.set_center( ob )
				bb.add( ob )
				if ob.properties["ps_bake_scale"]:
					bb = bb.normalised()
				if ob.properties["ps_bake_center"]:
					bb = bb.centered()
		# Good to go, do the bake
		success = False
		for ob in scene.objects.selected:
			if sculpty.active( ob ):
				if sculpty.bake_object( ob, bb, ob.properties["ps_bake_clear"] ):
					success = True
				for image in sculpty.map_images( ob.getData( False, True) ):
					n = Blender.sys.splitext( image.name )
					if n[0] in ["Untitled", "Sphere_map", "Torus_map", "Cylinder_map", "Plane_map", "Hemi_map", "Sphere", "Torus","Cylinder","Plane","Hemi" ]:
						image.name = ob.name
					if ob.properties["ps_bake_scale_rgb"]:
						if 'primstar' not in image.properties:
							image.properties['primstar'] = {}
						image.properties['primstar']['scale_x'] /= bb.rgb.scale.x
						image.properties['primstar']['scale_y'] /= bb.rgb.scale.y
						image.properties['primstar']['scale_z'] /= bb.rgb.scale.z
					if ob.properties["ps_bake_fill"]:
						sculpty.fill_holes( image )
					if ob.properties["ps_bake_final"]:
						sculpty.finalise( image )
						if ob.properties["ps_bake_protect"]:
							if ob.properties["ps_bake_preview"]:
								sculpty.bake_preview( image )
							else:
								sculpty.clear_alpha( image )

		print "--------------------------------"
		print 'finished baking: in %.4f sec.' % ((Blender.sys.time()- startTime))
		Blender.Redraw()
		if editmode: Blender.Window.EditMode(1)
		Blender.Window.WaitCursor(0)
		if not success:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["No objects selected"] )

# ===============================================================
# Main loop.
# Note: The UIBlock is redrawn with every mouse click, so that
# Toggle buttons are refreshed or made visible/invisible epending
# on the mesh type and build mode etc...
# The main loop terminates when the mouse clicks outside of the
# Window or when the mouse clicks on the OK button. If the OK
# button is clicked, the sculptie will be baked.
# ===============================================================
def main():
	create_gui_globals()
	GLOBALS['event'] = EVENT_REDRAW
	while GLOBALS['event'] != EVENT_EXIT and GLOBALS['event'] != EVENT_OK:
		Blender.Draw.UIBlock( drawCreateBox, 0 )
	if GLOBALS['event'] == EVENT_OK:
		bake_sculptie()

if __name__ == '__main__':
	main()
