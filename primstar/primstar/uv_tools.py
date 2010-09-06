# --------------------------------------------------------------------------
#
# This module contains a set of common used utility functions for uv editing
#
# --------------------------------------------------------------------------

__author__ = ["Gaia Clary", "Domino Marama"]
__url__ = ("http://www.machinimatrix.org", "http://dominodesigns.info")
__version__ = "1.0"

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) Machinimatrix.org
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
from math import atan2, pi, sin
from uvcalc_follow_active_coords import extend

#***********************************************
# constants
#***********************************************

low_u = 0.25
high_u = 0.75


def scale_map_uv(ob, doRotate):
    mesh = ob.getData(mesh=1)
    # -------------------------------
    #determine the size of the uv-map
    # -------------------------------
    uv = mesh.faces[0].uv
    umin = umax = uv[0][0]
    vmin = vmax = uv[0][1]

    for face in mesh.faces:
        for uv in face.uv:
                if uv[0] < umin:
                    umin = uv[0]
                if uv[0] > umax:
                    umax = uv[0]
                if uv[1] < vmin:
                    vmin = uv[1]
                if uv[1] > vmax:
                    vmax = uv[1]


    # --------------------------------------------------------------
    #make uv-map rectangular and rotate by -90 degrees
    #I still do not know, where this 90 degree rotation comes from.
    # --------------------------------------------------------------
    for face in mesh.faces:
        for uv in face.uv:
            normalise(uv, umin, umax, vmin, vmax, doRotate)


def normalise(fco, umin, umax, vmin, vmax, doRotate):
    x = fco[0]
    y = fco[1]
    if doRotate == 1:
        fco[0] = 1 - ((y - vmin) / (vmax - vmin))
        fco[1] = ((x - umin) / (umax - umin))
    else:
        fco[0] = ((x - umin) / (umax - umin))
        fco[1] = ((y - vmin) / (vmax - vmin))


def add_map_uv(ob, doRotate):
    if ob == None or ob.type != 'Mesh':
        Blender.Draw.PupMenu('ERROR: No mesh object.')
        return

    # Toggle Edit mode
    edit_mode = Blender.Window.EditMode()
    if edit_mode:
        Blender.Window.EditMode(0)

    #print "uv_tools.add_map_uv(ob,%s)" % (doRotate)
    me = ob.getData(mesh=1)
    me.sel = 1
    me.addUVLayer("sculptie")
    me.activeFace = 0
    
    try:
        extend(1, ob)
        scale_map_uv(ob, doRotate)
    except:
        eac_unwrap(ob, True)
    Blender.Window.EditMode(edit_mode)


def eac_unwrap(ob, all_faces=False):
    if ob.type == 'Mesh':
        mesh = ob.getData(mesh=1)
        if all_faces:
            face_list = [f for f in mesh.faces]
        else:
            face_list = [f for f in mesh.faces if f.sel]
        if not face_list:
            return
        vq = Blender.Mathutils.Quaternion(Blender.Window.GetViewQuat())
        for f in face_list:
            uvmap = []
            u_check1 = False
            u_check2 = False
            for v in f.verts:
                tv = vq * v.co
                x = tv.x
                y = tv.y
                z = tv.z
                ax = atan2(x, z)
                u = (1.0 + (ax / pi)) / 2.0
                ay = sin(atan2(y, z))
                v = (1.0 + ay) / 2.0
                if u <= low_u:
                    u_check1 = True
                if u >= high_u:
                    u_check2 = True
                uvmap.append(Blender.Mathutils.Vector(u, v))
            # crude face correction, needs improving
            if u_check1 and u_check2:
                for n in xrange(len(uvmap)):
                    if uvmap[n][0] > high_u:
                        uvmap[n][0] = 1.0 - uvmap[n][0]
            f.uv = uvmap


def snap_to_pixels(mesh, pow_two=False, image=None):
    editmode = Blender.Window.EditMode()
    if editmode:
        Blender.Window.EditMode(0)
    for f in mesh.faces:
        if f.image:
            if image == None or image == f.image:
                w, h = f.image.size
                for i in range(len(f.uv)):
                    if f.uvSel[i]:
                        u = int(round(f.uv[i][0], 6) * w)
                        v = int(round(f.uv[i][1], 6) * h)
                        if pow_two:
                            u = u & 0xFFFE
                            v = v & 0xFFFE
                        f.uv[i][0] = u / float(w)
                        f.uv[i][1] = v / float(h)
    mesh.update()
    Blender.Window.EditMode(editmode)
