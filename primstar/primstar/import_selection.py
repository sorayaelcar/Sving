#!BPY

"""
Name: 'Preview selection as Sculpties'
Blender: 248
Group: 'Object'
Tooltip: 'Preview selection as Sculpties'
"""

__author__ = ["Gaia Clary"]
__url__ = ("Online Help, http://blog.machinimatrix.org")
__version__ = "1.0.0"
__bpydoc__ = """\

Copy suitable objects to corresponding sculpt meshes

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

#***********************************************
# Import modules
#***********************************************

try:
    import psyco
    psyco.full()
except:
    pass

import Blender
import os
from primstar.bake_sculpt_mesh_util import BakeApp, get_pixelsum, mesh_compare
from primstar import sculpty
from primstar.sculpty import XYZ, debug, obChildren, BoundingBox, new_from_map, set_map, flip_map_uv, is_inside_out, sculptify


#************************************************
# functions
#************************************************

def color_range(image):
    c = image.getPixelI(0,0)
    min = XYZ(c[0], c[1], c[2])
    max = XYZ(c[0], c[1], c[2])

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            c = image.getPixelI(x, y)
            if c[0] < min.x : min.x = c[0]
            if c[1] < min.y : min.y = c[1]
            if c[2] < min.z : min.z = c[2]
            if c[0] > max.x : max.x = c[0]
            if c[1] > max.y : max.y = c[1]
            if c[2] > max.z : max.z = c[2]
    color_range = max - min
    #print "min:", min
    #print "max:", max
    #bprint "dif:", color_range
    return color_range

def is_smooth(mesh):
    for f in mesh.faces:
        if f.smooth == False: return False
    return True
    
def make_smooth(mesh, smooth_state=True):
    for f in mesh.faces:
        f.smooth = smooth_state


def create_from_object(ob, offset):

    # Create the new sculptie:
    mesh = ob.getData(False, True)

    activeUV = mesh.activeUVLayer
    mesh.activeUVLayer = "sculptie"
    image = mesh.faces[0].image
    mesh.activeUVLayer = activeUV
    new_object = new_from_map(image, False, False)
    
    # Workaround for a bug in the object display.
    # Just jump to edit mode and then back to object mode.
    editmode = Blender.Window.EditMode()
    if not editmode:
       Blender.Window.EditMode(1)
    Blender.Window.EditMode(0)

    ## Copy mesh mode:
    me = new_object.getData(False,True)
    me.mode = mesh.mode

    bb = BoundingBox(ob, False)
    dim   = bb.getDim()

    ## Copy rotation:
    mat = ob.getMatrix()
    scale = mat.scalePart()
    rot_quat = mat.toQuat()
    rot = rot_quat.toMatrix().resize4x4().invert()

    dim = Blender.Mathutils.Vector ( dim.x, dim.y, dim.z )

    me.transform(rot)
    rot.invert()
    me.transform(rot)

    new_object.rot = ob.rot

    ## Copy setting of smoothness:
    if is_smooth(mesh):
        make_smooth(me)
            
    # Move location to offset.
    loc = ob.getLocation()
    loc = (loc[0] + offset.x,
           loc[1] + offset.y,
           loc[2] + offset.z)    
    new_object.setLocation(loc)

    # ==========================================
    # Copy scaling
    # ==========================================

    c_range = color_range(image)
    c_range.x = dim.x * 255 / c_range.x
    c_range.y = dim.y * 255 / c_range.y
    c_range.z = dim.z * 255 / c_range.z

    new_object.setSize( c_range.x, c_range.y, c_range.z )

    # ==========================================
    # Copy material settings
    materials = ob.getMaterials()
    if materials != None:
        print "Copy", len(materials),"materials"
        new_object.setMaterials(materials)
    me.materials = mesh.materials
    new_object.colbits = ob.colbits

    # update and cleanup
    me.update()

    if editmode:
       Blender.Window.EditMode(1)

    return new_object, is_inside_out(me)


def new_from_object(ob, image_dict, offset):
    mesh = ob.getData(False, True)
    name = ob.getName()

    activeUV = mesh.activeUVLayer
    mesh.activeUVLayer = "sculptie"
    image = mesh.faces[0].image
    mesh.activeUVLayer = activeUV
    
    log = ""
    if image == None:
        log = "Error: No Sculptmap assigned to [" + ob.getName() + "] (Object not copied)|"
        new_object = None
    else:
        other_object = image_dict.get(image.getName())
        if other_object != None:
            if mesh_compare(ob, other_object) == False:
               log = log + "Error: multiple usage of sculptmap [" + image.getName() + "] for differently shaped object["+ob.getName()+"]|"
            else:
               log = log + "Info: Sculptmap [" + image.getName() + "] shared between ["+ob.getName()+"] and ["+other_object.getName()+"]|"

        if get_pixelsum(image) == 0:
            log = log + "Error: No Sculptmap baked for [" + ob.getName() + "]  (Object not copied)|"
            new_object = None
        else:
            image_dict[image.getName()]=ob
            new_object, inside_out = create_from_object(ob,offset)
            #print "Check ", new_object.getName(), "for inside out ..."
            if inside_out:
                log = log + "Warn: [" + ob.getName() + "] has got flipped normals. Please rebake before exporting.|" 

    return new_object, log



def obChildren(ob):
    return [ob_child for ob_child in Blender.Object.Get() \
        if ob_child.parent == ob]


def new_from_children(parent, processed_objects, image_dict, offset):

    report = ""
    new_children = []
    all_children = []
    
    siblings = obChildren(parent)
    for ob in siblings:
        allready_processed_object = processed_objects.get(ob.getName())
        if allready_processed_object == None:
            processed_objects[ob.getName()] = ob
            ac, children, creport = new_from_children(ob, processed_objects, image_dict, offset)
            if creport != "":
                report = report + creport
            if sculpty.check(ob):
                #print "Copy from ", ob.getName() 
                new_object, log = new_from_object(ob,image_dict, offset)
                if new_object != None:
                    if len(children) > 0:
                        Blender.Redraw()
                        new_object.makeParent(children)
                        all_children.extend(ac)
                    new_object.select(False)
                    new_children.append(new_object)
                #else:
                #    print "Warn: copy of [", ob.getName(), "] failed."
            else:
                log = "Warn: Not a sculptie [" + ob.getName() + "]  (Object not copied)|"
    
            if log != "":
                print log
                report = report + log
    return all_children, new_children, report


def new_from_selection(scene, target_location, editmode):
    # Create the set BBox
    # Note: We take ALL selected objects into account for the BBox calculation.
    bbox = BoundingBox()

    # Selection contains all selected objects in scene
    # roots contains all selected root objects (objects which have no selected parent)
    selection = []
    roots     = {}
    for ob in scene.objects.selected:
        #print "Add ", ob.getName(), " to BBox"
        bbox.add(ob)
        selection.append(ob)

        key = ob.getName()
        if roots.get(key) == None:
            newRoot = ob
            parent = ob.getParent()
            while parent != None and parent.isSelected():
                key = parent.getName()
                if roots.get(key) != None:
                    #print "Found key", key, "In roots list"
                    newRoot = None
                    break
                else:
                    newRoot = parent
                    parent = newRoot.getParent()
                    #print "key", parent.getName(), "not in roots list"
            if newRoot != None:
                key = newRoot.getName()
                roots[key] = newRoot
                print "Added new root :", key

    # unselect all curently selected objects:
    for ob in selection:
        ob.select(False)

    source_location = bbox.getCollectionLocation()
    offset = target_location - source_location
    
    target_list = []
    report = "";

    #Create copies of all objects in selection (if appropriate)
    image_dict = {}
    
    processed_objects = {}
    for key in roots.iterkeys():
        print "Processing root ", key
        root = roots[key]
        if processed_objects.get(key) == None:
            processed_objects[key] = root
            all_children, new_children, log = new_from_children(root, processed_objects, image_dict, offset)
            if log != "":
                report = report + log
            if sculpty.check(root):
                #print "Copy from ", ob.getName() 
                new_root, log = new_from_object(root,image_dict, offset)
                if new_root != None:
                    new_root.select(False)
                    if len(new_children) > 0:
                        Blender.Redraw()
                        print "Add",len(new_children),"Children to root", new_root.getName()
                        new_root.makeParent(new_children)
                        target_list.extend(new_children)
                    target_list.append(new_root)
                #else:
                #    print "Warn: copy of [", ob.getName(), "] failed."
            else:
                log = "Warn: Not a sculptie [" + root.getName() + "]  (Object not copied)|"
    
            if log != "":
                print log
                report = report + log


    # get over a bug in blender that fails to set 
    # correct lighting after creating a sculptie.
    for ob in target_list:
        ob.select(True)
        Blender.Window.EditMode(1)
        Blender.Window.EditMode(0) 
        ob.select(False)

    for ob in target_list:
        ob.select(True)

    return report


#***********************************************
# main
#***********************************************

def main():

    Blender.Window.WaitCursor(1)
    editmode = Blender.Window.EditMode()
    if editmode:
        Blender.Window.EditMode(0)
    
    scene = Blender.Scene.GetCurrent()
    cpos = Blender.Window.GetCursorPos()
    target_location = XYZ(cpos[0], cpos[1], cpos[2])
    report = new_from_selection(scene, target_location, editmode)
    Blender.Redraw()
    
    if editmode:
        Blender.Window.EditMode(1)
    
    if report != "":
        text = "Preview Report %t|" + report +"|OK"
        Blender.Draw.PupMenu(text)  
    Blender.Window.WaitCursor(0)
    
if __name__ == '__main__':
    main()
           