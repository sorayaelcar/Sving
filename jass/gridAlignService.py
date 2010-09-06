# SPACEHANDLER.VIEW3D.EVENT

# --------------------------------------------------------------------------
# Version: 1.2
# Release date: 11-feb-2010
# Tested on Blender: 249b
# Written by The Machinimatrix (gaia Clary, Hussayn Salomon)
#
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
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------


import Blender, bpy, sys
from Blender import *


def doit(activeObject, gridx, gridy, gridz):

    #keep current edit-mode and temporary leave it
    in_editmode = Window.EditMode()
    Window.EditMode(0)

    # make new mesh (reuse the objectName)
    mesh = activeObject.getData(mesh=1)

    # =================================================================
    # Find the boundingBox (maybe there is a better function for this ?
    # =================================================================

    xmin = mesh.verts[0].co[0]
    xmax = mesh.verts[0].co[0]
    ymin = mesh.verts[0].co[1]
    ymax = mesh.verts[0].co[1]
    zmin = mesh.verts[0].co[2]
    zmax = mesh.verts[0].co[2]
    
    precision=10000
    
    for v in mesh.verts :           
        x=v.co[0]
        y=v.co[1]
        z=v.co[2]
        if x < xmin: xmin = x
        if x > xmax: xmax = x
        if y < ymin: ymin = y
        if y > ymax: ymax = y
        if z < zmin: zmin = z
        if z > zmax: zmax = z

    xmin = round(xmin*precision)
    xmax = round(xmax*precision)
    ymin = round(ymin*precision)
    ymax = round(ymax*precision)
    zmin = round(zmin*precision)
    zmax = round(zmax*precision)
    
    
    bbox  = [(xmax-xmin)/precision, (ymax-ymin)/precision, (zmax-zmin)/precision]
    print "Calculated bounding box : [",  bbox, "]"


    # =================================================================
    # Now align the vertices along the grid
    # =================================================================

    aligned = 0
    for v in mesh.verts :
        if v.sel == 1:
            aligned += 1
            v.co[0]=nearStep(round(v.co[0]*precision), xmin, xmax, gridx)/precision
            v.co[1]=nearStep(round(v.co[1]*precision), ymin, ymax, gridy)/precision
            v.co[2]=nearStep(round(v.co[2]*precision), zmin, zmax, gridz)/precision

    print "Aligned ", aligned, " vertices"
    Blender.Redraw()
    Window.EditMode(in_editmode)
    Blender.Redraw()

def nearStep(location, min, max, gridVertexCount):
    fullLength = max - min
    unitLength = fullLength / (gridVertexCount - 1 )
    percent    = ((location - min) / (max - min))
    result = round(percent * (gridVertexCount - 1 ))*unitLength;
    return (min + result)

# ==============================================================
# ==============================================================

evt = Blender.event
val = Blender.eventValue
qual = Blender.Window.GetKeyQualifiers()

ALTPressed   = (qual & Window.Qual.ALT) == Window.Qual.ALT
SHIFTPressed = (qual & Window.Qual.SHIFT) == Window.Qual.SHIFT
CTRLPressed  = (qual & Window.Qual.CTRL) == Window.Qual.CTRL

return_it = False

if evt == Draw.MOUSEX:
    if CTRLPressed and ALTPressed:
        print val
    return_it = True   #get rid of the mouse events (too many to handle)
elif evt == Draw.MOUSEY:
    if CTRLPressed and ALTPressed:
        print val
    return_it = True   #get rid of the mouse events (too many to handle)
elif evt == Draw.GKEY:
    # Make sure that only the combination ALT-g works
    if ALTPressed:
        scn = bpy.data.scenes.active #get the current scene
        activeObject = scn.objects.active # get selected and thus the active object
        doit(activeObject, 256, 256, 256)
    else:
        return_it = True
else:
    #print "Let the 3D View itself process this event: %d with value %d" % (evt, val)
    return_it = True

# if Blender should not process itself the passed event:
if not return_it: Blender.event = None
