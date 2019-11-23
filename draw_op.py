import bpy

import bgl

import gpu

from gpu_extras.batch import batch_for_shader
from . import bvhReader


class OT_draw_operator(bpy.types.Operator):
    bl_idname = "object.draw_op"
    bl_label = "Draw operator"

    def __int__(self):
        self.draw_handle = None
        self.draw_event = None

        self.widgets = []


    def invoke(self, context, event):
        self.create_batch()
        args = (self, context)
        self.register_handlers(args, context)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        
    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_px, args, "WINDOW", "POST_VIEW")

        self.draw_event = context.window_manager.event_timer_add(0.1, window = context.window)

    def unergister_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")

        self.draw_handle = None
        self.draw_event = None

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        
        if event .type in {"ESC"}:
            return {'CANCELLED'}

        return {"PASS_THROUGH"}

    def finish(self):
        self.unergister_handlers(context)
        return {"FINISHED"}

    def create_batch(self):
        vertices = []
        for v in bvhReader.bvhUtils.HipLocations:
            vertices.append((v[0],-v[2],v[1]))

        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        self.batch = batch_for_shader(self.shader, 'LINE_STRIP', {"pos":vertices})

    def draw_callback_px(self, op, context):
        #Draw lines
        self.shader.bind()
        self.shader.uniform_float("color", (1,1,1,1))
        self.batch.draw(self.shader)
    