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
    "name": "Landscape Designer",
    "author": "晟暘科技",
    "version": (5, 8, 6),
    "blender": (2, 77),
    "location": "View3D > TOOLS",
    "description": "地景設計套裝",
    "wiki_url" : "http://chenyang56685193.com/",
    "category": "Mesh"}

import bpy

from bpy.props import StringProperty, FloatProperty, IntProperty
from bpy.types import Operator, Panel, WindowManager, UILayout
import bpy.utils.previews

from . import preferences
from . import bvhReader

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
        layout = self.layout
        row = layout.row()
        row.operator("ldops.bvh_reader", text = "匯入bvh")

classes = (
    DesignTool,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bvhReader.register()
    preferences.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bvhReader.unregister()
    preferences.unregister()


if __name__ == "__main__":
    __name__ = "landscapeDesigner"
    __package__ = "landscapeDesigner"
    register()