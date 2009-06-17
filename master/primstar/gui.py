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
import Tkinter
from binascii import hexlify

def hex_colour(theme_colour):
	return "#" + hexlify("".join([chr(i) for i in theme_colour[:-1]]))

class Theme:
	def __init__(self):
		ui = Blender.Window.Theme.Get()[0].get('ui')
		self.action = hex_colour(ui.action)
		self.draw_type = ui.drawType
		self.icon_theme = ui.iconTheme
		self.menu_back = hex_colour(ui.menu_back)
		self.menu_hilite = hex_colour(ui.menu_hilite)
		self.menu_item = hex_colour(ui.menu_item)
		self.menu_text = hex_colour(ui.menu_text)
		self.menu_text_hi = hex_colour(ui.menu_text_hi)
		self.neutral = hex_colour(ui.neutral)
		self.num = hex_colour(ui.num)
		self.outline = hex_colour(ui.outline)
		self.popup = hex_colour(ui.popup)
		self.setting = hex_colour(ui.setting)
		self.setting1 = hex_colour(ui.setting1)
		self.setting2 = hex_colour(ui.setting2)
		self.text = hex_colour(ui.text)
		self.text_hi = hex_colour(ui.text_hi)
		self.textfield = hex_colour(ui.textfield)
		self.textfield_hi = hex_colour(ui.textfield_hi)

class Root(Tkinter.Tk):
	def __init__(self, *args,**kw):
		Tkinter.Tk.__init__(self, *args, **kw)
		self.bg=theme.neutral
		self.focusmodel("passive")
		self.bind('<FocusOut>', self.focus_out_handler)
		self.bind('<FocusIn>', self.focus_in_handler)
		self.bind('<Configure>', self.configure_handler)
		self.bind('<Escape>', self.destroy_handler)
		self.protocol("WM_DELETE_WINDOW", self.destroy)
		px, py = self.winfo_pointerxy()
		self.geometry("+%d+%d"%(px - 100, py - 100))

	def focus_out_handler(self, event):
		self.grab_release()

	def focus_in_handler(self, event):
		self.grab_set()

	def configure_handler(self, event):
		Blender.Window.RedrawAll()
		self.grab_set()

	def destroy_handler(self, event=None):
		self.destroy()

class ModalRoot(Tkinter.Tk):
	def __init__(self, *args,**kw):
		Tkinter.Tk.__init__(self, *args, **kw)
		self.overrideredirect(True)
		self.configure(takefocus=True)
		self.bg=theme.neutral
		self.focusmodel("active")
		self.bind('<Escape>', self.destroy_handler)
		self.bind('<Leave>', self.destroy_handler)
		self.protocol("WM_DELETE_WINDOW", self.destroy)
		px, py = self.winfo_pointerxy()
		self.geometry("+%d+%d"%(px - 100, py - 100))
		self.update_idletasks()
		self.grab_set_global()

	def destroy_handler(self, event=None):
		self.destroy()

class Frame(Tkinter.Frame):
	def __init__(self, *args, **kw):
		Tkinter.Frame.__init__(self, *args,**kw)
		self.bg=theme.neutral

def main():
	root = ModalRoot()
	f = Frame(root)
	root.mainloop()

theme = Theme()

if __name__ == '__main__':
	main()