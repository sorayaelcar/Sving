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
import os
from math import sin, cos, pi, sqrt, log, ceil, floor
from Blender.Mathutils import Vector

from primstar.version import LABEL
from primstar.uv_tools import add_map_uv, flip_map_uv, snap_to_pixels

from sys import stderr

library_dirs = [
    Blender.Get('texturesdir'),
    Blender.Get('uscriptsdir'),
    Blender.Get('scriptsdir')]

for d in library_dirs:
    if d:
        lib_dir = os.path.join(d, 'primstar', 'library')
        if os.path.exists(lib_dir):
            break

#***********************************************
# constants
#***********************************************

DRAW_ADJUST = 1.0 / 512.0
ZERO_UV      = Blender.Mathutils.Vector(0.0, 0.0)

#***********************************************
# helper functions
#***********************************************


def debug(num, msg):
    if Blender.Get('rt') >= num:
        print >> stderr, 'debug: ', msg


def obChildren(ob):
    return [ob_child for ob_child in Blender.Object.Get() \
        if ob_child.parent == ob]

#***********************************************
# helper classes
#***********************************************


class XYZ:

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, key):
        # expose for templating
        return getattr(self, key)

    def __cmp__(self, other):
        if other.__class__ == XYZ:
            if self.x == other.x:
                if self.y == other.y:
                    return cmp(self.z, other.z)
                else:
                    return cmp(self.y, other.y)
            else:
                return cmp(self.x, other.x)
        return False

    def __sub__(self, other):
        return XYZ(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z)

    def __add__(self, other):
        return XYZ(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z)

    def __mul__(self, scalar):
        return XYZ(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar)

    def __neg__(self):
        return self * -1.0

    def __div__(self, scalar):
        return XYZ(
            float(self.x) / scalar,
            float(self.y) / scalar,
            float(self.z) / scalar)

    def __repr__(self):
        return "XYZ" + str(self)

    def __str__(self):
        return "(" + str(self.x) + ", " +\
            str(self.y) + ", " +\
            str(self.z) + ")"


class RGBRange:

    def __init__(self, minimum=XYZ(0, 0, 0), maximum=XYZ(255, 255, 255)):
        self.min = minimum
        self.max = maximum
        self.update()

    def convert(self, rgb):
        '''converts float rgb to integers from the range'''
        #GC: separated the calculations for better understanding
        #    Added round() before int() to prevent pixel jumps
        fx = self.min.x + self.range.x * max(0.0, min(1.0, rgb.x))
        fy = self.min.y + self.range.y * max(0.0, min(1.0, rgb.y))
        fz = self.min.z + self.range.z * max(0.0, min(1.0, rgb.z))
        x = int(round(fx))
        y = int(round(fy))
        z = int(round(fz))
        return XYZ(x,y,z)

    def update(self):
        '''Call after setting min and max to refresh the scale and center.'''
        self.range = self.max - self.min
        self.scale = self.range / 255.0
        self.center = (self.min + self.max * 0.5) / 255.0 - XYZ(0.5, 0.5, 0.5)

    def __repr__(self):
        return "RGBRange(" + repr(self.min) + ", " + repr(self.max) + ")"

#***********************************************
# classes
#***********************************************


class BoundingBox:
    '''class for calculating the bounding box for post modifier stack meshes'''

    def __init__(self, ob=None, local=False):
        self.rgb = RGBRange()
        self._dmin = XYZ(0.0, 0.0, 0.0)
        self._dmax = XYZ(0.0, 0.0, 0.0)
        self.local = local

        if ob != None:
            self.ob_count = 1
            self.globalLocation = get_object_world_center(ob)
            self.min, self.max = get_bounding_box(ob, self.local)
            #print "min,max:", self.min, " - ", self.max
            self._default = XYZ(False, False, False)
            self._dirty = XYZ(False, False, False)
        else:
            self.ob_count = 0
            self.globalLocation = XYZ(0.0, 0.0, 0.0)
            self._dirty = XYZ(True, True, True)
            self._default = XYZ(True, True, True)
            self.min = XYZ(0.0, 0.0, 0.0)
            self.max = XYZ(0.0, 0.0, 0.0)
        self.update()

    def __repr__(self):
        return "bb{min=" + repr(self.min) + ", max=" + repr(self.max) + \
                ", scale=" + repr(self.scale) + \
                ", center=" + repr(self.center) + "}"

    def add(self, ob):
        '''Expands box to contain object (if neccessary).'''
        minimum, maximum = get_bounding_box(ob, self.local)
        if self._dirty.x:
            if self._default.x:
                self._default.x = False
                self.min.x = minimum.x
                self.max.x = maximum.x
            else:
                self.min.x = self._dmin.x
                self.max.x = self._dmax.x
        if self._dirty.y:
            if self._default.y:
                self._default.y = False
                self.min.y = minimum.y
                self.max.y = maximum.y
            else:
                self.min.y = self._dmin.y
                self.max.y = self._dmax.y
        if self._dirty.z:
            if self._default.z:
                self._default.z = False
                self.min.z = minimum.z
                self.max.z = maximum.z
            else:
                self.min.z = self._dmin.z
                self.max.z = self._dmax.z
        if self.min.x > minimum.x:
            self.min.x = minimum.x
        if self.min.y > minimum.y:
            self.min.y = minimum.y
        if self.min.z > minimum.z:
            self.min.z = minimum.z
        if self.max.x < maximum.x:
            self.max.x = maximum.x
        if self.max.y < maximum.y:
            self.max.y = maximum.y
        if self.max.z < maximum.z:
            self.max.z = maximum.z

        self.ob_count += 1
        self.globalLocation += get_object_world_center(ob)

        self.update()

    def getCollectionLocation(self):
       if self.ob_count > 0 :
           return XYZ(self.globalLocation.x/ self.ob_count,
                      self.globalLocation.y/ self.ob_count,
                      self.globalLocation.z/ self.ob_count)
       else:
           return self.globalLocation

    def getDim(self):
        return XYZ( self.max.x - self.min.x,
                    self.max.y - self.min.y,
                    self.max.z - self.min.z)

    def update(self):
        '''Call after adding objects to refresh the scale and center.'''
        self.scale = self.max - self.min
        if self.scale.x == 0.0:
            self._dmin.x = self.min.x
            self._dmax.x = self.max.x
            self.min.x = -0.5
            self.max.x = 0.5
            self.scale.x = 1.0
            self._dirty.x = True
        else:
            self._dirty.x = False
        if self.scale.y == 0.0:
            self._dmin.y = self.min.y
            self._dmax.y = self.max.y
            self.min.y = -0.5
            self.max.y = 0.5
            self.scale.y = 1.0
            self._dirty.y = True
        else:
            self._dirty.y = False
        if self.scale.z == 0.0:
            self._dmin.z = self.min.z
            self._dmax.z = self.max.z
            self.min.z = -0.5
            self.max.z = 0.5
            self.scale.z = 1.0
            self._dirty.z = True
        else:
            self._dirty.z = False
        self.center = self.min + self.scale * 0.5
        #print "update min+scale*0.5 -> center:", self.min, self.scale, self.center

    def normalised(self):
        '''Returns a normalised version of the bounding box'''
        s = BoundingBox(local=self.local)
        if self.local:
            vmin = min(self.min.x, self.min.y, self.min.z)
            vmax = max(self.max.x, self.max.y, self.max.z)
            s.min = XYZ(vmin, vmin, vmin)
            s.max = XYZ(vmax, vmax, vmax)
        else:
            tmin = self.local_min()
            tmax = self.local_max()
            vmin = min(tmin.x, tmin.y, tmin.z)
            vmax = max(tmax.x, tmax.y, tmax.z)
            s.min = self.center + XYZ(vmin, vmin, vmin)
            s.max = self.center + XYZ(vmax, vmax, vmax)
        s.update()
        return s

    def centered(self):
        '''Returns a centered version of the bounding box'''
        s = BoundingBox(local=self.local)
        #print "Center: local bbox: ",s 
        if self.local:
            s.max = XYZ(max(abs(self.min.x), abs(self.max.x)),
                    max(abs(self.min.y), abs(self.max.y)),
                    max(abs(self.min.z), abs(self.max.z)))
            s.min = - s.max
            #print "Center: local: ",s 
        else:
            tmin = self.local_min()
            tmax = self.local_max()
            offset = XYZ(max(abs(tmin.x), abs(tmax.x)),
                    max(abs(tmin.y), abs(tmax.y)),
                    max(abs(tmin.z), abs(tmax.z)))
            s.min = self.center - offset
            s.max = self.center + offset
            #print "Center: global: ",s 
        s.update()
        return s


    def local_min(self):
        return self.min - self.center

    def local_max(self):
        return self.max - self.center

    def xyz_to_rgb(self, loc):
        '''converts a location in the bounding box to rgb sculpt map values'''
        return self.rgb.convert(self.xyz_to_float(loc))

    def xyz_to_float(self, loc):
        '''converts a location in the bounding box to floating point
        rgb sculpt map values'''
        x = (loc.x - self.min.x) / self.scale.x
        y = (loc.y - self.min.y) / self.scale.y
        z = (loc.z - self.min.z) / self.scale.z
        return XYZ(x, y, z)


class PlotPoint:

    def __init__(self):
        self.seam = False
        self.values = []
        self.offset = []

    def add(self, value, seam, offset):
        if self.seam and not seam:
            return
        if seam and not self.seam:
            self.seam = seam
            self.values = []
            self.offset = []
        self.offset.append(abs(offset))
        self.values.append(value)

    def __repr__(self):
        return "PlotPoint(%s, %s, %s)" % \
                (repr(self.values), repr(self.seam), repr(self.offset))


def create_new_image(name, width, height, depth):
    image = Blender.Image.New(name, width, height, depth)
    image.pack()
    #imageName = image.getName().replace(".", "_")
    #image.setName(imageName)
    return image

def create_grid_aligned_color(x,y,z):
    ix = int(round(x * 256))
    iy = int(round(y * 256))
    iz = int(round(z * 256))
    fx = float(ix) / 256.0
    fy = float(iy) / 256.0
    fz = float(iz) / 256.0
    return XYZ(fx, fy, fz)

class BakeMap:

    def __init__(self, image):
        self.map = []
        self.image = image
        self.bb_min = None
        self.bb_max = None
        self.scale = None
        self.center = None
        self.edges = {}
        self.map = [[PlotPoint() for y in range(image.size[1] + 1)] \
                for x in range(image.size[0] + 1)]

    def plot_line(self, v1, v2, col1, col2, seam):
        '''plot a gradient line in the bake buffer'''
        
        #print "plot_line begin"
        #print "Plot v1,v2,col1,col2:", v1, v2, col1.co, col2.co
        
        c1 = XYZ(col1.co.x, col1.co.y, col1.co.z)
        c2 = XYZ(col2.co.x, col2.co.y, col2.co.z)
        
        #print "Plot v1,v2,c1,c2:", v1, v2, c1, c2
        
        x1 = int(v1.x * self.image.size[0])
        y1 = int(v1.y * self.image.size[1])
        x2 = int(v2.x * self.image.size[0])
        y2 = int(v2.y * self.image.size[1])
        #print "x1,y1,x2,y2:", x1,y1,"  ", x2,y2
        
        ox1 = v1.x * self.image.size[0] - x1
        ox2 = v2.x * self.image.size[0] - x2
        oy1 = v1.y * self.image.size[1] - y1
        oy2 = v2.y * self.image.size[1] - y2
        #print "ox1,oy1,ox2,oy2:", ox1,oy1,"  ", ox2,oy2
        

        o1 = sqrt(ox1 * ox1 + oy1 * oy1)
        o2 = sqrt(ox2 * ox2 + oy2 * oy2)
        #print "o1,o2:", o1,o2

        # This is a degenerated edge (both endpoints are at the same location):        
        if x1 == x2 and y1 == y2:
            #if seam:
            #    print "degen plot point at: ", x1,y1, c1, c2
            self.plot_point(x1, y1, (c1 + c2) / 2, seam, o1 + 0.5 * (o2 - o1))
            return
            
        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            c1, c2 = c2, c1
            o1, o2 = o2, o1
        mix = c2 - c1
        deltax = x2 - x1
        deltay = abs(y2 - y1)
        deltao = o2 - o1
        error = deltax / 2
        y = y1
        if y1 < y2:
            ystep = 1
        else:
            ystep = -1
        for x in range(x1, x2 + 1):
            d = x - x1
            if d:
                d = float(d) / deltax
                colour = c1 + mix * d
                offset = o1 + deltao * d
            else:
                colour = c1
                offset = o1
            if steep:
                self.plot_point(y, x, colour, seam, offset)
            else:
                self.plot_point(x, y, colour, seam, offset)
            error = error - deltay
            if error < 0:
                y = y + ystep
                error = error + deltax

        #print "plot_line end"

    def plot_point(self, x, y, colour, seam, offset):
        '''plot a point in the bake buffer'''
        self.map[x][y].add(colour, seam, offset)
        #if seam:
        #    print x, y, colour

    def update_map(self):
        '''plot edge buffer into bake buffer and update minimum
        and maximum range'''
        #print "Update map with ", len(self.edges), " edges..."
        for key, line in self.edges.iteritems():
            seam = line['seam'] or line['count'] == 1
            self.plot_line(line['uv1'][0], line['uv2'][0],
                    line['v1'], line['v2'], seam)
            if line['count'] == 2:
                if (line['uv1'][0] != line['uv1'][1]) or \
                        (line['uv2'][0] != line['uv2'][1]):
                    self.plot_line(line['uv1'][1], line['uv2'][1], \
                            line['v1'], line['v2'], seam)
            if line['count'] >= 3:
                print "Skipping extra edges: %d not drawn" % \
                        (line['count'] - 2)
        for u in range(self.image.size[0] + 1):
            for v in range(self.image.size[1] + 1):
                if len(self.map[u][v].values) > 1:
                    value = XYZ()
                    offset = min(self.map[u][v].offset)
                    count = 0
                    for i in range(len(self.map[u][v].values)):
                        if self.map[u][v].offset[i] == offset:
                            value += self.map[u][v].values[i]
                            count += 1
                    self.map[u][v].values = [value / count]
                if self.map[u][v].values != []:
                    if self.bb_min:
                        self.bb_min.x = min(self.bb_min.x,
                                self.map[u][v].values[0].x)
                        self.bb_min.y = min(self.bb_min.y,
                                self.map[u][v].values[0].y)
                        self.bb_min.z = min(self.bb_min.z,
                                self.map[u][v].values[0].z)
                        self.bb_max.x = max(self.bb_max.x,
                                self.map[u][v].values[0].x)
                        self.bb_max.y = max(self.bb_max.y,
                                self.map[u][v].values[0].y)
                        self.bb_max.z = max(self.bb_max.z,
                                self.map[u][v].values[0].z)
                    else:
                        self.bb_min = XYZ() + self.map[u][v].values[0]
                        self.bb_max = XYZ() + self.map[u][v].values[0]
        self.update()

    def update(self):
        '''update scale and center from bb_min and bb_max'''
        self.scale = self.bb_max - self.bb_min
        self.center = self.bb_min + self.scale * 0.5

    def bake(self, rgb=RGBRange()):
        '''bake the map buffer to the image'''
        for u in range(self.image.size[0] + 1):
            u1 = u - (u == self.image.size[0])
            for v in range(self.image.size[1] + 1):
                v1 = v - (v == self.image.size[1])
                if self.map[u][v].values:
                    c = self.map[u][v].values[0] - self.bb_min
                    #print "color1: ", c, "scale:", self.scale
                    if self.scale.x:
                        c.x = c.x / self.scale.x + DRAW_ADJUST
                    else:
                        c.x = 0.5
                    if self.scale.y:
                        c.y = c.y / self.scale.y + DRAW_ADJUST
                    else:
                        c.y = 0.5
                    if self.scale.z:
                        c.z = c.z / self.scale.z + DRAW_ADJUST
                    else:
                        c.z = 0.5
                    #print "color2: ", c
                    c = rgb.convert(c)
                    #print "color3: ", c
                    self.image.setPixelI(u1, v1, (c.x, c.y, c.z, 255))
                    #print "set pixel: ", u1, v1, c


class LibPath:

    def __init__(self, path, root=None):
        self.path = path
        if root:
            self.local_path = path[len(root):]
        else:
            self.local_path = path
        self.name = Blender.sys.makename(path, strip=1)

    def __lt__(self, other):
        return self.path < other.path


class LibDir(LibPath):

    def __init__(self, path, root=None):
        LibPath.__init__(self, path, root)
        self.files = []
        self.dirs = []


class LibFile(LibPath):

    pass


def build_lib(path=None, LibDir=LibDir, LibFile=LibFile):
    if not path:
        path = lib_dir
    top = LibDir(path)
    path2dir = {path: top}
    for root, dirs, files in os.walk(path):
        dirobj = path2dir[root]
        for name in dirs:
            subdirobj = LibDir(os.path.join(root, name), top.path)
            path2dir[subdirobj.path] = subdirobj
            dirobj.dirs.append(subdirobj)
        for name in files:
            if name[-4:] == '.png':
                dirobj.files.append(LibFile(os.path.join(root, name), \
                        top.path))
                dirobj.files[-1].local_path = dirobj.files[-1].local_path[:-4]
    return top

#***********************************************
# functions
#***********************************************


def minimum(a,b):
    if a[0] > b[0]: x = b[0] 
    else: x = a[0]
    if a[1] > b[1]: y = b[1] 
    else: y = a[1]
    if a[2] > b[2]: z = b[2] 
    else: z = a[2]
    return (x,y,z)

def maximum(a,b):
    if a[0] < b[0]: x = b[0] 
    else: x = a[0]
    if a[1] < b[1]: y = b[1] 
    else: y = a[1]
    if a[2] < b[2]: z = b[2] 
    else: z = a[2]
    return (x,y,z)

def is_inside_out(mesh):
    v0 = mesh.verts[0]
    if v0 is None:
        return False
    
    min = v0.co
    max = v0.co

    nmin = min + v0.no*0.00001
    nmax = nmin

    for v in mesh.verts:
        p = v.co + v.no*0.00001
        nmin = minimum(nmin,p)
        nmax = maximum(nmax,p)
        min  = minimum(min, v.co)
        max  = maximum(max, v.co)

    bigger  = (nmax[0] - nmin[0]) * (nmax[1] - nmin[1]) * (nmax[2] - nmin[2])
    smaller = (max[0]  - min[0]  )* (max[1]  - min[1])  * (max[2]  - min[2] )
 
    return smaller > bigger

                    
def need_rebake(ob, auto_correct):
    mesh = ob.getData(False, True)
    name = ob.getName()

    activeUV = mesh.activeUVLayer
    mesh.activeUVLayer = "sculptie"
    image = mesh.faces[0].image
    mesh.activeUVLayer = activeUV
    bake_again = False

    new_object = new_from_map(image, False)
    editmode = Blender.Window.EditMode()
    if not editmode:
        Blender.Window.EditMode(1)
    Blender.Window.EditMode(0)
    me = new_object.getData(False,True)
    if is_inside_out(me):
        if auto_correct:
            flip_map_uv(mesh)
            mesh.recalcNormals()
            mesh.update()
        bake_again = True

    #else:
    #    print "need_rebake(): Face normals OK for ["+ob.getName()+"]. (no need to flip)"
    scene = Blender.Scene.GetCurrent()
    scene.objects.unlink(new_object)
    Blender.Window.EditMode(editmode)
    return bake_again
    
def active(ob):
    '''Returns True if object is an active sculptie.
    An active sculptie is a mesh with a 'sculptie' uv layer
    with an image assigned
    '''
    debug(50, "sculpty.active(%s)" % (ob.name))
    if ob.type == 'Mesh':
        mesh = ob.getData(False, True)
        if 'sculptie' in mesh.getUVLayerNames():
            currentUV = mesh.activeUVLayer
            mesh.activeUVLayer = "sculptie"
            for f in mesh.faces:
                if f.image != None:
                    mesh.activeUVLayer = currentUV
                    return True
            mesh.activeUVLayer = currentUV
    return False


def bake_default(image, sculpt_type, radius=0.25, levels=0):
    '''Bakes a mathematical sculpt map to image

    sculpt_type - one of "SPHERE", "TORUS Z", "TORUS X", "CYLINDER",
                                   "PLANE" or "HEMI"
    radius - inner radius value for torus
    '''
    debug(30, "sculpty.bake_default(%s, %s, %f)" % \
            (image.name, sculpt_type, radius))
    x = image.size[0]
    y = image.size[1]
    for u in range(x):
        path = float(u) / x
        if u == x - 1:
            path = 1.0
        for v in range(y):
            profile = float(v) / y
            if v == y - 1:
                profile = 1.0
            rgb = uv_to_rgb(sculpt_type, path, profile, radius, levels)
            image.setPixelF(u, v, (rgb.x, rgb.y, rgb.z, 1.0))


def bake_lod(image):
    '''Bakes the sculptie LOD points for the image size.
    The brighter the blue dots, the more LODs use that pixel.
    '''
    debug(30, "sculpty.bake_lod(%s)" % (image.name))
    x = image.size[0]
    y = image.size[1]
    for u in range(x):
        for v in range(y):
            image.setPixelF(u, v, (float(u) / x, float(v) / y, 0.0, 1.0))
    for l in range(4):
        sides = [6, 8, 16, 32][l]
        s, t = face_count(x, y, sides, sides, False)
        ss = [int(x * k / float(s)) for k in range(s)]
        ss.append(x - 1)
        ts = [int(y * k / float(t)) for k in range(t)]
        ts.append(y - 1)
        for s in ss:
            for t in ts:
                c = image.getPixelF(s, t)
                c[2] += 0.25
                image.setPixelF(s, t, c)


def bake_object(ob, linkset_BBox, clear=True, keep_seams=True, keep_center=True, optimise_resolution=True):
    '''Bakes the object's mesh to the specified bounding box.
    Returns False if object is not an active sculptie.
    '''
    #GC: Changed precision from 6 digits to 12 digits to prevent pixel jumping.
    debug(20, "sculpty.bake_object(%s, %d)" % (ob.name, clear))
    if not active(ob):
        return False
    mesh = Blender.Mesh.New()
    
    Blender.Window.WaitCursor(1)
    # biggestMultiple is used for size correction When optimize_resolution is True
    biggestMultiple = [ 1, 1, 1 ]
    
    #This is the BBox of the Object after all modifiers have been applied
    objectBoundingBox  = BoundingBox(ob, local=True)
    objectBlenderScale = ob.getSize()
    
    #print "======================================================"
    #print "Baking object [", ob.name, "]"
    Blender.Window.WaitCursor(1)
    #print "bake_object() BoundingBox: min         = ", objectBoundingBox.min
    #print "bake_object() BoundingBox: max         = ", objectBoundingBox.max
    #print "bake_object() Original object Dim      = ", objectBoundingBox.scale
    #print "bake_object() Original object Scale    = ", objectBlenderScale
    #print "bake_object() Original object location = ", ob.loc

    #if keep_center:
    #    # The bbox-size of the object changes such that 
    #    # the current object center will be the same as the bbox center
    #    print "bake_object() Keep center of:        = ", ob.name
    #    objectBoundingBox = objectBoundingBox.centered()            
    #else:
    #    print "bake_object() Reset center for       = ", ob.name

    if optimise_resolution:
        #print "bake_object() Optimize baking for    = ", ob.name
        
        ObjectDim = objectBoundingBox.scale
        #print "bake_object() ObjectDim is:          = ", ObjectDim
        LinkSetDim  = linkset_BBox.max-linkset_BBox.min
        #print "bake_object() LinkSetDim  is:        = ", LinkSetDim
    
        biggestMultiple  = [floor(LinkSetDim.x/ObjectDim.x),floor(LinkSetDim.y/ObjectDim.y),floor(LinkSetDim.z/ObjectDim.z)]
        if biggestMultiple[0] == 0: biggestMultiple[0] = 1
        if biggestMultiple[1] == 0: biggestMultiple[1] = 1
        if biggestMultiple[2] == 0: biggestMultiple[2] = 1
        #print "bake_object() biggestMultiple is:    = ", biggestMultiple

        # Stretch the Object to the tightest possible multiple of its current scale
        objectOptimizedScale = (objectBlenderScale[0]*biggestMultiple[0], objectBlenderScale[1]*biggestMultiple[1], objectBlenderScale[2]*biggestMultiple[2])
        ob.setSize(objectOptimizedScale)
        #print "bake_object() objectOptimizedScale   = ", objectOptimizedScale
        # remember to reset the size back to its original later (see below)

    me = ob.getData(False, True)
    currentUV = me.activeUVLayer
    me.activeUVLayer = "sculptie"
    
    
    #if is_negative_scaled(ob.getSize()):
    #    if ZERO_UV in me.faces[0].uv:
    #        print "is_negative_scaled(): Flip UVMap of ["+ob.getName()+"]. (reason: negative scale values)"
    #        flip_map_uv(me)
    #        me.update()
    #    #else:
    #    #    print "face coords are:", me.faces[0].uv
    editmode = Blender.Window.EditMode()
    if not editmode:
       Blender.Window.EditMode(1)
    Blender.Window.EditMode(0)
    Blender.Window.WaitCursor(1)
     
    me.activeUVLayer = currentUV
    
    # ================================
    # Now prepare for the actual bake 
    # ================================       
    mesh.getFromObject(ob, 0, 1)
    mesh.transform(remove_rotation(ob.matrix))

    images = map_images(mesh)
    maps = {}
    for i in images:
        maps[i.name] = BakeMap(i)
        if clear:
            clear_image(i)
                        

    # =====================================================================
    # Check for negative scaled objects and flip the sculptmap if necessary
    # =====================================================================
    currentUV = mesh.activeUVLayer
    mesh.activeUVLayer = "sculptie"

    edges = dict([(ed.key, {
        'count': 0,
        'seam': bool((ed.flag & Blender.Mesh.EdgeFlags.SEAM) and keep_seams),
        'v1': ed.v1,
        'v2': ed.v2}) for ed in mesh.edges])
    #print "mesh edges : ", mesh.edges

    for f in mesh.faces:
        if f.image:

            w,h = f.image.getSize()
            width,height = float(w), float(h)

            #print "process image ", f.image, " of size ", width, height
            for key in f.edge_keys:
                if key not in maps[f.image.name].edges:
                    maps[f.image.name].edges[key] = edges[key].copy()
                    maps[f.image.name].edges[key]['uv1'] = []
                    maps[f.image.name].edges[key]['uv2'] = []

                maps[f.image.name].edges[key]['count'] += 1

                verts = list(f.v) # support python < 2.6

                i = verts.index(edges[key]['v1'])
                x,y = pixel_aligned_bake(f.uv[i].x, f.uv[i].y, width, height)
                maps[f.image.name].edges[key]['uv1'].append(XYZ(x, y, 0.0))

                i = verts.index(edges[key]['v2'])
                x,y = pixel_aligned_bake(f.uv[i].x, f.uv[i].y, width, height)
                maps[f.image.name].edges[key]['uv2'].append(XYZ(x, y, 0.0))


    max_scale = None
    for m in maps.itervalues():
        m.update_map()
        if len(maps) == 1:
            loc = remove_rotation(ob.matrix).translationPart()
            offset = m.center - XYZ(loc[0], loc[1], loc[2])
            m.bb_min = m.center + linkset_BBox.min - offset
            m.bb_max = m.center + linkset_BBox.max - offset
            m.update()
        else:
            if not max_scale:
                max_scale = XYZ() + m.scale
            else:
                if max_scale.x < m.scale.x:
                    max_scale.x = m.scale.x
                if max_scale.y < m.scale.y:
                    max_scale.y = m.scale.y
                if max_scale.z < m.scale.z:
                    max_scale.z = m.scale.z


    collection_location = linkset_BBox.getCollectionLocation()
    loc = ob.getLocation()
    object_location     = XYZ(loc[0],loc[1],loc[2])
    relative_location   = object_location - collection_location 
    
    #print "collection_location:", collection_location
    #print "object_location    :", object_location
    #print "relative_location  :", relative_location

    sculptmap_name = ""
    for m in maps.itervalues():
        if 'primstar' not in m.image.properties:
            m.image.properties['primstar'] = {}
        
        # ======================================================================
        # Keep the object properties with the image. Needed for later LSL-export
        # ======================================================================
        m.image.properties['primstar']['rot_x'] = ob.rot.x
        m.image.properties['primstar']['rot_y'] = ob.rot.y
        m.image.properties['primstar']['rot_z'] = ob.rot.z
        #print "store rot(",ob.getName(),")",ob.rot
        
        if len(maps) > 1:
            m.image.properties['primstar']['loc_x'] = m.center.x - objectBoundingBox.center.x
            m.image.properties['primstar']['loc_y'] = m.center.y - objectBoundingBox.center.y
            m.image.properties['primstar']['loc_z'] = m.center.z - objectBoundingBox.center.z
            m.image.properties['primstar']['scale_x'] = max_scale.x / linkset_BBox.scale.x
            m.image.properties['primstar']['scale_y'] = max_scale.y / linkset_BBox.scale.y
            m.image.properties['primstar']['scale_z'] = max_scale.z / linkset_BBox.scale.z
            m.bb_min = m.center - max_scale * 0.5
            m.bb_max = m.center + max_scale * 0.5
            m.scale = max_scale

            m.image.properties['primstar']['size_x'] = m.scale.x / biggestMultiple[0]
            m.image.properties['primstar']['size_y'] = m.scale.y / biggestMultiple[1]
            m.image.properties['primstar']['size_z'] = m.scale.z / biggestMultiple[2]

            #print "m: in bake: size of ", m.image.name, " : ", m.image.properties['primstar']['size_x'], m.image.properties['primstar']['size_y'], m.image.properties['primstar']['size_z']

        else:
            loc =   XYZ(linkset_BBox.center.x - objectBoundingBox.center.x,
                        linkset_BBox.center.y - objectBoundingBox.center.y,
                        linkset_BBox.center.z - objectBoundingBox.center.z)

            #scale = XYZ( objectBlenderScale[0] * linkset_BBox.scale.x / (abs(objectBlenderScale[0]) * objectBoundingBox.scale.x * biggestMultiple[0] ),
            #             objectBlenderScale[1] * linkset_BBox.scale.y / (abs(objectBlenderScale[1]) * objectBoundingBox.scale.y * biggestMultiple[1] ),
            #             objectBlenderScale[2] * linkset_BBox.scale.z / (abs(objectBlenderScale[2]) * objectBoundingBox.scale.z * biggestMultiple[2] ))
            scale = XYZ( linkset_BBox.scale.x / (objectBoundingBox.scale.x * biggestMultiple[0] ),
                         linkset_BBox.scale.y / (objectBoundingBox.scale.y * biggestMultiple[1] ),
                         linkset_BBox.scale.z / (objectBoundingBox.scale.z * biggestMultiple[2] ))

            size =  XYZ(linkset_BBox.scale.x,
                        linkset_BBox.scale.y,
                        linkset_BBox.scale.z)

            m.image.properties['primstar']['loc_x']   = loc.x
            m.image.properties['primstar']['loc_y']   = loc.y
            m.image.properties['primstar']['loc_z']   = loc.z
            
            m.image.properties['primstar']['scale_x'] = scale.x
            m.image.properties['primstar']['scale_y'] = scale.y
            m.image.properties['primstar']['scale_z'] = scale.z
            
            m.image.properties['primstar']['size_x']  = size.x
            m.image.properties['primstar']['size_y']  = size.y
            m.image.properties['primstar']['size_z']  = size.z
            
            #print "bake_object() linkset_BBox.scale      = ", linkset_BBox.scale
            #print "bake_object() objectBoundingBox.scale = ", objectBoundingBox.scale
            #print "bake_object() scale(",m.image.name,") = ", scale
            #print "bake_object() size (",m.image.name,") = ", size
                
        m.image.properties['primstar']['rloc_x'] = relative_location.x
        m.image.properties['primstar']['rloc_y'] = relative_location.y
        m.image.properties['primstar']['rloc_z'] = relative_location.z

        m.image.properties['primstar']['multiple_x']  = biggestMultiple[0]
        m.image.properties['primstar']['multiple_y']  = biggestMultiple[1]
        m.image.properties['primstar']['multiple_z']  = biggestMultiple[2]
        
        m.image.source = Blender.Image.Sources['GENERATED']
        
        m.bake(linkset_BBox.rgb)
        sculptmap_name = m.image.getName()
        
    mesh.activeUVLayer = currentUV

    if optimise_resolution:
        # now set back the object size to its original value.
        # IMPORTANT! There seems to be a bug in Blender. Just setting
        # the object size does not seem sufficient. I have seen that
        # a subsequet creation of a BoundingBox() for this object does NOT
        # reflect the last setSize() changes! 
        # I noticed that the internal object state is correctly readjusted
        # after i called ob.getMatrix(). Hence a added this call here. Please
        # do not remove or multi part bakes will get borked!
        ob.setSize(objectBlenderScale)
        ob.getMatrix()

    print "Baked object [", ob.name, "] to image [", sculptmap_name, "]"
    #print "======================================================"

    return True

# ===================================================================
# GC (04-oct-2010):
# Method to pixel align UV-coordinates to the current image to bake to.
# It turned out that the best (most precise) bake results can be achieved
# When the UV-coordinates exactly match pixel locations. That seems
# to minimize rounding errors significantly. this method ensures that
# the baked coordinates are shifted to the nearest image pixel.
#
# UV coordinates are in the interval [0,1]
# width and height are the pixel sizes of the UV map.
# This method forces the UV coordinates to match pixel coordinates:
# ===================================================================
def pixel_aligned_bake(u,v, width, height):
    
    # transform from UV space into image space:
    l = round(width  * u)
    m = round(height * v)

    # inverse transform to UV space (now pixel aligned)
    x = l / width
    y = m / height
               
    #print "Processing pixel position: [", u,l,x, "][", v,m,y, "]"
    #print "pixel: [", l, ",", m, "]"
    
    return x,y

#def is_black_sculptie(ob):
#    result = False
#    me = ob.getData(False, True)
#    currentUV = me.activeUVLayer
#    me.activeUVLayer = "sculptie"
#    if is_negative_scaled(ob.getSize()):
#        if ZERO_UV in me.faces[0].uv:
#            result = True
#    me.activeUVLayer = currentUV
#    return result

def dump_images(ob, l="image: "):
    mesh = Blender.Mesh.New()
    mesh.getFromObject(ob, 0, 1)
    mesh.transform(remove_rotation(ob.matrix))
    images = map_images(mesh)
    for image in images:
        if 'primstar' not in image.properties:
            image.properties['primstar'] = {}
        #print l, "size of ", image.name, " : ", image.properties['primstar']['size_x'], image.properties['primstar']['size_y'], image.properties['primstar']['size_z']

def bake_preview(image):
    '''Bakes a pseudo 3D representation of the sculpt map image
    to it's alpha channel'''
    debug(30, "sculpty.bake_preview(%s)" % (image.name))
    clear_alpha(image)
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            c1 = image.getPixelF(x, y)
            f = (c1[1] * 0.35) + 0.65
            s = int((image.size[0] - 1) * (0.5 - (0.5 - c1[0]) * f))
            t = int((image.size[1] - 1) * (0.5 - (0.5 - c1[2]) * f))
            c2 = image.getPixelF(s, t)
            if c2[3] < c1[1]:
                c2[3] = c1[1]
                image.setPixelF(s, t, c2)


def check(ob):
    '''Returns true if the object is a mesh with a sculptie uv layer'''
    debug(50, "sculpty.check(%s)" % (ob.name))
    if ob.type == 'Mesh':
        mesh = ob.getData(False, True)
        if 'sculptie' in mesh.getUVLayerNames():
            return True
    return False


def check_clean(x, y, u, v, clean):
    '''Returns true if the U, V size with the clean setting aligns to the
    sculptie points on an X, Y sized image'''
    xs, ys = map_pixels(x, y, [3])
    if clean:
        w = int(pow(2, 1 + ceil(log(u) / log(2))) / 2)
        h = int(pow(2, 1 + ceil(log(v) / log(2))) / 2)
    else:
        w = u
        h = v
    for i in range(1, w):
        if int(x * i / float(w)) not in xs:
            return False
    for i in range(1, h):
        if int(y * i / float(h)) not in ys:
            return False
    return True


def clear_image(image):
    '''Clears the image to black with alpha 0'''
    debug(30, "sculpty.clear_image(%s)" % (image.name))
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            image.setPixelI(x, y, (0, 0, 0, 0))


def clear_alpha(image):
    '''Clears the alpha channel of the sculpt map image to hide the map'''
    debug(30, "sculpty.clear_alpha(%s)" % (image.name))
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            c1 = image.getPixelI(x, y)
            c1[3] = 0
            image.setPixelI(x, y, c1)


def draw_line(image, v1, v2, c1, c2, ends=False):
    '''Draws a gradient line on a sculpt map image'''
    x1 = v1.x
    if x1 == image.size[0] - 1:
        x1 = image.size[0]
    x2 = v2.x
    if x2 == image.size[0] - 1:
        x2 = image.size[0]
    y1 = v1.y
    if y1 == image.size[1] - 1:
        y1 = image.size[1]
    y2 = v2.y
    if y2 == image.size[1] - 1:
        y2 = image.size[1]
    steep = abs(y2 - y1) > abs(x2 - x1)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        c1, c2 = c2, c1
    mix = c2 - c1
    deltax = x2 - x1
    deltay = abs(y2 - y1)
    error = deltax / 2
    y = y1
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        draw = ends or (x != x1 and x != x2)
        if not draw:
            #make sure we can skip this pixel
            if steep:
                u, v = y, x
            else:
                u, v = x, y
            if u == image.size[0]:
                u -= 1
            if v == image.size[1]:
                v -= 1
            c = image.getPixelI(u, v)
            if c[3] == 0:
                draw = True
        if draw:
            d = x - x1
            if d:
                if d == deltax:
                    colour = c2
                else:
                    colour = c1 + mix * (DRAW_ADJUST + float(d) / deltax)
            else:
                colour = c1
            if steep:
                draw_point(image, y, x, colour)
            else:
                draw_point(image, x, y, colour)
        error = error - deltay
        if error < 0:
            y = y + ystep
            error = error + deltax


def draw_point(image, u, v, colour):
    '''Set pixel colour for given u,v on a sculpt map'''
    if u == image.size[0] - 1:
        return
    if v == image.size[1] - 1:
        return
    if u == image.size[0]:
        u = image.size[0] - 1
    if v == image.size[1]:
        v = image.size[1] - 1
    image.setPixelF(u, v, (colour.x, colour.y, colour.z, 1.0))


def face_count(width, height, x_faces, y_faces, model=True):
    '''Returns usable face count from input

    width - sculpt map width
    height - sculpt map width
    x_faces - desired x face count
    y_faces - desired y face count
    model - when true, returns 8 x 4 instead of 9 x 4 to give extra subdivision
    '''
    debug(40, "sculpty.face_count(%d, %d, %d, %d, %d)" % (
            width, height, x_faces, y_faces, model))
    ratio = float(width) / float(height)
    verts = int(min(0.25 * width * height, x_faces * y_faces))
    if (width != height) and model:
        verts = verts & 0xfff8
    y_faces = int(sqrt(verts / ratio))
    y_faces = max(y_faces, 4)
    x_faces = verts // y_faces
    x_faces = max(x_faces, 4)
    y_faces = verts // x_faces
    return int(x_faces), int(y_faces)


def fill_holes(image):
    '''Any pixels with alpha 0 on the image have colour
    interpolated from neighbours'''
    debug(30, "sculpty.fill_holes(%s)" % (image.name))

    def getFirstX(y):
        for x in range(image.size[0]):
            c = image.getPixelF(x, y)
            if c[0] + c[1] + c[2] + c[3] != 0:
                if x > 0:
                    fill = True
                return c
        return None

    def getFirstY(x):
        for y in range(image.size[1]):
            c = image.getPixelF(x, y)
            if c[0] + c[1] + c[2] + c[3] != 0:
                if y > 0:
                    fill = True
                return c
        return None

    def fillX():
        skipx = fill = False
        for v in range(image.size[1]):
            c = getFirstX(v)
            if not c:
                skipx = True
                continue
            sr = c[0]
            sg = c[1]
            sb = c[2]
            s = 0
            for u in range(1, image.size[0]):
                nc = image.getPixelF(u, v)
                if nc[0] + nc[1] + nc[2] + nc[3] == 0:
                    if not fill:
                        fill = True
                else:
                    if fill:
                        fill = False
                        draw_line(image, XYZ(s, v, 0),
                                XYZ(u, v, 0),
                                XYZ(sr, sg, sb),
                                XYZ(nc[0], nc[1], nc[2]))
                    s = u
                    sr = nc[0]
                    sg = nc[1]
                    sb = nc[2]
            if fill:
                fill = False
                draw_line(image, XYZ(s, v, 0),
                        XYZ(u, v, 0),
                        XYZ(sr, sg, sb),
                        XYZ(sr, sg, sb))
        return skipx

    def fillY():
        fill = False
        for u in range(image.size[0]):
            c = getFirstY(u)
            if not c:
                continue
            sr = c[0]
            sg = c[1]
            sb = c[2]
            s = 0
            for v in range(1, image.size[1]):
                nc = image.getPixelF(u, v)
                if nc[0] + nc[1] + nc[2] + nc[3] == 0:
                    if not fill:
                        fill = True
                else:
                    if fill:
                        fill = False
                        draw_line(image, XYZ(u, s, 0),
                                XYZ(u, v, 0),
                                XYZ(sr, sg, sb),
                                XYZ(nc[0], nc[1], nc[2]))
                    s = v
                    sr = nc[0]
                    sg = nc[1]
                    sb = nc[2]
            if fill:
                fill = False
                draw_line(image, XYZ(u, s, 0),
                        XYZ(u, v, 0),
                        XYZ(sr, sg, sb),
                        XYZ(sr, sg, sb))
    skipx = fillX()
    fillY()
    if skipx:
        fillX()


def finalise(image):
    '''Expands each active pixel of the sculpt map image'''
    debug(30, "sculpty.finalise(%s)" % (image.name))
    u_pixels, v_pixels = map_pixels(image.size[0], image.size[1])
    u_pixels.append(image.size[0])
    v_pixels.append(image.size[1])
    for x in u_pixels[0:-1]:
        for y in v_pixels[0:-1]:
            c = image.getPixelI(x, y)
            if c[3] == 0:
                continue
            if x and x - 1 not in u_pixels:
                image.setPixelI(x - 1, y, c)
                if y and y - 1 not in v_pixels:
                    image.setPixelI(x - 1, y - 1, c)
            if y and y - 1 not in v_pixels:
                image.setPixelI(x, y - 1, c)


def flip_pixels(pixels):
    '''Converts a list of pixels on a sculptie map to their mirror positions'''
    m = max(pixels)
    return [m - p for p in pixels]

def get_object_center(ob):
    #print "================================="       
    bb = ob.boundingBox
    amin_x = bb[0].x
    amax_x = amin_x
    amin_y = bb[0].y
    amax_y = amin_y
    amin_z = bb[0].z
    amax_z = amin_z
    
    vectorsum = (0,0,0)
    for co in bb:
        #print "bbox.co:", co
        if co.x < amin_x:
            amin_x = co.x
        elif co.x > amax_x:
            amax_x = co.x
        if co.y < amin_y:
            amin_y = co.y
        elif co.y > amax_y:
            amax_y = co.y
        if co.z < amin_z:
            amin_z = co.z
        elif co.z > amax_z:
            amax_z = co.z
    amin = XYZ(amin_x, amin_y, amin_z)
    amax = XYZ(amax_x, amax_y, amax_z)
    center = XYZ ((amin.x+amax.x)/2, (amin.y+amax.y)/2,(amin.z+amax.z)/2);

    #print "================================="       
    #print "Found Object Center:", center
    #print "================================="       
    return center

def get_bounding_box(ob, local=False):
    '''Returns the post modifier stack bounding box for the object'''
    debug(40, "sculpty.get_bounding_box(%s)" % (ob.name))

    mesh = Blender.Mesh.New()
    try:
        mesh.getFromObject(ob, 0, 1)
    except:
        return XYZ(0,0,0), XYZ(0,0,0)
        
    verts = mesh.verts
    if verts == None or len(verts)==0:
        return XYZ(0,0,0), XYZ(0,0,0)
    
    if local:
        scale = getCorrectedScaleValues(ob)
        mesh.transform(Blender.Mathutils.Matrix(
                [scale.x, 0, 0, 0],
                [0, scale.y, 0, 0],
                [0, 0, scale.z, 0],
                [0, 0, 0, 1.0]))
    else:
        mat = ob.getMatrix()
        mesh.transform(remove_rotation(mat))
        
    v0 = mesh.verts[0]
    min_x = v0.co.x
    max_x = min_x
    min_y = v0.co.y
    max_y = min_y
    min_z = v0.co.z
    max_z = min_z

    for v in mesh.verts:
        if v.co.x < min_x:
            min_x = v.co.x
        elif v.co.x > max_x:
            max_x = v.co.x
        if v.co.y < min_y:
            min_y = v.co.y
        elif v.co.y > max_y:
            max_y = v.co.y
        if v.co.z < min_z:
            min_z = v.co.z
        elif v.co.z > max_z:
            max_z = v.co.z

    min = XYZ(min_x, min_y, min_z)
    max = XYZ(max_x, max_y, max_z)
        
    return min, max


def lod_info(width, height, format="LOD%(lod)d: %(x_faces)d x %(y_faces)d\n"):
    '''Returns a string with the lod info for a map size of width * height'''
    debug(40, "sculpty.lod_info(%d, %d, %s)" % (width, height, format))
    info = ""
    for i in [3, 2, 1, 0]:
        faces = float([6, 8, 16, 32][i])
        x_faces, y_faces = lod_size(width, height, i)
        info += format % {'lod': i, 'x_faces': x_faces, 'y_faces': y_faces}
    return info


def lod_size(width, height, lod):
    '''Returns x and y face counts for the given map size and lod'''
    debug(40, "sculpty.lod_size(%d, %d, %d)" % (width, height, lod))
    sides = float([6, 8, 16, 32][lod])
    ratio = float(width) / float(height)
    verts = int(min(0.25 * width * height, sides * sides))
    y_faces = int(sqrt(verts / ratio))
    y_faces = max(y_faces, 4)
    x_faces = verts // y_faces
    x_faces = max(x_faces, 4)
    y_faces = verts // x_faces
    return int(x_faces), int(y_faces)


def map_images(mesh, layer='sculptie', layer2=None):
    '''Returns the list of images assigned to the 'sculptie' UV layer.'''
    debug(40, "sculpty.map_images(%s, %s)" % (mesh.name, layer))
    images = []
    images2 = []
    if layer in mesh.getUVLayerNames():
        currentUV = mesh.activeUVLayer
        mesh.activeUVLayer = layer
        for f in mesh.faces:
            if f.image != None:
                if f.image not in images:
                    images.append(f.image)
                    if layer2 != None:
                        if layer2 in mesh.getUVLayerNames():
                            mesh.activeUVLayer = layer2
                            images2.append(f.image)
                            mesh.activeUVLayer = layer
                        else:
                            images2.append(None)
        mesh.activeUVLayer = currentUV
    if layer2:
        return images, images2
    return images


def map_pixels(width, height, levels=[3, 2, 1, 0]):
    '''Returns ss and ts as lists of used pixels for the given map size.'''
    debug(40, "sculpty.map_pixels(%d, %d)" % (width, height))
    ss = [width - 1]
    ts = [height - 1]
    for i in levels:
        u, v = lod_size(width, height, i)
        for p in vertex_pixels(width, u):
            if p not in ss:
                ss.append(p)
        for p in vertex_pixels(height, v):
            if p not in ts:
                ts.append(p)
    ss.sort()
    ts.sort()
    return ss, ts


def map_size(x_faces, y_faces, levels):
    '''Suggests optimal sculpt map size for x_faces * y_faces * levels

    x_faces - x face count
    y_faces - y face count
    levels - subdivision levels

    returns

    s, t, w, h, cs, ct

    s - x face count
    t - y face count
    w - map width
    h - map height
    cs - True if x face count was corrected
    ct - True if y face count was corrected
    '''
    debug(30, "sculpty.map_size(%d, %d, %d)" % (x_faces, y_faces, levels))
    if (((x_faces == 9 and y_faces == 4) or (x_faces == 4 and y_faces == 9))
        and levels == 0):
        s = x_faces
        t = y_faces
        w = (x_faces - x_faces % 2) * 2
        h = (y_faces - y_faces % 2) * 2
        cs = ct = False
    else:
        try:
            w = int(pow(2, levels + 1 + ceil(log(x_faces) / log(2))))
        except OverflowError:
            w = 256
        try:
            h = int(pow(2, levels + 1 + ceil(log(y_faces) / log(2))))
        except OverflowError:
            h = 256
        while (w * h) > 8192:
            w = w / 2
            h = h / 2
        w, h = face_count(w, h, 32, 32)
        s = min(w, x_faces)
        t = min(h, y_faces)
        w = int(pow(2, levels + 1 + ceil(log(w >> levels) / log(2))))
        h = int(pow(2, levels + 1 + ceil(log(h >> levels) / log(2))))
        #if w == h == 8:
        #    # 8 x 8 won't upload
        #    w = 16
        #    h = 16
        cs = True
        ct = True
        if (s << (levels + 1) > w):
            s = w >> (levels + 1)
        if (t << (levels + 1) > h):
            t = h >> (levels + 1)
        if (s < x_faces):
            cs = False
        if (t < y_faces):
            ct = False
    return s, t, w, h, cs, ct

def dump_image(image):
    for row in range(0, image.size[1]):
        print image.getPixelI(0 , row)[:3], image.getPixelI(image.size[0] -1 , row)[:3] 

def map_type(image):
    '''Returns the sculpt type of the sculpt map image'''
    debug(20, "sculpty.map_type(%s)" % (image.name))
    poles = True
    xseam = True
    yseam = True
    #print "Determine map type from ", image.name
    #dump_image(image)

    p1 = image.getPixelI(0, 0)[:3]
    p2 = image.getPixelI(0, image.size[1] - 1)[:3]
    
    if p1 != p2:
        yseam = False
    for x in range(1, image.size[0]):
        p3 = image.getPixelI(x, 0)[:3]
        p4 = image.getPixelI(x, image.size[1] - 1)[:3]
        if p1 != p3 or p2 != p4:
            poles = False
        if p3 != p4:
            yseam = False
        p1 = p3
        p2 = p4
    for y in range(image.size[1]):
        p1 = image.getPixelI(0, y)[:3]
        p2 = image.getPixelI(image.size[0] - 1, y)[:3]
        if p1 != p2:
            xseam = False
    if xseam:
        if poles:
            return "SPHERE"
        if yseam:
            return "TORUS"
        return "CYLINDER"
    return "PLANE"


#def is_negative_scaled(size):
#    negativeScales = 0
#    for v in size:
#       if v < 0:
#           negativeScales += 1            
#    return negativeScales % 2 == 1

def new_from_map(image, view=True, doTransform=True):
    '''Returns a new sculptie object created from the sculpt map image.'''
    debug(10, "sculpty.new_from_map(%s)" % (image.name))
    Blender.Window.WaitCursor(1)
    in_editmode = Blender.Window.EditMode()
    if in_editmode:
        Blender.Window.EditMode(0)
    else:
        try:
            in_editmode = Blender.Get('add_editmode')
        except:
            pass

    sculpt_type = map_type(image)
    x_faces, y_faces = image.size
    x_faces, y_faces = face_count(x_faces, y_faces, 32, 32)
    multires = 0
    while multires < 2 and x_faces >= 8 and y_faces >= 8 \
        and not ((x_faces & 1) or (y_faces & 1)):
        x_faces = x_faces >> 1
        y_faces = y_faces >> 1
        multires += 1
    scene = Blender.Scene.GetCurrent()
    for ob in scene.objects:
        ob.sel = False
    mesh = new_mesh(image.name, sculpt_type, \
            x_faces, y_faces, clean_lods=False)
    ob = scene.objects.new(mesh, image.name)
    ob.setLocation(Blender.Window.GetCursorPos())
    ob.sel = True
    for f in mesh.faces:
        f.image = image
    mesh.flipNormals()
    if multires:
        mesh.multires = True
        mesh.addMultiresLevel(multires)
    mesh.sel = True
    update_from_map(mesh, image)
    try:
        quat = None
        if Blender.Get('add_view_align') and view:
            quat = Blender.Mathutils.Quaternion(Blender.Window.GetViewQuat())
            if quat:
                mat = quat.toMatrix()
                mat.invert()
                mat.resize4x4()
                ob.setMatrix(mat)
    except:
        pass

    if doTransform:
        try:
            #lx = image.properties['primstar']['loc_x']
            #ly = image.properties['primstar']['loc_y']
            #lz = image.properties['primstar']['loc_z']
            lx = image.properties['primstar']['rloc_x']
            ly = image.properties['primstar']['rloc_y']
            lz = image.properties['primstar']['rloc_z']
        
            loc = ob.getLocation('worldspace')
            ob.setLocation(loc[0] + lx, loc[1] + ly, loc[2] + lz)
    
            sizex = image.properties['primstar']['size_x'] / image.properties['primstar']['multiple_x'] 
            sizey = image.properties['primstar']['size_y'] / image.properties['primstar']['multiple_y'] 
            sizez = image.properties['primstar']['size_z'] / image.properties['primstar']['multiple_z'] 
            size = (sizex,sizey,sizez)
            ob.setSize(size)
    
            #print "use size:", size
    
            rotx = image.properties['primstar']['rot_x']
            roty = image.properties['primstar']['rot_y']
            rotz = image.properties['primstar']['rot_z']
    
            scale = (image.properties['primstar']['scale_x'],
                     image.properties['primstar']['scale_y'],
                     image.properties['primstar']['scale_z'])
    
            #print "use scale: ", scale
            #if is_negative_scaled(scale):
            #    print "add Add pi to rotz of ", ob.getName()
            #    rotz += pi
            #print "use rot  : ", rotx,roty,rotz
            ob.rot = (rotx, roty, rotz)
    
            
            #print "loc:", lx,ly,lz, "rot:", ob.rot, "size:", x,y,z
        except:
            pass
            
    if in_editmode:
        Blender.Window.EditMode(1)
    #Blender.Window.WaitCursor(0)
    return ob

def new_mesh(name, sculpt_type, x_faces, y_faces, levels=0, \
            clean_lods=True, radius=0.25):
    '''Returns a sculptie mesh created from the input

    name - the mesh name
    sculpt_type - one of "SPHERE", "TORUS Z", "TORUS X",
                                   "CYLINDER", "PLANE" or "HEMI"
    x_faces - x face count
    y_faces - y face count
    levels - LOD levels
    clean_lods - aligns UV layout with power of two grid if True
    '''
    debug(10, "sculpty.new_mesh(%s, %s,%d, %d, %d, %d, %f)" % (
            name,
            sculpt_type,
            x_faces,
            y_faces,
            levels,
            clean_lods,
            radius))
    mesh = Blender.Mesh.New(name)
    uv = []
    verts = []
    seams = []
    faces = []
    wrap_x = (sculpt_type != "PLANE") and (sculpt_type != "HEMI")
    wrap_y = (sculpt_type[:5] == "TORUS")
    verts_x = x_faces + 1
    verts_y = y_faces + 1
    actual_x = verts_x - wrap_x
    actual_y = verts_y - wrap_y
    uvgrid_y = []
    uvgrid_x = []
    uvgrid_s = []
    uvgrid_t = []
    s, t, w, h, clean_s, clean_t = map_size(x_faces, y_faces, levels)
    clean_s = clean_s & clean_lods
    clean_t = clean_t & clean_lods
    level_mask = 0xFFFE
    for i in range(levels):
        level_mask = level_mask << 1
    for i in range(s):
        p = w * i / float(s)
        if clean_s:
            p = int(p) & level_mask
        if p:
            p = p / float(w)
        uvgrid_s.append(p)
    uvgrid_s.append(1.0)
    for i in range(t):
        p = h * i / float(t)
        if clean_t:
            p = int(p) & level_mask
        if p:
            p = p / float(h)
        uvgrid_t.append(p)
    uvgrid_t.append(1.0)
    verts_s = s + 1 - wrap_x
    verts_t = t + 1 - wrap_y
    for i in range(verts_t):

        # -------------------------------------------------------------------
        # GC:
        # The profile is the relative z value in the range from 0 to 1
        # For spheres the mesh calculation creates 2 poles at z=0 and z=1
        # But hese poles make trouble when texturing comes into play. Hence
        # we take care that spheres will not get duplicate vertices at the 
        # poles and get slightly opened at their poles.
        # --------------------------------------------------------------------
        profile = float(i) / t
        
        for k in range(verts_s):
            path = float(k) / s
            pos = uv_to_rgb(sculpt_type, path, profile, radius, levels)
            vert = Blender.Mathutils.Vector(
                    pos.x - 0.5, pos.y - 0.5, pos.z - 0.5)
            mesh.verts.extend([vert])
            verts.append(mesh.verts[-1])
        if wrap_x:
            verts.append(mesh.verts[0 - verts_s])
            if i:
                seams.append(((i - 1) * verts_s, i * verts_s))
                if wrap_y:
                    if i == verts_t - 1:
                        seams.append((0, i * verts_s))
    if wrap_y:
        verts.extend(verts[:(s + 1)])
        for x in range(verts_s - 1):
            seams.append((x, x + 1))
        seams.append((0, verts_s - 1))
    for y in range(t):
        offset_y = y * (s + 1)
        for x in range(s):
            faces.append((verts[offset_y + x], verts[offset_y + s + 1 + x],
                    verts[offset_y + s + x + 2], verts[offset_y + x + 1]))
            if wrap_x and x == verts_s - 1 and (y == 0 or y == verts_t -1):
                # blender auto alters vert order - correct uv to match
                uv.append((Blender.Mathutils.Vector(
                        uvgrid_s[x + 1], uvgrid_t[y + 1]),
                        Blender.Mathutils.Vector(uvgrid_s[x + 1], uvgrid_t[y]),
                        Blender.Mathutils.Vector(uvgrid_s[x], uvgrid_t[y]),
                        Blender.Mathutils.Vector(
                            uvgrid_s[x], uvgrid_t[y + 1])))
            else:
                uv.append((Blender.Mathutils.Vector(uvgrid_s[x], uvgrid_t[y]),
                    Blender.Mathutils.Vector(uvgrid_s[x], uvgrid_t[y + 1]),
                    Blender.Mathutils.Vector(uvgrid_s[x + 1], uvgrid_t[y + 1]),
                    Blender.Mathutils.Vector(uvgrid_s[x + 1], uvgrid_t[y])))
    mesh.faces.extend(faces)
    mesh.faceUV = True
    for f in range(len(mesh.faces)):
        mesh.faces[f].uv = uv[f]
    mesh.renameUVLayer(mesh.activeUVLayer, "sculptie")
    if seams != []:
        for e in mesh.findEdges(seams):
            mesh.edges[e].flag = mesh.edges[e].flag | \
                    Blender.Mesh.EdgeFlags.SEAM
    mesh.mode = mesh.mode & ~Blender.Mesh.Modes['TWOSIDED']
    return mesh


def open(filename):
    '''Creates a sculptie object from the image map file'''
    debug(10, "sculpty.open(%s)" % (filename))
    image = Blender.Image.Load(filename)
    image.name = Blender.sys.makename(filename, strip=1)
    image.properties['primstar'] = {}
    image.properties['primstar']['size_x'] = 1.0
    image.properties['primstar']['size_y'] = 1.0
    image.properties['primstar']['size_z'] = 1.0
    return new_from_map(image)


def remove_rotation(matrix):
    t = Blender.Mathutils.TranslationMatrix(matrix.translationPart())
    s = matrix.scalePart()
    m = t * Blender.Mathutils.Matrix(
            [s[0], 0, 0, 0],
            [0, s[1], 0, 0],
            [0, 0, s[2], 0],
            [0, 0, 0, 1.0])
    return m.resize4x4()


def sculptify(ob, fromObjFile=False, force_new_image=False):
    debug(30, "sculpty.sculptify(%s) of type (%s)" % (ob.name,ob.type))
    if ob.type != 'Mesh':
        # add new mesh object
        scene = Blender.Scene.GetCurrent()
        name = ob.getName()
        me = Blender.Mesh.New(name)
        try:
            me.getFromObject(ob)
        except:
            return False # No mesh data
        if me.faces:
            old_ob = ob
            ob = scene.objects.new(me, name)
            ob.setMatrix(old_ob.matrix)
            ob.select(1)
            old_ob.select(0)

    if ob.type == 'Mesh':

        mesh = ob.getData(False, True)

        # =========================================================================
        # GC: If the mesh has got an uv layer named "sculptie", then this object
        # is already a sculptie and we just have to recreate the "sculptie" uv-layer
        # No need to rotate the uv-map because the sculptie is already setup such
        # that rotation is not needed.
        # NOTE: The original behaviour was:
        # If the object has uv layers, no uv layer was added, but the first 
        # available uv layer was renamed to "sculptie"
        # New behaviour: 
        #
        # * If the object has no uv layer at all, it is assumed to be a
        #   non sculptie object that will be transformed to a sculptie object.
        #   a rotation of 90 degree is needed for the uv-map.
        # * If the object has a uv-layer named "sculptie" this layer is removed and 
        #   recreated. The object is recognized as sculpty. No rotation is performed
        #   on the uv-map.
        # * If the object has uv-layers but no layer with name "sculptie" the object
        #   is NOT recognized as sculptie, a "sculptie" uv map is added and a rotation 
        #   by 90 degree is performed on the uv-map
        # ========================================================================
        if fromObjFile==False:
            doRotate=1  # preset to do rotate
            if len(mesh.getUVLayerNames()):
               # object has uv-layers
               if "sculptie" in mesh.getUVLayerNames():
                   # object is a sculptie, no rotation needed
                   # and uv-map removed.
                   print "Remove existing sculptie uv-map from Object", ob.name
                   doRotate=0
                   mesh.removeUVLayer("sculptie")
    
            print "Add new sculptie uv-map to Object ", ob.name
            add_map_uv(ob, doRotate)
            Blender.Redraw()
        else:
            if not len(mesh.getUVLayerNames()):
                print "Import from file: Add new sculptie uv-map to Object", ob.name
                add_map_uv(ob, 1)
                Blender.Redraw()
            if "sculptie" not in mesh.getUVLayerNames():
                print "Import from file: Rename UV-map to 'sculptie' for ", ob.name
                mesh.renameUVLayer(mesh.getUVLayerNames()[0], "sculptie")
        
        mesh.activeUVLayer = "sculptie"
        mesh.update()
        islands = []
        island = None
        zero_uv = Blender.Mathutils.Vector(0.0, 0.0)
        faces = [f for f in mesh.faces]

        if zero_uv not in faces[0].uv:
            #print "Faces reverse ..."
            faces.reverse()
        if zero_uv in faces[0].uv:
            #print "Zero_uv ..."
            for f in faces:
                if zero_uv in f.uv:
                    if island != None:
                        islands.append(island)
                    island = [f.index]
                else:
                    island.append(f.index)
            if island != None:
                islands.append(island)
        else:
            #print "Island append ..."
            islands.append([f.index for f in faces])

        for island in islands:
            #print "island process ..."
            add_image = False
            x_verts = 0
            y_verts = 0
            mesh.sel = False
            for i in island:
                f = mesh.faces[i]
                f.sel = True
                if force_new_image or f.image == None:
                    add_image = True
                for v in f.uv:
                    if v[1] == 0.0:
                        x_verts += 1
                    if v[0] == 0.0:
                        y_verts += 1
            #print "add_image = ", add_image
            #print "ob.modifiers process ..."
            for m in ob.modifiers:
                if m.type == Blender.Modifier.Types.SUBSURF:
                    p = pow(2, m[Blender.Modifier.Settings.RENDLEVELS])
                    x_verts *= p
                    y_verts *= p
            #print "x/y verts process ...: ", x_verts, y_verts
            if min(x_verts, y_verts) < 4:
                if add_image:
                    debug(35, "Unable to add image to %s x %s mesh" % \
                        (x_verts, y_verts))
                    return False # unable to complete
            elif add_image:
                #print "add image ..."
                x_verts = x_verts // 2 + 1
                y_verts = y_verts // 2 + 1
                #print "x/y: ", x_verts, y_verts
                s, t, w, h, cs, ct = map_size(x_verts, y_verts, 0)
                #print "s, t, w, h, cs, ct:", s, t, w, h, cs, ct
                image = create_new_image(mesh.name, w, h, 32)
                print "Created new image:", image.getName(), image.getFilename(), "w:", w, "h:", h
                bake_lod(image)
                set_map(mesh, image)
        Blender.Redraw()
        #print "done ..."
    return True # successful or skipped


def set_alpha(image, alpha):
    '''Sets the alpha channel of the sculpt map image to the alpha image'''
    debug(30, "sculpty.set_alpha(%s, %s)" % (image.name, alpha.name))
    for x in range(image.size[0]):
        u = int(x * alpha.size[0] / image.size[0])
        for y in range(image.size[1]):
            v = int(y * alpha.size[1] / image.size[1])
            c1 = image.getPixelI(x, y)
            c2 = alpha.getPixelI(u, v)
            #print "x,y,c1,c2",x,y,c1,c2
            c1[3] = (c2[0]+c2[1]+c2[2]+c2[3])/4
            image.setPixelI(x, y, c1)


#*********************************************************************
# Helper function set_selected_object_center()
#
# This function will first check if the object has got children.
# Then it recursively processes all children first. While this is
# done the parent-child relation will be temporarily removed. This
# is necessary because otherwise the children would jump away from
# their locations.
# When the recursive processing is finished, proceed with the 
# base object (ob) itself and actually set_center() for this object.
# finally if a parent/child relation was removed before, then put it
# back again.
# Note I:
# There is a bug in blender which let children jump away from their
# location even if the parent/child relation has been removed. As soon
# as the parent child relation is reestablished the jump occurs. I 
# believe that this is because of some missing internal data update
# in blender. This update can be forced by calling Blender.Redraw()
# And this is the reason why i added a Blender.Redraw() call just 
# before ob.makeParent() see below.
#*********************************************************************
def set_selected_object_center(ob, scene, processed_elements):
    #print "set_object_center() started"

    # Decouple all children (if any) we will take care of them later
    # That keeps the children from moving to wrong locations
    children = obChildren(ob)
    hasChildren = len(children) > 0
    if hasChildren:
        # Process all children (also the non selected !)
        # I do this because i might have selected childrens children
        # and in order to preserve children first policy i am tracking
        # the entire children list:

        for c in children:
            #print "set_object_center() Processing child ", c.getName()
            
            #size   = c.getSize()
            
            #negativeScales = 0
            #for v in size:
            #   if v < 0:
            #       negativeScales += 1            
            #if negativeScales % 2 == 1:
            #    tsize = (size[0]/abs(size[0]), size[1]/abs(size[1]), size[2]/abs(size[2]))
            #    c.setSize(tsize)
            c.clrParent(2, 0)
            #if negativeScales % 2 == 1:
            #    c.setSize(size)
                
            
            if processed_elements.get(c.getName()) is None:
                #print "set_object_center() child ", c.getName(), " not yet processed"
                #print "Dictionary is :", processed_elements
                set_selected_object_center(c, scene, processed_elements)

    # Now i am at the action point. Here the set_center() will be performed
    # but note that i potentially may have unselected object here from a
    # recursive call of this function. Hence i need to check if the current object
    # is a sculpty and is selected. Only then i actually call the set_center() function

    #print "set_object_center() add ", ob.getName(), " to processed_elements"
    processed_elements[ob.getName()]=ob
    if ob.isSelected() and check(ob):
        #print "set_object_center() call set_center() for: ", ob.getName()
        set_center(ob)

    # If this object has children, then the parent/child relation must be
    # reestablished now.
    # Note: the Blender.Redraw() before ob.makeParent() is necessary to 
    # prevent unwanted jumping of child objects. This IS ugly! But i 
    # have but found a better way to go:
    if hasChildren:
        #print "Blender.Redraw() for childset of ", ob.getName()
        Blender.Redraw()
        ob.makeParent(children,0,0)

    # Note: If this object has Children, then i have reestablished
    # the parent/child relation. Then i MUST do a Blender.Redraw() after the
    # ob.makeParent(). But because this is a very expensive function, i only
    # want to do that once after the complete object hierarchy has been processed
    # and that is the reason why i pass up hasChildren to the caller. So the
    # caller knows if an additional call to Blender.Redraw() is needed
    return hasChildren

#*********************************************************************
# Helper function set_selected_object_centers()
#
# iterates over all selected objects and adjusts the object center
# to the geometric center. This function shall only be called when 
# keep_center is NOT(!) enabled in the GUI (we do not check this here)
#
# Note I:
# The called function set_selected_object_center() will recursively
# set all selected object children. So we will end up in processing
# some objects twice (once in the recursive call to 
# set_selected_object_center() and once in the main loop here).
# Therefore i have added a dictionary "processed_elements" which 
# contains all processed objects. Thus i can ensure that each object 
# will be processed exactly once. See in the comments below.
#
# Note II:
# During recursive processing it can hapen that the parent-child
# association gets temporary disabled. Due to a bug in blender the
# dotted lines between parent and children will be temporary removed
# from the 3D view. In order to get them back into the 3D view after
# this function has finished, we need to perform a Blender.Redraw() 
# Therefore this function returns a boolean value "needUpdate" when 
# this situation occurs (chilren needed to be temporarily diconnected
# from parent)
#**********************************************************************
def set_selected_object_centers(scene):
    #print "center selected objects..."
    needUpdate = False;
    #print "set_selected_object_centers() processing center objects ..."
    processed_elements = {}
    for ob in scene.objects.selected:
        #print "set_selected_object_centers() Found selected object ", ob.getName()
        if check(ob):
            #print "set_selected_object_centers() Processing selected object as sculptie..."
            if processed_elements.get(ob.getName()) is None:
                #print "set_selected_object_centers() object ", ob.getName(), " not yet processed"
                needUpdate = set_selected_object_center(ob, scene, processed_elements) or needUpdate

    # needUpdate will contain True when at least one object in the selection has got children.
    # And in that case i must update the view after all objects have been processed.
    # if no object has children, then there is no need for updating the view.
    if needUpdate:
        #print "Final Redraw after set_selected_object_centers."
        Blender.Redraw()

#*************************************************************************
# This function returns the geometric object center (bounding box center)
# in absolute coordinates.
# Note I: I have used a trick to ensure a 6 digit precision in the fraction
# part of the numbers while i am summing up. Otherwise i sometimes can see 
# slight shifts of the objects. 6 digit precision however seems sufficient.
#
# Note II: I can use the weighted vector sum here because the 8 provided
# vectors are the corners of the bounding box. So the algorythm returns the
# exact center of the BoundingBox. I use this method because it is the
# only way to get a reliable object center even when the object scalings
# are negative!
#*************************************************************************
def get_object_world_center(ob):
    #print "================================="       
    bb = ob.boundingBox
    
    vectorsum = XYZ(0,0,0)
    for co in bb:
        vectorsum.x += 1000000 * co[0]
        vectorsum.y += 1000000 * co[1]
        vectorsum.z += 1000000 * co[2]
    center = XYZ (vectorsum.x/8000000, vectorsum.y/8000000, vectorsum.z/8000000 );

    #print "================================="       
    #print "Found Object Center:", center
    #print "================================="       
    return center

#******************************************************************
# The documentation says only positive scale values.
# But we get negative values here. And they seem to be wrong when
# negative scales (e.g. via a call to "s x -1" ) are involved.
# So i calculate them here by myself:
#******************************************************************
def getCorrectedScaleValues(ob):
    mat = ob.getMatrix()
    
    scaleValues = mat.scalePart()

    scaleValues = XYZ(abs(scaleValues.x),
                      abs(scaleValues.y),
                      abs(scaleValues.z))
    #print "scale values:",scaleValues

    # From here we get the true signs:
    size      = ob.getSize()
    scaleSign = XYZ(size[0] / abs(size[0]), 
                            size[1] / abs(size[1]),
                            size[2] / abs(size[2]))
    #print "scale sign  :",scaleSign

    # And this is the final corrected scaling:
    scale = XYZ(scaleValues.x * scaleSign.x,
                        scaleValues.y * scaleSign.y,
                        scaleValues.z * scaleSign.z)
    #print "scale       :",scale
    return scaleValues
    #return scale

#**********************************************************************
# Scripted equivalent to "Object -> Transform -> Center New"
# 
# Very important: This function strongly assumes that the given object 
# has no children!!! You MUST take care of this in the calling function.
# For more information see function set_selected_object_center()
#**********************************************************************
def set_center(ob, offset=XYZ(0.0, 0.0, 0.0)):
    '''Updates object center to middle of mesh plus offset

    ob - object to update
    offset - (x, y, z) offset for mesh center
    '''

    debug(30, "sculpty.set_center(%s, %s)" % (ob.name, str(offset)))
               
    # Determine where the object center SHOULD be. This is stored in
    # moveto_absolute. Then find out the delta between the curret location
    # and the destination location. this is stored in offset_absolute:
    fromloc = ob.getLocation()
    moveto_absolute = get_object_world_center(ob)
    offset_absolute = offset + XYZ(offset.x + moveto_absolute.x - fromloc[0],
                                   offset.y + moveto_absolute.y - fromloc[1],
                                   offset.z + moveto_absolute.z - fromloc[2] )

    # Now we have to perfrom some transformation magic because the object
    # might have been rotated and scaled and moved in object mode. So we have
    # to go through this here: first determine the local bbox center. and add
    # it to the given offset value (which in most cases is <0,0,0> I guess, the
    # offset is used fr some future enhancements ?
    bb = BoundingBox(ob, True)
    offset += bb.center

    # Here i get the mesh data. This date will be manipulated such that its geometric
    # center will be placed exactly to the CURRENT(!) object center. That is not yet
    # the target location of the object (see below)
    # Also see that i get a corrected scaling. I believe the scaling is calculated
    # completely wrong when negative scale values are involved. Also see the coments
    # in the getCorrectedScaleValues() function
    mesh = ob.getData()
    scale = getCorrectedScaleValues(ob)

    # Here the transformation is calculated.
    # This transformation basically rotates/moves
    # the mesh to its current object center:
    mat = ob.getMatrix()
    rot_quat = mat.toQuat()
    rot = rot_quat.toMatrix().resize4x4().invert()

    scaledOffset = Blender.Mathutils.Vector ( offset.x / scale.x , 
                                              offset.y / scale.y , 
                                              offset.z / scale.z )

    trans_mat = Blender.Mathutils.TranslationMatrix( scaledOffset *-1.0 ) * rot
    mesh.transform(trans_mat)

    # Now the mesh is moved to its current object center. We needed to revert 
    # the rotation because otherwise we would not end at the correct location. 
    # But of course we want the rotation back now and finally update the mesh.
    rot.invert()
    mesh.transform(rot)
    mesh.update()

    # Now the mesh is almost where we want it to be. It is now correctly rotated 
    # and its geometric center matches the current object center. Now we only need 
    # to move the entire object to its target.
    #
    # Note I: If you now are going to argument that all this could have been done with
    # the original atrix rotation stuff, then i am sorry to tell you that this does only
    # work for objects with positive scale values. With negative scale values there 
    # seem to be some quirks in the Blender-kernel which lead to completely wrong target
    # locations. The method i use here is the most stable (and for me also the simplest 
    # understandable) method i could find.

    toloc     = (fromloc[0] + offset_absolute.x,
                 fromloc[1] + offset_absolute.y,
                 fromloc[2] + offset_absolute.z )
    ob.setLocation(toloc)
    #print "move object ", " from:", fromloc, " to: ", toloc, "(",ob.getName(),")"


def set_map(mesh, image):
    '''Assigns the image to the selected 'sculptie' uv layer faces.'''
    debug(30, "sculpty.set_map(%s, %s)" % (mesh.name, image.name))
    currentUV = mesh.activeUVLayer
    mesh.activeUVLayer = "sculptie"
    if mesh.multires:
        levels = mesh.multiresDrawLevel
        mesh.multiresDrawLevel = 1
    for f in mesh.faces:
        if f.sel:
            f.image = image
    if mesh.multires:
        mesh.multiresDrawLevel = levels
    mesh.activeUVLayer = currentUV


def update_from_map(mesh, image):
    '''Updates the mesh to locations from the sculpt map image'''
    debug(30, "sculpty.update_from_map(%s, %s)" % (mesh.name, image.name))
    currentUV = mesh.activeUVLayer
    if "sculptie" in mesh.getUVLayerNames():
        mesh.activeUVLayer = "sculptie"
    verts = range(len(mesh.verts))
    for f in mesh.faces:
        for vi in range(len(f.verts)):
            if f.verts[vi].index in verts:
                verts.remove(f.verts[vi].index)
                if f.verts[vi].sel:
                    u = round(f.uv[vi].x, 12)
                    v = round(f.uv[vi].y, 12)
                    u = int(round(u * image.size[0]))
                    v = int(round(v * image.size[1]))
                    if u == image.size[0]:
                        u = image.size[0] - 1
                    if v == image.size[1]:
                        v = image.size[1] - 1
                    p = image.getPixelF(u, v)
                    x = p[0] - 0.5
                    y = p[1] - 0.5
                    z = p[2] - 0.5
                    f.verts[vi].co = Blender.Mathutils.Vector(x, y, z)
    mesh.activeUVLayer = currentUV
    mesh.sel = True


def uv_to_rgb(sculpt_type, u, v, radius=0.25, levels=0):
    '''Returns 3D location for the given UV co-ordinates on a
    default sculpt type'''
    debug(90, "sculpty.uv_to_rgb(%s, %f, %f, %f)" % \
            (sculpt_type, u, v, radius))
    a = pi + 2 * pi * u
    if sculpt_type == "SPHERE":
        # GC:
        # We have seen that singularities at the poles (duplicate vertices)
        # also create weird effects when texturing. So the
        # spheres get tiny little holes at the poles to avoid mathematical
        # precision problems during texturing. This is not a problem in general,
        # because SL closes the spheres at the poles automatically.
        # The correction values for profile have been determined heuristically.
        #
        # Another correction concerns the position of the poles when Multires or
        # Subsurf is turned on. For some reason the poles keep their position
        # and thus they get pointy and create a lemon like shape. The simplest
        # correction is to shift the poles into the direction of the sphere center 
        # by a tiny fraction. The levelCorrection factor has been determined 
        # heuristically.
        #
        # NOTE: Multires/Subsurf levels above 2 create heavily distorted results.
        # this needs to be checked further. If you need higher levels, the workaround is:
        # Create a level 2 sculptie, then add levels as needed manually.

        levelCorrection = 1
        if  v == 1.0 or v == 0.0 :
            levelCorrection = 0.98**(levels)

        ps = sin(pi * v) / 2.0
        r = 0.5 + sin(a) * ps
        g = 0.5 - cos(a) * ps
        b = 0.5 - levelCorrection * cos(pi * v) / 2.0
    elif sculpt_type == "CYLINDER":
        r = 0.5 + sin(a) / 2.0
        g = 0.5 - cos(a) / 2.0
        b = v
    elif sculpt_type == "TORUS Z":
        v += 0.25
        ps = ((1.0 - radius) - sin(2.0 * pi * v) * radius) / 2.0
        r = 0.5 + sin(a) * ps
        g = 0.5 - cos(a) * ps
        b = 0.5 + cos(2 * pi * v) / 2.0
    elif sculpt_type == "TORUS X":
        a = pi + 2 * pi * v
        u += 0.25
        ps = ((1.0 - radius) - sin(2.0 * pi * u) * radius) / 2.0
        r = 0.5 + cos(2 * pi * u) / 2.0
        g = 0.5 - cos(a) * ps
        b = 0.5 + sin(a) * ps
    elif sculpt_type == "HEMI":
        z = cos(2 * pi * min(u, v, 1.0 - u, 1.0 - v)) / -2.0
        pa = u - 0.5
        pr = v - 0.5
        ph = sqrt(pa * pa + pr * pr)
        ps = sqrt(sin((0.5 - z) * pi * 0.5) / 2.0)
        if ph == 0.0:
            ph = 1.0
        sr2 = sqrt(2.0)
        r = 0.5 + (pa / ph * ps) / sr2
        g = 0.5 + (pr / ph * ps) / sr2
        b = 0.5 + z
    else:
        r = u
        g = v
        b = 0.5
    return XYZ(r, g, b)


def vertex_pixels(size, faces):
    '''Returns a list of pixels used for vertex points on map size'''
    debug(50, "sculpty.vertex_pixels(%d, %d)" % (size, faces))
    pixels = [int(size * i / float(faces)) for i in range(faces)]
    pixels.append(faces - 1)
    return pixels
