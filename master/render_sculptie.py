#!BPY

"""
Name: 'Bake Second Life Sculpties'
Blender: 245
Group: 'Render'
Tooltip: 'Bake Sculptie Maps on Active objects'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.35"
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
# --------------------------------------------------------------------------

#***********************************************
# Import modules
#***********************************************

import Blender
import sculpty

#***********************************************
# main
#***********************************************

def main():
	scene = Blender.Scene.GetCurrent()
	try:
		doFinal = scene.objects.active.properties["bake_final"]
		doFill = scene.objects.active.properties["bake_fill"]
		keepScale = scene.objects.active.properties["bake_scale"]
		keepCenter = scene.objects.active.properties["bake_center"]
		doClear = scene.objects.active.properties["bake_clear"]
		doProtect = scene.objects.active.properties["bake_protect"]
		doPreview = scene.objects.active.properties["bake_preview"]
		minR = scene.objects.active.properties["bake_min_r"]
		minG = scene.objects.active.properties["bake_min_g"]
		minB = scene.objects.active.properties["bake_min_b"]
		maxR = scene.objects.active.properties["bake_max_r"]
		maxG = scene.objects.active.properties["bake_max_g"]
		maxB = scene.objects.active.properties["bake_max_b"]
		doScaleRGB = scene.objects.active.properties["bake_scale_rgb"]
	except:
		doFinal = True
		doFill = True
		keepScale = False
		keepCenter = False
		doClear = True
		doProtect = True
		doPreview = True
		minR = minG = minB = 0
		maxR = maxG = maxB = 255
		doScaleRGB = True
	block = []
	doFinal = Blender.Draw.Create( doFinal )
	doFill = Blender.Draw.Create( doFill )
	keepScale = Blender.Draw.Create( keepScale )
	keepCenter = Blender.Draw.Create( keepCenter )
	doClear = Blender.Draw.Create( doClear )
	doProtect = Blender.Draw.Create( doProtect )
	doPreview = Blender.Draw.Create( doPreview )
	minR = Blender.Draw.Create( minR )
	maxR = Blender.Draw.Create( maxR )
	minG = Blender.Draw.Create( minG )
	maxG = Blender.Draw.Create( maxG )
	minB = Blender.Draw.Create( minB )
	maxB = Blender.Draw.Create( maxB )
	doScaleRGB = Blender.Draw.Create( doScaleRGB )
	block.append (( "Clear", doClear ))
	block.append (( "Keep Scale", keepScale ))
	block.append (( "Keep Center", keepCenter ))
	block.append (( "Fill Holes", doFill ))
	block.append (( "Finalise", doFinal ))
	block.append (( "Protect Map", doProtect ))
	block.append (( "With Preview", doPreview ))
	block.append (( " " ))
	block.append (( "   Color Range Adjustment" ))
	block.append (( "Min R:", minR, 0, 255 ))
	block.append (( "Max R:", maxR, 0, 255 ))
	block.append (( "Min G:", minG, 0, 255 ))
	block.append (( "Max G:", maxG, 0, 255 ))
	block.append (( "Min B:", minB, 0, 255 ))
	block.append (( "Max B:", maxB, 0, 255 ))
	block.append (( "Include in Size", doScaleRGB ))

	if Blender.Draw.PupBlock( "Sculptie Bake Options", block ):
		print "--------------------------------"
		time1 = Blender.sys.time()  #for timing purposes
		editmode = Blender.Window.EditMode()
		if editmode: Blender.Window.EditMode(0)
		Blender.Window.WaitCursor(1)
		# prepare for bake, set centers and create bounding box
		bb = sculpty.BoundingBox()
		bb.rgb.min = sculpty.XYZ( minR.val, minG.val, minB.val )
		bb.rgb.max = sculpty.XYZ( maxR.val, maxG.val, maxB.val )
		bb.rgb.update()
		for ob in scene.objects.selected:
			if sculpty.check( ob ):
				ob.properties["bake_final"] = doFinal.val
				ob.properties["bake_fill"] = doFill.val
				ob.properties["bake_scale"] = keepScale.val
				ob.properties["bake_center"] = keepCenter.val
				ob.properties["bake_clear"] = doClear.val
				ob.properties["bake_protect"] = doProtect.val
				ob.properties["bake_preview"] = doPreview.val
				ob.properties["bake_min_r"] = minR.val
				ob.properties["bake_min_g"] = minG.val
				ob.properties["bake_min_b"] = minB.val
				ob.properties["bake_max_r"] = maxR.val
				ob.properties["bake_max_g"] = maxG.val
				ob.properties["bake_max_b"] = maxB.val
				ob.properties["bake_scale_rgb"] = doScaleRGB.val
				if not keepCenter.val:
					#center new
					sculpty.set_center( ob )
				bb.add( ob )
		if keepScale.val:
			bb = bb.normalised()
		if keepCenter.val:
			bb = bb.centered()
		if bb.min == bb.max:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["No objects selected"] )
		# Good to go, do the bake
		for ob in scene.objects.selected:
			if sculpty.active( ob ):
				sculpty.bake_object( ob, bb, doClear.val )
				for image in sculpty.map_images( ob.getData( False, True) ):
					n = Blender.sys.splitext( image.name )
					if n[0] in ["Untitled", "Sphere_map", "Torus_map", "Cylinder_map", "Plane_map", "Hemi_map", "Sphere", "Torus","Cylinder","Plane","Hemi" ]:
						image.name = ob.name
					if doScaleRGB.val:
						image.properties['scale_x'] /= bb.rgb.scale.x
						image.properties['scale_y'] /= bb.rgb.scale.y
						image.properties['scale_z'] /= bb.rgb.scale.z
					if doFill.val:
						sculpty.fill_holes( image )
					if doFinal.val:
						sculpty.expand_pixels( image )
						if doProtect.val:
							if doPreview.val:
								sculpty.bake_preview( image )
							else:
								sculpty.clear_alpha( image )

		print "--------------------------------"
		print 'finished baking: in %.4f sec.' % ((Blender.sys.time()-time1))
		Blender.Redraw()
		if editmode: Blender.Window.EditMode(1)
		Blender.Window.WaitCursor(0)

if __name__ == '__main__':
	main()
