#!BPY

# """
# Name: 'Jass'
# Blender: 249
# Group: 'Themes'
# Tooltip: 'Change current theme'
# """

__author__ = "Gaia Clary"
__version__ = "2.49b"
__url__ = ["blog.machinimatrix.org"]
__bpydoc__ = """\
This is Gaia's favorite Theme. Feel free to use it, modify it, abandon it, whatever...
"""

import Blender
from Blender.Window import Theme

theme = Theme.New('Rounded')

ui = theme.get('ui')
ui.action = [212, 178, 111, 255]
ui.drawType = 2
ui.iconTheme = ''
ui.menu_back = [255, 220, 188, 111]
ui.menu_hilite = [255, 130, 0, 255]
ui.menu_item = [0, 0, 33, 83]
ui.menu_text = [255, 255, 255, 255]
ui.menu_text_hi = [0, 0, 0, 255]
ui.neutral = [176, 176, 176, 255]
ui.num = [236, 191, 130, 255]
ui.outline = [0, 0, 0, 0]
ui.popup = [186, 168, 150, 255]
ui.setting = [127, 176, 161, 255]
ui.setting1 = [171, 162, 162, 255]
ui.setting2 = [158, 158, 158, 255]
ui.text = [0, 0, 0, 255]
ui.text_hi = [255, 255, 255, 255]
ui.textfield = [107, 107, 107, 255]
ui.textfield_hi = [198, 119, 119, 255]

buts = theme.get('buts')
buts.active = [255, 187, 255, 255]
buts.audio = [0, 0, 0, 0]
buts.back = [183, 150, 144, 255]
buts.bone_pose = [0, 0, 0, 0]
buts.bone_solid = [0, 0, 0, 0]
buts.edge = [0, 0, 0, 255]
buts.edge_facesel = [0, 0, 0, 0]
buts.edge_seam = [0, 0, 0, 0]
buts.edge_select = [144, 144, 48, 255]
buts.edge_sharp = [0, 0, 0, 0]
buts.editmesh_active = [0, 0, 0, 0]
buts.effect = [0, 0, 0, 0]
buts.face = [0, 50, 150, 30]
buts.face_dot = [0, 0, 0, 0]
buts.face_select = [200, 100, 200, 60]
buts.facedot_size = 0
buts.grid = [88, 88, 88, 255]
buts.group = [0, 0, 0, 0]
buts.group_active = [0, 0, 0, 0]
buts.header = [144, 140, 140, 255]
buts.hilite = [0, 0, 0, 0]
buts.image = [0, 0, 0, 0]
buts.lamp = [0, 0, 0, 0]
buts.meta = [0, 0, 0, 0]
buts.movie = [0, 0, 0, 0]
buts.normal = [0, 0, 0, 0]
buts.panel = [169, 38, 38, 51]
buts.plugin = [0, 0, 0, 0]
buts.scene = [0, 0, 0, 0]
buts.select = [255, 136, 255, 255]
buts.shade1 = [160, 160, 160, 100]
buts.shade2 = [127, 112, 112, 100]
buts.strip = [0, 0, 0, 0]
buts.strip_select = [0, 0, 0, 0]
buts.syntaxb = [0, 0, 0, 0]
buts.syntaxc = [0, 0, 0, 0]
buts.syntaxl = [0, 0, 0, 0]
buts.syntaxn = [0, 0, 0, 0]
buts.syntaxv = [0, 0, 0, 0]
buts.text = [255, 255, 255, 255]
buts.text_hi = [255, 255, 255, 255]
buts.transform = [255, 255, 255, 255]
buts.transition = [0, 0, 0, 0]
buts.vertex = [255, 112, 255, 255]
buts.vertex_select = [255, 255, 112, 255]
buts.vertex_size = 2
buts.wire = [0, 0, 0, 255]

view3d = theme.get('view3d')
view3d.active = [255, 255, 255, 255]
view3d.audio = [0, 0, 0, 0]
view3d.back = [129, 89, 82, 255]
view3d.bone_pose = [80, 200, 255, 80]
view3d.bone_solid = [200, 200, 200, 255]
view3d.edge = [0, 0, 0, 255]
view3d.edge_facesel = [0, 0, 0, 0]
view3d.edge_seam = [230, 150, 50, 255]
view3d.edge_select = [255, 255, 255, 255]
view3d.edge_sharp = [255, 32, 32, 255]
view3d.editmesh_active = [255, 255, 255, 128]
view3d.effect = [0, 0, 0, 0]
view3d.face = [255, 255, 255, 10]
view3d.face_dot = [255, 138, 48, 255]
view3d.face_select = [255, 130, 0, 60]
view3d.facedot_size = 4
view3d.grid = [143, 143, 143, 255]
view3d.group = [16, 64, 16, 255]
view3d.group_active = [102, 255, 102, 255]
view3d.header = [107, 107, 107, 255]
view3d.hilite = [0, 0, 0, 0]
view3d.image = [0, 0, 0, 0]
view3d.lamp = [0, 0, 0, 40]
view3d.meta = [0, 0, 0, 0]
view3d.movie = [0, 0, 0, 0]
view3d.normal = [34, 221, 221, 255]
view3d.panel = [0, 0, 0, 51]
view3d.plugin = [0, 0, 0, 0]
view3d.scene = [0, 0, 0, 0]
view3d.select = [217, 217, 217, 255]
view3d.shade1 = [160, 160, 160, 100]
view3d.shade2 = [127, 112, 112, 100]
view3d.strip = [0, 0, 0, 0]
view3d.strip_select = [0, 0, 0, 0]
view3d.syntaxb = [0, 0, 0, 0]
view3d.syntaxc = [0, 0, 0, 0]
view3d.syntaxl = [0, 0, 0, 0]
view3d.syntaxn = [0, 0, 0, 0]
view3d.syntaxv = [0, 0, 0, 0]
view3d.text = [0, 0, 0, 255]
view3d.text_hi = [255, 255, 255, 255]
view3d.transform = [255, 130, 0, 255]
view3d.transition = [0, 0, 0, 0]
view3d.vertex = [0, 0, 0, 255]
view3d.vertex_select = [255, 130, 0, 255]
view3d.vertex_size = 3
view3d.wire = [0, 0, 0, 255]

file = theme.get('file')
file.active = [255, 187, 255, 255]
file.audio = [0, 0, 0, 0]
file.back = [107, 107, 107, 255]
file.bone_pose = [0, 0, 0, 0]
file.bone_solid = [0, 0, 0, 0]
file.edge = [0, 0, 0, 255]
file.edge_facesel = [0, 0, 0, 0]
file.edge_seam = [0, 0, 0, 0]
file.edge_select = [144, 144, 48, 255]
file.edge_sharp = [0, 0, 0, 0]
file.editmesh_active = [0, 0, 0, 0]
file.effect = [0, 0, 0, 0]
file.face = [0, 50, 150, 30]
file.face_dot = [0, 0, 0, 0]
file.face_select = [200, 100, 200, 60]
file.facedot_size = 0
file.grid = [88, 88, 88, 255]
file.group = [0, 0, 0, 0]
file.group_active = [0, 0, 0, 0]
file.header = [107, 107, 107, 255]
file.hilite = [255, 130, 0, 255]
file.image = [0, 0, 0, 0]
file.lamp = [0, 0, 0, 0]
file.meta = [0, 0, 0, 0]
file.movie = [0, 0, 0, 0]
file.normal = [0, 0, 0, 0]
file.panel = [165, 165, 165, 150]
file.plugin = [0, 0, 0, 0]
file.scene = [0, 0, 0, 0]
file.select = [255, 136, 255, 255]
file.shade1 = [160, 160, 160, 100]
file.shade2 = [127, 112, 112, 100]
file.strip = [0, 0, 0, 0]
file.strip_select = [0, 0, 0, 0]
file.syntaxb = [0, 0, 0, 0]
file.syntaxc = [0, 0, 0, 0]
file.syntaxl = [0, 0, 0, 0]
file.syntaxn = [0, 0, 0, 0]
file.syntaxv = [0, 0, 0, 0]
file.text = [0, 0, 0, 255]
file.text_hi = [255, 255, 255, 255]
file.transform = [255, 255, 255, 255]
file.transition = [0, 0, 0, 0]
file.vertex = [255, 112, 255, 255]
file.vertex_select = [255, 255, 112, 255]
file.vertex_size = 2
file.wire = [0, 0, 0, 255]

ipo = theme.get('ipo')
ipo.active = [255, 187, 255, 255]
ipo.audio = [0, 0, 0, 0]
ipo.back = [107, 107, 107, 255]
ipo.bone_pose = [0, 0, 0, 0]
ipo.bone_solid = [0, 0, 0, 0]
ipo.edge = [0, 0, 0, 255]
ipo.edge_facesel = [0, 0, 0, 0]
ipo.edge_seam = [0, 0, 0, 0]
ipo.edge_select = [144, 144, 48, 255]
ipo.edge_sharp = [0, 0, 0, 0]
ipo.editmesh_active = [0, 0, 0, 0]
ipo.effect = [0, 0, 0, 0]
ipo.face = [0, 50, 150, 30]
ipo.face_dot = [0, 0, 0, 0]
ipo.face_select = [200, 100, 200, 60]
ipo.facedot_size = 0
ipo.grid = [94, 94, 94, 255]
ipo.group = [0, 0, 0, 0]
ipo.group_active = [0, 0, 0, 0]
ipo.header = [107, 107, 107, 255]
ipo.hilite = [96, 192, 64, 255]
ipo.image = [0, 0, 0, 0]
ipo.lamp = [0, 0, 0, 0]
ipo.meta = [0, 0, 0, 0]
ipo.movie = [0, 0, 0, 0]
ipo.normal = [0, 0, 0, 0]
ipo.panel = [107, 107, 107, 150]
ipo.plugin = [0, 0, 0, 0]
ipo.scene = [0, 0, 0, 0]
ipo.select = [255, 136, 255, 255]
ipo.shade1 = [107, 107, 107, 100]
ipo.shade2 = [143, 143, 143, 100]
ipo.strip = [0, 0, 0, 0]
ipo.strip_select = [0, 0, 0, 0]
ipo.syntaxb = [0, 0, 0, 0]
ipo.syntaxc = [0, 0, 0, 0]
ipo.syntaxl = [0, 0, 0, 0]
ipo.syntaxn = [0, 0, 0, 0]
ipo.syntaxv = [0, 0, 0, 0]
ipo.text = [0, 0, 0, 255]
ipo.text_hi = [255, 255, 255, 255]
ipo.transform = [255, 255, 255, 255]
ipo.transition = [0, 0, 0, 0]
ipo.vertex = [255, 255, 255, 255]
ipo.vertex_select = [255, 130, 0, 255]
ipo.vertex_size = 2
ipo.wire = [0, 0, 0, 255]

info = theme.get('info')
info.active = [255, 187, 255, 255]
info.audio = [0, 0, 0, 0]
info.back = [107, 107, 107, 255]
info.bone_pose = [0, 0, 0, 0]
info.bone_solid = [0, 0, 0, 0]
info.edge = [0, 0, 0, 255]
info.edge_facesel = [0, 0, 0, 0]
info.edge_seam = [0, 0, 0, 0]
info.edge_select = [144, 144, 48, 255]
info.edge_sharp = [0, 0, 0, 0]
info.editmesh_active = [0, 0, 0, 0]
info.effect = [0, 0, 0, 0]
info.face = [0, 50, 150, 30]
info.face_dot = [0, 0, 0, 0]
info.face_select = [200, 100, 200, 60]
info.facedot_size = 0
info.grid = [88, 88, 88, 255]
info.group = [0, 0, 0, 0]
info.group_active = [0, 0, 0, 0]
info.header = [107, 107, 107, 255]
info.hilite = [0, 0, 0, 0]
info.image = [0, 0, 0, 0]
info.lamp = [0, 0, 0, 0]
info.meta = [0, 0, 0, 0]
info.movie = [0, 0, 0, 0]
info.normal = [0, 0, 0, 0]
info.panel = [165, 165, 165, 150]
info.plugin = [0, 0, 0, 0]
info.scene = [0, 0, 0, 0]
info.select = [255, 136, 255, 255]
info.shade1 = [160, 160, 160, 100]
info.shade2 = [127, 112, 112, 100]
info.strip = [0, 0, 0, 0]
info.strip_select = [0, 0, 0, 0]
info.syntaxb = [0, 0, 0, 0]
info.syntaxc = [0, 0, 0, 0]
info.syntaxl = [0, 0, 0, 0]
info.syntaxn = [0, 0, 0, 0]
info.syntaxv = [0, 0, 0, 0]
info.text = [0, 0, 0, 255]
info.text_hi = [255, 255, 255, 255]
info.transform = [255, 255, 255, 255]
info.transition = [0, 0, 0, 0]
info.vertex = [255, 112, 255, 255]
info.vertex_select = [255, 255, 112, 255]
info.vertex_size = 2
info.wire = [0, 0, 0, 255]

sound = theme.get('sound')
sound.active = [255, 187, 255, 255]
sound.audio = [0, 0, 0, 0]
sound.back = [158, 158, 158, 255]
sound.bone_pose = [0, 0, 0, 0]
sound.bone_solid = [0, 0, 0, 0]
sound.edge = [0, 0, 0, 255]
sound.edge_facesel = [0, 0, 0, 0]
sound.edge_seam = [0, 0, 0, 0]
sound.edge_select = [144, 144, 48, 255]
sound.edge_sharp = [0, 0, 0, 0]
sound.editmesh_active = [0, 0, 0, 0]
sound.effect = [0, 0, 0, 0]
sound.face = [0, 50, 150, 30]
sound.face_dot = [0, 0, 0, 0]
sound.face_select = [200, 100, 200, 60]
sound.facedot_size = 0
sound.grid = [112, 112, 96, 255]
sound.group = [0, 0, 0, 0]
sound.group_active = [0, 0, 0, 0]
sound.header = [158, 158, 158, 255]
sound.hilite = [0, 0, 0, 0]
sound.image = [0, 0, 0, 0]
sound.lamp = [0, 0, 0, 0]
sound.meta = [0, 0, 0, 0]
sound.movie = [0, 0, 0, 0]
sound.normal = [0, 0, 0, 0]
sound.panel = [165, 165, 165, 150]
sound.plugin = [0, 0, 0, 0]
sound.scene = [0, 0, 0, 0]
sound.select = [255, 136, 255, 255]
sound.shade1 = [140, 140, 140, 255]
sound.shade2 = [127, 112, 112, 100]
sound.strip = [0, 0, 0, 0]
sound.strip_select = [0, 0, 0, 0]
sound.syntaxb = [0, 0, 0, 0]
sound.syntaxc = [0, 0, 0, 0]
sound.syntaxl = [0, 0, 0, 0]
sound.syntaxn = [0, 0, 0, 0]
sound.syntaxv = [0, 0, 0, 0]
sound.text = [0, 0, 0, 255]
sound.text_hi = [255, 255, 255, 255]
sound.transform = [255, 255, 255, 255]
sound.transition = [0, 0, 0, 0]
sound.vertex = [255, 112, 255, 255]
sound.vertex_select = [255, 255, 112, 255]
sound.vertex_size = 2
sound.wire = [0, 0, 0, 255]

action = theme.get('action')
action.active = [255, 187, 255, 255]
action.audio = [0, 0, 0, 0]
action.back = [107, 107, 107, 255]
action.bone_pose = [0, 0, 0, 0]
action.bone_solid = [0, 0, 0, 0]
action.edge = [0, 0, 0, 255]
action.edge_facesel = [0, 0, 0, 0]
action.edge_seam = [0, 0, 0, 0]
action.edge_select = [144, 144, 48, 255]
action.edge_sharp = [0, 0, 0, 0]
action.editmesh_active = [0, 0, 0, 0]
action.effect = [0, 0, 0, 0]
action.face = [143, 143, 143, 255]
action.face_dot = [0, 0, 0, 0]
action.face_select = [200, 100, 200, 60]
action.facedot_size = 0
action.grid = [94, 94, 94, 255]
action.group = [57, 125, 27, 255]
action.group_active = [125, 233, 96, 255]
action.header = [107, 107, 107, 255]
action.hilite = [255, 130, 0, 100]
action.image = [0, 0, 0, 0]
action.lamp = [0, 0, 0, 0]
action.meta = [0, 0, 0, 0]
action.movie = [0, 0, 0, 0]
action.normal = [0, 0, 0, 0]
action.panel = [165, 165, 165, 150]
action.plugin = [0, 0, 0, 0]
action.scene = [0, 0, 0, 0]
action.select = [255, 136, 255, 255]
action.shade1 = [107, 107, 107, 255]
action.shade2 = [178, 178, 178, 100]
action.strip = [228, 156, 198, 204]
action.strip_select = [255, 255, 170, 204]
action.syntaxb = [0, 0, 0, 0]
action.syntaxc = [0, 0, 0, 0]
action.syntaxl = [0, 0, 0, 0]
action.syntaxn = [0, 0, 0, 0]
action.syntaxv = [0, 0, 0, 0]
action.text = [0, 0, 0, 255]
action.text_hi = [255, 255, 255, 255]
action.transform = [255, 255, 255, 255]
action.transition = [0, 0, 0, 0]
action.vertex = [255, 112, 255, 255]
action.vertex_select = [255, 255, 112, 255]
action.vertex_size = 2
action.wire = [0, 0, 0, 255]

nla = theme.get('nla')
nla.active = [255, 187, 255, 255]
nla.audio = [0, 0, 0, 0]
nla.back = [107, 107, 107, 255]
nla.bone_pose = [0, 0, 0, 0]
nla.bone_solid = [0, 0, 0, 0]
nla.edge = [0, 0, 0, 255]
nla.edge_facesel = [0, 0, 0, 0]
nla.edge_seam = [0, 0, 0, 0]
nla.edge_select = [144, 144, 48, 255]
nla.edge_sharp = [0, 0, 0, 0]
nla.editmesh_active = [0, 0, 0, 0]
nla.effect = [0, 0, 0, 0]
nla.face = [0, 50, 150, 30]
nla.face_dot = [0, 0, 0, 0]
nla.face_select = [200, 100, 200, 60]
nla.facedot_size = 0
nla.grid = [94, 94, 94, 255]
nla.group = [0, 0, 0, 0]
nla.group_active = [0, 0, 0, 0]
nla.header = [143, 143, 143, 255]
nla.hilite = [255, 130, 0, 100]
nla.image = [0, 0, 0, 0]
nla.lamp = [0, 0, 0, 0]
nla.meta = [0, 0, 0, 0]
nla.movie = [0, 0, 0, 0]
nla.normal = [0, 0, 0, 0]
nla.panel = [165, 165, 165, 150]
nla.plugin = [0, 0, 0, 0]
nla.scene = [0, 0, 0, 0]
nla.select = [255, 136, 255, 255]
nla.shade1 = [107, 107, 107, 255]
nla.shade2 = [178, 178, 178, 100]
nla.strip = [228, 156, 198, 255]
nla.strip_select = [255, 255, 170, 255]
nla.syntaxb = [0, 0, 0, 0]
nla.syntaxc = [0, 0, 0, 0]
nla.syntaxl = [0, 0, 0, 0]
nla.syntaxn = [0, 0, 0, 0]
nla.syntaxv = [0, 0, 0, 0]
nla.text = [0, 0, 0, 255]
nla.text_hi = [255, 255, 255, 255]
nla.transform = [255, 255, 255, 255]
nla.transition = [0, 0, 0, 0]
nla.vertex = [255, 112, 255, 255]
nla.vertex_select = [255, 255, 112, 255]
nla.vertex_size = 2
nla.wire = [0, 0, 0, 255]

seq = theme.get('seq')
seq.active = [255, 187, 255, 255]
seq.audio = [46, 143, 143, 255]
seq.back = [107, 107, 107, 255]
seq.bone_pose = [80, 200, 255, 255]
seq.bone_solid = [0, 0, 0, 0]
seq.edge = [0, 0, 0, 255]
seq.edge_facesel = [0, 0, 0, 0]
seq.edge_seam = [0, 0, 0, 0]
seq.edge_select = [144, 144, 48, 255]
seq.edge_sharp = [0, 0, 0, 0]
seq.editmesh_active = [0, 0, 0, 0]
seq.effect = [169, 84, 124, 255]
seq.face = [0, 50, 150, 30]
seq.face_dot = [0, 0, 0, 0]
seq.face_select = [200, 100, 200, 60]
seq.facedot_size = 0
seq.grid = [88, 88, 88, 255]
seq.group = [0, 0, 0, 0]
seq.group_active = [0, 0, 0, 0]
seq.header = [107, 107, 107, 255]
seq.hilite = [0, 0, 0, 0]
seq.image = [109, 88, 129, 255]
seq.lamp = [0, 0, 0, 0]
seq.meta = [109, 145, 131, 255]
seq.movie = [81, 105, 135, 255]
seq.normal = [0, 0, 0, 0]
seq.panel = [165, 165, 165, 150]
seq.plugin = [126, 126, 80, 255]
seq.scene = [78, 152, 62, 255]
seq.select = [255, 136, 255, 255]
seq.shade1 = [160, 160, 160, 100]
seq.shade2 = [127, 112, 112, 100]
seq.strip = [0, 0, 0, 0]
seq.strip_select = [0, 0, 0, 0]
seq.syntaxb = [0, 0, 0, 0]
seq.syntaxc = [0, 0, 0, 0]
seq.syntaxl = [0, 0, 0, 0]
seq.syntaxn = [0, 0, 0, 0]
seq.syntaxv = [0, 0, 0, 0]
seq.text = [0, 0, 0, 255]
seq.text_hi = [255, 255, 255, 255]
seq.transform = [255, 255, 255, 255]
seq.transition = [162, 95, 111, 255]
seq.vertex = [255, 112, 255, 255]
seq.vertex_select = [255, 130, 0, 255]
seq.vertex_size = 2
seq.wire = [0, 0, 0, 255]

image = theme.get('image')
image.active = [255, 187, 255, 255]
image.audio = [0, 0, 0, 0]
image.back = [53, 53, 53, 255]
image.bone_pose = [80, 200, 255, 255]
image.bone_solid = [0, 0, 0, 0]
image.edge = [0, 0, 0, 255]
image.edge_facesel = [0, 0, 0, 0]
image.edge_seam = [0, 0, 0, 0]
image.edge_select = [144, 144, 48, 255]
image.edge_sharp = [0, 0, 0, 0]
image.editmesh_active = [0, 0, 0, 0]
image.effect = [0, 0, 0, 0]
image.face = [0, 50, 150, 30]
image.face_dot = [0, 0, 0, 0]
image.face_select = [200, 100, 200, 60]
image.facedot_size = 0
image.grid = [88, 88, 88, 255]
image.group = [0, 0, 0, 0]
image.group_active = [0, 0, 0, 0]
image.header = [195, 195, 195, 255]
image.hilite = [0, 0, 0, 0]
image.image = [0, 0, 0, 0]
image.lamp = [0, 0, 0, 0]
image.meta = [0, 0, 0, 0]
image.movie = [0, 0, 0, 0]
image.normal = [0, 0, 0, 0]
image.panel = [165, 165, 165, 150]
image.plugin = [0, 0, 0, 0]
image.scene = [0, 0, 0, 0]
image.select = [255, 136, 255, 255]
image.shade1 = [160, 160, 160, 100]
image.shade2 = [127, 112, 112, 100]
image.strip = [0, 0, 0, 0]
image.strip_select = [0, 0, 0, 0]
image.syntaxb = [0, 0, 0, 0]
image.syntaxc = [0, 0, 0, 0]
image.syntaxl = [0, 0, 0, 0]
image.syntaxn = [0, 0, 0, 0]
image.syntaxv = [0, 0, 0, 0]
image.text = [0, 0, 0, 255]
image.text_hi = [255, 255, 255, 255]
image.transform = [255, 255, 255, 255]
image.transition = [0, 0, 0, 0]
image.vertex = [255, 112, 255, 255]
image.vertex_select = [255, 255, 112, 255]
image.vertex_size = 2
image.wire = [0, 0, 0, 255]

imasel = theme.get('imasel')
imasel.active = [255, 187, 255, 255]
imasel.audio = [0, 0, 0, 0]
imasel.back = [107, 107, 107, 255]
imasel.bone_pose = [0, 0, 0, 0]
imasel.bone_solid = [0, 0, 0, 0]
imasel.edge = [0, 0, 0, 255]
imasel.edge_facesel = [0, 0, 0, 0]
imasel.edge_seam = [0, 0, 0, 0]
imasel.edge_select = [144, 144, 48, 255]
imasel.edge_sharp = [0, 0, 0, 0]
imasel.editmesh_active = [0, 0, 0, 0]
imasel.effect = [0, 0, 0, 0]
imasel.face = [0, 50, 150, 30]
imasel.face_dot = [0, 0, 0, 0]
imasel.face_select = [200, 100, 200, 60]
imasel.facedot_size = 0
imasel.grid = [88, 88, 88, 255]
imasel.group = [0, 0, 0, 0]
imasel.group_active = [0, 0, 0, 0]
imasel.header = [195, 195, 195, 255]
imasel.hilite = [0, 0, 0, 0]
imasel.image = [0, 0, 0, 0]
imasel.lamp = [0, 0, 0, 0]
imasel.meta = [0, 0, 0, 0]
imasel.movie = [0, 0, 0, 0]
imasel.normal = [0, 0, 0, 0]
imasel.panel = [165, 165, 165, 150]
imasel.plugin = [0, 0, 0, 0]
imasel.scene = [0, 0, 0, 0]
imasel.select = [255, 136, 255, 255]
imasel.shade1 = [143, 143, 143, 255]
imasel.shade2 = [127, 112, 112, 100]
imasel.strip = [0, 0, 0, 0]
imasel.strip_select = [0, 0, 0, 0]
imasel.syntaxb = [0, 0, 0, 0]
imasel.syntaxc = [0, 0, 0, 0]
imasel.syntaxl = [0, 0, 0, 0]
imasel.syntaxn = [0, 0, 0, 0]
imasel.syntaxv = [0, 0, 0, 0]
imasel.text = [0, 0, 0, 255]
imasel.text_hi = [255, 255, 255, 255]
imasel.transform = [255, 255, 255, 255]
imasel.transition = [0, 0, 0, 0]
imasel.vertex = [255, 112, 255, 255]
imasel.vertex_select = [255, 255, 112, 255]
imasel.vertex_size = 2
imasel.wire = [0, 0, 0, 255]

text = theme.get('text')
text.active = [255, 187, 255, 255]
text.audio = [0, 0, 0, 0]
text.back = [153, 153, 153, 255]
text.bone_pose = [0, 0, 0, 0]
text.bone_solid = [0, 0, 0, 0]
text.edge = [0, 0, 0, 255]
text.edge_facesel = [0, 0, 0, 0]
text.edge_seam = [0, 0, 0, 0]
text.edge_select = [144, 144, 48, 255]
text.edge_sharp = [0, 0, 0, 0]
text.editmesh_active = [0, 0, 0, 0]
text.effect = [0, 0, 0, 0]
text.face = [0, 50, 150, 30]
text.face_dot = [0, 0, 0, 0]
text.face_select = [200, 100, 200, 60]
text.facedot_size = 0
text.grid = [88, 88, 88, 255]
text.group = [0, 0, 0, 0]
text.group_active = [0, 0, 0, 0]
text.header = [153, 153, 153, 255]
text.hilite = [255, 0, 0, 255]
text.image = [0, 0, 0, 0]
text.lamp = [0, 0, 0, 0]
text.meta = [0, 0, 0, 0]
text.movie = [0, 0, 0, 0]
text.normal = [0, 0, 0, 0]
text.panel = [165, 165, 165, 150]
text.plugin = [0, 0, 0, 0]
text.scene = [0, 0, 0, 0]
text.select = [255, 136, 255, 255]
text.shade1 = [143, 143, 143, 255]
text.shade2 = [198, 119, 119, 255]
text.strip = [0, 0, 0, 0]
text.strip_select = [0, 0, 0, 0]
text.syntaxb = [128, 0, 80, 255]
text.syntaxc = [0, 100, 50, 255]
text.syntaxl = [100, 0, 0, 255]
text.syntaxn = [0, 0, 200, 255]
text.syntaxv = [95, 95, 0, 255]
text.text = [0, 0, 0, 255]
text.text_hi = [255, 255, 255, 255]
text.transform = [255, 255, 255, 255]
text.transition = [0, 0, 0, 0]
text.vertex = [255, 112, 255, 255]
text.vertex_select = [255, 255, 112, 255]
text.vertex_size = 2
text.wire = [0, 0, 0, 255]

oops = theme.get('oops')
oops.active = [255, 187, 255, 255]
oops.audio = [0, 0, 0, 0]
oops.back = [107, 107, 107, 255]
oops.bone_pose = [0, 0, 0, 0]
oops.bone_solid = [0, 0, 0, 0]
oops.edge = [0, 0, 0, 255]
oops.edge_facesel = [0, 0, 0, 0]
oops.edge_seam = [0, 0, 0, 0]
oops.edge_select = [144, 144, 48, 255]
oops.edge_sharp = [0, 0, 0, 0]
oops.editmesh_active = [0, 0, 0, 0]
oops.effect = [0, 0, 0, 0]
oops.face = [0, 50, 150, 30]
oops.face_dot = [0, 0, 0, 0]
oops.face_select = [200, 100, 200, 60]
oops.facedot_size = 0
oops.grid = [88, 88, 88, 255]
oops.group = [0, 0, 0, 0]
oops.group_active = [0, 0, 0, 0]
oops.header = [107, 107, 107, 255]
oops.hilite = [0, 0, 0, 0]
oops.image = [0, 0, 0, 0]
oops.lamp = [0, 0, 0, 0]
oops.meta = [0, 0, 0, 0]
oops.movie = [0, 0, 0, 0]
oops.normal = [0, 0, 0, 0]
oops.panel = [165, 165, 165, 150]
oops.plugin = [0, 0, 0, 0]
oops.scene = [0, 0, 0, 0]
oops.select = [255, 136, 255, 255]
oops.shade1 = [160, 160, 160, 100]
oops.shade2 = [127, 112, 112, 100]
oops.strip = [0, 0, 0, 0]
oops.strip_select = [0, 0, 0, 0]
oops.syntaxb = [0, 0, 0, 0]
oops.syntaxc = [0, 0, 0, 0]
oops.syntaxl = [0, 0, 0, 0]
oops.syntaxn = [0, 0, 0, 0]
oops.syntaxv = [0, 0, 0, 0]
oops.text = [0, 0, 0, 255]
oops.text_hi = [255, 255, 255, 255]
oops.transform = [255, 255, 255, 255]
oops.transition = [0, 0, 0, 0]
oops.vertex = [255, 112, 255, 255]
oops.vertex_select = [255, 255, 112, 255]
oops.vertex_size = 2
oops.wire = [0, 0, 0, 255]

time = theme.get('time')
time.active = [255, 187, 255, 255]
time.audio = [0, 0, 0, 0]
time.back = [158, 158, 158, 255]
time.bone_pose = [0, 0, 0, 0]
time.bone_solid = [0, 0, 0, 0]
time.edge = [0, 0, 0, 255]
time.edge_facesel = [0, 0, 0, 0]
time.edge_seam = [0, 0, 0, 0]
time.edge_select = [144, 144, 48, 255]
time.edge_sharp = [0, 0, 0, 0]
time.editmesh_active = [0, 0, 0, 0]
time.effect = [0, 0, 0, 0]
time.face = [0, 50, 150, 30]
time.face_dot = [0, 0, 0, 0]
time.face_select = [200, 100, 200, 60]
time.facedot_size = 0
time.grid = [112, 112, 96, 255]
time.group = [0, 0, 0, 0]
time.group_active = [0, 0, 0, 0]
time.header = [158, 158, 158, 255]
time.hilite = [0, 0, 0, 0]
time.image = [0, 0, 0, 0]
time.lamp = [0, 0, 0, 0]
time.meta = [0, 0, 0, 0]
time.movie = [0, 0, 0, 0]
time.normal = [0, 0, 0, 0]
time.panel = [165, 165, 165, 150]
time.plugin = [0, 0, 0, 0]
time.scene = [0, 0, 0, 0]
time.select = [255, 136, 255, 255]
time.shade1 = [140, 140, 140, 255]
time.shade2 = [127, 112, 112, 100]
time.strip = [0, 0, 0, 0]
time.strip_select = [0, 0, 0, 0]
time.syntaxb = [0, 0, 0, 0]
time.syntaxc = [0, 0, 0, 0]
time.syntaxl = [0, 0, 0, 0]
time.syntaxn = [0, 0, 0, 0]
time.syntaxv = [0, 0, 0, 0]
time.text = [0, 0, 0, 255]
time.text_hi = [255, 255, 255, 255]
time.transform = [255, 255, 255, 255]
time.transition = [0, 0, 0, 0]
time.vertex = [255, 112, 255, 255]
time.vertex_select = [255, 255, 112, 255]
time.vertex_size = 2
time.wire = [0, 0, 0, 255]

node = theme.get('node')
node.active = [255, 255, 255, 255]
node.audio = [0, 0, 0, 0]
node.back = [107, 107, 107, 255]
node.bone_pose = [80, 200, 255, 80]
node.bone_solid = [200, 200, 200, 255]
node.edge = [0, 0, 0, 255]
node.edge_facesel = [0, 0, 0, 0]
node.edge_seam = [230, 150, 50, 255]
node.edge_select = [255, 255, 255, 255]
node.edge_sharp = [0, 0, 0, 0]
node.editmesh_active = [0, 0, 0, 0]
node.effect = [0, 0, 0, 0]
node.face = [255, 255, 255, 10]
node.face_dot = [255, 138, 48, 255]
node.face_select = [255, 130, 0, 60]
node.facedot_size = 4
node.grid = [143, 143, 143, 255]
node.group = [0, 0, 0, 0]
node.group_active = [0, 0, 0, 0]
node.header = [107, 107, 107, 255]
node.hilite = [0, 0, 0, 0]
node.image = [0, 0, 0, 0]
node.lamp = [0, 0, 0, 40]
node.meta = [0, 0, 0, 0]
node.movie = [0, 0, 0, 0]
node.normal = [34, 221, 221, 255]
node.panel = [0, 0, 0, 51]
node.plugin = [0, 0, 0, 0]
node.scene = [0, 0, 0, 0]
node.select = [217, 217, 217, 255]
node.shade1 = [160, 160, 160, 100]
node.shade2 = [127, 112, 112, 100]
node.strip = [0, 0, 0, 0]
node.strip_select = [0, 0, 0, 0]
node.syntaxb = [127, 127, 127, 255]
node.syntaxc = [120, 145, 120, 255]
node.syntaxl = [150, 150, 150, 255]
node.syntaxn = [129, 131, 144, 255]
node.syntaxv = [142, 138, 145, 255]
node.text = [0, 0, 0, 255]
node.text_hi = [255, 255, 255, 255]
node.transform = [255, 130, 0, 255]
node.transition = [0, 0, 0, 0]
node.vertex = [0, 0, 0, 255]
node.vertex_select = [255, 130, 0, 255]
node.vertex_size = 3
node.wire = [0, 0, 0, 255]

Blender.Redraw(-1)