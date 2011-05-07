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
from Blender import Image

import os, math, string
import tkFileDialog
from primstar import sculpty
from Tkinter import *
from primstar import gui
from primstar.sculpty import sculptify, need_rebake, set_map, create_new_image

#***********************************************
# constants
#***********************************************

SCRIPT = 'render_sculptie_test'
BAKE_REGISTRY = 'PrimstarBake'
CREATE_REGISTRY = 'PrimstarAdd'
LABEL = '%s - Bake sculpt meshes' % (sculpty.LABEL)


#***********************************************
# bake settings
#***********************************************

bake_settings = Blender.Registry.GetKey(BAKE_REGISTRY, True)
if bake_settings == None:
    bake_settings = {}
default_bake_settings = {
        'keep_center': False,
        'keep_scale': False,
        'keep_seams': True,
        'optimize_resolution': True,
        'auto_correct': True,
        'clear': True,
        'fill': True,
        'finalise': True,
        'range_min': sculpty.XYZ(0, 0, 0),
        'range_max': sculpty.XYZ(255, 255, 255),
        'range_scale': True,
        'alpha': 2,
        'alpha_file': None,
        'save': True}


create_settings = Blender.Registry.GetKey(CREATE_REGISTRY, True)
if create_settings == None:
    create_settings = {}
default_create_settings = {
        'x_faces': 8,
        'y_faces': 8,
        'levels': 2,
        'subdivision': 1,
        'sub_type': 1,
        'clean_lods': True,
        'radius': 0.25,
        'shape_name': "Sphere",
        'shape_file': None,
        'quads': 1,
        'save': True}
for key, value in default_create_settings.iteritems():
    if key not in create_settings:
        create_settings[key] = value
    elif create_settings[key] == None:
        create_settings[key] = value



#***********************************************
# classes
#***********************************************


class BakeApp:

    def __init__(self):

        # Read from repository
        bake_settings = Blender.Registry.GetKey(BAKE_REGISTRY, True)
        if bake_settings == None:
            bake_settings = {}
        for key, value in default_bake_settings.iteritems():
            if key not in bake_settings:
                bake_settings[key] = value
            elif bake_settings[key] is None:
                bake_settings[key] = value
            #else:
            #    print "Got setting from repo:", key,value
                    
        # ==========================================
        # Settings
        # ==========================================
        #print "bake_sculpt_mesh_util(): Setting up BakeApp environment"
        self.keep_center         = bake_settings['keep_center']
        self.keep_scale          = bake_settings['keep_scale']
        self.keep_seams          = bake_settings['keep_seams']
        self.optimize_resolution = bake_settings['optimize_resolution']
        self.auto_correct        = bake_settings['auto_correct']
        self.clear               = bake_settings['clear']
        self.fill                = bake_settings['fill']
        self.finalise            = bake_settings['finalise']
        self.range_min_r         = bake_settings['range_min'].x
        self.range_min_g         = bake_settings['range_min'].y
        self.range_min_b         = bake_settings['range_min'].z
        self.range_max_r         = bake_settings['range_max'].x
        self.range_max_g         = bake_settings['range_max'].y
        self.range_max_b         = bake_settings['range_max'].z
        self.range_scale         = bake_settings['range_scale']
        self.alpha               = bake_settings['alpha']
        self.alpha_filename      = bake_settings['alpha_file']
        self.update_file()
        self.save_settings       = bake_settings['save']
        self.save_defaults       = False

        # Optimization makes only sense when in multi bake mode            
        self.sculptie_counter = 0
        scene = Blender.Scene.GetCurrent()
        for ob in scene.objects.selected:
            if sculpty.check(ob):
                self.sculptie_counter += 1
        self.activeObject = scene.objects.active
        if self.sculptie_counter == 1:
            self.optimize_resolution = False
            
    def bake(self):
        #print "bake_sculpt_mesh_util(): Baker started"
        startTime = Blender.sys.time()  #for timing purposes

        # We must bake in Object Mode (contraint imposed by blender)
        editmode = Blender.Window.EditMode()
        #print "Using editmode ... ", editmode
        Blender.Window.WaitCursor(1)
        if editmode:
            Blender.Window.EditMode(0)

        # prepare for bake, set centers and create bounding box
        bb = sculpty.BoundingBox(local=True)
        bb.rgb.min = sculpty.XYZ(
                self.range_min_r,
                self.range_min_g,
                self.range_min_b)
        bb.rgb.max = sculpty.XYZ(
                self.range_max_r,
                self.range_max_g,
                self.range_max_b)
        bb.rgb.update()

        
        scene = Blender.Scene.GetCurrent()
        if not self.keep_center:
            sculpty.set_selected_object_centers(scene)

        selection = []
        selection.extend(scene.objects.selected)
        for ob in selection:
            if sculpty.check(ob):
                bb.add(ob)            
        if self.keep_scale:
            bb = bb.normalised()
        if self.keep_center:
            bb = bb.centered()
        # Good to go, do the bake
        success = False
        image = None
        a = self.alpha
        if a == 3:
            alpha_image = Blender.Image.Load(self.alpha_filename)

        print "do_optimize is set to:", self.optimize_resolution
        image_dict = {}
        log = ""
        number_of_bake_candidates = len(selection)
        success = False
        for ob in selection:
            Blender.Window.WaitCursor(1)
            can_bake, reassigned_sculptmap, image, lg = check_for_bake(ob, image_dict, self.auto_correct)
            is_active = sculpty.active(ob)
            log = log + lg
            print "Object", ob.getName(), "can bake:",can_bake, "is active:", is_active
            if can_bake and is_active:

                if sculpty.bake_object(ob, bb, self.clear,
                            self.keep_seams, self.keep_center, self.optimize_resolution):
                    if need_rebake(ob, self.auto_correct):
                        if self.auto_correct:
                            sculpty.bake_object(ob, bb, self.clear,
                                self.keep_seams, self.keep_center, self.optimize_resolution)
                            log = log + "Info: Rebaked ob["+ob.getName()+"]. (reason: flipped vertex normals) |"
                            #print "rebake done"
                        else:
                            log = log + "Warn: ob["+ob.getName()+"] has flipped vertex normals. Please check for inside/out|"

                    success = success or True
                
                for image in sculpty.map_images(ob.getData(False, True)):
                    n = Blender.sys.splitext(image.name)
                    print "Baking [", n[0], "]"
                    if n[0] in ["Untitled", "Sphere_map", "Torus_map",
                            "Cylinder_map", "Plane_map", "Hemi_map",
                            "Sphere", "Torus", "Cylinder", "Plane", "Hemi"]:
                        image.name = ob.name
                    if self.range_scale:
                        if 'primstar' not in image.properties:
                            image.properties['primstar'] = {}
                        image.properties['primstar']['scale_x'] /= bb.rgb.scale.x
                        image.properties['primstar']['scale_y'] /= bb.rgb.scale.y
                        image.properties['primstar']['scale_z'] /= bb.rgb.scale.z
                    if self.fill:
                        sculpty.fill_holes(image)
                    if self.finalise:
                        sculpty.finalise(image)
                        if a == 2:
                            sculpty.bake_preview(image)
                        elif a == 1:
                            sculpty.clear_alpha(image)
                        elif a == 3:
                            sculpty.set_alpha(image, alpha_image)
                    if image.packed:
                        image.pack()
                    image.glFree()
        if self.activeObject != None:
            self.activeObject.select(True)
        if editmode:
            #print "Return to edit mode now ..."
            Blender.Window.EditMode(1)
        else:
            #print "Return to object mode now ..."
            if success and number_of_bake_candidates == 1:
                #print "stop by in edit mode"
                Blender.Window.EditMode(1)
                Blender.Redraw()
                Blender.Window.EditMode(0)

        for ob in selection:
            ob.select(True)
            
        if log != "":
            text = "Bake Report %t|" + log +"|OK"
            #print text
            Blender.Draw.PupMenu(text)  
        #Blender.Window.WaitCursor(0)
        #print "release cursor 2"
        Blender.Redraw()

        if success:
            gui.debug(1, 'finished baking: in %.4f sec.' % \
                    ((Blender.sys.time() - startTime)))
        else:
            gui.debug(0, 'bake failed after %.4f sec.' % \
                    ((Blender.sys.time() - startTime)))

    def set_file(self):
        self.master.withdraw()
        filename = tkFileDialog.askopenfilename(
                initialdir='~',
                title='Select a sculpt map',
                parent=self.master,
                filetypes=[
                        ('targa', '*.tga'),
                        ('bmp', '*.bmp'),
                        ('png', '*.png'),
                        ('all files', '.*')])
        self.alpha_filename = filename
        if not filename:
            self.alpha.set(2)
        else:
            self.alpha.set(3)
        self.update_file()

    def set_alpha(self):
        if not self.alpha_filename:
            self.master.mouse_exit += 1 #hack to stop early exit
            self.set_file()

    def update_file(self):
        if self.alpha_filename == None:
            self.alpha_file = "File"
        else:
            if not os.path.exists(self.alpha_filename):
                self.alpha_file="File"
            else:
                self.alpha_file = self.alpha_filename.split(os.sep)[-1]


class SculptieDefault:

    def __init__(self, shapename):

        # ==========================================
        # Settings frame
        # ==========================================

        self.shape_name = shapename
        self.shape_file = None
        
        # ==========================================
        # Geometry section
        # ==========================================

        self.x_faces    = create_settings['x_faces']
        self.y_faces    = create_settings['y_faces']
        self.radius     = create_settings['radius']
        self.clean_lods = create_settings['clean_lods']
        
        # ==========================================
        # Subdivision section
        # ==========================================

        self.levels      = create_settings['levels']
        self.sub_type    = create_settings['sub_type']
        self.subdivision = create_settings['subdivision']

        # ==========================================
        # Mesh Type Selection
        # ==========================================

        self.quads = create_settings['quads']
        
    def update_info(self, event=None):
        s, t, w, h, clean_s, clean_t = sculpty.map_size(self.x_faces,
                self.y_faces, self.levels)

    def add(self):
        Blender.Window.WaitCursor(1)
        editmode = Blender.Window.EditMode()
        if editmode:
            Blender.Window.EditMode(0)
        name = self.shape_name
        basename = name.split(os.sep)[-1]
        if self.shape_file:
            baseimage = Blender.Image.Load(self.shape_file)
            sculpt_type = sculpty.map_type(baseimage)
        else:
            sculpt_type = name.upper()
            baseimage = None
        gui.debug(11,
                "Add sculptie (%s) of type %s" % (name, sculpt_type),
                "add_mesh_sculpt_mesh")
        scene = Blender.Scene.GetCurrent()
        for ob in scene.objects:
            ob.sel = False
        try:
            mesh = sculpty.new_mesh(basename, sculpt_type,
                    self.x_faces, self.y_faces,
                    self.levels, self.clean_lods,
                    min(0.5, max(self.radius, 0.05)))
            s, t, w, h, clean_s, clean_t = sculpty.map_size(self.x_faces,
                    self.y_faces, self.levels)
            image = create_new_image(basename, w, h, 32)
            sculpty.bake_lod(image)
            ob = scene.objects.new(mesh, basename)
            mesh.flipNormals()
            ob.sel = True
            ob.setLocation(Blender.Window.GetCursorPos())
            sculpty.set_map(mesh, image)
            if baseimage:
                sculpty.update_from_map(mesh, baseimage)
            if self.levels:
                if self.sub_type:
                    mods = ob.modifiers
                    mod = mods.append(Blender.Modifier.Types.SUBSURF)
                    mod[Blender.Modifier.Settings.LEVELS] = self.levels
                    mod[Blender.Modifier.Settings.RENDLEVELS] = self.levels
                    mod[Blender.Modifier.Settings.UV] = False
                    if not self.subdivision:
                        mod[Blender.Modifier.Settings.TYPES] = 1
                else:
                    mesh.multires = True
                    mesh.addMultiresLevel(self.levels,
                        ('simple', 'catmull-clark')[self.subdivision])
                    mesh.sel = True
            if self.subdivision:
                for f in mesh.faces:
                    f.smooth = True
            # adjust scale for subdivision
            minimum, maximum = sculpty.get_bounding_box(ob)
            x = 1.0 / (maximum.x - minimum.x)
            y = 1.0 / (maximum.y - minimum.y)
            try:
                z = 1.0 / (maximum.z - minimum.z)
            except:
                z = 0.0
            if sculpt_type == "TORUS Z":
                z = min(0.5, max(self.radius, 0.05)) * z
                print "Create a Torus Z with radius ", z
            elif sculpt_type == "TORUS X":
                x = min(0.5, max(self.radius, 0.05)) * x
                print "Create a Torus X with radius ", x
            elif sculpt_type == "HEMI":
                z = 0.5 * z
            tran = Blender.Mathutils.Matrix([x, 0.0, 0.0], [0.0, y, 0.0],
                    [0.0, 0.0, z]).resize4x4()
            mesh.transform(tran)
            # align to view
            try:
                quat = None
                if Blender.Get('add_view_align'):
                    quat = Blender.Mathutils.Quaternion(
                            Blender.Window.GetViewQuat())
                    if quat:
                        mat = quat.toMatrix()
                        mat.invert()
                        mat.resize4x4()
                        ob.setMatrix(mat)
            except:
                pass
        except RuntimeError:
            raise
        Blender.Window.EditMode(editmode)
        Blender.Window.WaitCursor(0)
        return ob


#***********************************************
# functions
#***********************************************

def is_negative_scaled(object):
    try:
        size = object.getSize()
        negativeScales = 0
        for v in size:
           if v < 0:
               negativeScales += 1            
        result = negativeScales % 2 == 1
    except:
        print "Object ", object, "has no size. ignore"
        result = False
    return result

def is_mirrored_by_scale(s1,s2):
    n1 = (s1[0]/abs(s1[0]), s1[1]/abs(s1[1]), s1[2]/abs(s1[2]))
    n2 = (s2[0]/abs(s2[0]), s2[1]/abs(s2[1]), s2[2]/abs(s2[2]))
    return (n1[0] != n2[0]) or (n1[1] != n2[1]) or (n1[2] != n2[2])

#************************************************
# Check if 2 objects have equal meshes
# return True if objects are equal
# otherwise returns False
# Note: The comparator takes also the 
# modifier stack into account
#************************************************
def mesh_compare(ob1, ob2):
    m1 = Blender.Mesh.New()
    m2 = Blender.Mesh.New()
    m1.getFromObject(ob1, 0, 1)
    m2.getFromObject(ob2, 0, 1)
    size = ob1.getSize()
    mp   = (size[0]/256, size[1]/256, size[2]/256 )
    min_dist_squared = mp[0] * mp[0] + mp[1] * mp[1] + mp[2] * mp[2]

    if is_mirrored_by_scale(ob1.getSize(),ob2.getSize()):
        print "Objects are mirrored by scale:", ob1.name, ob2.name
        return False;

    # ==========================
    #print "test on equal vertex count"
    # ==========================
    l1 = len(m1.verts)
    l2 = len(m2.verts)
    if l1 != l2:
        print "Meshes differ in vertex count ", ob1.name, ob2.name
        return False
    #else:
    #    print "Meshes vertex count is: ", l1

    # ================================
    # print "test ", ob1.name, ", ", ob2.name, " on equal vertex positions:"
    # ================================  

    for v1 in m1.verts:
        v2 = m2.verts[v1.index]
        if v1.co != v2.co:
            dist = (v1.co[0]-v2.co[0], v1.co[1]-v2.co[1], v1.co[2]-v2.co[2])
            dist_squared = dist[0]*dist[0] + dist[1]*dist[1] + dist[2]*dist[2]
            if dist_squared > min_dist_squared:
	            print "Meshes differ in vertex location ", ob1.name, ob2.name
	            print "Meshes differ in vertex location ", v1.co,    v2.co
	            print "Meshes vertex distance is        ", dist_squared, min_dist_squared
	            return False
        #else:
        #print v1.co, v2.co

    #print "Meshes are equal ", ob1.name, ob2.name
    return True

def mirror_direction_name(name,source,target):
    result = None
    y = string.lower(name)
    index = string.find(y,source)
    if index == -1:
        s=target
        target=source
        source=s
        index = string.find(y,source)
    
    if index != -1:
        ms = name[index:index+len(source)]
        ml  = target
        print ms
        if ms[0] != ml[0]:
            s=string.swapcase(ml[0])
            ml = s + ml[1:]
        print ml
        result = string.replace(name,ms,ml)
    
    return result
    

def mirror_name(name):
    result = mirror_direction_name(name,"right", "left")
    if result is not None: return result
    result = mirror_direction_name(name,"top", "bottom")
    if result is not None: return result
    result = mirror_direction_name(name,"front", "back")
    return result

def adjust_image_name(ob,image):
    new_image_name = mirror_name(image.getName())
    if new_image_name == None:
        new_image_name = mirror_name(ob.getName())
        if new_image_name == None:
            new_image_name = image.getName()
    image.setName(new_image_name)

def assign_new_image(ob, could_be_mirror=False):
        mesh = ob.getData(False, True)
        name = ob.getName()

        activeUV = mesh.activeUVLayer
        mesh.activeUVLayer = "sculptie"
        image = mesh.faces[0].image
        try:
           width  = image.getSize()[0]
           height = image.getSize()[1]
        except:
           if image == None:
               print "No image data available for object", name
           else:
               print "Can not get image data from object", name,"image",image.getName()
           print "Need to Resculptify object ..."
           sculptify(ob, force_new_image=True)
           mesh = ob.getData(False, True)
           image = mesh.faces[0].image
           #print "image",sel.name,"is assigned to ", ob.getName()
           #print "Resculptify created image", image.name, "of type", image.source
           if could_be_mirror:
               adjust_image_name(ob,image)
           return image

        object_name = ob.getName().split(os.sep)[-1]
        new_image = create_new_image(object_name, width, height, 32)
        selected_verts = mesh.verts.selected()
        mesh.sel = True
        set_map(mesh, new_image)    
        mesh.sel = False
        for i in selected_verts:
            mesh.verts[i].sel=1
        mesh.update()
        mesh.activeUVLayer = activeUV
        if could_be_mirror:
            adjust_image_name(ob,new_image)
        print "assign_new_image()ob.name:",ob.name,"new_image:",new_image.name
        return new_image


def get_pixelsum(image):
    pixelsum = 0
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pixel = image.getPixelI(x, y)
            pixelsum += pixel[0] + pixel[1] + pixel[2]
    return pixelsum

def check_for_bake(ob, image_dict, auto_correct=True):
    #print "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
    #print "check_for_bake() object:", ob.getName()
    can_bake             = False
    reassigned_sculptmap = False
    
    mesh = ob.getData(False, True)
    name = ob.getName()

    log = ""

    try:
        activeUV = mesh.activeUVLayer
    except:
        msg = "Err : Can't bake [" + name+ "] (no UVLayer found in mesh)"
        log = msg + "|"
        print msg
        return False, False, None, log

    try:
        mesh.activeUVLayer = "sculptie"
    except:
        msg = "Err : Can't bake [" + name+ "] (\"sculptie\" layer not found in mesh)"
        log = msg + "|"
        print msg
        return False, False, None, log
         
    image = mesh.faces[0].image
    mesh.activeUVLayer = activeUV
    #if image == None:
    #    print "check_for_bake() image : None"
    #else:
    if image != None:
        #print "check_for_bake() image :", image.name
        image_name = image.getName()
        file_name  = image.getFilename()
        if image.source != Blender.Image.Sources['GENERATED'] and not image.packed and not os.path.exists(file_name):
            msg = ": ["+ob.getName()+"]: image "+image_name+"(" + file_name + ") not found"
            if auto_correct:
                msg = "Fix : ["+ob.getName()+"]: image file not found ("+file_name+"). Recreate with 'sculptify object'"
                log = log + msg +"|"
            else:
                msg = "Err " + msg
                log = log + msg + "|"
            print msg    
            image=None
        else:
            try:
                size = image.getSize()
            except:
                msg = " ["+ob.getName()+"]: image "+image_name+" has no size info."
                if auto_correct:
                    msg = "Fix :" + msg
                else:
                    msg = "Err :" + msg
                log = log + msg +"|"
                print msg
                image=None

    if image == None:
        if auto_correct:
            image = assign_new_image(ob)
            reassigned_sculptmap = True
            can_bake = True
            image_dict[image.name]=ob
            msg = "Fix : ["+ob.getName()+"]: assigned sculptmap to new image [" + image.name + "]"
            log = log + msg + "|"
            print msg
            #print "Added image", image.name, "to image_dict"
        else:
            msg = "Err : ob["+ob.getName()+"]: no image found (Can't bake)"
            log = log + msg + "|"
            can_bake = False

    else:
        #print "check_for_bake: testing on image ", image.name
        other_object = image_dict.get(image.name)
        if other_object != None:
            #print "Image shared:", image.name, "between objects", ob.getName(),"<->",other_object.getName()
            if mesh_compare(ob, other_object) == False:
                if auto_correct:
                    new_image = assign_new_image(ob)
                    msg = "Warn: ["+ob.getName()+"]: reassigned sculptmap from [" + image.name + "] to [" + new_image.name+ "]"
                    reassigned_sculptmap = True
                    image = new_image
                    image_dict[image.name]=ob
                    #print "Added image ", image.name, " to image_dict"
                else:
                    msg = "Info: Sculptmap [" + image.name + "] shared between ["+ob.getName()+"] and ["+other_object.getName()+"]"
            else:
                msg = "Info: Sculptmap [" + image.name + "] shared between ["+ob.getName()+"] and ["+other_object.getName()+"]"
            log = log + msg + "|"
            print msg
        else:
            image_dict[image.name]=ob
            #print "Added image ", image.name, " to image_dict"

        can_bake = True
        #if is_black_sculptie(ob):
        #   log = log + "Info: Negative scale values for [" + ob.getName() + "] need to flip the UV-map |"

    if can_bake and auto_correct:
        #print "Check for mirror along x ..."
        #print "is negative scaled = ", is_negative_scaled(ob)
        if ob.getParent() == None and is_negative_scaled(ob):
            size = ob.getSize()
            if size[0] < 0:
                size = (-size[0], -size[1], size[2])
                rot  = ob.rot
                rot  = (rot[0], rot[1], rot[2]+math.pi)
                ob.setEuler(rot)
                ob.setSize(size)
                log = log + "Info: [" + ob.getName() + "]: mirror along x replaced by rotation along Z and mirror along y|"

    #print log
    #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    return can_bake, reassigned_sculptmap, image, log
        