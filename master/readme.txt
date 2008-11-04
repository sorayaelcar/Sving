
Create, Import & Export Sculpties In Blender by Domino Marama
Copyright 2007-2008 Domino Designs Limited

**** Introduction ****

These Blender scripts provide "sculptie map" ( https://wiki.secondlife.com/wiki/Sculpted_Prims:_FAQ )
support to Blender. They use the addMultiresLevel feature that was introduced in Blender 2.46 which
you can get from http://www.blender.org/download/get-blender/

**** Installation ****

copy the .py files to your Blender scripts directory. The exact directory varies depending on the
options you selected during the install of Blender.

If you go to Help - System - System Information it will create a text document with the correct path in.

Go to the "Text Editor" and you should see a toolbar icon that looks like up and down triangles.

Click that and select "system-info.txt" Scroll up and you should see the directories listed.

--------->8-------------
- Directories:

Blender home dir:
/home/domino/.blender

Default dir for scripts:
/home/domino/.blender/scripts

Default "bpydata/" data dir for scripts:
/home/domino/.blender/scripts/bpydata

User defined dir for scripts:
/media/data/blender_scripts/

------------>8--------------

You can put the scripts in either "Default dir for scripts" or "User defined dir for scripts"

http://wiki.blender.org/index.php/Manual/Python_Scripting has more information on the text editor.

**** Checking Install ****

Run Blender and in the "File - Import" menu you should see a new option
for 'Second Life Sculptie'
	
If the option is missing, select the scripts window and use
"Scripts - Update Menus" to refresh the menus.

**** Creating a new Sculptie ****

From the Blender menus select Add - Mesh - Sculpt Mesh.
This will show a dialog where you can choose the sculptie type and
alter the number of faces and multires levels. Normally you would
only select the type as the default settings are correct. Changing
the faces and multires level is provided for advanced techniques
of Sculptie making.

You can then move the vertice in edit mode or sculpt mode to create
the desired sculptie shape. When finished you can create (or update)
the sculptie map by selecting Render - Bake Second Life Sculpties
from the menus.

This will update the sculptie maps for all selected meshes. They will
use the same scale, so if you want maximum detail only select one mesh
before baking.

If you are doing animated sculpties then all objects should have the
same centre and any required offset done in mesh edit mode. Select all
stages of the animation to bake at the same time.

You can see and save the map images in the UV/Image Editor window.

After saving, the sculptie map is scaled to one Blender Unit (1m in
Second Life) in all three directions. If you prefer the sculptie to
keep it's proportions at a sacrifice of some detail, then you can
uncheck "Normalise". The console window will have the LSL script
commands to recreate the sculpties in SL.

The baker uses the UV map so any object mapped to a full flat square
will work. If you have some mesh parts missing, then selecting
"Fill Holes" will surface over missing pieces for the sculptie map.

**** Importing an existing sculptie ****

Simply select 'Second Life Sculptie' from the "File - Import" menu and
choose the sculptie map to import (hint: click filename with middle mouse
button to open quickly). You will be given an options dialog that will
let you select the sculptured prim type and the scale (these match the
sizes in Second Life).

The mesh will be imported with 3 multires levels. You can switch between
them on the editing panel. These correspond to the 3 highest levels of
detail in Second Life so you can check how gracefully your sculptie
degrades when viewed from a distance.

**** Export to LSL ****

Simply select "Second Life LSL" from the "File - Export" menu and
choose a directory to export to. This will save the selected sculptie's
map and texture plus a short LSL script to recreate the prim inworld.

In Second Life, upload the .tga files from the directory. Create a new
prim and edit the contents. Add the .tga files to the contents. Create
a "New Script" in the contents and edit it.

In a text editor open the .LSL file, select all and copy.

Go back to Second Life and select all the script then paste the script
you copied from the text editor over it. Save the script and it will run
and turn the prim into the sculptie you exported from Blender.
