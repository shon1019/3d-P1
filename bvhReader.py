import bpy


from bpy.props import (
        StringProperty,
        IntProperty,
        PointerProperty,
        )
        
from bpy.types import Operator
from . import SolveLeastSquare

'''
1.移除root位移
2.算最近pose
3.concate
4.camera focus
'''

class bvhUtils():
    firstLoad = False
    #當前物體
    obj = None
    #hip的位置的list
    HipLocations = []
    #曲線
    curveOB = None

class recompute(bpy.types.Operator):
    bl_idname = "ldops.recompute"
    bl_label = "recompute"

    def execute(self, context):
        bvhUtils.obj.select_set(True)
        context.view_layer.objects.active = bvhUtils.curveOB
        bvhUtils.curveOB.select_set(True)
        bpy.ops.object.parent_set(type='FOLLOW') #follow path
        return {'FINISHED'}

class concat(bpy.types.Operator):
    bl_idname = "ldops.concat"
    bl_label = "concat"

    def execute(self, context):
        obj = context.object
        obj.animation_data.action = None
        obj.animation_data.nla_tracks.new()
        obj.animation_data.nla_tracks.new()
        #------------------------------------------------------------------
        obj.animation_data.nla_tracks['NlaTrack'].strips.new("dance", 1.0, bpy.data.actions['dance1'])
        obj.animation_data.nla_tracks['NlaTrack.001'].strips.new("dance", 1.0, bpy.data.actions['dance'])
        return {'FINISHED'}

class cameraTrack(bpy.types.Operator):
    bl_idname = "ldops.cameraTrack"
    bl_label = "cameraTrack"

    def execute(self, context):
        camera = bpy.data.objects['Camera']

        camera.select_set(True)
        context.view_layer.objects.active = bvhUtils.curveOB
        bvhUtils.curveOB.select_set(True)
        bpy.ops.object.parent_set(type='FOLLOW') #follow path

        targetobj = context.object
        ttc = camera.constraints.new(type='TRACK_TO')
        ttc.target = targetobj
        ttc.track_axis = 'TRACK_NEGATIVE_Z'
        ttc.up_axis = 'UP_Y'

        return {'FINISHED'}


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
        pref = bpy.context.preferences.addons[__package__].preferences
        sc = context.scene
        #reader
        bpy.ops.import_anim.bvh(filepath=self.filepath)
        obj = context.object
        bvhUtils.obj = obj
        if bvhUtils.firstLoad :
            #地2隻不要顯示
            obj.hide_viewport = True
        aniTime = 0

        bvhUtils.firstLoad = True
        print("*------------------------")
        for i in range (1, context.scene.frame_end):
            aniTime += 1
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
                print(i)
                print("*------------------------")
                print(tmpLocation[0] )
                print(bvhUtils.HipLocations[i-2][0])
                print(tmpLocation[1])
                print(bvhUtils.HipLocations[i-2][1])
                print(tmpLocation[2])
                print(bvhUtils.HipLocations[i-2][2])
                break

        points = SolveLeastSquare.leastsq(bvhUtils.HipLocations)
        curveData = bpy.data.curves.new('myCurve', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2

        # map coords to spline
        polyline = curveData.splines.new('BEZIER')
        # polyline.bezier_points
        polyline.bezier_points.add(len(points)/4)
        x,y,z = points[0]
        polyline.bezier_points[0].co = (x, -z, 0)
        x,y,z = points[1]
        polyline.bezier_points[0].handle_left = (x, -z, 0)
        x,y,z = points[2]
        polyline.bezier_points[1].handle_right = (x, -z, 0)
        x,y,z = points[3]
        polyline.bezier_points[1].co = (x, -z, 0)
        # for i, coord in enumerate(points):
        #     x,y,z = coord
        #     print(coord)
        #     if i%2 == 0:
        #         x,y,z = points[i*2+1]
        #         polyline.bezier_points[i].handle_left = (x, -z, y)
        #     else:
        #         x,y,z = points[i*2+1]
        #         polyline.bezier_points[i].handle_right = (x, -z, y)  
        # create Object
        curveOB = bpy.data.objects.new('myCurve', curveData)

        # attach to scene and validate context
        bvhUtils.curveOB = curveOB
        scn = context.scene
        scn.collection.objects.link(curveOB)

        #remove all root translate
        bvh = context.object
        obj.rotation_euler[2] = 3.14
        print(aniTime)
        for i in range(0, aniTime):
            
            sc.frame_set(i)
            obj.pose.bones['Hips'].location[0] = 0
            obj.pose.bones['Hips'].location[1] = 0
            obj.pose.bones['Hips'].location[2] = 0
            bvh.pose.bones['Hips'].keyframe_delete(data_path="location",frame = i)
            
        
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}




def register():
    bpy.utils.register_class(bvhReader)
    bpy.utils.register_class(recompute)

def unregister():
    bpy.utils.unregister_class(bvhReader)
    bpy.utils.register_class(recompute)


'''
obj.animation_data.action = None
C.object.animation_data.nla_tracks.new()
C.object.animation_data.nla_tracks.new()
C.object.animation_data.nla_tracks['NlaTrack'].strips.new("dance", 1.0, bpy.data.actions['dance'])
C.object.animation_data.nla_tracks['NlaTrack.001'].strips.new("dance", 1.0, bpy.data.actions['dance'])
'''

'''
targetobj = bpy.data.objects['']
ttc = camera.constraints.new(type='TRACK_TO')
ttc.target = targetobj
ttc.track_axis = 'TRACK_NEGATIVE_Z'
ttc.up_axis = 'UP_Y'
'''
