#!BPY
"""
Name: 'GUI Test'
Blender: 246
Group: 'AddMesh'
Tooltip: 'Add a Second Life sculptie compatible mesh - Test GUI'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.00"
__bpydoc__ = """\

Sculpt Mesh

This script creates an object with a gridded UV map suitable for Second Life sculpties.
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

import Blender
from primstar import sculpty
import os
from Tkinter import *
from binascii import hexlify

class MenuMap(sculpty.LibFile):
	def get_command(self, app):
		def new_command():
			app.set_sculpt_type(self.local_path)
		return new_command

class MenuDir(sculpty.LibDir):
	def add_to_menu(self, app, menu):
		for f in self.files:
			menu.add_command(label=f.name, command=f.get_command(app))
		for d in self.dirs:
			submenu = Menu(menu, tearoff=0)
			d.add_to_menu( app, submenu )
			menu.add_cascade(label=d.name, menu=submenu)

class GuiApp:
	def __init__(self, master, theme):
		w,h = 32, 256

		self.master = master
		self.master.grab_set()
		
		# remove the popup as soon as user moves the mouse out of the widget:
		self.master.bind( "<Button>", self.destroyHandler)
		
		frame = LabelFrame(master,
				border=3,
				bg=hex_colour(theme.neutral),
				text="Primstar - Add sculpt mesh",
				labelanchor=N)
		frame.pack()
		fi = Frame(frame, bg=hex_colour(theme.neutral))
		fi.pack()
		f = LabelFrame(fi,
				text="Geometry",
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text))
		f.pack(padx=5, pady=5, side=LEFT)
		ff = Frame(f, bg=hex_colour(theme.neutral))
		ff.pack()
		fx = Frame(ff, bg=hex_colour(theme.neutral))
		fx.pack()
		t = Label(fx,
			text="X Faces",
			justify=RIGHT,
			bg=hex_colour(theme.neutral),
			fg=hex_colour(theme.text))
		t.pack(padx=5, pady=5, side=LEFT)
		self.x_faces = IntVar(self.master, 8)
		s = Spinbox(fx,
				textvariable=self.x_faces,
				from_=1,
				to=256,
				width=3,
				bg=hex_colour(theme.num),
				fg=hex_colour(theme.text),
				activebackground=hex_colour(theme.setting))
		s.pack(padx=5, pady=5, side=RIGHT)
		fy = Frame(ff, bg=hex_colour(theme.neutral))
		fy.pack()
		t = Label(fy,
				text="Y Faces",
				justify=RIGHT,
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text))
		t.pack(padx=5, pady=5, side=LEFT)
		self.y_faces = IntVar(self.master, 8)
		s = Spinbox(fy,
				textvariable=self.y_faces,
				from_=1,
				to=256,
				width=3,
				bg=hex_colour(theme.num),
				fg=hex_colour(theme.text),
				activebackground=hex_colour(theme.setting))
		s.pack(padx=5, pady=5, side=RIGHT)
		fs = LabelFrame(fi,
				text="Subdivision",
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text))
		fs.pack(padx=5, pady=5)
		self.levels = IntVar(self.master, 2)
		fl = Frame(fs, bg=hex_colour(theme.neutral))
		fl.pack()
		t = Label(fl,
				text="Levels",
				justify=RIGHT,
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text))
		t.pack(padx=5, pady=5, side=LEFT)
		s = Spinbox(fl,
				textvariable=self.levels,
				from_=0,
				to=6,
				width=3,
				bg=hex_colour(theme.num),
				fg=hex_colour(theme.text),
				activebackground=hex_colour(theme.setting))
		s.pack(padx=5, pady=5, side=RIGHT)
		self.subdivision = IntVar(self.master, 1)
		r = Frame(fs, bg=hex_colour(theme.neutral))
		r.pack(side=LEFT)
		Radiobutton(r,
				text="Simple",
				variable=self.subdivision,
				highlightthickness=0,
				bg=hex_colour(theme.neutral),
				value=0).pack()
		Radiobutton(r,
				text="Catmull",
				variable=self.subdivision,
				highlightthickness=0,
				bg=hex_colour(theme.neutral),
				value=1).pack()
		self.sub_type = IntVar(self.master, 1)
		r = Frame(fs, bg=hex_colour(theme.neutral))
		r.pack(side=RIGHT)
		Radiobutton(r,
				text="Multires",
				variable=self.sub_type,
				highlightthickness=0,
				bg=hex_colour(theme.neutral),
				value=0).pack()
		Radiobutton(r,
				text="Subsurf",
				variable=self.sub_type,
				highlightthickness=0,
				bg=hex_colour(theme.neutral),
				value=1).pack()
		self.clean_lods = BooleanVar( self.master, True )
		c = Checkbutton(f,
				text="Clean LODs",
				variable=self.clean_lods,
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text),
				activebackground=hex_colour(theme.setting),
				border=2,
				highlightthickness=0)
		c.pack(padx=5, pady=5, side=BOTTOM)
		f = LabelFrame(frame,
				text="Map Image",
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text),
				labelanchor=N)
		f.pack(padx=5, pady=5, side=LEFT)
		self.lod_display = Label(f,
				text=sculpty.lod_info(w, h)[:-1],
				justify=LEFT,
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text))
		self.lod_display.pack(padx=5, pady=5, ipadx=3, ipady=3, side=LEFT)
		self.map_type = Button(frame,
				text="Type",
				command=self.set_map_type,
				border=1,
				bg=hex_colour(theme.textfield),
				fg=hex_colour(theme.text),
				activebackground=hex_colour(theme.setting))
		self.map_type.pack(padx=5, pady=5, fill=X)
		self.sculpt_menu = Menu(frame,
				tearoff=0,
				background=hex_colour(theme.menu_item),
				foreground=hex_colour(theme.menu_text),
				activebackground=hex_colour(theme.menu_hilite),
				activeforeground=hex_colour(theme.menu_text_hi))
		for sculpt_type in [ "Sphere", "Torus", "Plane", "Cylinder", "Hemi"]:
			def type_command( sculpt_type ):
				def new_command():
					self.set_sculpt_type(sculpt_type)
				return new_command
			self.sculpt_menu.add_command(label=sculpt_type,
					command=type_command(sculpt_type))
		library = sculpty.build_lib(LibDir=MenuDir, LibFile=MenuMap)
		library.add_to_menu(self, self.sculpt_menu)
		self.set_sculpt_type("Sphere")
		b = Button(frame, text="Add",
				command=self.add,
				border=1,
				bg=hex_colour(theme.action),
				activebackground=hex_colour(theme.action),
				fg=hex_colour(theme.menu_text),
				activeforeground=hex_colour(theme.menu_text_hi))
		b.pack( padx=5, pady=5, fill=X )
		b = Button(frame, text="Close",
				command=self.master.destroy,
				border=1,
				bg=hex_colour(theme.action),
				activebackground=hex_colour(theme.action),
				fg=hex_colour(theme.menu_text),
				activeforeground=hex_colour(theme.menu_text_hi))
		b.pack( padx=5, pady=5, fill=X )

	def set_map_type(self):
		t = self.map_type.cget('text').split(os.sep)
		if t[0]:
			t = t[0]
		else:
			t = t[1]
		i = self.sculpt_menu.index( t )
		y = self.map_type.winfo_rooty() - self.sculpt_menu.yposition( i )
		x  = self.master.winfo_pointerx() - self.sculpt_menu.winfo_reqwidth() // 2
		self.sculpt_menu.post(x, y)

	def set_sculpt_type(self, sculpt_type):
		self.map_type.configure(text=sculpt_type)
		self.redraw()

	def redraw(self):
		self.master.update_idletasks()
		Blender.Redraw()

	def add(self):
		Blender.Window.WaitCursor(1)
		name = self.map_type.cget('text')
		if name[:1] == os.sep:
			basename = name.split(os.sep)[1]
			baseimage = Blender.Image.Load(os.path.join(sculpty.lib_dir, name[1:]) + '.png')
			sculpt_type = sculpty.map_type(baseimage)
		else:
			basename = name
			sculpt_type = name.upper()
			baseimage = None
		scene = Blender.Scene.GetCurrent()
		for ob in scene.objects:
			ob.sel = False
		try:
			mesh = sculpty.new_mesh( basename,sculpt_type,
					self.x_faces.get(), self.y_faces.get(),
					self.levels.get(), self.clean_lods.get(), 0.25) #todo: 0.25 radius needs gui add..
			s, t, w, h, clean_s, clean_t = sculpty.map_size(self.x_faces.get(), self.y_faces.get(), self.levels.get())
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
					mod[Blender.Modifier.Settings.RENDLEVELS] = self.levels.get()
					mod[Blender.Modifier.Settings.UV] = False
					if not self.subdivision.get():
						mod[Blender.Modifier.Settings.TYPES] = 1
				else:
					mesh.multires = True
					mesh.addMultiresLevel(multires, ('simple', 'catmull-clark')[self.subdivision.get()])
					mesh.sel = True
			# adjust scale for subdivision
			minimum, maximum = sculpty.get_bounding_box(ob)
			x = 1.0 / (maximum.x - minimum.x)
			y = 1.0 / (maximum.y - minimum.y)
			try:
				z = 1.0 / (maximum.z - minimum.z)
			except:
				z = 0.0
			if sculpt_type == "TORUS":
				z = 0.25 * z #todo: radius again
			elif sculpt_type == "HEMI":
				z = 0.5 * z
			tran = Blender.Mathutils.Matrix([ x, 0.0, 0.0 ], [0.0, y, 0.0], [0.0, 0.0, z]).resize4x4()
			mesh.transform(tran)
			# align to view
			try:
				quat = None
				if Blender.Get('add_view_align'):
					quat = Blender.Mathutils.Quaternion(Blender.Window.GetViewQuat())
					if quat:
						mat = quat.toMatrix()
						mat.invert()
						mat.resize4x4()
						ob.setMatrix(mat)
			except:
				pass
		except RuntimeError:
			#todo tkinter this
			Blender.Draw.PupBlock("Unable to create sculptie", ["Please decrease face counts","or subdivision levels"])
		Blender.Window.WaitCursor(0)
		self.redraw()

	# =================================================================================
	# This handler is called whenever the mouse leaves a widget inside the self.master.
	# If the mouse leaves the self.master itself, the whole application will be
	# destroyed.
	# =================================================================================
	def destroyHandler(self, event):
		print "leave [", event.widget.winfo_name(), "]"
		
		if(event.widget == self.master):
			print "Mouse left application. Self destroy"
			#self.master.destroy()

def hex_colour(theme_colour):
	return "#" + hexlify("".join([chr(i) for i in theme_colour[:-1]]))


def main():
	root = Tk()
	root.title("Add sculpt mesh")
	root.overrideredirect(1)

	# ==========================================================================
	# Calculate the position where the popup appears. Assume the dimension of 
	# the window is 256*256 pixel and correct the window position so thet the
	# mouse is in the center of the window 
	# ==========================================================================
	xPos, yPos      = root.winfo_pointerxy()
	root.geometry('+'+str(xPos-128)+'+'+str(yPos-128))

	theme = Blender.Window.Theme.Get()[0].get('ui')
	root.bg = hex_colour(theme.neutral)
	gui = GuiApp(root, theme)
	
	
	root.mainloop()

if __name__ == '__main__':
	main()