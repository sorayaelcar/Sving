# --------------------------------------------------------------------------
#
# This module contains a set of common used utility functions for the conversion
# of NURBS to Sculpties.
#
# --------------------------------------------------------------------------

__author__ = ["Gaia Clary"]
__url__ = ("http://www.machinimatrix.org")
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

import Blender, BPyMesh
from Blender import *
from math import sqrt


def scale_map_uv(ob, doRotate):
    me    = ob.getData(mesh=1)
    faces = me.faces
    # -------------------------------
    #determine the size of the uv-map
    # -------------------------------
    uv   = me.faces[0].uv
    umin = umax=uv[0][0]
    vmin = vmax=uv[0][1]

    for f in faces:
        for t in Blender.Geometry.PolyFill([ f.uv ]):
            for i in t:
                if f.uv[i][0] < umin: umin = f.uv[i][0]
                if f.uv[i][0] > umax: umax = f.uv[i][0]
                if f.uv[i][1] < vmin: vmin = f.uv[i][1]
                if f.uv[i][1] > vmax: vmax = f.uv[i][1]


    # --------------------------------------------------------------
    #make uv-map rectangular and rotate by -90 degrees
    #I still do not know, where this 90 degree rotation comes from.
    # --------------------------------------------------------------
    for f in faces:
        normalise(f.uv[0], umin, umax, vmin, vmax, doRotate)
        normalise(f.uv[1], umin, umax, vmin, vmax, doRotate)
        normalise(f.uv[2], umin, umax, vmin, vmax, doRotate)
        normalise(f.uv[3], umin, umax, vmin, vmax, doRotate)


def normalise(fco, umin, umax, vmin, vmax, doRotate):
    x = fco[0]
    y = fco[1]
    if doRotate == 1:
        fco[0] = 1 - ((y - vmin) / (vmax-vmin))
        fco[1] =     ((x - umin) / (umax-umin))
    else:
        fco[0] = ((x - umin) / (umax-umin))
        fco[1] = ((y - vmin) / (vmax-vmin))


# ---------------------------------------------------------------------
# The following code is an almost verbatim copy from the file
# uvcalc_follow_active_coords.py of the blender standard distribution.
# The only difference is, that the rendering always uses no loops, thus
# blender does not ask for the unwrap type any more.
# A better way to do this would be to add an API to the uvcalc script.
# But this is beyond my possibilities. So for the moment, all i can do,
# is to copy the script content and use the modified version from here.
# --------------------------------------------------------------------

def add_map_uv(ob):

    # print ob, ob.type
    if ob == None or ob.type != 'Mesh':
        Draw.PupMenu('ERROR: No mesh object.')
        return

    # Toggle Edit mode
    is_editmode = Window.EditMode()
    if is_editmode:
        Window.EditMode(0)

    me = ob.getData(mesh=1)
    me.sel = 1
    me.addUVLayer("sculptie")
    me.activeFace = 0
    me_verts = me.verts

    # 0:normal extend, 1:edge length
    EXTEND_MODE = 1

    Window.WaitCursor(1)
    t = Blender.sys.time()
    edge_average_lengths = {}

    OTHER_INDEX = 2,3,0,1
    FAST_INDICIES = 0,2,1,3 # order is faster
    def extend_uvs(face_source, face_target, edge_key):
        '''
        Takes 2 faces,
        Projects its extends its UV coords onto the face next to it.
        Both faces must share an edge.
        '''

        def face_edge_vs(vi):
            # assunme a quad
            return [(vi[0], vi[1]), (vi[1], vi[2]), (vi[2], vi[3]), (vi[3], vi[0])]

        uvs_source = face_source.uv
        uvs_target = face_target.uv

        vidx_source = [v.index for v in face_source]
        vidx_target = [v.index for v in face_target]

        # vertex index is the key, uv is the value
        uvs_vhash_source = dict( [ (vindex, uvs_source[i]) for i, vindex in enumerate(vidx_source)] )
        uvs_vhash_target = dict( [ (vindex, uvs_target[i]) for i, vindex in enumerate(vidx_target)] )

        edge_idxs_source = face_edge_vs(vidx_source)
        edge_idxs_target = face_edge_vs(vidx_target)

        source_matching_edge = -1
        target_matching_edge = -1

        edge_key_swap = edge_key[1], edge_key[0]

        try:	source_matching_edge = edge_idxs_source.index(edge_key)
        except:	source_matching_edge = edge_idxs_source.index(edge_key_swap)
        try:	target_matching_edge = edge_idxs_target.index(edge_key)
        except:	target_matching_edge = edge_idxs_target.index(edge_key_swap)



        edgepair_inner_source = edge_idxs_source[source_matching_edge]
        edgepair_inner_target = edge_idxs_target[target_matching_edge]
        edgepair_outer_source = edge_idxs_source[OTHER_INDEX[source_matching_edge]]
        edgepair_outer_target = edge_idxs_target[OTHER_INDEX[target_matching_edge]]

        if edge_idxs_source[source_matching_edge] == edge_idxs_target[target_matching_edge]:
            iA= 0; iB= 1 # Flipped, most common
        else: # The normals of these faces must be different
            iA= 1; iB= 0


        # Set the target UV's touching source face, no tricky calc needed,
        uvs_vhash_target[edgepair_inner_target[0]][:] = uvs_vhash_source[edgepair_inner_source[iA]]
        uvs_vhash_target[edgepair_inner_target[1]][:] = uvs_vhash_source[edgepair_inner_source[iB]]


        # Set the 2 UV's on the target face that are not touching
        # for this we need to do basic expaning on the source faces UV's
        if EXTEND_MODE == 2:

            try: # divide by zero is possible
                '''
                measure the length of each face from the middle of each edge to the opposite
                allong the axis we are copying, use this
                '''
                i1a= edgepair_outer_target[iB]
                i2a= edgepair_inner_target[iA]
                if i1a>i2a: i1a, i2a = i2a, i1a

                i1b= edgepair_outer_source[iB]
                i2b= edgepair_inner_source[iA]
                if i1b>i2b: i1b, i2b = i2b, i1b
                # print edge_average_lengths
                factor = edge_average_lengths[i1a, i2a][0] / edge_average_lengths[i1b, i2b][0]
            except:
                # Div By Zero?
                factor = 1.0

            uvs_vhash_target[edgepair_outer_target[iB]][:] = uvs_vhash_source[edgepair_inner_source[0]]  +factor * (uvs_vhash_source[edgepair_inner_source[0]] - uvs_vhash_source[edgepair_outer_source[1]])
            uvs_vhash_target[edgepair_outer_target[iA]][:] = uvs_vhash_source[edgepair_inner_source[1]]  +factor * (uvs_vhash_source[edgepair_inner_source[1]] - uvs_vhash_source[edgepair_outer_source[0]])

        else:
            # same as above but with no factor
            uvs_vhash_target[edgepair_outer_target[iB]][:] = uvs_vhash_source[edgepair_inner_source[0]] + (uvs_vhash_source[edgepair_inner_source[0]] - uvs_vhash_source[edgepair_outer_source[1]])
            uvs_vhash_target[edgepair_outer_target[iA]][:] = uvs_vhash_source[edgepair_inner_source[1]] + (uvs_vhash_source[edgepair_inner_source[1]] - uvs_vhash_source[edgepair_outer_source[0]])

    if not me.faceUV:
        Draw.PupMenu('ERROR: Mesh has no face UV coords.')
        return

    face_act = 	me.activeFace
    if face_act == -1:
        Draw.PupMenu('ERROR: No active face')
        return

    face_sel= [f for f in me.faces if len(f) == 4 and f.sel]

    face_act_local_index = -1
    for i, f in enumerate(face_sel):
        if f.index == face_act:
            face_act_local_index = i
            break

    if face_act_local_index == -1:
        Draw.PupMenu('ERROR: Active face not selected')
        return



    # Modes
    # 0 unsearched
    # 1:mapped, use search from this face. - removed!!
    # 2:all siblings have been searched. dont search again.
    face_modes = [0] * len(face_sel)
    face_modes[face_act_local_index] = 1 # extend UV's from this face.


    # Edge connectivty
    edge_faces = {}
    for i, f in enumerate(face_sel):
        for edkey in f.edge_keys:
            try:	edge_faces[edkey].append(i)
            except:	edge_faces[edkey] = [i]

    SEAM = Mesh.EdgeFlags.SEAM

    if EXTEND_MODE == 2:
        edge_loops = BPyMesh.getFaceLoopEdges(face_sel, [ed.key for ed in me.edges if ed.flag & SEAM] )
        me_verts = me.verts
        for loop in edge_loops:
            looplen = [0.0]
            for ed in loop:
                edge_average_lengths[ed] = looplen
                looplen[0] += (me_verts[ed[0]].co - me_verts[ed[1]].co).length
            looplen[0] = looplen[0] / len(loop)



    # remove seams, so we dont map accross seams.
    for ed in me.edges:
        if ed.flag & SEAM:
            # remove the edge pair if we can
            try:	del edge_faces[ed.key]
            except:	pass
    # Done finding seams


    # face connectivity - faces around each face
    # only store a list of indicies for each face.
    face_faces = [[] for i in xrange(len(face_sel))]

    for edge_key, faces in edge_faces.iteritems():
        if len(faces) == 2: # Only do edges with 2 face users for now
            face_faces[faces[0]].append((faces[1], edge_key))
            face_faces[faces[1]].append((faces[0], edge_key))


    # Now we know what face is connected to what other face, map them by connectivity
    ok = True
    while ok:
        ok = False
        for i in xrange(len(face_sel)):
            if face_modes[i] == 1: # searchable
                for f_sibling, edge_key in face_faces[i]:
                    if face_modes[f_sibling] == 0:
                        face_modes[f_sibling] = 1 # mapped and search from.
                        extend_uvs(face_sel[i], face_sel[f_sibling], edge_key)
                        face_modes[i] = 1 # we can map from this one now.
                        ok= True # keep searching

                face_modes[i] = 2 # dont search again
    scale_map_uv(ob, 1)
    print  Blender.sys.time() - t

    if is_editmode:
        Window.EditMode(1)
    else:
        me.update()

    Window.RedrawAll()
    Window.WaitCursor(0)

# -----------------------------------------------------------------------
# End of file copy
# -----------------------------------------------------------------------
