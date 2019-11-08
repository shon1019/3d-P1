import bpy


from bpy.props import (
        StringProperty,
        IntProperty,
        PointerProperty,
        )
        
from bpy.types import Operator

class bvhUtils():
    firstLoad = False

class bvhReader(bpy.types.Operator):
    """bvhReader"""
    bl_idname = "ldops.bvh_reader"
    bl_label = "bvhReader"

    filter_glob = bpy.props.StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(subtype="FILE_PATH") 

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self) 
        return {'RUNNING_MODAL'}

    def execute(self, context):
        pref = bpy.context.user_preferences.addons[__package__].preferences
        bpy.ops.import_anim.bvh(filepath=self.filepath)
        if bvhUtils.firstLoad :
            context.object.hide = True
        
        return {'FINISHED'}

classes = (
    bvhReader,
    bvhUtils,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

