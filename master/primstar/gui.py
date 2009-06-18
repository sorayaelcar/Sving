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
from sys import platform
import Tkinter
from binascii import hexlify

def debug(num,msg):
	if Blender.Get('rt') >= num:
		print 'debug:', (' '*num), msg

def hex_color(theme_color):
	return "#" + hexlify("".join([chr(i) for i in theme_color[:-1]]))

def float_alpha(theme_color):
	return float(theme_color[3]) / 255.0

def mix_color(color1, color2, reverse=False):
	if reverse:
		a = float_alpha(color1)
	else:
		a = float_alpha(color2)
	r = color1[0] * (1.0 - a) + color2[0] * a
	g = color1[1] * (1.0 - a) + color2[1] * a
	b = color1[2] * (1.0 - a) + color2[2] * a
	return hex_color([int(r), int(g), int(b), 255])

def add_only(kw, item, value):
	if item not in kw.keys():
		kw[item] = value

class Theme:
	def __init__(self):
		self.ui = Blender.Window.Theme.Get()[0].get('ui')
		self.buts = Blender.Window.Theme.Get()[0].get(
				Blender.Window.Types.BUTS)
		self.others = {
				'panel':mix_color(self.buts.back, self.buts.panel)}
		self.defaults = {
				'activebackground':hex_color(self.ui.action),
				'activeforeground':hex_color(self.ui.text_hi),
				'background':hex_color(self.buts.back),
				'disabledforeground':hex_color(self.ui.neutral),
				'foreground':hex_color(self.ui.menu_text),
				'highlightbackground':hex_color(self.ui.menu_back),
				'highlightcolor':hex_color(self.ui.outline),
				'selectcolor':hex_color(self.ui.setting2),
				'selectforeground':hex_color(self.ui.text_hi),
				'selectbackground':hex_color(self.ui.textfield_hi),
				'highlightthickness':0}

	def config(self, widget, kw={}):
		# don't override user supplied kw, only add missing entries
		if Tkinter.Checkbutton in widget.__class__.__bases__:
			add_only(kw,'background', self.others['panel'])

		if Tkinter.Entry in widget.__class__.__bases__:
			add_only(kw,'background', hex_color(self.ui.textfield))
			add_only(kw,'highlightthickness', 2 )
			add_only(kw, 'highlightbackground', self.others['panel'])

		if Tkinter.Frame in widget.__class__.__bases__:
			add_only(kw,'background', self.others['panel'])

		if Tkinter.LabelFrame in widget.__class__.__bases__:
			add_only(kw,'background', self.others['panel'])
			add_only(kw,'padx', 5)
			add_only(kw,'pady', 5)

		if Tkinter.Spinbox in widget.__class__.__bases__:
			add_only(kw, 'background', hex_color(self.ui.textfield))
			add_only(kw,'highlightthickness', 2 )
			add_only(kw, 'highlightbackground', self.others['panel'])

		# add default settings
		for item in widget.config():
			if item in self.defaults.keys():
				add_only(kw, item, self.defaults[item])
		widget.config(**kw)

class Root(Tkinter.Tk):
	def __init__(self, **kw):
		Tkinter.Tk.__init__(self)
		theme.config(self, kw)
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
	def __init__(self, **kw):
		self._init=False
		Tkinter.Tk.__init__(self)
		self.overrideredirect(True)
		kw['takefocus']=True
		theme.config(self, kw)
		# OS specific features
		if platform == "win32":
			self.attributes("-topmost", 1)
		# event handling
		px, py = self.winfo_pointerxy()
		self.geometry("+%d+%d"%(px - 100, py - 100))
		self.update_idletasks()
		self.bind('<Escape>', self.destroy_handler)
		self.bind('<Leave>', self.leave_handler)
		self.bind('<Enter>',self.enter_handler)
		self.protocol("WM_DELETE_WINDOW", self.destroy)
		self.focus_force()

	def destroy_handler(self, event):
		self.destroy()

	def leave_handler(self, event):
		debug(60,"Leave: %s"%str(event.widget))
		if self._init:
			if event.widget == self:
				px, py = self.winfo_pointerxy()
				if self.winfo_containing(px, py) == None:
					self.destroy()
		else:
			self._init = True
			# skip first leave event (in case not under mouse on creation)

	def enter_handler(self, event):
		debug(60,"Enter: %s"%str(event.widget))
		if self.grab_status() == None:
			self.grab_set_global()
		self.update_idletasks()

class BitmapImage(Tkinter.BitmapImage):
	def __init__(self, parent, **kw):
		Tkinter.BitmapImage.__init__(self, parent)
		theme.config(self, kw)

class Button(Tkinter.Button):
	def __init__(self, parent, **kw):
		Tkinter.Button.__init__(self, parent)
		theme.config(self,kw)

class Canvas(Tkinter.Canvas):
	def __init__(self, parent, **kw):
		Tkinter.Canvas.__init__(self, parent)
		theme.config(self, kw)

class Checkbutton(Tkinter.Checkbutton):
	def __init__(self, parent, **kw):
		Tkinter.Checkbutton.__init__(self, parent)
		theme.config(self, kw)

class Entry(Tkinter.Entry):
	def __init__(self, parent, **kw):
		Tkinter.Entry.__init__(self, parent)
		theme.config(self, kw)

class Frame(Tkinter.Frame):
	def __init__(self, parent, **kw):
		Tkinter.Frame.__init__(self, parent)
		theme.config(self, kw)

class Label(Tkinter.Label):
	def __init__(self, parent, **kw):
		Tkinter.Label(self, parent)
		theme.config(self, kw)

class LabelFrame(Tkinter.LabelFrame):
	def __init__(self, parent, **kw):
		Tkinter.LabelFrame.__init__(self, parent)
		theme.config(self, kw)

class Listbox(Tkinter.Listbox):
	def __init__(self, parent, **kw):
		Tkinter.Listbox.__init__(self, parent)
		theme.config(self, kw)

class Menu(Tkinter.Menu):
	def __init__(self, parent, **kw):
		Tkinter.Menu.__init__(self, parent)
		theme.config(self, kw)

class Menubutton(Tkinter.Menubutton):
	def __init__(self, parent, **kw):
		Tkinter.Menubutton.__init__(self, parent)
		theme.config(self, kw)

class Message(Tkinter.Message):
	def __init__(self, parent, **kw):
		Tkinter.Message.__init__(self, parent)
		theme.config(self, kw)

class OptionMenu(Tkinter.OptionMenu):
	def __init__(self, parent, **kw):
		Tkinter.OptionMenu.__init__(self, parent)
		theme.config(self, kw)

class PanedWindow(Tkinter.PanedWindow):
	def __init__(self, parent, **kw):
		Tkinter.PanedWindow.__init__(self, parent)
		theme.config(self, kw)

class PhotoImage(Tkinter.PhotoImage):
	def __init__(self, parent, **kw):
		Tkinter.PhotoImage.__init__(self, parent)
		theme.config(self, kw)

class Radiobutton(Tkinter.Radiobutton):
	def __init__(self, parent, **kw):
		Tkinter.Radiobutton.__init__(self, parent)
		theme.config(self, kw)

class Scale(Tkinter.Scale):
	def __init__(self, parent, **kw):
		Tkinter.Scale.__init__(self, parent)
		theme.config(self, kw)

class Scrollbar(Tkinter.Scrollbar):
	def __init__(self, parent, **kw):
		Tkinter.Scrollbar.__init__(self, parent)
		theme.config(self, kw)

class Spinbox(Tkinter.Spinbox):
	def __init__(self, parent, **kw):
		Tkinter.Spinbox.__init__(self, parent)
		theme.config(self, kw)

class Text(Tkinter.Text):
	def __init__(self, parent, **kw):
		Tkinter.Text.__init__(self, parent)
		theme.config(self, kw)

class Toplevel(Tkinter.Toplevel):
	def __init__(self, parent, **kw):
		Tkinter.Toplevel.__init__(self, parent)
		theme.config(self, kw)

def main():
	root=None
	try:
		root = ModalRoot()
		f = Frame(root)
		f.pack()
		Lf = LabelFrame(f, text="Label Frame")
		Lf.pack(padx=5, pady=5)
		Button(Lf, text="Panic", command=root.destroy).pack()
		Button(Lf, text="Disabled", state=Tkinter.DISABLED).pack()
		Checkbutton(Lf, text="Checkbutton").pack()
		Entry(Lf, text="Entry").pack()
		Spinbox(Lf).pack()
		root.mainloop()
	except:
		if root:
			root.destroy()
		raise

theme = Theme()

if __name__ == '__main__':
	main()