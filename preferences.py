import bpy
from bpy.props import *
  
IntegrateMethod = [
    ("Eular","Eular","",1),
    ("RungeKutta2","RungeKutta2","",2),
    ("Verlet","Verlet","",3),
    ("Leapfrog","Leapfrog","",4),
    ("Symplectic","Symplectic","",5)
    ]
    
class hairUtilitiesPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    frameRate = IntProperty(name="Frame Rate", default=60, min = 1, max = 60)
    timeStep = FloatProperty(name="Time Step", default=0.2)
    mass = FloatProperty(name="質量", default=1)
    damping = FloatProperty(name="damping", default=0.02)
    spring = FloatProperty(name="spring", default=0.02)
    windForce = FloatVectorProperty(name = "風力", default = (0.5, 0, 0.2))
    gravity = FloatVectorProperty(name = "風力", default = (0, -9.8, 0))
    # mesh variables
    numX = IntProperty(name = "寬", default=5)
    numY = IntProperty(name = "高", default=5)
    lastMode = EnumProperty(name = "積分方式", items=IntegrateMethod, default = 'Eular')
    integrateMode = EnumProperty(name = "積分方式", items=IntegrateMethod, default = 'Eular')

def register():
    bpy.utils.register_class(hairUtilitiesPreferences)

def unregister():
    bpy.utils.unregister_class(hairUtilitiesPreferences)