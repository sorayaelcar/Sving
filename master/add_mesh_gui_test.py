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
import sculpty
from Tkinter import *

class GuiApp:
	def __init__(self, master):
		w,h = 32, 256
		self.master = master
		frame = Frame(master)
		frame.pack()
		self.lod_display = Label(frame, text=sculpty.lod_info(w, h), relief=GROOVE, justify=LEFT)
		self.lod_display.pack(padx=5, pady=5, ipadx=3, ipady=3, side=LEFT)
		self.map_type = Button(frame, text="Type", command=self.set_map_type)
		self.map_type.pack(padx=5, pady=5)
		self.sculpt_menu = Menu(frame, tearoff=0)
		for sculpt_type in [ "Sphere", "Torus", "Plane", "Cylinder", "Hemi"]:
			def type_command( sculpt_type ):
				def new_command():
					self.set_sculpt_type(sculpt_type)
				return new_command
			self.sculpt_menu.add_command(label=sculpt_type, command=type_command(sculpt_type))
		self.set_sculpt_type("Sphere")
		b = Button(frame, text="Add", command=self.add)
		b.pack( padx=5, pady=5 )

	def set_map_type(self):
		self.sculpt_menu.post(160,70)

	def set_sculpt_type(self, sculpt_type):
		self.map_type.configure(text=sculpt_type)
		self.redraw()

	def redraw(self):
		self.map_type.update_idletasks()
		Blender.Redraw()

	def add(self):
		print "Create a " + self.map_type.cget('text') + " sculptie"
		# self.master.destroy()

def main():
	root = Tk()
	root.title("Add sculpt mesh")
	gui = GuiApp(root)
	root.mainloop()

if __name__ == '__main__':
	main()