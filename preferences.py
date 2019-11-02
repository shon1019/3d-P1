import bpy



class BvhUtilitiesPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    projectManager = ProjectManager()

classes = (
    BvhUtilitiesPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)