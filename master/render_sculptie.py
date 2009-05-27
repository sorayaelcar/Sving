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
	block = []
	doFinal = Blender.Draw.Create( True )
	keepScale = Blender.Draw.Create( False )
	doExpand = Blender.Draw.Create( False )
	keepCentre = Blender.Draw.Create( False )
	doClear = Blender.Draw.Create( True )
	doProtect = Blender.Draw.Create( True )
	doPreview = Blender.Draw.Create( True )
	minR = Blender.Draw.Create( 0 )
	maxR = Blender.Draw.Create( 255 )
	minG = Blender.Draw.Create( 0 )
	maxG = Blender.Draw.Create( 255 )
	minB = Blender.Draw.Create( 0 )
	maxB = Blender.Draw.Create( 255 )
	doScaleRGB = Blender.Draw.Create( True )
	block.append (( "Clear", doClear ))
	block.append (( "Keep Scale", keepScale ))
	block.append (( "Keep Center", keepCentre ))
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
		scene = Blender.Scene.GetCurrent()
		editmode = Blender.Window.EditMode()
		if editmode: Blender.Window.EditMode(0)
		Blender.Window.WaitCursor(1)
		# prepare for bake, set centers and create bounding box
		bb = sculpty.bounding_box()
		bb.rgb.min = sculpty.xyz( minR.val, minG.val, minB.val )
		bb.rgb.max = sculpty.xyz( maxR.val, maxG.val, maxB.val )
		bb.rgb.update()
		for ob in scene.objects.selected:
			if sculpty.check( ob ):
				if not keepCentre.val:
					#center new
					sculpty.set_center( ob )
				bb.add( ob )
		if keepScale.val:
			bb = bb.normalised()
		if keepCentre.val:
			bb = bb.centered()
		if bb.min == bb.max:
			Blender.Draw.PupBlock( "Sculptie Bake Error", ["No objects selected"] )
		# Good to go, do the bake
		for ob in scene.objects.selected:
			if sculpty.active( ob ):
				sculpty.bake_object( ob, bb, doClear.val, doFinal.val )
				for image in sculpty.map_images( ob.getData( False, True) ):
					n = Blender.sys.splitext( image.name )
					if n[0] in ["Untitled", "Sphere_map", "Torus_map", "Cylinder_map", "Plane_map", "Hemi_map", "Sphere", "Torus","Cylinder","Plane","Hemi" ]:
						image.name = ob.name
					if doScaleRGB.val:
						image.properties['scale_x'] /= bb.rgb.scale.x
						image.properties['scale_y'] /= bb.rgb.scale.y
						image.properties['scale_z'] /= bb.rgb.scale.z
					if doFinal.val and doProtect.val:
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
