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
from sys import platform, stderr
import Tkinter
from binascii import hexlify


def debug(num, msg, script="gui"):
    if Blender.Get('rt') >= num:
        print >> stderr, "debug %s %03d -" % (script, num), msg


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


def focus_force(event):
    event.widget.focus_force()


def ignore(event):
    return "break"


def redraw(event=None):
    if event:
        event.widget.master.update_idletasks()
    Blender.Redraw()


class Theme:

    def __init__(self):
        self.ui = Blender.Window.Theme.Get()[0].get('ui')
        self.buts = Blender.Window.Theme.Get()[0].get(
                Blender.Window.Types.BUTS)
        self.others = {
                'panel': mix_color(self.buts.back, self.buts.panel)}
        self.defaults = {
                'activebackground': hex_color(self.ui.action),
                'activeforeground': hex_color(self.ui.text_hi),
                'background': hex_color(self.buts.back),
                'buttonbackground': hex_color(self.ui.popup),
                'disabledforeground': hex_color(self.ui.neutral),
                'foreground': hex_color(self.ui.text),
                'highlightbackground': self.others['panel'],
                'highlightcolor': hex_color(self.ui.outline),
                'highlightthickness': 2,
                'selectcolor': hex_color(self.ui.setting2),
                'selectforeground': hex_color(self.ui.text_hi),
                'selectbackground': hex_color(self.ui.textfield_hi),
                'troughcolor': hex_color(self.ui.num),
                'font': ('Helvetica', 9)}

    def config(self, widget, kw={}):
        # don't override user supplied kw, only add missing entries
        if Tkinter.BitmapImage in widget.__class__.__bases__:
            add_only(kw, 'background', hex_color(self.ui.menu_item))

        if Tkinter.Checkbutton in widget.__class__.__bases__:
            add_only(kw, 'background', self.others['panel'])

        if Tkinter.Entry in widget.__class__.__bases__:
            add_only(kw, 'background', hex_color(self.ui.textfield))

        if Tkinter.Frame in widget.__class__.__bases__:
            add_only(kw, 'background', self.others['panel'])
            add_only(kw, 'highlightthickness', 0)

        if Tkinter.Label in widget.__class__.__bases__:
            add_only(kw, 'background', self.others['panel'])

        if Tkinter.LabelFrame in widget.__class__.__bases__:
            add_only(kw, 'background', self.others['panel'])
            add_only(kw, 'padx', 5)
            add_only(kw, 'pady', 5)
            add_only(kw, 'highlightthickness', 0)
            add_only(kw, 'font', ('Helvetica', 9, 'bold'))

        if Tkinter.Menu in widget.__class__.__bases__:
            add_only(kw, 'background', hex_color(self.ui.menu_item))
            add_only(kw, 'foreground', hex_color(self.ui.menu_text))
            add_only(kw, 'activebackground', hex_color(self.ui.menu_hilite))
            add_only(kw, 'activeforeground', hex_color(self.ui.menu_text_hi))

        if Tkinter.Menubutton in widget.__class__.__bases__:
            add_only(kw, 'background', hex_color(self.buts.header))
            add_only(kw, 'foreground', hex_color(self.ui.menu_text))
            add_only(kw, 'activebackground', hex_color(self.ui.menu_hilite))
            add_only(kw, 'activeforeground', hex_color(self.ui.menu_text_hi))
            add_only(kw, 'highlightthickness', 0)

        if Tkinter.OptionMenu in widget.__class__.__bases__:
            add_only(kw, 'background', hex_color(self.ui.menu_item))
            add_only(kw, 'foreground', hex_color(self.ui.menu_text))
            add_only(kw, 'activebackground', hex_color(self.ui.menu_hilite))
            add_only(kw, 'activeforeground', hex_color(self.ui.menu_text_hi))

        if Tkinter.Radiobutton in widget.__class__.__bases__:
            add_only(kw, 'background', self.others['panel'])

        if Tkinter.Scale in widget.__class__.__bases__:
            add_only(kw, 'background', self.others['panel'])

        if Tkinter.Spinbox in widget.__class__.__bases__:
            add_only(kw, 'background', hex_color(self.ui.textfield))

        if Tkinter.Tk in widget.__class__.__bases__:
            add_only(kw, 'highlightthickness', 0)

        # add default settings
        for item in widget.config():
            if item in self.defaults.keys():
                add_only(kw, item, self.defaults[item])
        widget.config(**kw)


class Root(Tkinter.Tk):

    def __init__(self, **kw):
        Tkinter.Tk.__init__(self)
        add_only(kw, 'focusmodel', 'passive')
        theme.config(self, kw)
        # event handling
        self.bind('<FocusOut>', self.focus_out_handler)
        self.bind('<FocusIn>', self.focus_in_handler)
        self.bind('<Configure>', self.configure_handler)
        self.bind('<Escape>', self.destroy_handler)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        px, py = self.winfo_pointerxy()
        self.geometry("+%d+%d" % (px - 100, py - 100))

    def focus_out_handler(self, event):
        self.grab_release()

    def focus_in_handler(self, event):
        self.grab_set()

    def configure_handler(self, event):
        Blender.Window.RedrawAll()
        self.grab_set()

    def destroy_handler(self, event):
        self.quit()


class ModalRoot(Tkinter.Tk):

    def __init__(self, **kw):
        self._init = False
        Tkinter.Tk.__init__(self)
        if platform != "darwin":
            self.overrideredirect(True)
        theme.config(self, kw)
        # event handling
        px, py = self.winfo_pointerxy()
        self.geometry("+%d+%d" % (px - 100, py - 100))
        self.update_idletasks()
        self.bind('<Escape>', self.destroy_handler)
        self.bind('<Enter>', self.enter_handler)
        self.bind('<Button-1>', self.click_handler)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.mouse_exit = False
        # OS specific features
        if platform == "win32":
            self.attributes("-topmost", 1)
            self.bind('<FocusOut>', self.focus_out_handler)
        if platform == "darwin":
            self.focus_set()
        else:
            self.focus_force()

    def destroy_handler(self, event):
        self.grab_release()
        self.quit()

    def enter_handler(self, event):
        debug(60, "Enter: %s" % str(event.widget))
        if event.widget == self:
            self.mouse_exit = True
            if self.grab_status() == None:
                if platform == "win32":
                    self.grab_set()
                else:
                    self.grab_set_global()

    def focus_out_handler(self, event):
        debug(60, "Focus out: %s" % str(event.widget))
        if self.mouse_exit and event.widget == self\
                and self.state() == 'normal':
            # Windows specific quit
            debug(70, "Mouse exit: %s" % str(event.widget))
            self.quit()

    def click_handler(self, event):
        debug(60, "Left Click: %s" % str(event.widget))
        if self.winfo_containing(event.x_root, event.y_root) == None:
            # Linux and Mac quit
            debug(70, "Mouse exit: %s" % str(event.widget))
            self.quit()

    def deiconify(self):
        Blender.Redraw()
        Tkinter.Tk.deiconify(self)
        if self.grab_status() == None:
            if platform == "win32":
                self.grab_set()
            else:
                self.grab_set_global()

    def withdraw(self):
        Tkinter.Tk.withdraw(self)
        Blender.Redraw()


class BitmapImage(Tkinter.BitmapImage):

    def __init__(self, data=None, **kw):
        Tkinter.BitmapImage.__init__(self, data=data)
        #theme.config(self, kw)


class Button(Tkinter.Button):

    def __init__(self, parent, **kw):
        Tkinter.Button.__init__(self, parent)
        theme.config(self, kw)


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
        self.bind('<Button-1>', focus_force)


class Frame(Tkinter.Frame):

    def __init__(self, parent, **kw):
        Tkinter.Frame.__init__(self, parent)
        theme.config(self, kw)


class Label(Tkinter.Label):

    def __init__(self, parent, **kw):
        Tkinter.Label.__init__(self, parent)
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

    def __init__(self, **kw):
        Tkinter.PhotoImage.__init__(self)
        theme.config(self, kw)


class Radiobutton(Tkinter.Radiobutton):

    def __init__(self, parent, **kw):
        Tkinter.Radiobutton.__init__(self, parent)
        theme.config(self, kw)


class Scale(Tkinter.Scale):

    def __init__(self, parent, **kw):
        Tkinter.Scale.__init__(self, parent)
        theme.config(self, kw)
        self.bind('<Button-1>', focus_force)


class Scrollbar(Tkinter.Scrollbar):

    def __init__(self, parent, **kw):
        Tkinter.Scrollbar.__init__(self, parent)
        theme.config(self, kw)


class Spinbox(Tkinter.Spinbox):

    def __init__(self, parent, **kw):
        Tkinter.Spinbox.__init__(self, parent)
        theme.config(self, kw)
        self.bind('<Button-1>', focus_force)


class Text(Tkinter.Text):

    def __init__(self, parent, **kw):
        Tkinter.Text.__init__(self, parent)
        theme.config(self, kw)


class Toplevel(Tkinter.Toplevel):

    def __init__(self, parent, **kw):
        Tkinter.Toplevel.__init__(self, parent)
        theme.config(self, kw)


def main():
    root = None
    try:
        root = ModalRoot()
        f = Frame(root, relief=Tkinter.RAISED, borderwidth=1)
        f.pack()
        mb = Menubutton(f, text="About")
        mb.pack()
        Lf = LabelFrame(f, text="Label Frame")
        Lf.pack(padx=5, pady=5)
        Button(Lf, text="Panic", command=root.destroy).pack()
        Button(Lf, text="Disabled", state=Tkinter.DISABLED).pack()
        Checkbutton(Lf, text="Checkbutton").pack()
        Entry(Lf, text="Entry").pack()
        Spinbox(Lf).pack()
        Scale(Lf).pack()
        root.mainloop()
        root.destroy()
    except:
        if root:
            root.quit()
            root.destroy()
        raise

theme = Theme()

if __name__ == '__main__':
    main()
