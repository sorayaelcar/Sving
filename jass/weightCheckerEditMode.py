#!BPY
"""
Name: 'Check for Unweighted Verts'
Blender: 249
Group: 'Mesh'
Tooltip: 'Check Armature for unweighted vertices'
"""

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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

from Blender import Scene, Mesh, Window, Draw, Modifier, sys
import BPyMessages
import bpy

def find_unassigned_verts(ob, verbose=False):
    #print ob.getName()
    mesh = ob.getData(False,True)
    log = ""

    for modifier in ob.modifiers:
        if modifier.type == Modifier.Types.ARMATURE:
            #print "Processing armature ", modifier.name
            for v in mesh.verts:
                v.sel=False

            armatureObject = modifier[Modifier.Settings.OBJECT]
            armature = armatureObject.getData()
            for boneName in armature.bones.keys():
                verts = None
                try:
                    verts = mesh.getVertsFromGroup(boneName)
                except:
                    if verbose: log = log + "Info:" + modifier.name+"."+boneName+"has no associated vertex Group|"
                if verts != None:
                    #print boneName, len(verts)
                    for index in verts:
                        mesh.verts[index].sel=True

            unassigned_verts_count = 0
            for v in mesh.verts:
                if v.sel==False: unassigned_verts_count += 1
                v.sel= not v.sel
        
            if unassigned_verts_count > 0:
                log = log + "Err : The Armature " + modifier.name + " has " + str(unassigned_verts_count) + " unweighted vertices|"
            else:
                log = log + "Info: The Armature " + modifier.name + " has a clean weighted mesh|"

    if log == "":
        log = "Warn: No Armature found for " + ob.getName() + "|"
    return log
        
def main():
    
    # Gets the current scene, there can be many scenes in 1 blend file.
    sce = bpy.data.scenes.active
    
    # Get the active object, there can only ever be 1
    # and the active object is always the editmode object.
    ob_act = sce.objects.active
    
    if not ob_act or ob_act.type != 'Mesh':
        BPyMessages.Error_NoMeshActive()
        return 
    
    
    # Saves the editmode state and go's out of 
    # editmode if its enabled, we cant make
    # changes to the mesh data while in editmode.
    is_editmode = Window.EditMode()
    if is_editmode: Window.EditMode(0)
    
    Window.WaitCursor(1)
    t = sys.time()
    
    # Run the mesh editing function
    report = find_unassigned_verts(ob_act)
    
    # Restore editmode if it was enabled
    if is_editmode: Window.EditMode(1)

    if report != "":
        report = report + "!!! I have selected all affected verts. Please lookup your mesh !!!"
        text = "Report: %t|" + report +"|OK"
        Draw.PupMenu(text)  
    
    Window.WaitCursor(0)
    
    
# This lets you can import the script without running it
if __name__ == '__main__':
    main()