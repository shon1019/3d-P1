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
        sc = context.scene
        #hip的位置的list
        HipLocations = []

        bpy.ops.import_anim.bvh(filepath=self.filepath)
        obj = context.object
        #該動畫結束時間
        endFrame = obj.animation_data.nla_tracks['NlaTrack'].strips[0].frame_end
        if bvhUtils.firstLoad :
            #地2隻不要顯示
            obj.hide = True
        for i in range (0, endFrame + 1):
            sc.frame_set(i)
            tmpLocation = []
            tmpLocation.append(obj.pose.bones['Hips'].location[0]) 
            tmpLocation.append(obj.pose.bones['Hips'].location[1]) 
            tmpLocation.append(obj.pose.bones['Hips'].location[2]) 
            HipLocations.append(tmpLocation)
        
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

