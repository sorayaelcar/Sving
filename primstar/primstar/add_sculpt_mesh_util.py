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

#***********************************************
# Import modules
#***********************************************

try:
    import psyco
    psyco.full()
except:
    pass

import Blender

from primstar import sculpty
import os
from Tkinter import *
import tkFileDialog
from primstar import gui
from sculpty import create_new_image
#***********************************************
# constants
#***********************************************

LABEL = "%s - Add sculpt mesh" % (sculpty.LABEL)
SCRIPT = 'add_mesh_gui_test'
REGISTRY = 'PrimstarAdd'

#***********************************************
# settings
#***********************************************

settings = Blender.Registry.GetKey(REGISTRY, True)
if settings == None:
    settings = {}
default_settings = {
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
for key, value in default_settings.iteritems():
    if key not in settings:
        settings[key] = value
    elif settings[key] == None:
        settings[key] = value


#***********************************************
# classes
#***********************************************

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

        self.x_faces    = settings['x_faces']
        self.y_faces    = settings['y_faces']
        self.radius     = settings['radius']
        self.clean_lods = settings['clean_lods']
        
        # ==========================================
        # Subdivision section
        # ==========================================

        self.levels      = settings['levels']
        self.sub_type    = settings['sub_type']
        self.subdivision = settings['subdivision']

        # ==========================================
        # Mesh Type Selection
        # ==========================================

        self.quads = settings['quads']
        
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
            print "add_sculpt_mesh_util: Packed image", image.getName()
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

        