import bpy
from bpy.props import *



class hairUtilitiesPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    mass = FloatProperty(name="質量", default=1)
    windForce = FloatVectorProperty(name = "風力", default = (0.5, 0, 0.2))
    gravity = FloatVectorProperty(name = "風力", default = (0, -9.8, 0))
    # mesh variables
    numX = IntProperty(name = "寬", default=25)
    numY = IntProperty(name = "高", default=25)


def register():
    bpy.utils.register_class(hairUtilitiesPreferences)

def unregister():
    bpy.utils.unregister_class(hairUtilitiesPreferences)