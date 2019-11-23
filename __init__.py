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
    "name": "landscapeDesigner",
    "author": "晟暘科技",
    "version": (5, 8, 6),
    "blender": (2, 80, 0),
    "location": "View3D > UI",
    "description": "地景設計套裝",
    "wiki_url" : "http://chenyang56685193.com/",
    "category": "Mesh"}


import bpy

from bpy.props import StringProperty, FloatProperty, IntProperty
from bpy.types import Operator, Panel, WindowManager, UILayout
import bpy.utils.previews

from . import preferences
from . import bvhReader

from . draw_op import OT_draw_operator

# Main Operators
class P1(bpy.types.Panel):
    bl_idname = "P1_PT_Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "liveDesign"
    bl_label = "P1"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("ldops.bvh_reader", text = "import bvh")
        row.operator("object.draw_op", text = "Draw Ori Line")
        row.operator("ldops.recompute", text = "comput")

# Main Operators
class P2(bpy.types.Panel):
    bl_idname = "P2_PT_Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "liveDesign"
    bl_label = "P2"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        row = layout.row()

classes = (
    P1,
    P2,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bvhReader.register()
    preferences.register()

    bpy.utils.register_class(OT_draw_operator)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bvhReader.unregister()
    preferences.unregister()

if __name__ == "__main__":
    __name__ = "landscapeDesigner"
    __package__ = "landscapeDesigner"
    register()