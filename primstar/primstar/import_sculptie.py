#!BPY

"""
Name: 'Second Life Sculptie (.tga, .png, .obj, .dae)'
Blender: 246
Group: 'Import'
Tooltip: 'Import Second Life sculptie from image, obj, or Collada 1.4 files'
"""

__author__ = ["Domino Marama"]
__url__ = ("Online Help, http://dominodesigns.info/manuals/primstar/import-sculptie")
__version__ = "1.0.0"
__bpydoc__ = """\

Sculptie Importer

This script creates a sculptie object from a Second Life sculptie map or meshes
in obj and Collada 1.4 formats.
"""

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
from primstar import sculpty
from colladaImEx.translator import Translator
try:
    from import_obj import load_obj
except ImportError:
    try:
        from blender.import_obj import load_obj
    except ImportError:
        print """Debian and Ubuntu users should run 'sudo touch /usr/share/blender/scripts/blender/__init__.py' to allow import of Blender scripts"""
        raise


def import_collada(filename):
    t = Translator(True, '0.3.161', False, filename,
            False, False, False, False, True, False, False, True,
            False, False, False, False, True, False)
    sculptify_scene()


def import_obj(filename):
    load_obj(filename)
    sculptify_scene()


def sculptify_scene():
    scene = Blender.Scene.GetCurrent()
    for ob in scene.objects.selected:
        if not sculpty.sculptify(ob, fromObjFile=True):
            Blender.Draw.PupBlock("Sculptie Import Error",
                    ["Unable to determine map size", "Please check your UVs"])
        else:
            if ob.type == 'Mesh':
                scene.objects.active = ob

#***********************************************
# load sculptie file
#***********************************************


def load_sculptie(filename):
    time1 = Blender.sys.time()
    Blender.SaveUndoState("Import Sculptie")
    #print "--------------------------------"
    print 'Importing "%s"' % filename
    scene = Blender.Scene.GetCurrent()
    for ob in scene.objects.selected:
        ob.sel = False
    in_editmode = Blender.Window.EditMode()
    # MUST leave edit mode before changing an active mesh:
    if in_editmode:
        Blender.Window.EditMode(0)
    else:
        try:
            in_editmode = Blender.Get('add_editmode')
        except:
            pass
    f, e = Blender.sys.splitext(filename)
    e = e.lower()
    if e == '.dae':
        import_collada(filename)
    elif e == '.obj':
        import_obj(filename)
    else:
        try:
            ob = sculpty.open(filename)
        except:
            Blender.Draw.PupBlock("Sculptie Import Error",
                    ["Unsupported file type", "Use .dae or an image file"])
    if in_editmode:
        Blender.Window.EditMode(1)
    Blender.Redraw()
    print 'Loaded Sculptmap "%s" in %.4f sec.' % (
            filename, (Blender.sys.time() - time1))

#***********************************************
# register callback
#***********************************************


def my_callback(filename):
    load_sculptie(filename)


if __name__ == '__main__':
    Blender.Window.FileSelector(my_callback, "Import Sculptie")
