import bpy


from bpy.props import (
        StringProperty,
        IntProperty,
        PointerProperty,
        )
        
from bpy.types import Operator

class bvhUtils():
    firstLoad = False
    #當前物體
    obj = None
    #hip的位置的list
    HipLocations = []

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
        #reader
        bpy.ops.import_anim.bvh(filepath=self.filepath)
        obj = context.object
        bvhUtils.obj = obj
        if bvhUtils.firstLoad :
            #地2隻不要顯示
            obj.hide = True
        for i in range (1, context.scene.frame_end):
            sc.frame_set(i)
            tmpLocation = []
            tmpLocation.append(obj.pose.bones['Hips'].location[0]) 
            tmpLocation.append(obj.pose.bones['Hips'].location[1]) 
            tmpLocation.append(obj.pose.bones['Hips'].location[2]) 
            #偵測動畫結束沒
            if i > 1 and (tmpLocation[0] !=  bvhUtils.HipLocations[i-2][0] or tmpLocation[1] != bvhUtils.HipLocations[i-2][1] or tmpLocation[2] != bvhUtils.HipLocations[i-2][2]):
                bvhUtils.HipLocations.append(tmpLocation)
            elif i == 1:
                bvhUtils.HipLocations.append(tmpLocation)
            else:
                break
        
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

