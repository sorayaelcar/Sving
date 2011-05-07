# SPACEHANDLER.VIEW3D.EVENT

# --------------------------------------------------------------------------
# Version: 1.2
# Release date: 11-feb-2010
# Tested on Blender: 249b
# Written by The Machinimatrix (gaia Clary)
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
from primstar.bake_sculpt_mesh_util import BakeApp


def bake():
    app = BakeApp()
    app.bake()

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
elif evt == Draw.RKEY:
    # Make sure that only the combination ALT-g works
    if ALTPressed:
        scn = bpy.data.scenes.active #get the current scene
        activeObject = scn.objects.active # get selected and thus the active object
        bake()
    else:
        return_it = True
else:
    #print "Let the 3D View itself process this event: %d with value %d" % (evt, val)
    return_it = True

# if Blender should not process itself the passed event:
if not return_it: Blender.event = None
