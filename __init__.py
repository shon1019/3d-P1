# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "P1",
    "author": "shion",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "Sequencer -> Track View Properties",
    "description": "Load a CMX formatted EDL into the sequencer",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Import-Export/EDL_Import",
    "category": "Import-Export",
}

import bpy


from bpy.props import (
        StringProperty,
        IntProperty,
        PointerProperty,
        )

from bpy.types import Operator

if "bpy" in locals():
    import importlib
    importlib.reload(preferences)
# ----------------------------------------------------------------------------
# Main Operators
class DesignTool(bpy.types.Panel):
    bl_idname = "animationTool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "liveDesign"
    bl_label = "動畫工具"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        row = layout.row()

classes = (
    DesignTool,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)



if __name__ == "__main__":
    register()