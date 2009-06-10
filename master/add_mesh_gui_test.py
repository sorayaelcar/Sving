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
from binascii import hexlify

class GuiApp:
	def __init__(self, master, theme):
		w,h = 32, 256
		self.master = master
		frame = Frame(master,relief=RAISED,border=1, bg=hex_colour(theme.neutral))
		frame.pack()
		self.lod_display = Label(frame,
				text=sculpty.lod_info(w, h),
				relief=GROOVE,
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
				bg=hex_colour(theme.menu_item),
				fg=hex_colour(theme.menu_text),
				activebackground=hex_colour(theme.menu_hilite),
				activeforeground=hex_colour(theme.menu_text_hi))
		for sculpt_type in [ "Sphere", "Torus", "Plane", "Cylinder", "Hemi"]:
			def type_command( sculpt_type ):
				def new_command():
					self.set_sculpt_type(sculpt_type)
				return new_command
			self.sculpt_menu.add_command(label=sculpt_type,
					command=type_command(sculpt_type))
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
		self.sculpt_menu.post(250,70)

	def set_sculpt_type(self, sculpt_type):
		self.map_type.configure(text=sculpt_type)
		self.redraw()

	def redraw(self):
		self.master.update_idletasks()
		Blender.Redraw()

	def add(self):
		print "Create a " + self.map_type.cget('text') + " sculptie"
		# self.master.destroy()

def hex_colour(theme_colour):
	return "#" + hexlify("".join([chr(i) for i in theme_colour[:-1]]))

def main():
	root = Tk()
	root.title("Add sculpt mesh")
	root.overrideredirect(1)
	root.geometry('+100+100')
	theme = Blender.Window.Theme.Get()[0].get('ui')
	gui = GuiApp(root, theme)
	root.mainloop()

if __name__ == '__main__':
	main()