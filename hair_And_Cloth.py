import bpy


from bpy.props import (
        StringProperty,
        IntProperty,
        PointerProperty,
        )
        
from bpy.types import Operator

class ParticleCreaterUtils():
    #布的大小 100 * 100
    particleSizw = 100
    #particle 的距離 1
    particledis = 1
    #重力
    gravity = 9.8

class ParticleUtils():
    position = 0
    velocity = 0
    mass = 0
    force = 0

class ParticleCreater(bpy.types.Operator):
    """ParticleCreater"""
    bl_idname = "ldops.particle_creater"
    bl_label = "ParticleCreater"

    def execute(self, context):
        pref = bpy.context.user_preferences.addons[__package__].preferences
        
        
        return {'FINISHED'}

classes = (
    ParticleCreater,
    ParticleCreaterUtils,
    ParticleUtils,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

