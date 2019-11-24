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
from . import hair_And_Cloth

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
        row.operator("ldops.aaa", text = "comput")

        

class aaa(bpy.types.Operator):
    """bvhReader"""
    bl_idname = "ldops.aaa"
    bl_label = "aaa"

    def execute(self, context):
        hair_And_Cloth.ParticleCreaterUtils.mesh = bpy.data.meshes.new("wave")
        hair_And_Cloth.ParticleCreaterUtils.cloth = bpy.data.objects.new("wave", hair_And_Cloth.ParticleCreaterUtils.mesh)
        hair_And_Cloth.ParticleCreaterUtils.cloth1 = hair_And_Cloth.Cloth(14, 10, hair_And_Cloth.ParticleCreaterUtils.numX, hair_And_Cloth.ParticleCreaterUtils.numX) # one Cloth object of the Cloth class
        bpy.context.collection.objects.link(hair_And_Cloth.ParticleCreaterUtils.cloth)
        bpy.ops.mesh.primitive_uv_sphere_add(radius = 1, location = hair_And_Cloth.ParticleCreaterUtils.ball_pos)
        hair_And_Cloth.ParticleCreaterUtils.ball = context.object

        hair_And_Cloth.register()
        return {'FINISHED'}

classes = (
    P1,
    P2,
    aaa,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bvhReader.register()
    preferences.register()
    bpy.utils.register_class(OT_draw_operator)
    #hair_And_Cloth.register()
    print("123")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bvhReader.unregister()
    preferences.unregister()
    

if __name__ == "__main__":
    __name__ = "landscapeDesigner"
    __package__ = "landscapeDesigner"
    register()