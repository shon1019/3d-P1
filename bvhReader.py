import bpy


from bpy.props import (
        StringProperty,
        IntProperty,
        PointerProperty,
        )
        
from bpy.types import Operator



class bvhReader(bpy.types.Operator):
    """bvhReader"""
    bl_idname = "ldops.bvh_reader"
    bl_label = "bvhReader"

    def execute(self, context):

        return {'FINISHED'}

classes = (
    bvhReader,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

