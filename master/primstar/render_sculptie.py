#!BPY

"""
Name: 'Bake Sculpt Meshes'
Blender: 245
Group: 'Render'
Tooltip: 'Bake Sculptie Maps on Active objects'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.90"
__bpydoc__ = """\

Bake Sculptie Map

This script requires a square planar mapping. It bakes the local vertex
positions to the image assigned to the 'sculptie' UV layer.
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


import Blender
import os
import tkFileDialog
from primstar import sculpty
from Tkinter import *
from primstar import gui

#***********************************************
# constants
#***********************************************

SCRIPT = 'render_sculptie_test'
REGISTRY = 'PrimstarBake'
LABEL = '%s - Bake sculpt meshes'%(sculpty.LABEL)

#***********************************************
# settings
#***********************************************

settings = Blender.Registry.GetKey(REGISTRY, True)
if settings == None:
	settings = {}
default_settings={
		'keep_center':False,
		'keep_scale':False,
		'keep_seams':True,
		'clear':True,
		'fill':True,
		'finalise':True,
		'range_min':sculpty.XYZ(0, 0, 0),
		'range_max':sculpty.XYZ(255, 255, 255),
		'range_scale':True,
		'alpha':2,
		'alpha_file':None,
		'save':True
}
for key, value in default_settings.iteritems():
	if key not in settings:
		settings[key] = value

#***********************************************
# classes
#***********************************************

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
		# Settings
		# ==========================================

		self.keep_center = BooleanVar(self.master, settings['keep_center'])
		self.keep_scale = BooleanVar(self.master, settings['keep_scale'])
		self.keep_seams = BooleanVar(self.master, settings['keep_seams'])
		self.clear = BooleanVar(self.master, settings['clear'])
		self.fill = BooleanVar(self.master, settings['fill'])
		self.finalise = BooleanVar(self.master, settings['finalise'])
		self.range_min_r = IntVar(self.master, settings['range_min'].x)
		self.range_min_g = IntVar(self.master, settings['range_min'].y)
		self.range_min_b = IntVar(self.master, settings['range_min'].z)
		self.range_max_r = IntVar(self.master, settings['range_max'].x)
		self.range_max_g = IntVar(self.master, settings['range_max'].y)
		self.range_max_b = IntVar(self.master, settings['range_max'].z)
		self.range_scale = BooleanVar(self.master, settings['range_scale'])
		self.alpha = IntVar(self.master, settings['alpha'])
		self.alpha_filename = settings['alpha_file']
		self.alpha_file = StringVar(self.master)
		self.update_file()
		self.save_settings = BooleanVar(self.master, settings['save'])
		self.save_defaults = BooleanVar(self.master, False)

		# ==========================================
		# Main window frame
		# ==========================================

		top_frame = gui.Frame(master, border=4)
		top_frame.pack()
		frame = gui.LabelFrame(top_frame,
				text=LABEL,
				labelanchor=NW)
		frame.pack()
		settings_frame = gui.Frame(frame)
		settings_frame.pack(fill=X)

		# ==========================================
		# Bake settings frame
		# ==========================================

		f = gui.LabelFrame(settings_frame,
				text="Bake")
		f.pack(side=LEFT, fill=Y)
		w = gui.Checkbutton(f,
				text="Keep Center",
				variable=self.keep_center)
		w.pack(anchor=W, expand=True)
		w = gui.Checkbutton(f,
				text="Keep Scale",
				variable=self.keep_scale)
		w.pack(anchor=W, expand=True)
		w = gui.Checkbutton(f,
				text="Keep Seams",
				variable=self.keep_seams)
		w.pack(anchor=W, expand=True)

		# ==========================================
		# Image settings frame
		# ==========================================

		f = gui.LabelFrame(settings_frame,
				text="Image")
		f.pack(side=LEFT, fill=Y)
		w = gui.Checkbutton(f,
				text="Clear",
				variable=self.clear)
		w.pack(anchor=W, expand=True)
		w = gui.Checkbutton(f,
				text="Fill",
				variable=self.fill)
		w.pack(anchor=W, expand=True)
		w = gui.Checkbutton(f,
				text="Finalise",
				variable=self.finalise)
		w.pack(anchor=W, expand=True)

		# ==========================================
		# Range settings frame
		# ==========================================

		f = gui.LabelFrame(settings_frame,
				text="Range")
		f.pack(side=LEFT, fill=Y)
		fr = gui.Frame(f)
		fr.pack(fill=X)
		w = gui.Spinbox(fr,
				textvariable=self.range_max_r,
				from_=0,
				to=255,
				width=4)
		w.pack(side=RIGHT)
		w = gui.Spinbox(fr,
				textvariable=self.range_min_r,
				from_=0,
				to=255,
				width=4)
		w.pack(side=RIGHT)
		t = gui.Label(fr,
				text="Red",
				justify=RIGHT)
		t.pack(side=RIGHT)
		fr = gui.Frame(f)
		fr.pack(fill=X)
		w = gui.Spinbox(fr,
				textvariable=self.range_max_g,
				from_=0,
				to=255,
				width=4)
		w.pack(side=RIGHT)
		w = gui.Spinbox(fr,
				textvariable=self.range_min_g,
				from_=0,
				to=255,
				width=4)
		w.pack(side=RIGHT)
		t = gui.Label(fr,
				text="Green",
				justify=RIGHT)
		t.pack(side=RIGHT)
		fr = gui.Frame(f)
		fr.pack(fill=X)
		w = gui.Spinbox(fr,
				textvariable=self.range_max_b,
				from_=0,
				to=255,
				width=4)
		w.pack(side=RIGHT)
		w = gui.Spinbox(fr,
				textvariable=self.range_min_b,
				from_=0,
				to=255,
				width=4)
		w.pack(side=RIGHT)
		t = gui.Label(fr,
				text="Blue",
				justify=RIGHT)
		t.pack(side=RIGHT)
		w = gui.Checkbutton(f,
				text="Adjust Scale",
				variable=self.range_scale)
		w.pack()

		# ==========================================
		# Alpha settings frame
		# ==========================================

		f = gui.LabelFrame(frame,
				text="Alpha")
		f.pack(fill=X)
		fr = gui.Frame(f)
		fr.pack()
		gui.Radiobutton(fr,
				text="Preview",
				variable=self.alpha,
				value=2).pack(side=LEFT, anchor=W)
		gui.Radiobutton(fr,
				text="Solid",
				variable=self.alpha,
				value=0).pack(side=LEFT, anchor=W)
		gui.Radiobutton(fr,
				text="Transparent",
				variable=self.alpha,
				value=1).pack(side=LEFT, anchor=W)
		gui.Radiobutton(fr,
				textvariable=self.alpha_file,
				variable=self.alpha,
				command=self.set_alpha,
				value=3).pack(side=LEFT,anchor=W)
		gui.Button(fr,
				image=self.file_icon,
				compound=LEFT,
				command=self.set_file,
				default=ACTIVE).pack(side=RIGHT)

		# ==========================================
		# Save settings frame
		# ==========================================

		save_frame = gui.Frame(frame)
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
		# Bake button
		# ==========================================

		w = gui.Button(save_frame,
				text="Bake",
				image=self.cube_icon,
				compound=LEFT,
				command=self.bake,
				default=ACTIVE)
		w.pack(side=LEFT,fill=BOTH, expand=True, anchor=SE, pady=5)

	def bake(self):
		startTime = Blender.sys.time()  #for timing purposes
		editmode  = Blender.Window.EditMode()
		if editmode: Blender.Window.EditMode(0)
		self.master.configure(cursor="clock")
		# prepare for bake, set centers and create bounding box
		bb = sculpty.BoundingBox()
		bb.rgb.min = sculpty.XYZ(self.range_min_r.get(),self.range_min_g.get(),self.range_min_b.get())
		bb.rgb.max = sculpty.XYZ(self.range_max_r.get(),self.range_max_g.get(),self.range_max_b.get())
		bb.rgb.update()

		scene = Blender.Scene.GetCurrent()
		for ob in scene.objects.selected:
			if sculpty.check( ob ):
				if not self.keep_center.get():
					#center new
					sculpty.set_center( ob )
				bb.add( ob )
				if self.keep_scale.get():
					bb = bb.normalised()
				if self.keep_center.get():
					bb = bb.centered()
		# Good to go, do the bake
		success = False
		image = None
		a = self.alpha.get()
		if a == 3:
			alpha_image = Blender.Image.Load(self.alpha_filename)
		for ob in scene.objects.selected:
			if sculpty.active( ob ):
				if sculpty.bake_object(ob, bb, self.clear.get(), self.keep_seams.get()):
					success = True
				for image in sculpty.map_images( ob.getData( False, True) ):
					n = Blender.sys.splitext( image.name )
					if n[0] in ["Untitled", "Sphere_map", "Torus_map", "Cylinder_map", "Plane_map", "Hemi_map", "Sphere", "Torus","Cylinder","Plane","Hemi" ]:
						image.name = ob.name
					if self.range_scale.get():
						if 'primstar' not in image.properties:
							image.properties['primstar'] = {}
						image.properties['primstar']['scale_x'] /= bb.rgb.scale.x
						image.properties['primstar']['scale_y'] /= bb.rgb.scale.y
						image.properties['primstar']['scale_z'] /= bb.rgb.scale.z
					if self.fill.get():
						sculpty.fill_holes( image )
					if self.finalise.get():
						sculpty.finalise( image )
						if a == 2:
							sculpty.bake_preview(image)
						elif a == 1:
							sculpty.clear_alpha(image)
						elif a == 3:
							sculpty.set_alpha(image, alpha_image)
		Blender.Redraw()
		if editmode: Blender.Window.EditMode(1)
		if success:
			gui.debug(1, 'finished baking: in %.4f sec.' % ((Blender.sys.time()- startTime)))
		else:
			gui.debug(1, 'bake failed after %.4f sec.' % ((Blender.sys.time()- startTime)))
		if self.save_settings.get() or self.save_defaults.get():
			range_min = sculpty.XYZ(self.range_min_r.get(),self.range_min_g.get(),self.range_min_b.get())
			range_max = sculpty.XYZ(self.range_max_r.get(),self.range_max_g.get(),self.range_max_b.get())
			settings = {
				'keep_center':self.keep_center.get(),
				'keep_scale':self.keep_scale.get(),
				'keep_seams':self.keep_seams.get(),
				'clear':self.clear.get(),
				'fill':self.fill.get(),
				'finalise':self.finalise.get(),
				'range_min':range_min,
				'range_max':range_max,
				'range_scale':self.range_scale.get(),
				'alpha':self.alpha.get(),
				'alpha_file':self.alpha_filename,
				'save':self.save_settings.get()
			}
			Blender.Registry.SetKey(REGISTRY, settings, self.save_defaults.get())
		self.master.quit()

	def redraw(self):
		self.master.update_idletasks()
		Blender.Redraw()

	def set_file(self):
		self.master.withdraw()
		filename = tkFileDialog.askopenfilename(
				initialdir='~',
				title='Select a sculpt map',
				parent=self.master,
				filetypes=[
						('targa', '*.tga'),
						('bmp','*.bmp'),
						('png','*.png'),
						('all files', '.*')])
		self.master.deiconify()
		self.redraw()
		self.alpha_filename = filename
		if not filename:
			self.alpha.set(2)
		self.update_file()

	def set_alpha(self):
		if not self.alpha_filename:
			self.master.mouse_exit += 1 #hack to stop early exit
			self.set_file()

	def update_file(self):
		if self.alpha_filename == None:
			self.alpha_file.set("File")
		else:
			if not os.path.exists(self.alpha_filename):
				self.alpha_file.set("File")
			else:
				self.alpha_file.set(self.alpha_filename.split(os.sep)[-1])
		self.redraw()

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
			root.destroy()
		raise
	gui.debug(1, "ended in %.4f sec."%(Blender.sys.time() - start_time), SCRIPT)

if __name__ == '__main__':
	gui.theme = gui.Theme() # refresh theme in case user changed prefs.
	main()
