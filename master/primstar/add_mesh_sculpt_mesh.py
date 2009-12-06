#!BPY
"""
Name: 'Sculpt Mesh'
Blender: 246
Group: 'AddMesh'
Tooltip: 'Add a Second Life sculptie compatible mesh'
"""

__author__ = ["Domino Marama", "Gaia Clary"]
__url__ = ("Online Help, http://dominodesigns.info/manuals/primstar/create-sculptie")
__version__ = "0.90"
__bpydoc__ = """\

Sculpt Mesh

This script creates an object with a gridded UV map suitable
for Second Life sculpties.
"""

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
# Inc., 59 Temple Place - Suite 330, Boston, maximum  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

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


class MenuMap(sculpty.LibFile):

    def get_command(self, app):

        def new_command():
            app.set_shape(self.local_path, self.path)
        return new_command


class MenuDir(sculpty.LibDir):

    def add_to_menu(self, app, menu):
        for f in self.files:
            menu.add_command(label=f.name, command=f.get_command(app))
        if self.dirs and self.files:
            menu.add_separator()
        for d in self.dirs:
            submenu = gui.Menu(menu, tearoff=0)
            d.add_to_menu(app, submenu)
            menu.add_cascade(label=d.name, menu=submenu)


class GuiApp:

    def __init__(self, master):
        self.master = master
        self.cube_icon = gui.BitmapImage(data="""#define cube_width 16
#define cube_height 16
static unsigned char cube_bits[] = {
   0x00, 0x00, 0x80, 0x03, 0x70, 0x1c, 0x8c, 0x62, 0x94, 0x53, 0x64, 0x4c,
   0xa4, 0x4b, 0x2c, 0x69, 0x34, 0x59, 0x64, 0x4d, 0xa4, 0x4b, 0x2c, 0x69,
   0x30, 0x19, 0x40, 0x05, 0x80, 0x03, 0x00, 0x00 };
""")
        self.file_icon = gui.BitmapImage(data="""#define file_open_width 16
#define file_open_height 16
static unsigned char file_open_bits[] = {
   0x00, 0x00, 0x08, 0x00, 0x0c, 0x00, 0xfe, 0x01, 0x0c, 0x02, 0x08, 0x04,
   0x00, 0x04, 0xf0, 0x00, 0x08, 0x7f, 0xf8, 0x40, 0x08, 0x40, 0x08, 0x40,
   0x08, 0x40, 0x08, 0x40, 0xf8, 0x7f, 0x00, 0x00 };
""")

        # ==========================================
        # Main window frame
        # ==========================================

        top_frame = gui.Frame(self.master, border=4)
        top_frame.pack()
        frame = gui.LabelFrame(top_frame,
                text=LABEL,
                labelanchor=NW)
        frame.pack()

        # ==========================================
        # Settings frame
        # ==========================================

        shape_frame = gui.Frame(frame)
        shape_frame.pack(fill=X)
        t = gui.Label(shape_frame,
                text="Shape",
                justify=RIGHT,
                font=('Helvetica', 9, 'bold'))
        t.pack(side=LEFT)
        self.shape_name = StringVar(self.master)
        self.shape_name.set(settings['shape_name'])
        self.shape_file = settings['shape_file']
        self.map_type = gui.Button(shape_frame,
                textvariable=self.shape_name,
                command=self.set_map_type,
                cursor='based_arrow_down',
                background=gui.hex_color(gui.theme.ui.textfield),
                relief=SUNKEN,
                pady=1,
                anchor=NW)
        self.map_type.pack(expand=True, fill=X, side=LEFT)
        file_button = gui.Button(shape_frame,
                image=self.file_icon,
                compound=LEFT,
                command=self.set_file,
                default=ACTIVE)
        file_button.pack(side=RIGHT)

        # ==========================================
        # Geometry section
        # ==========================================

        f = gui.LabelFrame(frame,
                text="Geometry")
        f.pack(side=LEFT, fill=Y)
        fx = gui.Frame(f)
        fx.pack(expand=True)
        t = gui.Label(fx,
            text="X Faces",
            justify=RIGHT)
        t.pack(side=LEFT)
        self.x_faces = IntVar(self.master)
        self.x_faces.set(settings['x_faces'])
        self.x_faces_input = gui.Spinbox(fx,
                textvariable=self.x_faces,
                from_=1,
                to=256,
                width=3,
                command=self.update_info)
        self.x_faces_input.bind('<Key>', self.update_info)
        self.x_faces_input.pack(side=RIGHT)
        fy = gui.Frame(f)
        fy.pack(expand=True)
        t = gui.Label(fy,
                text="Y Faces",
                justify=RIGHT)
        t.pack(side=LEFT)
        self.y_faces = IntVar(self.master)
        self.y_faces.set(settings['y_faces'])
        self.y_faces_input = gui.Spinbox(fy,
                textvariable=self.y_faces,
                from_=1,
                to=256,
                width=3,
                command=self.update_info)
        self.y_faces_input.bind('<Key>', self.update_info)
        self.y_faces_input.pack(side=RIGHT)
        fr = gui.Frame(f)
        fr.pack(expand=True)
        t = gui.Label(fr,
                text="Radius",
                justify=RIGHT)
        t.pack(side=LEFT)
        self.radius = DoubleVar(self.master)
        self.radius.set(settings['radius'])
        self.radius_input = gui.Spinbox(fr,
                textvariable=self.radius,
                from_=0.05,
                to=0.5,
                increment=0.025,
                format="%4.3f",
                width=5)
        self.radius_input.pack(side=RIGHT)
        self.clean_lods = BooleanVar(self.master)
        self.clean_lods.set(settings['clean_lods'])
        self.clean_lods_input = gui.Checkbutton(f,
                text="Clean LODs",
                variable=self.clean_lods,
                command=self.update_info)
        self.clean_lods_input.pack(expand=True)

        # ==========================================
        # Subdivision section
        # ==========================================

        middle_frame = gui.Frame(frame)
        middle_frame.pack(side=LEFT, padx=4, fill=BOTH)
        fs = gui.LabelFrame(middle_frame,
                text="Subdivision")
        fs.pack(fill=X)
        self.levels = IntVar(self.master)
        self.levels.set(settings['levels'])
        fl = gui.Frame(fs)
        fl.pack()
        t = gui.Label(fl,
                text="Levels",
                justify=RIGHT)
        t.pack(side=LEFT)
        self.levels_input = gui.Spinbox(fl,
                textvariable=self.levels,
                from_=0,
                to=6,
                width=3,
                command=self.update_info)
        self.levels_input.bind('<Key>', self.update_info)
        self.levels_input.pack(side=RIGHT)
        self.sub_type = IntVar(self.master)
        self.sub_type.set(settings['sub_type'])
        r = gui.Frame(fs)
        r.pack(side=LEFT)
        gui.Radiobutton(r,
                text="Subsurf",
                variable=self.sub_type,
                value=1).pack()
        gui.Radiobutton(r,
                text="Multires",
                variable=self.sub_type,
                value=0).pack()
        self.subdivision = IntVar(self.master)
        self.subdivision.set(settings['subdivision'])
        r = gui.Frame(fs)
        r.pack(side=RIGHT)
        gui.Radiobutton(r,
                text="Catmull",
                variable=self.subdivision,
                value=1).pack()
        gui.Radiobutton(r,
                text="Simple",
                variable=self.subdivision,
                value=0).pack()

        # ==========================================
        # Mesh Type Selection
        # ==========================================

        mesh_frame = gui.LabelFrame(middle_frame, text="Mesh Type")
        mesh_frame.pack(fill=X)
        self.quads = IntVar(self.master)
        self.quads.set(settings['quads'])
        gui.Radiobutton(mesh_frame,
                text="Quads",
                variable=self.quads,
                value=1).pack(side=LEFT)
        gui.Radiobutton(mesh_frame,
                state=DISABLED,
                text="Triangles",
                variable=self.quads,
                value=0).pack(side=LEFT)

        # ==========================================
        # LOD display and Create button
        # ==========================================

        build_frame = gui.Frame(frame)
        build_frame.pack(fill=Y, side=LEFT)
        self.info_text = StringVar(self.master)
        self.info_frame = gui.LabelFrame(build_frame)
        self.info_frame.pack()
        self.lod_display = gui.Label(self.info_frame,
                textvariable=self.info_text,
                justify=LEFT)
        self.lod_display.pack()
        self.create_button = gui.Button(build_frame,
                text="Build",
                image=self.cube_icon,
                compound=LEFT,
                command=self.add,
                default=ACTIVE)
        self.create_button.pack(fill=BOTH, expand=True, anchor=SE, pady=5)
        self.update_info()

        # ==========================================
        # Save settings frame
        # ==========================================

        self.save_defaults = BooleanVar(self.master)
        self.save_defaults.set(False)
        self.save_settings = BooleanVar(self.master)
        self.save_settings.set(settings['save'])
        save_frame = gui.Frame(build_frame)
        save_frame.pack(fill=Y)
        t = gui.Checkbutton(save_frame,
                text="Save",
                variable=self.save_settings)
        t.pack(side=LEFT)
        t = gui.Checkbutton(save_frame,
                text="Defaults",
                variable=self.save_defaults)
        t.pack(side=LEFT)

        # ==========================================
        # Popup menu for base mesh shape
        # ==========================================

        self.sculpt_menu = gui.Menu(self.master, tearoff=0)
        for sculpt_type in ["Cylinder", "Hemi", "Plane",
                "Sphere", "Torus X", "Torus Z"]:

            def type_command(sculpt_type):

                def new_command():
                    self.set_shape(sculpt_type)
                return new_command
            self.sculpt_menu.add_command(label=sculpt_type,
                    command=type_command(sculpt_type))
        self.sculpt_menu.add_separator()
        library = sculpty.build_lib(LibDir=MenuDir, LibFile=MenuMap)
        library.add_to_menu(self, self.sculpt_menu)
        self.set_shape(settings['shape_name'], settings['shape_file'])
        self.master.bind('<Button-1>', self.click_handler)

    def click_handler(self, event):
        if self.sculpt_menu.winfo_ismapped():
            self.sculpt_menu.unpost()
            self.redraw()
        else:
            gui.ModalRoot.click_handler(self.master, event)

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
        self.master.deiconify()
        self.redraw()
        if filename:
            self.set_shape(Blender.sys.makename(filename), filename)
            i = Blender.Image.Load(filename)
            sculpt_type = sculpty.map_type(i)
            if sculpt_type[:5] == "TORUS":
                self.radius_input.config(state=NORMAL)
            else:
                self.radius_input.config(state=DISABLED)
            x_faces, y_faces = i.size
            x_faces, y_faces = sculpty.face_count(x_faces, y_faces, 32, 32)
            self.x_faces_input.config(to=i.size[0] / 2)
            self.y_faces_input.config(to=i.size[1] / 2)
            levels = 0
            while levels < 2 and not x_faces % 2 and not y_faces % 2 \
                    and x_faces > 4 and y_faces > 4:
                levels += 1
                x_faces /= 2
                y_faces /= 2
            self.x_faces.set(x_faces)
            self.y_faces.set(y_faces)
            self.levels.set(levels)
            self.update_info()

    def set_map_type(self):
        t = self.shape_name.get().split(os.sep)
        if t[0]:
            t = t[0]
        else:
            t = t[1]
        try:
            i = self.sculpt_menu.index(t)
        except:
            i = self.sculpt_menu.index("Sphere")
        y = self.map_type.winfo_rooty() - self.sculpt_menu.yposition(i) + 8
        x = self.master.winfo_pointerx()\
                - self.sculpt_menu.winfo_reqwidth() // 2
        self.sculpt_menu.post(x, y)

    def set_shape(self, name, filename=None):
        gui.debug(40, "set_shape(\"%s\", \"%s\")" % (name, filename))
        self.shape_name.set(name)
        self.shape_file = filename
        if filename:
            # reading the image file leaves it in the blend
            # can uncomment this when able to remove the temporary image
            #i = Blender.Image.Load(filename)
            #sculpt_type = sculpty.map_type(i)
            #if sculpt_type == "TORUS":
            self.radius_input.config(state=NORMAL)
            #else:
            #	self.radius_input.config(state=DISABLED)
            #self.x_faces_input.config(to=i.size[0] / 2)
            #self.y_faces_input.config(to=i.size[1] / 2)
        else:
            if name[:5] == "Torus":
                self.radius_input.config(state=NORMAL)
            else:
                self.radius_input.config(state=DISABLED)
        self.x_faces_input.config(to=256)
        self.y_faces_input.config(to=256)
        self.update_info()
        self.redraw()

    def redraw(self):
        self.master.update_idletasks()
        if gui.platform == 'darwin':
            self.master.update()
        Blender.Redraw()

    def update_info(self, event=None):
        s, t, w, h, clean_s, clean_t = sculpty.map_size(self.x_faces.get(),
                self.y_faces.get(), self.levels.get())
        self.info_frame.config(text="Map Size - %d x %d" % (w, h))
        self.info_text.set(sculpty.lod_info(w, h)[:-1])
        if sculpty.check_clean(w, h, self.x_faces.get(), self.y_faces.get(),
                    self.clean_lods.get()):
            self.clean_lods_input.configure(
                    background=gui.theme.others['panel'],
                    foreground=gui.theme.defaults['foreground'])
            pow2 = [2, 4, 8, 16, 32, 64, 128, 256]
            if self.x_faces.get() in pow2 and self.y_faces.get() in pow2:
                self.clean_lods_input.configure(state=DISABLED)
            else:
                self.clean_lods_input.configure(state=NORMAL)
        else:
            self.clean_lods_input.configure(
                    background=gui.theme.defaults['foreground'],
                    foreground=gui.theme.others['panel'],
                    state=NORMAL)
        if self.shape_name.get() not in ['Plane', 'Hemi']:
            if self.x_faces.get() < 3:
                clean_s = False
                self.create_button.configure(state=DISABLED)
            if self.y_faces.get() < 3:
                clean_t = False
                self.create_button.configure(state=DISABLED)
            elif self.x_faces.get() > 2:
                self.create_button.configure(state=NORMAL)
        else:
            self.create_button.configure(state=NORMAL)
        if clean_s and clean_t:
            self.levels_input.configure(
                    background=gui.hex_color(gui.theme.ui.textfield),
                    foreground=gui.theme.defaults['foreground'])
        else:
            self.levels_input.configure(
                    background=gui.theme.defaults['foreground'],
                    foreground=gui.hex_color(gui.theme.ui.textfield))
        if clean_s:
            self.x_faces_input.configure(
                    background=gui.hex_color(gui.theme.ui.textfield),
                    foreground=gui.theme.defaults['foreground'])
        else:
            self.x_faces_input.configure(
                    background=gui.theme.defaults['foreground'],
                    foreground=gui.hex_color(gui.theme.ui.textfield))
        if clean_t:
            self.y_faces_input.configure(
                    background=gui.hex_color(gui.theme.ui.textfield),
                    foreground=gui.theme.defaults['foreground'])
        else:
            self.y_faces_input.configure(
                    background=gui.theme.defaults['foreground'],
                    foreground=gui.hex_color(gui.theme.ui.textfield))

    def add(self):
        Blender.Window.WaitCursor(1)
        editmode = Blender.Window.EditMode()
        if editmode:
            Blender.Window.EditMode(0)
        name = self.shape_name.get()
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
                    self.x_faces.get(), self.y_faces.get(),
                    self.levels.get(), self.clean_lods.get(),
                    min(0.5, max(self.radius.get(), 0.05)))
            s, t, w, h, clean_s, clean_t = sculpty.map_size(self.x_faces.get(),
                    self.y_faces.get(), self.levels.get())
            image = Blender.Image.New(basename, w, h, 32)
            sculpty.bake_lod(image)
            ob = scene.objects.new(mesh, basename)
            mesh.flipNormals()
            ob.sel = True
            ob.setLocation(Blender.Window.GetCursorPos())
            sculpty.set_map(mesh, image)
            if baseimage:
                sculpty.update_from_map(mesh, baseimage)
            if self.levels.get():
                if self.sub_type.get():
                    mods = ob.modifiers
                    mod = mods.append(Blender.Modifier.Types.SUBSURF)
                    mod[Blender.Modifier.Settings.LEVELS] = self.levels.get()
                    mod[Blender.Modifier.Settings.RENDLEVELS] = \
                            self.levels.get()
                    mod[Blender.Modifier.Settings.UV] = False
                    if not self.subdivision.get():
                        mod[Blender.Modifier.Settings.TYPES] = 1
                else:
                    mesh.multires = True
                    mesh.addMultiresLevel(self.levels.get(),
                        ('simple', 'catmull-clark')[self.subdivision.get()])
                    mesh.sel = True
            if self.subdivision.get():
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
                z = min(0.5, max(self.radius.get(), 0.05)) * z
            elif sculpt_type == "TORUS X":
                x = min(0.5, max(self.radius.get(), 0.05)) * x
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
            if self.save_settings.get() or self.save_defaults.get():
                settings = {
                    'x_faces': self.x_faces.get(),
                    'y_faces': self.y_faces.get(),
                    'levels': self.levels.get(),
                    'subdivision': self.subdivision.get(),
                    'sub_type': self.sub_type.get(),
                    'clean_lods': self.clean_lods.get(),
                    'radius': self.radius.get(),
                    'shape_name': self.shape_name.get(),
                    'shape_file': self.shape_file,
                    'quads': self.quads.get(),
                    'save': self.save_settings.get()}
                Blender.Registry.SetKey(REGISTRY, settings,
                        self.save_defaults.get())
        except RuntimeError:
            raise
        Blender.Window.EditMode(editmode)
        Blender.Window.WaitCursor(0)
        self.master.quit()

#***********************************************
# main
#***********************************************


def main():
    root = None
    start_time = Blender.sys.time()
    gui.debug(1, "started", SCRIPT)
    try:
        root = gui.ModalRoot()
        app = GuiApp(root)
        app.redraw()
        root.mainloop()
        root.destroy()
    except:
        if root:
            root.grab_release()
            root.quit()
            root.destroy()
        raise
    gui.debug(1, "ended in %.4f sec." % (
            Blender.sys.time() - start_time), SCRIPT)

if __name__ == '__main__':
    gui.theme = gui.Theme() # refresh theme in case user changed prefs.
    main()
