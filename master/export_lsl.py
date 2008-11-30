#!BPY

"""
Name: 'Second Life LSL (to dir)'
Blender: 245
Group: 'Export'
Tooltip: 'Export lsl and tga files for Second Life (to dir)'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.07"
__bpydoc__ = """\

LSL Exporter

This script exports Second Life sculpties in lsl + tga files
"""

#Changes:
#0.07
# BETLOG Hax 2008-10-22
#- added PRIM_POSITION and altered output LSL  to include offsets when in a linkset
#0.06 Domino Marama 2008-07-09
#- minor bug fixes
#0.05 Domino Marama 2008-06-29
#- LSL now removes used items from prim contents
#0.04 Domino Marama 2008-06-29
#- ALL_FACES bug in lsl fixed
#0.03 Domino Marama 2008-06-28
#- missed quotes in lsl for texture
#0.02 Domino Marama 2008-06-28
#- refactored
#- added basic texture support
#0.01 Domino Marama 2008-06-27
#- initial version

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) Domino Designs Limited
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
from render_sculptie import updateSculptieMap, scaleRange

#***********************************************
# classes
#***********************************************
class prim:
    def __init__( self, name ):
        self.name = name
        self.children = []
        self.textures = []
        self.primtype = 0
        self.sculpttype = 0
        self.sculptimage = None
        self.meshscale = ( 1.0, 1.0, 1.0 )
        self.scale = ( 1.0, 1.0, 1.0 )
        self.rotation = ( 0.0, 0.0, 0.0, 1.0 )
        self.location = ( 0.0, 0.0, 0.0 )

    def fromOb( self, ob ):
        self.primtype = ob.getProperty( 'LL_PRIM_TYPE' ).getData()
        r = ob.getMatrix().rotationPart().invert().toQuat()
        self.rotation = ( r[1], r[2], r[3], r[0] )
        if self.primtype == 7:
            self.sculpttype = ob.getProperty( 'LL_SCULPT_TYPE' ).getData()
            mesh = ob.getData( False, True )
            ms = scaleRange( [ ob ], True )
            ms = ( ms.x, ms.y, ms.z )
            currentUV = mesh.activeUVLayer
            if "sculptie" in mesh.getUVLayerNames():
                mesh.activeUVLayer = "sculptie"
                mesh.update()
                image = mesh.faces[0].image
                if image:
                    filebase = Blender.sys.basename( image.name )
                    if filebase[-4:] in [ ".tga", ".TGA" ]:
                        si = Blender.sys.splitext(filebase)[0]
                    else:
                        si = filebase
                    self.sculptimage = texture( si, image )
                    if 'scale_x' in image.properties:
			    ms = ( ms[0] / image.properties['scale_x'],
				ms[1] / image.properties['scale_y'],
				ms[2] / image.properties['scale_z'] )
                else:
                    self.sculptimage = None
            if "UVTex" in mesh.getUVLayerNames():
                mesh.activeUVLayer = "UVTex"
                mesh.update()
                image = mesh.faces[0].image
                if image:
                    filebase = Blender.sys.basename( image.filename )
                    if filebase[-4:] in [ ".tga", ".TGA" ]:
                        newtex = texture( Blender.sys.splitext(filebase)[0], image )
                    else:
                        newtex = texture( filebase, image )
                    self.textures.append( newtex )
            mesh.activeUVLayer = currentUV
            mesh.update()
            self.location = ( ob.loc[0], ob.loc[1], ob.loc[2] )
            self.scale = ( ob.SizeX * ms[0], ob.SizeY * ms[1], ob.SizeZ * ms[2] )

    def toLSL( self, prefix = "" ):
        pt = ["missing","missing","missing","missing","missing","missing","missing","SCULPT"][ self.primtype ]
        st = ["NONE", "SPHERE", "TORUS", "PLANE", "CYLINDER"][self.sculpttype]
        lsl = prefix + "list params = [\n\t\t\tPRIM_TYPE, PRIM_TYPE_%s, "%( pt )
        if self.primtype == 7:
            st = ["NONE", "SPHERE", "TORUS", "PLANE", "CYLINDER"][self.sculpttype]
            lsl += "\"%s\", PRIM_SCULPT_TYPE_%s "%( self.sculptimage.name, st )
        lsl += "\n\t\t\t,PRIM_SIZE, < %.5f, %.5f, %.5f > "%( self.scale )
        lsl += "\n\t\t\t,PRIM_ROTATION, < %.5f, %.5f, %.5f, %.5f >"%( self.rotation )
        lsl += "\n\t\t];"
        lsl += "\n\t\tif (llGetLinkNumber() > 1)"
        lsl += "\n\t\t\tparams += [PRIM_POSITION, < %.5f, %.5f, %.5f > ];\n"%( self.location )
        for t in self.textures:
            lsl += ", " + t.toLSL()
        lsl += prefix + "\tllSetObjectName( \"%s\" );\n\t\tllSetPrimitiveParams(params);\n"%( self.name )
        return lsl

class texture:
    def __init__( self, name, image = None ):
        self.name = name
        self.image = image
        self.offset = ( 0.0, 0.0 )
        self.repeat = ( 1.0, 1.0 )
        self.rotation = 0.0
        if name == "UVTex":
            self.face = 0
        elif name[:5] == "UVTex":
            self.face = int( name[6:] )
        else:
            self.face = -1

    def toLSL( self ):
        lsl = "PRIM_TEXTURE, "
        if self.face == -1:
            lsl += "ALL_SIDES, "
        else:
            lsl += str( self.face ) + ", "
        lsl += "tK" + str( self.face ) + ", "
        lsl += "<" + str( self.repeat[0] ) + ", " + str( self.repeat[1] ) + ", 0.0>, "
        lsl += "<" + str( self.offset[0] ) + ", " + str( self.offset[1] ) + ", 0.0>, "
        lsl += str( self.rotation )
        return lsl

    def saveImageAs( self, filename ):
        oldfile = self.image.filename
        self.image.filename = filename
        self.image.save()
        self.image.filename = oldfile

#***********************************************
# simple export to .lsl files + .tga images
#***********************************************

def export_lsl( filename ):
    Blender.Window.WaitCursor(1)
    prims = []
    basepath = Blender.sys.dirname( filename )
    scene = Blender.Scene.GetCurrent()
    for ob in scene.objects.selected:
        # collect prims
        if ob.type == 'Mesh':
            try:
                primtype = ob.getProperty( 'LL_PRIM_TYPE' ).getData()
            except:
                continue
            newprim = prim( ob.name )
            newprim.fromOb( ob )
            if newprim.primtype == 7 and newprim.sculpttype > 0:
                if newprim.sculptimage == None:
                    sn = updateSculptieMap( ob )
                    newprim.sculptimage = texture( sn , Blender.Image.Get( sn ) )
            prims.append( newprim )

    # save prims
    for p in prims:
        lsl_t_h = ""
        if p.sculptimage:
            p.sculptimage.saveImageAs( Blender.sys.join( basepath, p.sculptimage.name + ".tga" ) )
        i = 0
        for t in p.textures:
            t.saveImageAs( Blender.sys.join( basepath, t.name + ".tga" ) )
            lsl_t_h += "\t\tkey tK" + str( t.face ) + " = llGetInventoryKey( \"" + t.name + "\" );\n"
            lsl_t_h += "\t\tllRemoveInventory( \"" + t.name + "\" );\n"
        lsl =  "string tS;\ndefault\n{\ton_rez(integer start_param)\n\t{\tllResetScript();\n\t}\n\tstate_entry()\n\t{"
        lsl += lsl_t_h + p.toLSL( "\t" )
        if p.sculptimage:
            lsl += "\t\tllRemoveInventory( \"" + p.sculptimage.name +"\" );\n"
        lsl += "\t\tllRemoveInventory( tS = llGetScriptName() );\n\t\tllSetScriptState( tS, FALSE );\n\t}\n\tchanged(integer change)\n\t{\tif (change & CHANGED_LINK)\n\t\t\tllResetScript();\n\t}\n}"
        f = open( Blender.sys.join( basepath, p.name + ".lsl" ), 'w' )
        f.write( lsl )
        f.close()

    Blender.Window.WaitCursor(0)

#***********************************************
# register callback
#***********************************************
def my_callback(filename):
    export_lsl(filename)

if __name__ == '__main__':
    Blender.Window.FileSelector(my_callback, "Export LSL", '.')


