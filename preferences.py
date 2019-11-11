import bpy



class BvhUtilitiesPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

class hairUtilitiesPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

classes = (
    BvhUtilitiesPreferences,
    hairUtilitiesPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)