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
from os import name as OSNAME
import Tkinter
from binascii import hexlify

def hex_colour(theme_colour):
	return "#" + hexlify("".join([chr(i) for i in theme_colour[:-1]]))

def float_alpha(theme_colour):
	return float(theme_colour[3]) / 255.0

class Theme:
	def __init__(self):
		ui = Blender.Window.Theme.Get()[0].get('ui')
		self.action = {'colour':hex_colour(ui.action),
				'alpha':float_alpha(ui.action)}
		self.draw_type = ui.drawType
		self.icon_theme = ui.iconTheme
		self.menu_back = {'colour':hex_colour(ui.menu_back),
				'alpha':float_alpha(ui.menu_back)}
		self.menu_hilite = {'colour':hex_colour(ui.menu_hilite),
				'alpha':float_alpha(ui.menu_hilite)}
		self.menu_item = {'colour':hex_colour(ui.menu_item),
				'alpha':float_alpha(ui.menu_item)}
		self.menu_text = {'colour':hex_colour(ui.menu_text),
				'alpha':float_alpha(ui.menu_text)}
		self.menu_text_hi = {'colour':hex_colour(ui.menu_text_hi),
				'alpha':float_alpha(ui.menu_text_hi)}
		self.neutral = {'colour':hex_colour(ui.neutral),
				'alpha':float_alpha(ui.neutral)}
		self.num = {'colour':hex_colour(ui.num),
				'alpha':float_alpha(ui.num)}
		self.outline = {'colour':hex_colour(ui.outline),
				'alpha':float_alpha(ui.outline)}
		self.popup = {'colour':hex_colour(ui.popup),
				'alpha':float_alpha(ui.popup)}
		self.setting = {'colour':hex_colour(ui.setting),
				'alpha':float_alpha(ui.setting)}
		self.setting1 = {'colour':hex_colour(ui.setting1),
				'alpha':float_alpha(ui.setting1)}
		self.setting2 = {'colour':hex_colour(ui.setting2),
				'alpha':float_alpha(ui.setting2)}
		self.text = {'colour':hex_colour(ui.text),
				'alpha':float_alpha(ui.text)}
		self.text_hi = {'colour':hex_colour(ui.text_hi),
				'alpha':float_alpha(ui.text_hi)}
		self.textfield = {'colour':hex_colour(ui.textfield),
				'alpha':float_alpha(ui.textfield)}
		self.textfield_hi = {'colour':hex_colour(ui.textfield_hi),
				'alpha':float_alpha(ui.textfield_hi)}

class Root(Tkinter.Tk):
	def __init__(self, *args,**kw):
		Tkinter.Tk.__init__(self, *args, **kw)
		self.bg=theme.neutral['colour']
		# OS specific features
		if OSNAME in ['nt','mac']:
			self.attributes("-alpha". theme.neutral['alpha'])
		# event handling
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

	def destroy_handler(self, event):
		self.destroy()

class ModalRoot(Tkinter.Tk):
	def __init__(self, *args,**kw):
		Tkinter.Tk.__init__(self, *args, **kw)
		self.overrideredirect(True)
		self.configure(takefocus=True)
		if OSNAME == "nt":
			self.attributes("-topmost", 1)   # Required for Windows
		self.bg=theme.neutral['colour']
		# OS specific features
		if OSNAME in ['nt','mac']:
			self.attributes("-alpha", theme.neutral['alpha'])
		# event handling
		self.focusmodel("active")
		self.bind('<Escape>', self.destroy_handler)
		self.bind('<Leave>', self.destroy_handler)
		self.protocol("WM_DELETE_WINDOW", self.destroy)
		px, py = self.winfo_pointerxy()
		self.geometry("+%d+%d"%(px - 100, py - 100))
		self.update_idletasks()
		self.focus_set()
		self.grab_set_global()

	def destroy_handler(self, event):
		self.destroy()

class Frame(Tkinter.Frame):
	def __init__(self, *args, **kw):
		Tkinter.Frame.__init__(self, *args,**kw)
		self.bg=theme.neutral['colour']
		# OS specific features
		if OSNAME in ['nt','mac']:
			self.attributes("-alpha", theme.neutral['alpha'])

def main():
	root = ModalRoot()
	f = Frame(root)
	root.mainloop()

theme = Theme()

if __name__ == '__main__':
	main()